"""
Unit tests for result aggregator.
"""
import pytest
import os
import json
import pandas as pd
from research.analysis.aggregator import aggregate_raw_results


def test_aggregate_raw_results(tmp_path):
    raw_dir = tmp_path / "raw"
    processed_dir = tmp_path / "processed"
    raw_dir.mkdir(parents=True)
    
    # Create two dummy raw results
    dummy1 = {
        "experiment_id": "exp_1",
        "dataset_name": "adult",
        "model_name": "logistic_regression",
        "mitigation_name": "correlation_remover",
        "random_seed": 42,
        "is_synthetic_benchmark": True,
        "baseline_evaluation": {"performance": {"accuracy": {"value": 0.82}}, "fairness": {"demographic_parity_difference": {"value": 0.18}}},
        "mitigated_evaluation": {"performance": {"accuracy": {"value": 0.80}}, "fairness": {"demographic_parity_difference": {"value": 0.05}}},
        "attribution_comparison": {"cosine_similarity": 0.94},
        "trade_off_deltas": {"delta_accuracy": -0.02, "delta_demographic_parity_difference": -0.13}
    }
    dummy2 = {
        "experiment_id": "exp_2",
        "dataset_name": "adult",
        "model_name": "logistic_regression",
        "mitigation_name": "correlation_remover",
        "random_seed": 123,
        "is_synthetic_benchmark": True,
        "baseline_evaluation": {"performance": {"accuracy": {"value": 0.84}}, "fairness": {"demographic_parity_difference": {"value": 0.20}}},
        "mitigated_evaluation": {"performance": {"accuracy": {"value": 0.81}}, "fairness": {"demographic_parity_difference": {"value": 0.07}}},
        "attribution_comparison": {"cosine_similarity": 0.92},
        "trade_off_deltas": {"delta_accuracy": -0.03, "delta_demographic_parity_difference": -0.13}
    }
    
    with open(raw_dir / "res1.json", "w") as f:
        json.dump(dummy1, f)
    with open(raw_dir / "res2.json", "w") as f:
        json.dump(dummy2, f)
        
    summary_df = aggregate_raw_results(raw_dir=str(raw_dir), output_dir=str(processed_dir))
    
    assert summary_df is not None
    assert len(summary_df) == 1
    assert "delta_accuracy_mean" in summary_df.columns
    assert "delta_dpd_mean" in summary_df.columns
    assert summary_df["delta_accuracy_mean"].iloc[0] == pytest.approx(-0.025, abs=1e-4)
