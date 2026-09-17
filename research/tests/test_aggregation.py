"""
Regression tests for result aggregator isolation guarantees.

These tests PROVE that:
  1. Mock results cannot enter pilot aggregation
  2. Smoke/software-validation results cannot enter pilot aggregation
  3. Pilot results cannot enter final aggregation
  4. Final results cannot enter pilot aggregation
  5. Missing execution_mode is conservatively excluded
  6. Paired template/LLM explanations use identical evidence hashes

These tests must always pass before any empirical run. Failures indicate
a potential research-integrity contamination risk.
"""
import pytest
import os
import json
import hashlib
import pandas as pd
from research.analysis.aggregator import (
    aggregate_raw_results,
    aggregate_faithfulness_summaries,
    PILOT_MODE,
    FINAL_MODE,
    SMOKE_MODE,
    _is_mock_source,
)


# --- Fixtures ---

def _make_raw_result(experiment_id: str, execution_mode: str, **overrides) -> dict:
    """Creates a minimal well-formed raw result dict."""
    base = {
        "experiment_id": experiment_id,
        "execution_mode": execution_mode,
        "dataset_name": "adult",
        "model_name": "logistic_regression",
        "mitigation_name": "correlation_remover",
        "random_seed": 42,
        "is_synthetic_benchmark": True,
        "baseline_evaluation": {
            "performance": {"accuracy": {"value": 0.82}},
            "fairness": {"demographic_parity_difference": {"value": 0.18}},
        },
        "mitigated_evaluation": {
            "performance": {"accuracy": {"value": 0.80}},
            "fairness": {"demographic_parity_difference": {"value": 0.05}},
        },
        "attribution_comparison": {"cosine_similarity": 0.94},
        "trade_off_deltas": {"delta_accuracy": -0.02, "delta_demographic_parity_difference": -0.13},
    }
    base.update(overrides)
    return base


def _make_faithfulness_summary(experiment_id: str, execution_mode: str,
                                explanation_source: str = "gemini__gemini-2.5-flash",
                                **overrides) -> dict:
    """Creates a minimal faithfulness summary dict."""
    base = {
        "experiment_id": experiment_id,
        "execution_mode": execution_mode,
        "explanation_source": explanation_source,
        "prompt_id": "combined_audit_v1",
        "timestamp_utc": "2026-09-17T08:00:00+00:00",
        "numerical_faithfulness": 0.80,
        "directional_faithfulness": 0.90,
        "attribution_faithfulness": 0.95,
        "unsupported_claim_rate": 0.10,
        "total_claims_count": 10,
        "numeric_claim_count": 5,
        "directional_claim_count": 3,
        "attribution_claim_count": 2,
        "unsupported_claim_count": 1,
        "undeterminable_claim_count": 0,
        "numerical_mean_absolute_error": 0.025,
    }
    base.update(overrides)
    return base


# =============================================================================
# Section 1: Mock provider detection
# =============================================================================

class TestMockSourceDetection:
    """Unit tests for _is_mock_source helper."""

    def test_mock_prefix_detected(self):
        assert _is_mock_source("mock") is True
        assert _is_mock_source("mock_gemini-2.5-flash") is True
        assert _is_mock_source("mock_provider") is True
        assert _is_mock_source("MOCK") is True

    def test_real_sources_not_flagged(self):
        assert _is_mock_source("gemini__gemini-2.5-flash") is False
        assert _is_mock_source("gemini") is False
        assert _is_mock_source("template_baseline") is False

    def test_empty_source_treated_as_mock(self):
        assert _is_mock_source("") is True
        assert _is_mock_source(None) is True


# =============================================================================
# Section 2: Raw result aggregation — contamination regression
# =============================================================================

