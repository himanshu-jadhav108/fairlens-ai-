"""
Comprehensive Adversarial Test Suite for FairLens AI Research.
Validates numerical precision, cross-metric isolation, directional semantics,
qualitative magnitude routing, attribution ties, unsupported claims,
provenance determinism, and aggregation safeguards.
"""
import pytest
import json
from unittest.mock import MagicMock, patch

from research.evidence.schemas import (
    AuditEvidence, DatasetEvidence, ModelEvidence,
    AuditStateEvidence, ObservedMetric, MetricComparison,
    SHAPAuditEvidence, FeatureImportanceEvidence,
    MetricType, Direction, SemanticInterpretation
)
from research.faithfulness.taxonomy import ClaimType, ClaimClassification
from research.faithfulness.numerical import NumericalFaithfulnessEvaluator
from research.faithfulness.directional import DirectionalFaithfulnessEvaluator
from research.faithfulness.attribution import AttributionFaithfulnessEvaluator
from research.faithfulness.unsupported_claims import UnsupportedClaimsDetector
from research.faithfulness.evaluator import FaithfulnessEvaluator
from research.faithfulness.coverage import EvidenceCoverageEvaluator
from research.baselines.template_explainer import TemplateExplainer
from research.statistics.faithfulness_analysis import compute_paired_faithfulness_comparison
from research.llm.providers.gemini import GeminiProvider
from research.llm.schemas import LLMGenerationConfig
from research.analysis.aggregator import aggregate_raw_results, aggregate_faithfulness_summaries


@pytest.fixture
def adversarial_evidence():
    """Builds a rich, canonical AuditEvidence instance with controlled ground truth."""
    dataset = DatasetEvidence(
        dataset_name="adult",
        sensitive_column="sex",
        privileged_group="Male",
        unprivileged_group="Female",
        target_column="income",
        train_samples=1000,
        val_samples=200,
        test_samples=300,
        is_synthetic_benchmark=True
    )
    model = ModelEvidence(
        model_family="logistic_regression",
        hyperparameters={"C": 1.0},
        random_seed=42,
        mitigation_applied="correlation_remover",
        mitigation_strategy="preprocessing"
    )
    baseline_state = AuditStateEvidence(
        state_name="baseline",
        fairness_metrics={
            "demographic_parity_difference": ObservedMetric("demographic_parity_difference", MetricType.FAIRNESS, 0.4200),
            "equalized_odds_difference": ObservedMetric("equalized_odds_difference", MetricType.FAIRNESS, -0.0500),
            "disparate_impact_ratio": ObservedMetric("disparate_impact_ratio", MetricType.FAIRNESS, 0.8200)
        },
        performance_metrics={
            "accuracy": ObservedMetric("accuracy", MetricType.PERFORMANCE, 0.9100),
            "f1_score": ObservedMetric("f1_score", MetricType.PERFORMANCE, 0.8000),
            "roc_auc": ObservedMetric("roc_auc", MetricType.PERFORMANCE, 0.8000)
        }
    )
    mitigated_state = AuditStateEvidence(
        state_name="mitigated",
        fairness_metrics={
            "demographic_parity_difference": ObservedMetric("demographic_parity_difference", MetricType.FAIRNESS, 0.0100),
            "equalized_odds_difference": ObservedMetric("equalized_odds_difference", MetricType.FAIRNESS, 0.0200),
            "disparate_impact_ratio": ObservedMetric("disparate_impact_ratio", MetricType.FAIRNESS, 0.9800)
        },
        performance_metrics={
            "accuracy": ObservedMetric("accuracy", MetricType.PERFORMANCE, 0.8300),
            "f1_score": ObservedMetric("f1_score", MetricType.PERFORMANCE, 0.7600),
            "roc_auc": ObservedMetric("roc_auc", MetricType.PERFORMANCE, 0.7700)
        },
        shap_evidence=SHAPAuditEvidence(
            explainer_type="ExactExplainer",
            n_eval_samples=50,
            n_background_samples=25,
            ranked_features=[
                FeatureImportanceEvidence("capital_gain", 0.12500, 1),
                FeatureImportanceEvidence("education_num", 0.12500, 2),  # Tied with rank 1
                FeatureImportanceEvidence("age", 0.08200, 3),
                FeatureImportanceEvidence("hours_per_week", 0.05100, 4),
                FeatureImportanceEvidence("marriage", 0.03000, 5),
                FeatureImportanceEvidence("occupation", 0.01200, 6)
            ],
            top_k_features=["capital_gain", "education_num", "age", "hours_per_week", "marriage"]
        )
    )
    comparisons = [
        MetricComparison(
            metric_name="demographic_parity_difference",
            metric_type=MetricType.FAIRNESS,
            before=0.4200,
            after=0.0100,
            absolute_change=-0.4100,
            relative_change=-0.9762,
            direction=Direction.DECREASE,
            interpretation=SemanticInterpretation.IMPROVEMENT,
            ideal_target=0.0,
            semantics_rationale="Decrease toward 0 represents greater fairness."
        ),
        MetricComparison(
            metric_name="equalized_odds_difference",
            metric_type=MetricType.FAIRNESS,
            before=-0.0500,
            after=0.0200,
            absolute_change=0.0700,
            relative_change=-1.4000,
            direction=Direction.INCREASE,
            interpretation=SemanticInterpretation.IMPROVEMENT,
            ideal_target=0.0,
            semantics_rationale="Movement toward zero represents fairness improvement."
        ),
        MetricComparison(
            metric_name="disparate_impact_ratio",
            metric_type=MetricType.FAIRNESS,
            before=0.8200,
            after=0.9800,
            absolute_change=0.1600,
            relative_change=0.1951,
            direction=Direction.INCREASE,
            interpretation=SemanticInterpretation.IMPROVEMENT,
            ideal_target=1.0,
            semantics_rationale="Increase toward 1.0 represents four-fifths rule compliance."
        ),
        MetricComparison(
            metric_name="accuracy",
            metric_type=MetricType.PERFORMANCE,
            before=0.9100,
            after=0.8300,
            absolute_change=-0.0800,
            relative_change=-0.0879,
            direction=Direction.DECREASE,
            interpretation=SemanticInterpretation.DEGRADATION,
            ideal_target=1.0,
            semantics_rationale="Performance decreased post-mitigation."
        )
    ]
    return AuditEvidence(
        experiment_id="adv_exp_001",
        dataset=dataset,
        model=model,
        baseline_state=baseline_state,
        mitigated_state=mitigated_state,
        metric_comparisons=comparisons
    )


