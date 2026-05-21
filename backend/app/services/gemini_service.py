import json
import logging
import google.generativeai as genai
from typing import Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from google.api_core.exceptions import ResourceExhausted, InternalServerError, ServiceUnavailable

from ..core.config import settings
from ..prompts.fairness_prompts import build_bias_explanation_prompt, BIAS_EXPLANATION_JSON_SCHEMA

logger = logging.getLogger(__name__)

# Configure the Gemini API securely using the validated environment variable
genai.configure(api_key=settings.GEMINI_API_KEY)

# Initialize the model with structured JSON enforcement
# We use gemini-2.5-flash as it is supported by the new genai endpoints
_model = genai.GenerativeModel(
    "gemini-2.5-flash",
    generation_config={
        "response_mime_type": "application/json",
        "response_schema": BIAS_EXPLANATION_JSON_SCHEMA,
    }
)

@retry(
    stop=stop_after_attempt(4),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((ResourceExhausted, InternalServerError, ServiceUnavailable)),
    before_sleep=lambda retry_state: logger.warning(
        f"Retrying Gemini API call. Attempt {retry_state.attempt_number} failed. Retrying..."
    )
)
def _call_gemini_with_retry(prompt: str) -> str:
    """
    Internal function to call Gemini with robust exponential backoff.
    It retries on 429 (ResourceExhausted) and 5xx (InternalServerError, ServiceUnavailable).
    """
    response = _model.generate_content(prompt)
    return response.text

def generate_bias_explanation(metrics: Dict[str, Any], shap_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a human-readable explanation of bias findings using Gemini.
    """
    dpd = metrics.get('demographic_parity_difference', 0)
    eod = metrics.get('equalized_odds_difference', 0)
    acc = metrics.get('accuracy', 0)
    
    prompt = build_bias_explanation_prompt(metrics, shap_data)
    
    try:
        response_text = _call_gemini_with_retry(prompt)
        
        # Because we enforce response_mime_type="application/json", we can safely load this.
        parsed_response = json.loads(response_text)
        return parsed_response

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Gemini JSON response: {e}")
        return _fallback_response(dpd, eod, "Error parsing model response.")
    except Exception as e:
        logger.error(f"Gemini API failed permanently after retries: {e}")
        return _fallback_response(dpd, eod, f"AI Explanation Failed. Ensure API key is correct and valid. Error: {e}")

def _fallback_response(dpd: float, eod: float, error_msg: str) -> Dict[str, Any]:
    """Provides a graceful degradation if the AI completely fails."""
    return {
        "explanation": f"## AI Explanation Unavailable\n\n**Note**: {error_msg}\n\nDemographic Parity Difference: {dpd:.4f}\nEqualized Odds Difference: {eod:.4f}.",
        "summary": {
            "verdict": "fair" if (dpd < 0.05 and eod < 0.05) else "biased",
            "dpd_severity": "low" if dpd < 0.05 else "moderate" if dpd < 0.15 else "high",
            "eod_severity": "low" if eod < 0.05 else "moderate" if eod < 0.15 else "high",
        }
    }
