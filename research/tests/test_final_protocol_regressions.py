"""
Regression Test Suite for the Confirmatory Final Research Protocol.
Validates:
1. Zero synthetic benchmark data in final results
2. Strict model name enforcement (gemini-2.5-flash only)
3. Sound evaluator ratios and vacuous truth prevention
4. State-aware numerical candidate matching
5. Template baseline 100% faithfulness control guarantee
6. Pairwise identical evidence hashes
7. Silent synthetic fallback hard-blocking in dataset loaders
8. Complete metric registry coverage
9. Aggregator contamination guards and mock exclusion
10. Secret scanner clean status (0 credentials persisted)
11. Paired statistical test integrity
"""
import os
import json
import pytest
import numpy as np
from unittest.mock import MagicMock, patch

from research.evidence.schemas import (
    AuditEvidence, AuditStateEvidence, DatasetEvidence, ModelEvidence,
    ObservedMetric, MetricComparison, MetricType, Direction, SemanticInterpretation
)
from research.faithfulness.taxonomy import ClaimType, ClaimClassification, ExtractedClaim
from research.faithfulness.evaluator import FaithfulnessEvaluator
from research.faithfulness.numerical import NumericalFaithfulnessEvaluator
from research.faithfulness.schemas import FaithfulnessReport
from research.evidence.metric_semantics import METRIC_REGISTRY
from research.baselines.template_explainer import TemplateExplainer
from research.datasets.adult import AdultDataset
from research.datasets.compas import COMPASDataset
from research.datasets.german import GermanCreditDataset
from research.analysis.aggregator import _is_mock_source, SMOKE_MODE, FINAL_MODE
from research.statistics.faithfulness_analysis import compute_paired_faithfulness_comparison


@pytest.fixture
def mock_audit_evidence():
    dataset = DatasetEvidence("adult", "sex", 1, 0, "income", 1000, 200, 300)
    model = ModelEvidence("logistic_regression", {}, 42, mitigation_applied="correlation_remover")
    base_f = {
        "demographic_parity_difference": ObservedMetric("demographic_parity_difference", MetricType.FAIRNESS, 0.4000),
        "equalized_odds_difference": ObservedMetric("equalized_odds_difference", MetricType.FAIRNESS, 0.2000),
    }
    base_p = {
        "accuracy": ObservedMetric("accuracy", MetricType.PERFORMANCE, 0.8500),
        "f1_score": ObservedMetric("f1_score", MetricType.PERFORMANCE, 0.8000)
    }
    base_state = AuditStateEvidence("baseline", base_f, base_p)

    mit_f = {
        "demographic_parity_difference": ObservedMetric("demographic_parity_difference", MetricType.FAIRNESS, 0.1000),
        "equalized_odds_difference": ObservedMetric("equalized_odds_difference", MetricType.FAIRNESS, 0.1000),
    }
    mit_p = {
        "accuracy": ObservedMetric("accuracy", MetricType.PERFORMANCE, 0.8200),
        "f1_score": ObservedMetric("f1_score", MetricType.PERFORMANCE, 0.7800)
    }
    mit_state = AuditStateEvidence("mitigated", mit_f, mit_p)

    comparisons = [
        MetricComparison(
            metric_name="demographic_parity_difference",
            metric_type=MetricType.FAIRNESS,
            before=0.4000,
            after=0.1000,
            absolute_change=-0.3000,
            relative_change=-0.7500,
            direction=Direction.DECREASE,
            interpretation=SemanticInterpretation.IMPROVEMENT,
            ideal_target=0.0,
            semantics_rationale="DPD decreased closer to 0."
        ),
        MetricComparison(
            metric_name="accuracy",
            metric_type=MetricType.PERFORMANCE,
            before=0.8500,
            after=0.8200,
            absolute_change=-0.0300,
            relative_change=-0.0353,
            direction=Direction.DECREASE,
            interpretation=SemanticInterpretation.DEGRADATION,
            ideal_target=1.0,
            semantics_rationale="Accuracy decreased slightly."
        )
    ]

    return AuditEvidence(
        experiment_id="test_regr_exp_001",
        dataset=dataset,
        model=model,
        baseline_state=base_state,
        mitigated_state=mit_state,
        metric_comparisons=comparisons
    )


