"""
LLM Configuration and Environment Loading.
"""
import os
from typing import Optional
from .schemas import LLMGenerationConfig


def get_gemini_api_key() -> Optional[str]:
    """
    Safely retrieves GEMINI_API_KEY from environment variables.
    Returns None if not set. Never hardcodes keys.
    """
    return os.environ.get("GEMINI_API_KEY")


def get_default_generation_config(
    model_name: str = "gemini-2.5-flash",
    temperature: float = 0.2,
    max_output_tokens: int = 1500,
    seed: Optional[int] = 42
) -> LLMGenerationConfig:
    """Returns standard research generation config with low temperature for reproducible audits."""
    return LLMGenerationConfig(
        model_name=model_name,
        temperature=temperature,
        max_output_tokens=max_output_tokens,
        top_p=0.95,
        seed=seed,
        system_instruction=(
            "You are a rigorous, objective Machine Learning Fairness Auditor. "
            "Your task is to provide clear, faithful, and scientifically accurate natural-language "
            "explanations of quantitative fairness audit evidence. Strictly adhere to the supplied data."
        )
    )
