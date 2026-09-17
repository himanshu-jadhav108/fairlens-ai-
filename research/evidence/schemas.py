"""
Structured Audit Evidence Schemas for FairLens AI Research.

This module defines machine-readable schemas for evidence provided to LLMs and
evaluators, enforcing a strict separation between:
1. OBSERVED VALUE: The empirical measurement computed on audit splits.
2. DERIVED VALUE: Explicit mathematical derivations (deltas, ratios, rankings).
3. INTERPRETATION: Metric-specific domain meaning (fairness improvement vs degradation).
"""
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional
from enum import Enum
import hashlib
import json


class MetricType(str, Enum):
    FAIRNESS = "fairness"
    PERFORMANCE = "performance"


class Direction(str, Enum):
    INCREASE = "increase"
    DECREASE = "decrease"
    UNCHANGED = "unchanged"


class SemanticInterpretation(str, Enum):
    IMPROVEMENT = "improvement"
    DEGRADATION = "degradation"
    UNCHANGED = "unchanged"
    AMBIGUOUS = "ambiguous"


@dataclass
class ObservedMetric:
    """An empirically measured value."""
    metric_name: str
    metric_type: MetricType
    value: Optional[float]
    is_defined: bool = True
    subgroup: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MetricComparison:
    """
    Structured comparison between baseline and mitigated audit states.
    Explicitly distinguishes observed values, derived mathematical values,
    and domain semantic interpretation.
    """
    metric_name: str
    metric_type: MetricType
    # Observed values
    before: Optional[float]
    after: Optional[float]
    # Derived values
    absolute_change: Optional[float]
    relative_change: Optional[float]
    direction: Direction
    # Interpretation
    interpretation: SemanticInterpretation
    ideal_target: float
    semantics_rationale: str


@dataclass
class FeatureImportanceEvidence:
    """SHAP attribution evidence for a single feature."""
    feature_name: str
    mean_abs_shap: float
    rank: int
    attribution_direction: Optional[str] = None  # "positive", "negative", or "mixed"


@dataclass
class SHAPAuditEvidence:
    """SHAP explainer evidence."""
    explainer_type: str
    n_eval_samples: int
    n_background_samples: int
    ranked_features: List[FeatureImportanceEvidence] = field(default_factory=list)
    top_k_features: List[str] = field(default_factory=list)
    subgroup_top_features: Dict[str, List[str]] = field(default_factory=dict)


@dataclass
class DatasetEvidence:
    """Authoritative metadata and subgroup definitions of the audited dataset."""
    dataset_name: str
    sensitive_column: str
    privileged_group: Any
    unprivileged_group: Any
    target_column: str
    train_samples: int
    val_samples: int
    test_samples: int
    is_synthetic_benchmark: bool = False


@dataclass
class ModelEvidence:
    """Model architecture and training configuration."""
    model_family: str
    hyperparameters: Dict[str, Any]
    random_seed: int
    mitigation_applied: Optional[str] = None
    mitigation_strategy: Optional[str] = None
    mitigation_parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AuditStateEvidence:
    """Audit evidence for a single model state (baseline or mitigated)."""
    state_name: str  # "baseline" or "mitigated"
    fairness_metrics: Dict[str, ObservedMetric]
    performance_metrics: Dict[str, ObservedMetric]
    shap_evidence: Optional[SHAPAuditEvidence] = None


@dataclass
class AuditEvidence:
    """
    Complete structured audit evidence container passed to LLM and evaluators.
    Contains canonical ground truth evidence for an experiment.
    """
    experiment_id: str
    dataset: DatasetEvidence
    model: ModelEvidence
    baseline_state: AuditStateEvidence
    mitigated_state: Optional[AuditStateEvidence] = None
    metric_comparisons: List[MetricComparison] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    def compute_evidence_hash(self) -> str:
        """Computes deterministic SHA-256 hash of the canonical evidence payload."""
        data_str = json.dumps(self.to_dict(), sort_keys=True, default=str)
        return hashlib.sha256(data_str.encode("utf-8")).hexdigest()

    @property
    def evidence_hash(self) -> str:
        """Convenience property returning SHA-256 evidence hash."""
        return self.compute_evidence_hash()

    def to_dict(self) -> Dict[str, Any]:
        """Convert dataclass to dictionary."""
        return asdict(self)


    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AuditEvidence":
        """Reconstruct AuditEvidence from dictionary."""
        # Convert nested dicts to dataclasses
        dataset = DatasetEvidence(**data["dataset"])
        model = ModelEvidence(**data["model"])

        def parse_audit_state(s_dict: Optional[Dict[str, Any]]) -> Optional[AuditStateEvidence]:
            if not s_dict:
                return None
            f_metrics = {}
            for k, v in s_dict["fairness_metrics"].items():
                f_metrics[k] = ObservedMetric(
                    metric_name=v["metric_name"],
                    metric_type=MetricType(v["metric_type"]),
                    value=v["value"],
                    is_defined=v.get("is_defined", True),
                    subgroup=v.get("subgroup"),
                    details=v.get("details", {})
                )
            p_metrics = {}
            for k, v in s_dict["performance_metrics"].items():
                p_metrics[k] = ObservedMetric(
                    metric_name=v["metric_name"],
                    metric_type=MetricType(v["metric_type"]),
                    value=v["value"],
                    is_defined=v.get("is_defined", True),
                    subgroup=v.get("subgroup"),
                    details=v.get("details", {})
                )
            shap_ev = None
            if s_dict.get("shap_evidence"):
                ranked = [FeatureImportanceEvidence(**item) for item in s_dict["shap_evidence"]["ranked_features"]]
                shap_ev = SHAPAuditEvidence(
                    explainer_type=s_dict["shap_evidence"]["explainer_type"],
                    n_eval_samples=s_dict["shap_evidence"]["n_eval_samples"],
                    n_background_samples=s_dict["shap_evidence"]["n_background_samples"],
                    ranked_features=ranked,
                    top_k_features=s_dict["shap_evidence"].get("top_k_features", []),
                    subgroup_top_features=s_dict["shap_evidence"].get("subgroup_top_features", {})
                )
            return AuditStateEvidence(
                state_name=s_dict["state_name"],
                fairness_metrics=f_metrics,
                performance_metrics=p_metrics,
                shap_evidence=shap_ev
            )

        baseline = parse_audit_state(data["baseline_state"])
        mitigated = parse_audit_state(data.get("mitigated_state"))

        comparisons = []
        for c in data.get("metric_comparisons", []):
            comparisons.append(MetricComparison(
                metric_name=c["metric_name"],
                metric_type=MetricType(c["metric_type"]),
                before=c["before"],
                after=c["after"],
                absolute_change=c["absolute_change"],
                relative_change=c["relative_change"],
                direction=Direction(c["direction"]),
                interpretation=SemanticInterpretation(c["interpretation"]),
                ideal_target=c["ideal_target"],
                semantics_rationale=c["semantics_rationale"]
            ))

        return cls(
            experiment_id=data["experiment_id"],
            dataset=dataset,
            model=model,
            baseline_state=baseline,
            mitigated_state=mitigated,
            metric_comparisons=comparisons,
            notes=data.get("notes", [])
        )