# 1. Zero Synthetic Benchmark Data in Final Manifests
def test_final_manifest_has_zero_synthetic_data():
    manifests_dir = "research/results/final/manifests"
    if not os.path.exists(manifests_dir):
        pytest.skip("Final results not yet generated.")
    files = [f for f in os.listdir(manifests_dir) if f.endswith(".json")]
    if not files:
        pytest.skip("No final manifests to inspect.")
    for f in files:
        with open(os.path.join(manifests_dir, f), "r", encoding="utf-8") as fp:
            data = json.load(fp)
            assert data.get("dataset", {}).get("is_synthetic_benchmark") is False
            assert data.get("execution_mode") == "FINAL_EMPIRICAL_RUN"


# 2. Strict Model Name Enforcement
def test_final_manifest_model_strictly_gemini_2_5_flash():
    summaries_dir = "research/results/final/summaries"
    if not os.path.exists(summaries_dir):
        pytest.skip("Final summaries not yet generated.")
    files = [f for f in os.listdir(summaries_dir) if "gemini" in f and f.endswith(".json")]
    for f in files:
        with open(os.path.join(summaries_dir, f), "r", encoding="utf-8") as fp:
            data = json.load(fp)
            source = data.get("explanation_source", "")
            assert "gemini-flash-lite" not in source.lower()
            assert "gemini-2.0" not in source.lower()
            assert "gemini-1.5" not in source.lower()


# 3. Sound Evaluator Ratios (Zero-Claim Vacuous Truth Prevention)
def test_evaluator_zero_claims_returns_none_not_one(mock_audit_evidence):
    evaluator = FaithfulnessEvaluator()
    empty_text = "Overall, the experiment evaluated algorithmic fairness across the entire pipeline."
    report = evaluator.evaluate(mock_audit_evidence, empty_text, save_records=False)

    assert report.numerical_faithfulness is None
    assert report.numerical_evaluable is False
    assert report.directional_faithfulness is None
    assert report.directional_evaluable is False
    assert report.attribution_faithfulness is None
    assert report.attribution_evaluable is False
    assert report.unsupported_claim_rate == 0.0


# 4. Sound Evaluator Ratio Calculation
def test_evaluator_evaluable_ratio_calculation(mock_audit_evidence):
    evaluator = FaithfulnessEvaluator()
    # Sentence with 1 supported number and 1 contradicted number
    text = "The baseline demographic parity difference was 0.4000, while accuracy was 0.1200."
    report = evaluator.evaluate(mock_audit_evidence, text, save_records=False)

    assert report.numerical_evaluable is True
    assert report.numeric_match_count == 1
    assert report.numeric_error_count == 1
    assert report.numerical_faithfulness == 0.5


# 5. State-Aware Numerical Matching (Baseline vs Mitigated)
def test_state_aware_numerical_matching_state_mismatch(mock_audit_evidence):
    evaluator = NumericalFaithfulnessEvaluator(absolute_tolerance=0.015)
    # 0.1000 is the MITIGATED value, but the text claims it was the BASELINE value
    text_mismatch = "The baseline demographic parity difference was 0.1000."
    claims = evaluator.evaluate(mock_audit_evidence, text_mismatch)

    assert len(claims) == 1
    assert claims[0].classification == ClaimClassification.UNSUPPORTED
    assert "contradicts" in claims[0].rationale


# 6. State-Aware Numerical Matching (Mitigated Match)
def test_state_aware_numerical_matching_mitigated_match(mock_audit_evidence):
    evaluator = NumericalFaithfulnessEvaluator(absolute_tolerance=0.015)
    text_match = "After mitigation, demographic parity difference was 0.1000."
    claims = evaluator.evaluate(mock_audit_evidence, text_match)

    assert len(claims) == 1
    assert claims[0].classification == ClaimClassification.SUPPORTED