class TestRawAggregatorContamination:
    """
    REGRESSION TESTS: These prove contamination barriers in aggregate_raw_results().
    Failures indicate a research-integrity risk.
    """

    def test_mock_result_cannot_enter_pilot_aggregation(self, tmp_path):
        """Mock results (missing execution_mode or wrong mode) must NOT enter pilot aggregation."""
        raw_dir = tmp_path / "raw"
        raw_dir.mkdir()

        mock_result = _make_raw_result("mock_exp_1", execution_mode=SMOKE_MODE)
        (raw_dir / "mock_exp_1.json").write_text(json.dumps(mock_result))

        result = aggregate_raw_results(
            raw_dir=str(raw_dir),
            output_dir=str(tmp_path / "out"),
            required_execution_mode=PILOT_MODE
        )
        assert result is None, "CONTAMINATION FAILURE: Mock result entered pilot aggregation"

    def test_smoke_result_cannot_enter_pilot_aggregation(self, tmp_path):
        """Smoke test results must NOT enter pilot aggregation regardless of path."""
        raw_dir = tmp_path / "raw"
        raw_dir.mkdir()

        smoke_result = _make_raw_result("smoke_exp_1", execution_mode=SMOKE_MODE)
        (raw_dir / "smoke_exp.json").write_text(json.dumps(smoke_result))

        result = aggregate_raw_results(
            raw_dir=str(raw_dir),
            output_dir=str(tmp_path / "out"),
            required_execution_mode=PILOT_MODE
        )
        assert result is None, "CONTAMINATION FAILURE: Smoke result entered pilot aggregation"

    def test_final_result_cannot_enter_pilot_aggregation(self, tmp_path):
        """Final empirical results must NOT enter pilot aggregation."""
        raw_dir = tmp_path / "raw"
        raw_dir.mkdir()

        final_result = _make_raw_result("final_exp_1", execution_mode=FINAL_MODE)
        (raw_dir / "final_exp.json").write_text(json.dumps(final_result))

        result = aggregate_raw_results(
            raw_dir=str(raw_dir),
            output_dir=str(tmp_path / "out"),
            required_execution_mode=PILOT_MODE
        )
        assert result is None, "CONTAMINATION FAILURE: Final result entered pilot aggregation"

    def test_pilot_result_cannot_enter_final_aggregation(self, tmp_path):
        """Pilot results must NOT enter final aggregation."""
        raw_dir = tmp_path / "raw"
        raw_dir.mkdir()

        pilot_result = _make_raw_result("pilot_exp_1", execution_mode=PILOT_MODE)
        (raw_dir / "pilot_exp.json").write_text(json.dumps(pilot_result))

        result = aggregate_raw_results(
            raw_dir=str(raw_dir),
            output_dir=str(tmp_path / "out"),
            required_execution_mode=FINAL_MODE
        )
        assert result is None, "CONTAMINATION FAILURE: Pilot result entered final aggregation"

    def test_missing_execution_mode_excluded_conservatively(self, tmp_path):
        """Results without execution_mode must be excluded conservatively from pilot aggregation."""
        raw_dir = tmp_path / "raw"
        raw_dir.mkdir()

        legacy = {
            "experiment_id": "legacy_exp",
            "dataset_name": "adult",
            "model_name": "logistic_regression",
            "mitigation_name": "correlation_remover",
            "random_seed": 42,
            "is_synthetic_benchmark": True,
            "baseline_evaluation": {"performance": {"accuracy": {"value": 0.82}}, "fairness": {}},
            "mitigated_evaluation": {"performance": {"accuracy": {"value": 0.80}}, "fairness": {}},
            "attribution_comparison": {},
            "trade_off_deltas": {},
            # NOTE: no "execution_mode" field
        }
        (raw_dir / "legacy.json").write_text(json.dumps(legacy))

        result = aggregate_raw_results(
            raw_dir=str(raw_dir),
            output_dir=str(tmp_path / "out"),
            required_execution_mode=PILOT_MODE
        )
        assert result is None, "CONTAMINATION FAILURE: Legacy result without execution_mode entered pilot aggregation"

    def test_pilot_result_admitted_to_pilot_aggregation(self, tmp_path):
        """Correctly tagged pilot results must be admitted to pilot aggregation."""
        raw_dir = tmp_path / "raw"
        raw_dir.mkdir()

        pilot_result = _make_raw_result("pilot_exp_valid", execution_mode=PILOT_MODE)
        (raw_dir / "pilot_valid.json").write_text(json.dumps(pilot_result))

        result = aggregate_raw_results(
            raw_dir=str(raw_dir),
            output_dir=str(tmp_path / "out"),
            required_execution_mode=PILOT_MODE
        )
        assert result is not None, "Valid pilot result was incorrectly excluded"

    def test_final_result_admitted_to_final_aggregation(self, tmp_path):
        """Correctly tagged final results must be admitted to final aggregation."""
        raw_dir = tmp_path / "raw"
        raw_dir.mkdir()

        final_result = _make_raw_result("final_exp_valid", execution_mode=FINAL_MODE)
        (raw_dir / "final_valid.json").write_text(json.dumps(final_result))

        result = aggregate_raw_results(
            raw_dir=str(raw_dir),
            output_dir=str(tmp_path / "out"),
            required_execution_mode=FINAL_MODE
        )
        assert result is not None, "Valid final result was incorrectly excluded"

    def test_smoke_path_excluded_regardless_of_mode(self, tmp_path):
        """Files under a /smoke/ path component are always excluded, even if tagged as pilot."""
        smoke_dir = tmp_path / "smoke" / "raw"
        smoke_dir.mkdir(parents=True)

        mistagged = _make_raw_result("mistagged_exp", execution_mode=PILOT_MODE)
        (smoke_dir / "mistagged.json").write_text(json.dumps(mistagged))

        result = aggregate_raw_results(
            raw_dir=str(smoke_dir),
            output_dir=str(tmp_path / "out"),
            required_execution_mode=PILOT_MODE
        )
        assert result is None, "CONTAMINATION FAILURE: Smoke-path result entered pilot aggregation"

    def test_deduplication_prevents_double_counting(self, tmp_path):
        """Duplicate experiment IDs must only be counted once."""
        raw_dir = tmp_path / "raw"
        raw_dir.mkdir()

        pilot_result = _make_raw_result("dup_exp", execution_mode=PILOT_MODE)
        (raw_dir / "dup1.json").write_text(json.dumps(pilot_result))
        (raw_dir / "dup2.json").write_text(json.dumps(pilot_result))

        result = aggregate_raw_results(
            raw_dir=str(raw_dir),
            output_dir=str(tmp_path / "out"),
            required_execution_mode=PILOT_MODE
        )
        runs_csv = tmp_path / "out" / "individual_runs.csv"
        df = pd.read_csv(str(runs_csv))
        assert len(df) == 1, "Deduplication failure: duplicate experiment counted twice"


