"""
Deterministic Mock LLM Provider for CI and Offline Smoke Tests.
Zero API key or internet access required.
"""
import time
from typing import Optional, Dict, Any
from .base import BaseLLMProvider
from ..schemas import LLMGenerationConfig, LLMResponse


class MockLLMProvider(BaseLLMProvider):
    """
    Mock LLM provider generating deterministic responses.
    Supports injecting specific error patterns for testing faithfulness evaluators.
    """

    def __init__(self, mode: str = "faithful", custom_response: Optional[str] = None):
        """
        Args:
            mode: "faithful", "numerical_error", "directional_error", "attribution_error",
                  "causal_claim", or "custom".
            custom_response: Pre-defined string if mode=="custom".
        """
        self.mode = mode
        self.custom_response = custom_response

    @property
    def provider_name(self) -> str:
        return "mock"

    @property
    def sdk_version(self) -> str:
        return "mock-1.0.0"

    def generate(
        self,
        prompt: str,
        config: Optional[LLMGenerationConfig] = None
    ) -> LLMResponse:
        start_time = time.time()
        cfg = config or LLMGenerationConfig()

        if self.mode == "custom" and self.custom_response is not None:
            text = self.custom_response
        elif self.mode == "numerical_error":
            text = (
                "The audit shows baseline demographic parity difference was 0.9999, which is extremely high. "
                "Following mitigation, the demographic parity difference dropped to 0.0812. "
                "Accuracy decreased slightly."
            )
        elif self.mode == "directional_error":
            text = (
                "Following bias mitigation, demographic parity difference increased significantly from baseline. "
                "The disparate impact worsened further away from parity."
            )
        elif self.mode == "attribution_error":
            text = (
                "SHAP analysis indicates that non_existent_synthetic_feature was the single most influential predictor, "
                "dominating model decisions."
            )
        elif self.mode == "causal_claim":
            text = (
                "The audit demonstrates that the applicant's age directly caused the algorithm to reject credit applications, "
                "proving systemic discriminatory intent."
            )
        else:
            # Standard faithful mock response constructed to explain common structured metrics
            text = (
                "Fairness Audit Summary:\n"
                "The evaluated model exhibited a baseline demographic parity difference of 0.4200 and accuracy of 0.8500. "
                "After applying bias mitigation, demographic parity difference decreased to 0.0800, representing a significant "
                "fairness improvement toward parity. Model accuracy decreased moderately to 0.8200. "
                "SHAP feature importance analysis confirms that feature_0 and feature_1 were the top predictors governing outcomes."
            )

        latency = round(time.time() - start_time, 4)
        return LLMResponse(
            raw_text=text,
            provider_name=self.provider_name,
            model_name=cfg.model_name,
            prompt_tokens=len(prompt.split()),
            completion_tokens=len(text.split()),
            latency_seconds=latency,
            finish_reason="STOP",
            metadata={"mock_mode": self.mode}
        )
