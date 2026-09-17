"""
LLM Providers registry and exports.
"""
from typing import Dict, Type
from .base import BaseLLMProvider
from .mock import MockLLMProvider

try:
    from .gemini import GeminiProvider
    _HAS_GEMINI = True
except Exception:
    GeminiProvider = None
    _HAS_GEMINI = False


def get_llm_provider(name: str, **kwargs) -> BaseLLMProvider:
    """Factory to instantiate LLM providers by name."""
    provider_lower = name.lower()
    if provider_lower == "mock":
        return MockLLMProvider(**kwargs)
    elif provider_lower == "gemini":
        if not _HAS_GEMINI or GeminiProvider is None:
            raise ImportError("GeminiProvider is not available. Check google-generativeai installation.")
        return GeminiProvider(**kwargs)
    else:
        raise ValueError(f"Unknown LLM provider: '{name}'. Supported: 'mock', 'gemini'.")


__all__ = ["BaseLLMProvider", "MockLLMProvider", "GeminiProvider", "get_llm_provider"]