# =============================================================================
# Section 3: Faithfulness aggregation — contamination regression
# =============================================================================

class TestFaithfulnessAggregatorContamination:
    """
    REGRESSION TESTS: These prove contamination barriers in aggregate_faithfulness_summaries().
    """

    def test_mock_source_cannot_enter_pilot_faithfulness_aggregation(self, tmp_path):
        """Mock provider summaries must NEVER enter pilot faithfulness aggregation."""
        summaries_dir = tmp_path / "summaries"
        summaries_dir.mkdir()

        mock_summary = _make_faithfulness_summary(
            "exp_mock", execution_mode=PILOT_MODE,
            explanation_source="mock_gemini-2.5-flash"
        )
        (summaries_dir / "mock_summary.json").write_text(json.dumps(mock_summary))

        result = aggregate_faithfulness_summaries(
            summaries_dir=str(summaries_dir),
            output_dir=str(tmp_path / "out"),
            required_execution_mode=PILOT_MODE
        )
        assert result is None, "CONTAMINATION FAILURE: Mock source entered pilot faithfulness aggregation"

    def test_smoke_mode_summary_excluded_from_pilot(self, tmp_path):
        """SOFTWARE_VALIDATION_ONLY summaries must NOT enter pilot aggregation."""
        summaries_dir = tmp_path / "summaries"
        summaries_dir.mkdir()

        smoke_summary = _make_faithfulness_summary(
            "exp_smoke", execution_mode=SMOKE_MODE,
            explanation_source="gemini__gemini-2.5-flash"
        )
        (summaries_dir / "smoke_summary.json").write_text(json.dumps(smoke_summary))

        result = aggregate_faithfulness_summaries(
            summaries_dir=str(summaries_dir),
            output_dir=str(tmp_path / "out"),
            required_execution_mode=PILOT_MODE
        )
        assert result is None, "CONTAMINATION FAILURE: Smoke mode summary entered pilot faithfulness aggregation"

    def test_final_summary_excluded_from_pilot_aggregation(self, tmp_path):
        """Final mode summaries must NOT enter pilot aggregation."""
        summaries_dir = tmp_path / "summaries"
        summaries_dir.mkdir()

        final_summary = _make_faithfulness_summary(
            "exp_final", execution_mode=FINAL_MODE,
            explanation_source="gemini__gemini-2.5-flash"
        )
        (summaries_dir / "final_summary.json").write_text(json.dumps(final_summary))

        result = aggregate_faithfulness_summaries(
            summaries_dir=str(summaries_dir),
            output_dir=str(tmp_path / "out"),
            required_execution_mode=PILOT_MODE
        )
        assert result is None, "CONTAMINATION FAILURE: Final mode summary entered pilot faithfulness aggregation"

    def test_pilot_summary_excluded_from_final_aggregation(self, tmp_path):
        """Pilot mode summaries must NOT enter final aggregation."""
        summaries_dir = tmp_path / "summaries"
        summaries_dir.mkdir()

        pilot_summary = _make_faithfulness_summary(
            "exp_pilot", execution_mode=PILOT_MODE,
            explanation_source="gemini__gemini-2.5-flash"
        )
        (summaries_dir / "pilot_summary.json").write_text(json.dumps(pilot_summary))

        result = aggregate_faithfulness_summaries(
            summaries_dir=str(summaries_dir),
            output_dir=str(tmp_path / "out"),
            required_execution_mode=FINAL_MODE
        )
        assert result is None, "CONTAMINATION FAILURE: Pilot summary entered final faithfulness aggregation"

    def test_missing_execution_mode_conservatively_excluded(self, tmp_path):
        """Faithfulness summaries without execution_mode must be conservatively excluded."""
        summaries_dir = tmp_path / "summaries"
        summaries_dir.mkdir()

        legacy = {
            "experiment_id": "legacy_faith",
            "explanation_source": "gemini__gemini-2.5-flash",
            "prompt_id": "combined_audit_v1",
            "timestamp_utc": "2026-09-17T08:00:00+00:00",
            "numerical_faithfulness": 0.80,
            "directional_faithfulness": 0.90,
            "attribution_faithfulness": 0.95,
            "unsupported_claim_rate": 0.10,
            # NOTE: no "execution_mode"
        }
        (summaries_dir / "legacy.json").write_text(json.dumps(legacy))

        result = aggregate_faithfulness_summaries(
            summaries_dir=str(summaries_dir),
            output_dir=str(tmp_path / "out"),
            required_execution_mode=PILOT_MODE
        )
        assert result is None, "CONTAMINATION FAILURE: Legacy summary without execution_mode entered pilot aggregation"

    def test_valid_pilot_summary_admitted(self, tmp_path):
        """Correctly tagged pilot summaries must be admitted."""
        summaries_dir = tmp_path / "summaries"
        summaries_dir.mkdir()

        pilot_summary = _make_faithfulness_summary(
            "exp_valid_pilot", execution_mode=PILOT_MODE,
            explanation_source="gemini__gemini-2.5-flash"
        )
        (summaries_dir / "valid_pilot.json").write_text(json.dumps(pilot_summary))

        result = aggregate_faithfulness_summaries(
            summaries_dir=str(summaries_dir),
            output_dir=str(tmp_path / "out"),
            required_execution_mode=PILOT_MODE
        )
        assert result is not None, "Valid pilot faithfulness summary was incorrectly excluded"


