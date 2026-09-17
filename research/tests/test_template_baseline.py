"""
Unit tests for Deterministic Template Explainer Baseline.
"""
import pytest
from research.baselines.template_explainer import TemplateExplainer
from research.evidence.schemas import (
    AuditEvidence, AuditStateEvidence, DatasetEvidence, ModelEvidence,
    ObservedMetric, MetricComparison, MetricType, Direction, SemanticInterpretation
)


def test_template_explainer_generates_faithful_text():
    dataset = DatasetEvidence("adult", "sex", 1, 0, "income", 1000, 200, 300)
    model = ModelEvidence("logistic_regression", {}, 42, mitigation_applied="correlation_remover")
    base_state = AuditStateEvidence(
        "baseline",
        {"demographic_parity_difference": ObservedMetric("demographic_parity_difference", MetricType.FAIRNESS, 0.4200)},
        {"accuracy": ObservedMetric("accuracy", MetricType.PERFORMANCE, 0.8500)}
    )
    mit_state = AuditStateEvidence(
        "mitigated",
        {"demographic_parity_difference": ObservedMetric("demographic_parity_difference", MetricType.FAIRNESS, 0.0800)},
        {"accuracy": ObservedMetric("accuracy", MetricType.PERFORMANCE, 0.8200)}
    )
    comp = [
        MetricComparison(
            "demographic_parity_difference",
            MetricType.FAIRNESS,
            0.4200,
            0.0800,
            -0.3400,
            -0.8095,
            Direction.DECREASE,
            SemanticInterpretation.IMPROVEMENT,
            0.0,
            "DPD moved closer to 0.0."
        )
    ]
    evidence = AuditEvidence("exp_tmpl_01", dataset, model, base_state, mit_state, comp)

    explainer = TemplateExplainer(top_k_features=5)
    text = explainer.generate_explanation(evidence)

    assert "0.4200" in text
    assert "0.0800" in text
    assert "-0.3400" in text
    assert "decrease" in text
    assert "improvement" in text