# =====================================================================
# 1. NUMERICAL FAITHFULNESS ADVERSARIAL TESTS (CASES A - J)
# =====================================================================

def test_case_a_correct_association(adversarial_evidence):
    """Case A: Correct association of DPD=0.42 and Accuracy=0.91."""
    evaluator = NumericalFaithfulnessEvaluator()
    text = "The demographic parity difference was 0.42 and accuracy was 0.91."
    claims = evaluator.evaluate(adversarial_evidence, text)
    assert len(claims) == 2
    assert all(c.classification == ClaimClassification.SUPPORTED for c in claims)


def test_case_b_cross_metric_swap(adversarial_evidence):
    """Case B: Cross-metric swap (DPD=0.91, Accuracy=0.42) -> Both unsupported."""
    evaluator = NumericalFaithfulnessEvaluator()
    text = "The demographic parity difference was 0.91 and accuracy was 0.42."
    claims = evaluator.evaluate(adversarial_evidence, text)
    assert len(claims) == 2
    assert all(c.classification == ClaimClassification.UNSUPPORTED for c in claims)


def test_case_c_correct_value_wrong_metric(adversarial_evidence):
    """Case C: Correct value 0.42 claimed for accuracy instead of DPD -> Unsupported."""
    evaluator = NumericalFaithfulnessEvaluator()
    text = "Accuracy was 0.42."
    claims = evaluator.evaluate(adversarial_evidence, text)
    assert len(claims) == 1
    assert claims[0].classification == ClaimClassification.UNSUPPORTED