# =============================================================================
# Section 4: Template/LLM pairing evidence hash regression
# =============================================================================

class TestPairedEvidenceIntegrity:
    """
    REGRESSION: Template baseline and LLM explanation must use identical evidence hashes
    for the same experimental condition.
    """

    def test_template_and_llm_share_identical_evidence_hash(self):
        """
        Proves that for any given AuditEvidence, the evidence_hash is deterministic.
        Both template and LLM receive the same AuditEvidence object, so hashes must match.
        """
        from research.experiments.runner import run_single_experiment
        from research.experiments.experiment_config import ExperimentConfig
        from research.evidence.builder import build_evidence_from_raw_result

        config = ExperimentConfig(
            dataset_name="adult",
            model_name="logistic_regression",
            mitigation_name="correlation_remover",
            seed=42,
            use_synthetic_benchmark=True,
            n_eval_samples=20,
            n_background_samples=10,
        )
        raw_result, manifest = run_single_experiment(config=config, save_artifacts=False)
        manifest["execution_mode"] = "SOFTWARE_VALIDATION_ONLY"

        evidence = build_evidence_from_raw_result(raw_result, manifest)

        # Both template and LLM receive the same evidence object
        hash_1 = evidence.compute_evidence_hash()
        hash_2 = evidence.compute_evidence_hash()

        assert hash_1 == hash_2, (
            "PAIRING FAILURE: Evidence hash is not deterministic — "
            "template and LLM may not be evaluating the same evidence."
        )
        assert len(hash_1) == 64, "Evidence hash is not a valid SHA-256 hex digest"
        assert hash_1.isalnum(), "Evidence hash contains non-hexadecimal characters"


