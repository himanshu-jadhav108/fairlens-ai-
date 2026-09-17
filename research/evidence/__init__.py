"""
Evidence module exports.
"""
from .schemas import (
    AuditEvidence,
    AuditStateEvidence,
    DatasetEvidence,
    ModelEvidence,
    ObservedMetric,
    MetricComparison,
    FeatureImportanceEvidence,
    SHAPAuditEvidence,
    MetricType,
    Direction,
    SemanticInterpretation
)
from .builder import (
    build_evidence_from_raw_result,
    build_audit_state,
    compute_direction_and_interpretation
)
from .metric_semantics import (
    MetricSemantics,
    METRIC_REGISTRY,
    get_metric_semantics
)


__all__ = [
    "AuditEvidence",
    "AuditStateEvidence",
    "DatasetEvidence",
    "ModelEvidence",
    "ObservedMetric",
    "MetricComparison",
    "FeatureImportanceEvidence",
    "SHAPAuditEvidence",
    "MetricType",
    "Direction",
    "SemanticInterpretation",
    "build_evidence_from_raw_result",
    "build_audit_state",
    "compute_direction_and_interpretation",
    "MetricSemantics",
    "METRIC_REGISTRY",
    "get_metric_semantics"
]
