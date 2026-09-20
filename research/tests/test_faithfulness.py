"""
Unit tests for Faithfulness Evaluation Suite.
Verifies numerical, directional, attribution, and unsupported claims evaluators.
"""
import pytest
from research.faithfulness.taxonomy import ClaimType, ClaimClassification
from research.faithfulness.numerical import NumericalFaithfulnessEvaluator
from research.faithfulness.directional import DirectionalFaithfulnessEvaluator
from research.faithfulness.attribution import AttributionFaithfulnessEvaluator
from research.faithfulness.unsupported_claims import UnsupportedClaimsDetector
from research.faithfulness.evaluator import FaithfulnessEvaluator
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


@pytest.fixture
def sample_evidence():
    dataset = DatasetEvidence("adult", "sex", 1, 0, "income", 1000, 200, 300)
    model = ModelEvidence("logistic_regression", {}, 42, mitigation_applied="correlation_remover")
    
    # Baseline
    base_f = {
        "demographic_parity_difference": ObservedMetric("demographic_parity_difference", MetricType.FAIRNESS, 0.4200),
        "equalized_odds_difference": ObservedMetric("equalized_odds_difference", MetricType.FAIRNESS, 0.1800),
    }
    base_p = {
        "accuracy": ObservedMetric("accuracy", MetricType.PERFORMANCE, 0.8500),
        "f1_score": ObservedMetric("f1_score", MetricType.PERFORMANCE, 0.8200)
    }
    base_state = AuditStateEvidence("baseline", base_f, base_p)

    # Mitigated
    mit_f = {
        "demographic_parity_difference": ObservedMetric("demographic_parity_difference", MetricType.FAIRNESS, 0.0800),
        "equalized_odds_difference": ObservedMetric("equalized_odds_difference", MetricType.FAIRNESS, 0.1800),
    }
    mit_p = {
        "accuracy": ObservedMetric("accuracy", MetricType.PERFORMANCE, 0.8200),
        "f1_score": ObservedMetric("f1_score", MetricType.PERFORMANCE, 0.7900)
    }
    shap_ev = SHAPAuditEvidence(
        explainer_type="LinearExplainer",
        n_eval_samples=50,
        n_background_samples=25,
        ranked_features=[
            FeatureImportanceEvidence("capital_gain", 0.35, 1),
            FeatureImportanceEvidence("education_num", 0.22, 2),
            FeatureImportanceEvidence("hours_per_week", 0.15, 3),
            FeatureImportanceEvidence("age", 0.10, 4)
        ],
        top_k_features=["capital_gain", "education_num", "hours_per_week", "age"]
    )
    mit_state = AuditStateEvidence("mitigated", mit_f, mit_p, shap_evidence=shap_ev)

    # Comparisons
    comparisons = [
        MetricComparison(
            metric_name="demographic_parity_difference",
            metric_type=MetricType.FAIRNESS,
            before=0.4200,
            after=0.0800,
            absolute_change=-0.3400,
            relative_change=-0.8095,
            direction=Direction.DECREASE,
            interpretation=SemanticInterpretation.IMPROVEMENT,
            ideal_target=0.0,
            semantics_rationale="DPD decreased closer to 0.0."
        ),
        MetricComparison(
            metric_name="equalized_odds_difference",
            metric_type=MetricType.FAIRNESS,
            before=0.1800,
            after=0.1800,
            absolute_change=0.0000,
            relative_change=0.0000,
            direction=Direction.UNCHANGED,
            interpretation=SemanticInterpretation.UNCHANGED,
            ideal_target=0.0,
            semantics_rationale="EOD remained unchanged."
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
            semantics_rationale="Accuracy decreased."
        )
    ]

    return AuditEvidence(
        experiment_id="test_faithfulness_exp",
        dataset=dataset,
        model=model,
        baseline_state=base_state,
        mitigated_state=mit_state,
        metric_comparisons=comparisons
    )