def test_case_d_rounding_within_tolerance(adversarial_evidence):
    """Case D: Rounding within scientific tolerance policy (0.015)."""
    # Create evidence where DPD is 0.4237
    adversarial_evidence.baseline_state.fairness_metrics["demographic_parity_difference"].value = 0.4237
    evaluator = NumericalFaithfulnessEvaluator(absolute_tolerance=0.015)
    text = "DPD was approximately 0.42."
    claims = evaluator.evaluate(adversarial_evidence, text)
    assert len(claims) == 1
    assert claims[0].classification == ClaimClassification.SUPPORTED
    assert claims[0].metadata["abs_diff"] <= 0.015


def test_case_e_percentage_vs_decimal(adversarial_evidence):
    """Case E: Percentage versus decimal representation (82% == 0.82) -> Supported."""
    evaluator = NumericalFaithfulnessEvaluator()
    text = "The disparate impact ratio was 82%."
    claims = evaluator.evaluate(adversarial_evidence, text)
    assert len(claims) == 1
    assert claims[0].classification == ClaimClassification.SUPPORTED
    assert claims[0].extracted_values["value"] == pytest.approx(0.82, abs=1e-4)
    assert claims[0].metadata["is_percentage_converted"] is True


def test_case_f_negative_values_and_signs(adversarial_evidence):
    """Case F: Negative metric values (equalized odds difference = -0.05)."""
    evaluator = NumericalFaithfulnessEvaluator()
    # Correct negative sign
    text_correct = "Equalized odds difference was -0.05."
    claims_correct = evaluator.evaluate(adversarial_evidence, text_correct)
    assert len(claims_correct) == 1
    assert claims_correct[0].classification == ClaimClassification.SUPPORTED

    # Inverted positive sign
    text_wrong = "Equalized odds difference was +0.05."
    claims_wrong = evaluator.evaluate(adversarial_evidence, text_wrong)
    assert len(claims_wrong) == 1
    assert claims_wrong[0].classification == ClaimClassification.UNSUPPORTED


def test_case_g_multiple_occurrences_no_leak(adversarial_evidence):
    """Case G: Values appearing across other metrics (0.80) do not support false DPD claim."""
    evaluator = NumericalFaithfulnessEvaluator()
    # Both f1_score and roc_auc are 0.80, but DPD is 0.42 / 0.01
    text = "Demographic parity difference was 0.80."
    claims = evaluator.evaluate(adversarial_evidence, text)
    assert len(claims) == 1
    assert claims[0].classification == ClaimClassification.UNSUPPORTED


def test_case_h_no_metric_association_undeterminable(adversarial_evidence):
    """Case H: Numerical claim with no associated metric -> UNDETERMINABLE."""
    evaluator = NumericalFaithfulnessEvaluator()
    text = "The value was 0.42."
    claims = evaluator.evaluate(adversarial_evidence, text)
    assert len(claims) == 1
    assert claims[0].classification == ClaimClassification.UNDETERMINABLE
    assert claims[0].ground_truth["canonical_metric"] is None


def test_case_i_multiple_numbers_in_one_sentence(adversarial_evidence):
    """Case I: Multiple numbers in one compound sentence separated by conjunctions."""
    evaluator = NumericalFaithfulnessEvaluator()
    text = "DPD changed from 0.42 to 0.01 while accuracy changed from 0.91 to 0.83."
    claims = evaluator.evaluate(adversarial_evidence, text)
    assert len(claims) == 4
    assert all(c.classification == ClaimClassification.SUPPORTED for c in claims)
    # Check metric associations
    dpd_claims = [c for c in claims if c.ground_truth["canonical_metric"] == "demographic_parity_difference"]
    acc_claims = [c for c in claims if c.ground_truth["canonical_metric"] == "accuracy"]
    assert len(dpd_claims) == 2
    assert len(acc_claims) == 2


def test_case_j_contradictory_numerical_claims(adversarial_evidence):
    """Case J: Contradictory claims are evaluated independently, not averaged or suppressed."""
    evaluator = NumericalFaithfulnessEvaluator()
    text = "DPD decreased to 0.01. However, later analysis states DPD was 0.35 after mitigation."
    claims = evaluator.evaluate(adversarial_evidence, text)
    assert len(claims) == 2
    classifications = [c.classification for c in claims]
    assert ClaimClassification.SUPPORTED in classifications
    assert ClaimClassification.UNSUPPORTED in classifications