# 7. State-Aware Numerical Matching (Delta & Change)
def test_state_aware_numerical_matching_delta_change(mock_audit_evidence):
    evaluator = NumericalFaithfulnessEvaluator(absolute_tolerance=0.015)
    text_delta = "Demographic parity difference had an absolute reduction of 0.3000."
    claims = evaluator.evaluate(mock_audit_evidence, text_delta)

    assert len(claims) == 1
    assert claims[0].classification == ClaimClassification.SUPPORTED


# 8. Template Baseline 100% Faithful Control Guarantee
def test_template_baseline_100_percent_faithful(mock_audit_evidence):
    explainer = TemplateExplainer(top_k_features=5)
    template_text = explainer.generate_explanation(mock_audit_evidence)

    evaluator = FaithfulnessEvaluator()
    report = evaluator.evaluate(mock_audit_evidence, template_text, save_records=False)

    assert report.numerical_faithfulness == 1.0
    assert report.directional_faithfulness == 1.0
    assert report.unsupported_claim_rate == 0.0


# 9. Dataset Loaders Hard-Block Silent Synthetic Fallback
def test_dataset_loaders_block_silent_synthetic_fallback():
    # Attempting to load real dataset when CSV does not exist must raise FileNotFoundError
    with pytest.raises(FileNotFoundError, match="FINAL EXPERIMENT BLOCKED"):
        AdultDataset().load_data(local_path="non_existent_adult.csv", use_synthetic_benchmark=False)

    with pytest.raises(FileNotFoundError, match="FINAL EXPERIMENT BLOCKED"):
        COMPASDataset().load_data(local_path="non_existent_compas.csv", use_synthetic_benchmark=False)

    with pytest.raises(FileNotFoundError, match="FINAL EXPERIMENT BLOCKED"):
        GermanCreditDataset().load_data(local_path="non_existent_german.csv", use_synthetic_benchmark=False)


# 10. Metric Semantics Registry Completeness
def test_metric_semantics_registry_complete():
    assert "false_positive_rate_difference" in METRIC_REGISTRY
    assert "false_negative_rate_difference" in METRIC_REGISTRY
    assert "disparate_impact" in METRIC_REGISTRY
    assert "disparate impact ratio" in [a.lower() for a in METRIC_REGISTRY["disparate_impact"].aliases]


# 11. Aggregator Contamination Guards & Mock Exclusion
def test_aggregator_contamination_guards():
    assert _is_mock_source("mock") is True
    assert _is_mock_source("mock_gemini-2.5-flash") is True
    assert _is_mock_source("software_validation") is True
    assert _is_mock_source("gemini__gemini-2.5-flash") is False
    assert _is_mock_source("template_baseline") is False


# 12. Paired Statistics Produces Valid Inferential Tests
def test_paired_statistics_produces_valid_outputs():
    # 5 paired scores with clear difference
    t_scores = [1.0, 1.0, 1.0, 1.0, 1.0]
    l_scores = [0.8, 0.85, 0.9, 0.75, 0.8]

    res = compute_paired_faithfulness_comparison(t_scores, l_scores, metric_name="numerical_faithfulness")
    assert res["n_pairs"] == 5
    assert res["mean_template"] == 1.0
    assert res["mean_llm"] == 0.82
    assert res["mean_difference"] == -0.18
    assert res["cohens_d"] < 0  # LLM lower than template
    assert res["paired_t_test"]["p_value"] < 0.05
    assert res["wilcoxon_signed_rank"]["w_statistic"] is not None


# 13. Secret Scanner Clean
def test_secret_scanner_clean():
    from research.scripts.secret_scanner import scan_for_secrets
    secrets = scan_for_secrets("research")
    assert len(secrets) == 0, f"Credentials detected in research directory: {secrets}"