def test_numerical_exact_match_and_tolerance(sample_evidence):
    evaluator = NumericalFaithfulnessEvaluator(absolute_tolerance=0.015, relative_tolerance=0.05)

    # 1. Exact match (0.4200 for DPD)
    text_exact = "The baseline demographic parity difference was 0.4200."
    claims_exact = evaluator.evaluate(sample_evidence, text_exact)
    assert len(claims_exact) == 1
    assert claims_exact[0].classification == ClaimClassification.SUPPORTED

    # 2. Within tolerance (0.421 vs 0.420, abs diff = 0.001 < 0.015)
    text_tol = "Demographic parity difference was observed at 0.421."
    claims_tol = evaluator.evaluate(sample_evidence, text_tol)
    assert len(claims_tol) == 1
    assert claims_tol[0].classification == ClaimClassification.SUPPORTED

    # 3. Wrong number (0.9500 vs 0.4200) -> UNSUPPORTED
    text_wrong = "The baseline demographic parity difference was 0.9500."
    claims_wrong = evaluator.evaluate(sample_evidence, text_wrong)
    assert len(claims_wrong) == 1
    assert claims_wrong[0].classification == ClaimClassification.UNSUPPORTED

    # 4. State mismatch: baseline claimed to have mitigated value (0.0800) -> UNSUPPORTED
    text_state_mismatch = "The baseline demographic parity difference was 0.0800."
    claims_mismatch = evaluator.evaluate(sample_evidence, text_state_mismatch)
    assert len(claims_mismatch) == 1
    assert claims_mismatch[0].classification == ClaimClassification.UNSUPPORTED

    # 5. Mitigated state match: 0.0800 correctly attributed to mitigated -> SUPPORTED
    text_mitigated_match = "After mitigation, demographic parity difference was 0.0800."
    claims_mit_match = evaluator.evaluate(sample_evidence, text_mitigated_match)
    assert len(claims_mit_match) == 1
    assert claims_mit_match[0].classification == ClaimClassification.SUPPORTED

    # 6. Change metric match: reduction of 0.3400 -> SUPPORTED
    text_change_match = "Demographic parity difference showed a reduction of 0.3400."
    claims_change = evaluator.evaluate(sample_evidence, text_change_match)
    assert len(claims_change) == 1
    assert claims_change[0].classification == ClaimClassification.SUPPORTED


def test_vacuous_truth_handling_in_evaluator(sample_evidence):
    """
    Test that explanations with zero evaluable claims return None (not 1.0)
    and set evaluable = False, preventing vacuous truth distortion.
    """
    evaluator = FaithfulnessEvaluator()
    empty_text = "The machine learning experiment ran smoothly."
    report = evaluator.evaluate(sample_evidence, empty_text, save_records=False)

    assert report.numerical_faithfulness is None
    assert report.numerical_evaluable is False
    assert report.directional_faithfulness is None
    assert report.directional_evaluable is False
    assert report.attribution_faithfulness is None
    assert report.attribution_evaluable is False
    assert report.unsupported_claim_rate == 0.0
    assert report.total_claims_count == 0


def test_directional_faithfulness(sample_evidence):
    evaluator = DirectionalFaithfulnessEvaluator()

    # 1. Correct decrease claim
    text_dec = "Following mitigation, demographic parity difference decreased significantly."
    claims_dec = evaluator.evaluate(sample_evidence, text_dec)
    assert any(c.classification == ClaimClassification.SUPPORTED for c in claims_dec)

    # 2. Wrong direction claim (increased instead of decreased)
    text_inc = "Following mitigation, demographic parity difference increased significantly."
    claims_inc = evaluator.evaluate(sample_evidence, text_inc)
    assert any(c.classification == ClaimClassification.UNSUPPORTED for c in claims_inc)

    # 3. Correct unchanged condition
    text_unchanged = "Equalized odds difference remained unchanged after mitigation."
    claims_unchanged = evaluator.evaluate(sample_evidence, text_unchanged)
    assert any(c.classification == ClaimClassification.SUPPORTED for c in claims_unchanged)

    # 4. Correct semantic interpretation (fairness improved)
    text_interp = "The mitigation resulted in an improved demographic parity difference."
    claims_interp = evaluator.evaluate(sample_evidence, text_interp)
    assert any(c.classification == ClaimClassification.SUPPORTED for c in claims_interp)