# =====================================================================
# 2. DIRECTIONAL & MAGNITUDE ADVERSARIAL TESTS
# =====================================================================

def test_directional_mathematical_vs_normative_separation(adversarial_evidence):
    """Verifies that mathematical direction and normative domain interpretation are separate."""
    evaluator = DirectionalFaithfulnessEvaluator()
    # DPD decreased (math: decrease) and improved toward parity (normative: improvement)
    text = "Demographic parity difference decreased, representing an improvement in fairness."
    claims = evaluator.evaluate(adversarial_evidence, text)
    assert len(claims) == 2

    math_claim = next(c for c in claims if c.claim_type == ClaimType.DIRECTIONAL)
    interp_claim = next(c for c in claims if c.claim_type == ClaimType.FAIRNESS_INTERPRETATION)

    assert math_claim.classification == ClaimClassification.SUPPORTED
    assert interp_claim.classification == ClaimClassification.SUPPORTED


def test_directional_performance_degradation(adversarial_evidence):
    """Accuracy dropped from 0.91 to 0.83; claiming performance improved is unsupported."""
    evaluator = DirectionalFaithfulnessEvaluator()
    text = "Accuracy decreased, but overall performance improved."
    claims = evaluator.evaluate(adversarial_evidence, text)

    interp_claim = next(c for c in claims if c.claim_type == ClaimType.PERFORMANCE)
    assert interp_claim.classification == ClaimClassification.UNSUPPORTED


def test_qualitative_magnitude_routed_to_undeterminable(adversarial_evidence):
    """Qualitative magnitude claims MUST NOT be marked supported; routed to UNDETERMINABLE."""
    evaluator = DirectionalFaithfulnessEvaluator()
    terms = [
        "substantially", "dramatically", "drastically", "significantly",
        "slightly", "marginally", "modestly", "moderately"
    ]
    for term in terms:
        text = f"Demographic parity difference decreased {term}."
        claims = evaluator.evaluate(adversarial_evidence, text)
        mag_claims = [c for c in claims if c.claim_type == ClaimType.MAGNITUDE]
        assert len(mag_claims) == 1, f"Failed for term: {term}"
        assert mag_claims[0].classification == ClaimClassification.UNDETERMINABLE


# =====================================================================
# 3. ATTRIBUTION ADVERSARIAL TESTS
# =====================================================================

def test_attribution_tied_rank1_supported(adversarial_evidence):
    """Features with equal top SHAP importance (ties) must both be supported as rank 1."""
    evaluator = AttributionFaithfulnessEvaluator(top_k=5)
    # capital_gain and education_num are tied with mean |SHAP| = 0.12500
    text1 = "The most influential feature was capital_gain."
    text2 = "The most influential feature was education_num."

    claims1 = evaluator.evaluate(adversarial_evidence, text1)
    claims2 = evaluator.evaluate(adversarial_evidence, text2)

    assert len(claims1) == 1 and claims1[0].classification == ClaimClassification.SUPPORTED
    assert len(claims2) == 1 and claims2[0].classification == ClaimClassification.SUPPORTED


def test_attribution_wrong_top_feature(adversarial_evidence):
    """Claiming rank 3 feature (age) as top predictor is unsupported."""
    evaluator = AttributionFaithfulnessEvaluator(top_k=5)
    text = "The top predictor was age."
    claims = evaluator.evaluate(adversarial_evidence, text)
    assert len(claims) == 1
    assert claims[0].classification == ClaimClassification.PARTIALLY_SUPPORTED  # in top-k but not top-1


def test_attribution_feature_name_no_substring_guessing(adversarial_evidence):
    """Candidate 'age' must NEVER match 'marriage' substring."""
    evaluator = AttributionFaithfulnessEvaluator(top_k=5)
    resolved = evaluator._resolve_feature_name("age", {"marriage", "capital_gain"})
    assert resolved is None  # Must NOT resolve to 'marriage'


def test_attribution_ranking_ordering(adversarial_evidence):
    """Explicit rank assertions."""
    evaluator = AttributionFaithfulnessEvaluator(top_k=5)
    text_correct = "capital_gain ranked 1st."
    text_wrong = "capital_gain ranked 4th."

    claims_c = evaluator.evaluate(adversarial_evidence, text_correct)
    claims_w = evaluator.evaluate(adversarial_evidence, text_wrong)

    assert claims_c[0].classification == ClaimClassification.SUPPORTED
    assert claims_w[0].classification == ClaimClassification.UNSUPPORTED


