"""
Unit tests for single experiment runner and manifest generation.
"""
import pytest
import os
from research.experiments.experiment_config import ExperimentConfig
from research.experiments.runner import run_single_experiment


def test_single_experiment_and_manifest(tmp_path):
    results_dir = str(tmp_path / "test_results")
    
    cfg = ExperimentConfig(
        dataset_name="adult",
        model_name="logistic_regression",
        mitigation_name="correlation_remover",
        seed=42,
        use_synthetic_benchmark=True,
        n_eval_samples=25,
        n_background_samples=25
    )
    
    raw_res, manifest = run_single_experiment(
        config=cfg,
        results_dir=results_dir,
        save_artifacts=True
    )
    
    # Verify raw result
    assert raw_res["experiment_id"] == cfg.experiment_id
    assert "baseline_evaluation" in raw_res
    assert "mitigated_evaluation" in raw_res
    assert "attribution_comparison" in raw_res
    assert "trade_off_deltas" in raw_res
    
    # Verify manifest (Correction 4)
    assert manifest["experiment_id"] == cfg.experiment_id
    assert "git_commit_hash" in manifest
    assert "environment" in manifest
    assert "scikit_learn_version" in manifest["environment"]
    assert "fairlearn_version" in manifest["environment"]
    assert "shap_version" in manifest["environment"]
    assert manifest["dataset"]["is_synthetic_benchmark"] is True
    
    # Verify artifacts written to disk
    manifest_file = os.path.join(results_dir, "manifests", f"{cfg.experiment_id}.json")
    raw_file = os.path.join(results_dir, "raw", f"adult__logistic_regression__correlation_remover__seed42.json")
    assert os.path.exists(manifest_file)
    assert os.path.exists(raw_file)
