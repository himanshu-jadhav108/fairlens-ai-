"""
Explanation Generator with Full Provenance Recording.
Combines structured AuditEvidence, versioned prompts, and LLMProvider to generate
natural-language explanations while strictly tracking input hashes, parameters, and outputs.
"""
import os
import json
import datetime
import subprocess
from typing import Optional, Dict, Any, Tuple
from ..evidence.schemas import AuditEvidence
from .schemas import LLMGenerationConfig, ExplanationRecord, LLMResponse
from .providers.base import BaseLLMProvider
from .prompts.registry import build_prompt


def get_git_commit_hash() -> str:
    """Safely obtain Git commit hash."""
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            stderr=subprocess.DEVNULL
        ).decode("ascii").strip()
        return commit
    except Exception:
        return "git_commit_unavailable"


class ExplanationGenerator:
    """Orchestrates generation of natural-language explanations with full provenance."""

    def __init__(
        self,
        provider: BaseLLMProvider,
        config: Optional[LLMGenerationConfig] = None
    ):
        self.provider = provider
        self.config = config or LLMGenerationConfig()

    def generate_explanation(
        self,
        evidence: AuditEvidence,
        prompt_id: str = "combined_audit_v1",
        audit_state: str = "comparison",
        output_dir: Optional[str] = "research/results/raw"
    ) -> ExplanationRecord:
        """
        Generates explanation and returns a complete ExplanationRecord.
        Optionally saves raw output to results directory.
        """
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        git_hash = get_git_commit_hash()
        evidence_hash = evidence.compute_evidence_hash()

        prompt_str = build_prompt(evidence, prompt_id=prompt_id)

        # Call provider
        response: LLMResponse = self.provider.generate(prompt_str, config=self.config)

        record = ExplanationRecord(
            experiment_id=evidence.experiment_id,
            dataset_name=evidence.dataset.dataset_name,
            model_name=evidence.model.model_family,
            mitigation_name=evidence.model.mitigation_applied,
            audit_state=audit_state,
            llm_provider=self.provider.provider_name,
            llm_model=response.model_name,
            sdk_version=self.provider.sdk_version,
            prompt_id=prompt_id,
            prompt_version="v1",
            generation_parameters={
                "temperature": self.config.temperature,
                "max_output_tokens": self.config.max_output_tokens,
                "top_p": self.config.top_p,
                "seed": self.config.seed
            },
            input_evidence_hash=evidence_hash,
            output_text=response.raw_text,
            timestamp_utc=timestamp,
            git_commit_hash=git_hash,
            metadata={
                "latency_seconds": response.latency_seconds,
                "finish_reason": response.finish_reason,
                "prompt_tokens": response.prompt_tokens,
                "completion_tokens": response.completion_tokens,
                **response.metadata
            }
        )

        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            out_filename = f"explanation__{record.experiment_id}__{record.llm_provider}__{record.prompt_id}.json"
            out_path = os.path.join(output_dir, out_filename)
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(record.to_dict(), f, indent=2)

        return record