# =====================================================================
# 4. UNSUPPORTED CLAIMS ADVERSARIAL TESTS
# =====================================================================

def test_unsupported_claim_adversarial_patterns(adversarial_evidence):
    """Tests all required unevidenced and invalid assertions."""
    detector = UnsupportedClaimsDetector()

    cases = [
        ("Removing gender caused the fairness improvement.", ClaimType.CAUSAL),
        ("Gender causes the model's predictions.", ClaimType.CAUSAL),
        ("The model is completely fair.", ClaimType.FAIRNESS_INTERPRETATION),
        ("This model has no bias.", ClaimType.FAIRNESS_INTERPRETATION),
        ("The model is fair for everyone.", ClaimType.FAIRNESS_INTERPRETATION),
        ("The mitigation guarantees fairness.", ClaimType.OTHER),
        ("CorrelationRemover is the best mitigation.", ClaimType.OTHER),
        ("The model is more fair in every respect.", ClaimType.OTHER),
        ("The mitigation improved performance.", ClaimType.PERFORMANCE),
    ]

    for statement, expected_type in cases:
        claims = detector.evaluate(adversarial_evidence, statement)
        assert len(claims) >= 1, f"Failed to extract unsupported claim from: '{statement}'"
        assert claims[0].claim_type == expected_type, f"Type mismatch for: '{statement}'"
        assert claims[0].classification == ClaimClassification.UNSUPPORTED, f"Must be UNSUPPORTED: '{statement}'"


# =====================================================================
# 5. CLAIM PROVENANCE & EVIDENCE HASH AUDIT
# =====================================================================

def test_evidence_hash_determinism_and_perturbation(adversarial_evidence):
    """Evidence hash must be deterministic, canonical, and change upon perturbation."""
    h1 = adversarial_evidence.compute_evidence_hash()
    h2 = adversarial_evidence.compute_evidence_hash()
    assert h1 == h2  # Deterministic

    # Perturb evidence
    adversarial_evidence.baseline_state.fairness_metrics["demographic_parity_difference"].value = 0.4201
    h3 = adversarial_evidence.compute_evidence_hash()
    assert h1 != h3  # Perturbation changes hash


def test_claim_provenance_persisted_fields(adversarial_evidence):
    """Every claim must persist complete provenance and expected/extracted values."""
    evaluator = FaithfulnessEvaluator()
    text = "Demographic parity difference was 0.4200."
    report = evaluator.evaluate(adversarial_evidence, text, save_records=False)
    assert len(report.claims) >= 1
    claim = report.claims[0]

    assert claim.claim_text in text or text.startswith(claim.claim_text)
    assert claim.claim_type == ClaimType.NUMERICAL
    assert claim.classification == ClaimClassification.SUPPORTED
    assert claim.evidence_hash == adversarial_evidence.evidence_hash
    assert claim.experiment_id == adversarial_evidence.experiment_id
    assert "value" in claim.extracted_values
    assert "matched_value" in claim.expected_values


# =====================================================================
# 6. CONTROL BASELINE EQUIVALENCE & COVERAGE DECOUPLING
# =====================================================================

def test_template_baseline_receives_identical_evidence(adversarial_evidence):
    """Template explainer generates faithful explanation from identical evidence."""
    explainer = TemplateExplainer()
    template_text = explainer.generate_explanation(adversarial_evidence)

    evaluator = FaithfulnessEvaluator()
    report = evaluator.evaluate(adversarial_evidence, template_text, save_records=False)

    # Deterministic template baseline should have 100% numerical and directional faithfulness
    assert report.numerical_faithfulness == 1.0
    assert report.directional_faithfulness == 1.0
    assert report.unsupported_claim_rate == 0.0