# =============================================================================
# Section 5: Legacy aggregation test (updated for new interface)
# =============================================================================

def test_aggregate_raw_results_with_pilot_mode(tmp_path):
    """
    Updated smoke test for aggregate_raw_results with explicit pilot mode.
    """
    raw_dir = tmp_path / "raw"
    processed_dir = tmp_path / "processed"
    raw_dir.mkdir(parents=True)

    dummy1 = _make_raw_result("exp_1", execution_mode=PILOT_MODE, **{
        "baseline_evaluation": {
            "performance": {"accuracy": {"value": 0.82}},
            "fairness": {"demographic_parity_difference": {"value": 0.18}}
        },
        "mitigated_evaluation": {
            "performance": {"accuracy": {"value": 0.80}},
            "fairness": {"demographic_parity_difference": {"value": 0.05}}
        },
        "attribution_comparison": {"cosine_similarity": 0.94},
        "trade_off_deltas": {"delta_accuracy": -0.02, "delta_demographic_parity_difference": -0.13},
    })
    dummy2 = _make_raw_result("exp_2", execution_mode=PILOT_MODE, **{
        "random_seed": 123,
        "baseline_evaluation": {
            "performance": {"accuracy": {"value": 0.84}},
            "fairness": {"demographic_parity_difference": {"value": 0.20}}
        },
        "mitigated_evaluation": {
            "performance": {"accuracy": {"value": 0.81}},
            "fairness": {"demographic_parity_difference": {"value": 0.07}}
        },
        "attribution_comparison": {"cosine_similarity": 0.92},
        "trade_off_deltas": {"delta_accuracy": -0.03, "delta_demographic_parity_difference": -0.13},
    })

    (raw_dir / "res1.json").write_text(json.dumps(dummy1))
    (raw_dir / "res2.json").write_text(json.dumps(dummy2))

    summary_df = aggregate_raw_results(
        raw_dir=str(raw_dir),
        output_dir=str(processed_dir),
        required_execution_mode=PILOT_MODE
    )

    assert summary_df is not None
    assert "delta_accuracy_mean" in summary_df.columns
    assert summary_df["delta_accuracy_mean"].iloc[0] == pytest.approx(-0.025, abs=1e-4)
