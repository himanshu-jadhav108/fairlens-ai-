"""
LLM Generation Schemas and Provenance Records.
"""
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional
import datetime


@dataclass
class LLMGenerationConfig:
    """Configurable generation parameters for LLM providers."""
    model_name: str = "gemini-2.5-flash"
    temperature: float = 0.2
    max_output_tokens: int = 1500
    top_p: float = 0.95
    seed: Optional[int] = 42
    system_instruction: Optional[str] = None


@dataclass
class LLMResponse:
    """Standardized response from an LLM provider."""
    raw_text: str
    provider_name: str
    model_name: str
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    latency_seconds: Optional[float] = None
    finish_reason: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExplanationRecord:
    """Complete provenance record for an explanation generation run."""
    experiment_id: str
    dataset_name: str
    model_name: str
    mitigation_name: Optional[str]
    audit_state: str  # "baseline", "mitigated", or "comparison"
    llm_provider: str
    llm_model: str
    sdk_version: str
    prompt_id: str
    prompt_version: str
    generation_parameters: Dict[str, Any]
    input_evidence_hash: str
    output_text: str
    timestamp_utc: str
    git_commit_hash: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