def test_coverage_does_not_penalize_faithfulness(adversarial_evidence):
    """A concise, 1-claim explanation has 100% faithfulness while having low coverage."""
    text = "Demographic parity difference was 0.4200."
    evaluator = FaithfulnessEvaluator()
    cov_evaluator = EvidenceCoverageEvaluator()

    faith_report = evaluator.evaluate(adversarial_evidence, text, save_records=False)
    cov_report = cov_evaluator.evaluate(adversarial_evidence, text)

    assert faith_report.numerical_faithfulness == 1.0
    assert cov_report.overall_coverage_rate < 0.40  # Low coverage
    # Ensure FaithfulnessReport contains NO coverage field
    assert not hasattr(faith_report, "overall_coverage_rate")


# =====================================================================
# 7. STATISTICAL UNIT & MINIMUM SAMPLE SIZE GUARD
# =====================================================================

def test_statistical_minimum_sample_size_guard():
    """Paired inferential test with N < 3 returns defined=False."""
    res = compute_paired_faithfulness_comparison(
        template_scores=[0.95, 0.90],
        llm_scores=[0.85, 0.80],
        metric_name="numerical_faithfulness"
    )
    assert res["defined"] is False
    assert "insufficient" in res["reason"].lower()


# =====================================================================
# 8. SMOKE ISOLATION & DEDUPLICATION IN AGGREGATOR
# =====================================================================

def test_aggregator_smoke_isolation_and_deduplication(tmp_path):
    """Aggregator strictly ignores smoke results and prevents double-counting duplicates."""
    raw_dir = tmp_path / "raw"
    smoke_dir = tmp_path / "smoke" / "raw"
    proc_dir = tmp_path / "processed"
    raw_dir.mkdir(parents=True)
    smoke_dir.mkdir(parents=True)

    # Valid empirical run
    valid_run = {
        "experiment_id": "valid_exp_1",
        "dataset_name": "adult",
        "model_name": "logistic_regression",
        "mitigation_name": "correlation_remover",
        "random_seed": 42,
        "is_synthetic_benchmark": True,
        "execution_mode": "EMPIRICAL_RESEARCH_RUN",
        "baseline_evaluation": {"performance": {"accuracy": {"value": 0.85}}, "fairness": {"demographic_parity_difference": {"value": 0.20}}},
        "mitigated_evaluation": {"performance": {"accuracy": {"value": 0.83}}, "fairness": {"demographic_parity_difference": {"value": 0.05}}},
        "attribution_comparison": {"cosine_similarity": 0.95},
        "trade_off_deltas": {"delta_accuracy": -0.02, "delta_demographic_parity_difference": -0.15}
    }

    # Smoke run
    smoke_run = dict(valid_run, experiment_id="smoke_exp", execution_mode="SOFTWARE_VALIDATION_ONLY")

    # Duplicate run
    dup_run = dict(valid_run)

    with open(raw_dir / "run1.json", "w") as f:
        json.dump(valid_run, f)
    with open(raw_dir / "run1_dup.json", "w") as f:
        json.dump(dup_run, f)
    with open(raw_dir / "smoke_run.json", "w") as f:
        json.dump(smoke_run, f)

    df = aggregate_raw_results(raw_dir=str(raw_dir), output_dir=str(proc_dir))
    assert df is not None
    # Only 1 run should be aggregated (smoke skipped, duplicate skipped)
    ind_runs = (proc_dir / "individual_runs.csv")
    assert ind_runs.exists()
    import pandas as pd
    ind_df = pd.read_csv(ind_runs)
    assert len(ind_df) == 1
    assert ind_df["experiment_id"].iloc[0] == "valid_exp_1"


# =====================================================================
# 9. API FAILURE INTEGRITY
# =====================================================================

def test_gemini_empty_response_raises_error():
    """Empty response from Gemini must raise RuntimeError and never enter evaluation."""
    fake_response = MagicMock()
    fake_response.text = "   "  # Whitespace only
    fake_candidate = MagicMock()
    fake_candidate.finish_reason = "SAFETY"
    fake_response.candidates = [fake_candidate]

    with patch("research.llm.providers.gemini.genai") as mock_genai:
        mock_model = MagicMock()
        mock_model.generate_content.return_value = fake_response
        mock_genai.GenerativeModel.return_value = mock_model

        provider = GeminiProvider(api_key="fake-key")
        with pytest.raises(RuntimeError, match="empty explanation"):
            provider.generate("Test prompt")
