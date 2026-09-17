"""
Abstract Base LLM Provider.
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from ..schemas import LLMGenerationConfig, LLMResponse


class BaseLLMProvider(ABC):
    """Abstract interface for all research LLM providers."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of the provider (e.g., 'gemini', 'mock')."""
        pass

    @property
    @abstractmethod
    def sdk_version(self) -> str:
        """Version of the underlying client SDK."""
        pass

    @abstractmethod
    def generate(
        self,
        prompt: str,
        config: Optional[LLMGenerationConfig] = None
    ) -> LLMResponse:
        """
        Executes text generation using the configured LLM provider.
        Must return a standardized LLMResponse.
        """
        pass
