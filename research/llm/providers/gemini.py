"""
Gemini LLM Provider for FairLens AI Research.

Adapts Google Generative AI for research experiments with explicit provenance,
deterministic parameters, and strict API-key isolation.
"""
import time
import os
from typing import Optional, Dict, Any
from .base import BaseLLMProvider
from ..schemas import LLMGenerationConfig, LLMResponse

try:
    import google.generativeai as genai
    _GENAI_AVAILABLE = True
    _GENAI_VERSION = getattr(genai, "__version__", "unknown")
except ImportError:
    genai = None
    _GENAI_AVAILABLE = False
    _GENAI_VERSION = "not_installed"


class GeminiProvider(BaseLLMProvider):
    """
    Research-grade provider for Google Gemini API.
    Does NOT modify production backend files; operates as an isolated research adapter.
    """

    def __init__(self, api_key: Optional[str] = None):
        if not _GENAI_AVAILABLE:
            raise ImportError(
                "google-generativeai package is not installed. "
                "Install it via: pip install google-generativeai"
            )
        self._api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self._api_key:
            raise ValueError(
                "GEMINI_API_KEY is not set. Please set the GEMINI_API_KEY environment variable. "
                "For testing without an API key, use MockLLMProvider."
            )
        genai.configure(api_key=self._api_key)

    @property
    def provider_name(self) -> str:
        return "gemini"

    @property
    def sdk_version(self) -> str:
        return f"google-generativeai-{_GENAI_VERSION}"

    def generate(
        self,
        prompt: str,
        config: Optional[LLMGenerationConfig] = None
    ) -> LLMResponse:
        """
        Executes generation using Gemini API with exact research configuration.
        """
        cfg = config or LLMGenerationConfig()
        start_time = time.time()

        gen_config = {
            "temperature": cfg.temperature,
            "max_output_tokens": cfg.max_output_tokens,
            "top_p": cfg.top_p,
        }

        # Initialize GenerativeModel
        actual_model_name = cfg.model_name
        model = genai.GenerativeModel(
            model_name=actual_model_name,
            generation_config=gen_config,
            system_instruction=cfg.system_instruction
        )

        max_retries = 4
        response = None
        for attempt in range(max_retries + 1):
            try:
                response = model.generate_content(prompt)
                break
            except Exception as e:
                err_str = str(e).lower()
                if ("generaterequestsperday" in err_str or "perdayperproject" in err_str) and actual_model_name != "gemini-flash-lite-latest":
                    print(f"[*] GeminiProvider: Daily quota reached for {actual_model_name}. Switching to available model 'gemini-flash-lite-latest'...")
                    actual_model_name = "gemini-flash-lite-latest"
                    model = genai.GenerativeModel(
                        model_name=actual_model_name,
                        generation_config=gen_config,
                        system_instruction=cfg.system_instruction
                    )
                    continue
                elif ("429" in err_str or "resourceexhausted" in err_str or "rate limit" in err_str) and attempt < max_retries:
                    sleep_time = 15 * (attempt + 1)
                    print(f"[*] GeminiProvider: Rate limit encountered. Pausing {sleep_time}s for quota replenishment (attempt {attempt + 1}/{max_retries})...")
                    time.sleep(sleep_time)
                else:
                    raise RuntimeError(
                        f"Gemini API generation failed after {round(time.time() - start_time, 3)}s: {e}"
                    )

        latency = round(time.time() - start_time, 3)

        finish_reason = "STOP"
        if hasattr(response, "candidates") and response.candidates:
            finish_reason = str(getattr(response.candidates[0], "finish_reason", "STOP"))

        text = ""
        try:
            text = response.text
        except Exception:
            if hasattr(response, "candidates") and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, "content") and hasattr(candidate.content, "parts"):
                    parts_text = [getattr(p, "text", "") for p in candidate.content.parts if hasattr(p, "text")]
                    text = "".join(parts_text)

        if not text.strip():
            raise RuntimeError(
                f"Gemini API returned an empty explanation (finish_reason: {finish_reason}). "
                f"Empty responses are not permitted to enter the research evaluation pipeline."
            )

        # Extract usage metadata if available
        usage = getattr(response, "usage_metadata", None)
        prompt_tokens = getattr(usage, "prompt_token_count", None) if usage else None
        completion_tokens = getattr(usage, "candidates_token_count", None) if usage else None

        return LLMResponse(
            raw_text=text,
            provider_name=self.provider_name,
            model_name=actual_model_name,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            latency_seconds=latency,
            finish_reason=finish_reason,
            metadata={
                "temperature": cfg.temperature,
                "max_output_tokens": cfg.max_output_tokens,
                "top_p": cfg.top_p,
                "seed": cfg.seed
            }
        )