def test_attribution_faithfulness(sample_evidence):
    evaluator = AttributionFaithfulnessEvaluator(top_k=3)

    # 1. Correct top feature: capital_gain
    text_top = "The most influential feature was capital_gain in determining model predictions."
    claims_top = evaluator.evaluate(sample_evidence, text_top)
    assert len(claims_top) == 1
    assert claims_top[0].classification == ClaimClassification.SUPPORTED

    # 2. Wrong top feature: claiming age (which is rank 4) was the most influential
    text_wrong_top = "Age was the most influential feature governing outcomes."
    claims_wrong_top = evaluator.evaluate(sample_evidence, text_wrong_top)
    assert len(claims_wrong_top) == 1
    assert claims_wrong_top[0].classification == ClaimClassification.UNSUPPORTED

    # 3. Hallucinated nonexistent feature
    text_halluc = "The most influential feature was nonexistent_synthetic_feature."
    claims_halluc = evaluator.evaluate(sample_evidence, text_halluc)
    assert len(claims_halluc) == 1
    assert claims_halluc[0].classification == ClaimClassification.UNSUPPORTED


def test_unsupported_causal_and_undeterminable_claims(sample_evidence):
    detector = UnsupportedClaimsDetector()

    # 1. Unsupported causal claim
    text_causal = "The applicant's age directly caused the model to reject older individuals."
    claims_causal = detector.evaluate(sample_evidence, text_causal)
    assert len(claims_causal) == 1
    assert claims_causal[0].claim_type == ClaimType.CAUSAL
    assert claims_causal[0].classification == ClaimClassification.UNSUPPORTED

    # 2. Unsupported absolute fairness claim
    text_abs = "Following mitigation, the predictive system became completely fair."
    claims_abs = detector.evaluate(sample_evidence, text_abs)
    assert len(claims_abs) == 1
    assert claims_abs[0].classification == ClaimClassification.UNSUPPORTED

    # 3. Complex claim flagged for human annotation (UNDETERMINABLE)
    text_undet = "This pattern appears to suggest underlying societal bias in lending."
    claims_undet = detector.evaluate(sample_evidence, text_undet)
    assert len(claims_undet) == 1
    assert claims_undet[0].classification == ClaimClassification.UNDETERMINABLE


def test_faithfulness_evaluator_orchestrator(sample_evidence, tmp_path):
    evaluator = FaithfulnessEvaluator(absolute_tolerance=0.015, relative_tolerance=0.05)
    
    explanation_text = (
        "Baseline demographic parity difference was 0.4200, while accuracy was 0.8500. "
        "After applying bias mitigation, demographic parity difference decreased to 0.0800. "
        "The most influential feature was capital_gain."
    )

    report = evaluator.evaluate(
        evidence=sample_evidence,
        explanation_text=explanation_text,
        explanation_source="mock_faithful",
        prompt_id="combined_audit_v1",
        save_records=True,
        output_claims_dir=str(tmp_path / "claims"),
        output_summaries_dir=str(tmp_path / "summaries")
    )

    assert report.numerical_faithfulness == 1.0
    assert report.directional_faithfulness == 1.0
    assert report.attribution_faithfulness == 1.0
    assert report.unsupported_claim_rate == 0.0
    assert report.total_claims_count > 0
    assert (tmp_path / "claims").exists()
    assert (tmp_path / "summaries").exists()


def test_cross_metric_number_swapping(sample_evidence):
    """
    Section 3 & 9: Verify that correct numbers attached to the WRONG metrics
    are strictly classified as UNSUPPORTED.
    Evidence: DPD = 0.4200, Accuracy = 0.8500.
    Explanation erroneously swaps them: "Accuracy was 0.4200 while DPD was 0.8500."
    """
    evaluator = NumericalFaithfulnessEvaluator(absolute_tolerance=0.015)
    swapped_text = "Accuracy was 0.4200 while demographic parity difference was 0.8500."
    claims = evaluator.evaluate(sample_evidence, swapped_text)
    
    assert len(claims) == 2
    # Both numbers exist in evidence, but are associated with the wrong metric
    for claim in claims:
        assert claim.classification == ClaimClassification.UNSUPPORTED
        assert claim.referenced_evidence is not None
        assert claim.evidence_hash == sample_evidence.evidence_hash


def test_qualitative_magnitude_undeterminable(sample_evidence):
    """
    Section 5: Subjective/qualitative magnitude terms ("substantially", "slightly")
    cannot be deterministically evaluated and MUST be classified as UNDETERMINABLE.
    """
    evaluator = DirectionalFaithfulnessEvaluator()
    text = "Demographic parity difference decreased substantially after mitigation."
    claims = evaluator.evaluate(sample_evidence, text)
    
    # Must have mathematical direction (SUPPORTED) and magnitude (UNDETERMINABLE)
    mag_claims = [c for c in claims if c.claim_type == ClaimType.MAGNITUDE]
    assert len(mag_claims) >= 1
    assert mag_claims[0].classification == ClaimClassification.UNDETERMINABLE
    assert "substantially" in mag_claims[0].rationale


