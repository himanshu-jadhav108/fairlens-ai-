"""
Unit tests for Structured Audit Evidence Schemas and Builder.
"""
import pytest
import math
from research.evidence.schemas import (
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
from research.evidence.builder import (
    compute_direction_and_interpretation,
    build_audit_state,
    build_evidence_from_raw_result
)


def test_metric_direction_and_interpretation_semantics():
    # 1. DPD: 0.42 -> 0.08 is decrease in magnitude and fairness IMPROVEMENT
    dpd_res = compute_direction_and_interpretation(
        metric_name="demographic_parity_difference",
        metric_type=MetricType.FAIRNESS,
        before=0.42,
        after=0.08
    )
    assert dpd_res["direction"] == Direction.DECREASE
    assert dpd_res["interpretation"] == SemanticInterpretation.IMPROVEMENT
    assert dpd_res["absolute_change"] == -0.34

    # 2. DPD: 0.05 -> 0.25 is increase in magnitude and fairness DEGRADATION
    dpd_deg = compute_direction_and_interpretation(
        metric_name="demographic_parity_difference",
        metric_type=MetricType.FAIRNESS,
        before=0.05,
        after=0.25
    )
    assert dpd_deg["direction"] == Direction.INCREASE
    assert dpd_deg["interpretation"] == SemanticInterpretation.DEGRADATION

    # 3. Disparate Impact: 0.60 -> 0.90 is increase and fairness IMPROVEMENT (closer to 1.0)
    di_res = compute_direction_and_interpretation(
        metric_name="disparate_impact",
        metric_type=MetricType.FAIRNESS,
        before=0.60,
        after=0.90
    )
    assert di_res["direction"] == Direction.INCREASE
    assert di_res["interpretation"] == SemanticInterpretation.IMPROVEMENT

    # 4. Accuracy: 0.85 -> 0.81 is decrease and performance DEGRADATION
    acc_res = compute_direction_and_interpretation(
        metric_name="accuracy",
        metric_type=MetricType.PERFORMANCE,
        before=0.85,
        after=0.81
    )
    assert acc_res["direction"] == Direction.DECREASE
    assert acc_res["interpretation"] == SemanticInterpretation.DEGRADATION

    # 5. Unchanged metric: 0.8500 -> 0.8500
    unchanged_res = compute_direction_and_interpretation(
        metric_name="accuracy",
        metric_type=MetricType.PERFORMANCE,
        before=0.8500,
        after=0.8500
    )
    assert unchanged_res["direction"] == Direction.UNCHANGED
    assert unchanged_res["interpretation"] == SemanticInterpretation.UNCHANGED


def test_audit_evidence_roundtrip_serialization():
    dataset = DatasetEvidence(
        dataset_name="adult",
        sensitive_column="sex",
        privileged_group=1,
        unprivileged_group=0,
        target_column="income",
        train_samples=1000,
        val_samples=200,
        test_samples=300
    )
    model = ModelEvidence(
        model_family="logistic_regression",
        hyperparameters={"C": 1.0},
        random_seed=42,
        mitigation_applied="correlation_remover"
    )
    base_state = AuditStateEvidence(
        state_name="baseline",
        fairness_metrics={
            "dpd": ObservedMetric("dpd", MetricType.FAIRNESS, 0.42)
        },
        performance_metrics={
            "accuracy": ObservedMetric("accuracy", MetricType.PERFORMANCE, 0.85)
        }
    )

    evidence = AuditEvidence(
        experiment_id="test_exp_001",
        dataset=dataset,
        model=model,
        baseline_state=base_state
    )

    # Compute hash
    h1 = evidence.compute_evidence_hash()
    assert len(h1) == 64  # SHA-256

    # Roundtrip
    d = evidence.to_dict()
    reconstructed = AuditEvidence.from_dict(d)
    h2 = reconstructed.compute_evidence_hash()
    assert h1 == h2
    assert reconstructed.experiment_id == "test_exp_001"
    assert reconstructed.dataset.dataset_name == "adult"