def test_overgeneralization_certainty_and_optimality(sample_evidence):
    """
    Section 7: Evaluator must catch overgeneralizations, certainty claims,
    and ungrounded optimality assertions.
    """
    detector = UnsupportedClaimsDetector()

    # 1. Overgeneralization
    overgen_text = "The machine learning model is now fair for everyone across all demographics."
    claims_overgen = detector.evaluate(sample_evidence, overgen_text)
    assert any(c.classification == ClaimClassification.UNSUPPORTED for c in claims_overgen)

    # 2. Certainty guarantee
    cert_text = "The debiasing procedure guarantees that fairness is preserved."
    claims_cert = detector.evaluate(sample_evidence, cert_text)
    assert any(c.classification == ClaimClassification.UNSUPPORTED for c in claims_cert)

    # 3. Optimality claim
    opt_text = "CorrelationRemover is the best mitigation algorithm for algorithmic fairness."
    claims_opt = detector.evaluate(sample_evidence, opt_text)
    assert any(c.classification == ClaimClassification.UNSUPPORTED for c in claims_opt)


def test_unsupported_performance_claim_on_degraded_model(sample_evidence):
    """
    Section 7: Evaluator must catch claims that performance improved when
    the empirical evidence shows predictive performance degraded.
    """
    detector = UnsupportedClaimsDetector()
    text = "The mitigation successfully improved model performance."
    claims = detector.evaluate(sample_evidence, text)
    
    assert len(claims) >= 1
    assert claims[0].claim_type == ClaimType.PERFORMANCE
    assert claims[0].classification == ClaimClassification.UNSUPPORTED


def test_evidence_coverage_decoupled(sample_evidence):
    """
    Section 19: Evidence coverage is an orthogonal secondary metric measuring
    completeness, completely separate from faithfulness (truthfulness).
    """
    from research.faithfulness.coverage import EvidenceCoverageEvaluator
    
    coverage_eval = EvidenceCoverageEvaluator(top_k_features=4)
    
    # Text only mentions DPD and capital_gain (omitting EOD, Accuracy, F1)
    partial_text = "Demographic parity difference was 0.4200. The top feature was capital_gain."
    report = coverage_eval.evaluate(sample_evidence, partial_text, explanation_source="test_source")
    
    # 1 of 2 fairness metrics (DPD mentioned, EOD omitted) -> 50%
    assert report.fairness_coverage_rate == 0.5
    # 0 of 2 performance metrics (Accuracy and F1 omitted) -> 0%
    assert report.performance_coverage_rate == 0.0
    # 1 of 4 features (capital_gain mentioned) -> 25%
    assert report.feature_coverage_rate == 0.25
    assert report.overall_coverage_rate < 1.0


def test_weighted_cohen_kappa():
    """
    Section 16: Test unweighted and weighted Cohen's Kappa for ordinal labels.
    """
    from research.annotation.agreement import compute_cohen_kappa, compute_weighted_cohen_kappa
    
    # Perfect agreement
    rater_a = ["SUPPORTED", "UNSUPPORTED", "PARTIALLY_SUPPORTED", "SUPPORTED"]
    rater_b = ["SUPPORTED", "UNSUPPORTED", "PARTIALLY_SUPPORTED", "SUPPORTED"]
    assert compute_cohen_kappa(rater_a, rater_b)["cohen_kappa"] == 1.0
    assert compute_weighted_cohen_kappa(rater_a, rater_b)["weighted_kappa"] == 1.0

    # Mild disagreement (SUPPORTED vs PARTIALLY_SUPPORTED) vs Severe (SUPPORTED vs UNSUPPORTED)
    labels_1 = ["SUPPORTED", "SUPPORTED", "PARTIALLY_SUPPORTED", "UNSUPPORTED"]
    labels_2 = ["PARTIALLY_SUPPORTED", "SUPPORTED", "PARTIALLY_SUPPORTED", "UNSUPPORTED"]
    
    res_weighted = compute_weighted_cohen_kappa(labels_1, labels_2, weight_type="quadratic")
    assert res_weighted["weighted_kappa"] > 0.0
    assert res_weighted["weight_type"] == "quadratic"

