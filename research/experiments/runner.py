"""
Single Experiment Runner for FairLens AI Research.
Executes paired baseline vs. mitigated experimental evaluations with complete provenance,
manifest generation, and leak-free split isolation.
"""
import os
import sys
import json
import time
import datetime
import subprocess
from typing import Dict, Any, Tuple, Optional
import numpy as np
import pandas as pd
import sklearn
import fairlearn
import shap
import scipy

try:
    import xgboost
    _XGB_VERSION = str(xgboost.__version__)
except ImportError:
    _XGB_VERSION = "not_installed"

from .experiment_config import ExperimentConfig
from .baseline import evaluate_baseline_model
from ..datasets.registry import get_dataset
from ..preprocessing.preprocessor import ResearchPreprocessor
from ..models.registry import get_model
from ..mitigation.registry import get_mitigation
from ..fairness_metrics.evaluator import FairnessEvaluator
from ..performance_metrics.evaluator import PerformanceEvaluator
from ..explainability.shap_engine import SHAPEngine
from ..explainability.comparison import compare_attributions


def get_git_commit_hash() -> str:
    """Safely obtain current Git commit hash for provenance recording."""
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            stderr=subprocess.DEVNULL
        ).decode("ascii").strip()
        return commit
    except Exception:
        return "git_commit_unavailable"


def run_single_experiment(
    config: ExperimentConfig,
    results_dir: str = "research/results",
    save_artifacts: bool = True
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Executes a single end-to-end experiment with paired baseline and mitigated evaluations.
    Returns: (result_dict, manifest_dict)
    """
    start_time = time.time()
    git_hash = get_git_commit_hash()
    timestamp_str = datetime.datetime.now(datetime.timezone.utc).isoformat()

    # 1. Dataset Loading & Partitioning
    dataset_loader = get_dataset(config.dataset_name)
    df = dataset_loader.load_data(
        use_synthetic_benchmark=config.use_synthetic_benchmark,
        local_path=config.local_dataset_path
    )
    splits = dataset_loader.create_splits(
        df=df,
        train_ratio=config.train_ratio,
        val_ratio=config.val_ratio,
        test_ratio=config.test_ratio,
        random_seed=config.seed
    )

    # 2. Leak-Free Preprocessing (fitted strictly on training split)
    preprocessor = ResearchPreprocessor(
        categorical_columns=dataset_loader.metadata.categorical_columns,
        numeric_columns=dataset_loader.metadata.numeric_columns,
        drop_sensitive_from_features=False,
        sensitive_col=dataset_loader.metadata.sensitive_column
    )
    X_train_proc = preprocessor.fit_transform(splits.X_train)
    X_val_proc = preprocessor.transform(splits.X_val)
    X_test_proc = preprocessor.transform(splits.X_test)
    proc_feature_names = preprocessor.transformed_feature_names

    # 3. Baseline Evaluation
    baseline_model = get_model(config.model_name, random_state=config.seed, **config.model_params)
    baseline_eval = evaluate_baseline_model(
        model=baseline_model,
        X_train=X_train_proc,
        y_train=splits.y_train,
        X_test=X_test_proc,
        y_test=splits.y_test,
        s_test=splits.s_test,
        feature_names=proc_feature_names,
        sensitive_col_name=dataset_loader.metadata.sensitive_column,
        privileged_group=dataset_loader.metadata.privileged_value,
        unprivileged_group=dataset_loader.metadata.unprivileged_value,
        n_eval_samples=config.n_eval_samples,
        n_background_samples=config.n_background_samples,
        explainer_type=config.explainer_type,
        seed=config.seed
    )

    # 4. Mitigated Model Evaluation
    mit_base_model = get_model(config.model_name, random_state=config.seed, **config.model_params)
    mitigation = get_mitigation(
        config.mitigation_name,
        base_model=mit_base_model,
        **config.mitigation_params
    )
    
    # Fit mitigation (validation split used for threshold calibration to prevent test leakage)
    mitigation.fit(
        X_train=X_train_proc,
        y_train=splits.y_train,
        s_train=splits.s_train,
        X_val=X_val_proc,
        y_val=splits.y_val,
        s_val=splits.s_val
    )

    # Test set predictions
    y_pred_mit = mitigation.predict(X_test_proc, s=splits.s_test)
    try:
        y_prob_mit = mitigation.predict_proba(X_test_proc, s=splits.s_test)
    except Exception:
        y_prob_mit = None

    # Mitigated performance evaluation
    mit_perf_eval = PerformanceEvaluator(
        y_true=splits.y_test.values,
        y_pred=y_pred_mit,
        y_prob=y_prob_mit
    )
    mit_perf = mit_perf_eval.evaluate_all()

    # Mitigated fairness evaluation
    mit_fair_eval = FairnessEvaluator(
        y_true=splits.y_test.values,
        y_pred=y_pred_mit,
        sensitive_features=splits.s_test.values,
        sensitive_col_name=dataset_loader.metadata.sensitive_column,
        privileged_group=dataset_loader.metadata.privileged_value,
        unprivileged_group=dataset_loader.metadata.unprivileged_value
    )
    mit_fair = mit_fair_eval.evaluate_all()

    # Mitigated SHAP attribution
    mit_shap_engine = SHAPEngine(
        estimator=mitigation.get_mitigated_estimator(),
        X_train=X_train_proc,
        X_test=X_test_proc,
        feature_names=proc_feature_names,
        sensitive_test=splits.s_test.values,
        explainer_type=config.explainer_type,
        n_eval_samples=config.n_eval_samples,
        n_background_samples=config.n_background_samples,
        random_seed=config.seed
    )
    mit_global_shap = mit_shap_engine.get_global_importance()
    mit_subgroup_shap = mit_shap_engine.get_subgroup_importance()
    mit_shap_provenance = mit_shap_engine.get_provenance_metadata()

    # 5. Feature Attribution Comparison (Provisional)
    attribution_comparison = compare_attributions(
        baseline_importance=baseline_eval["explainability"]["global_importance"],
        mitigated_importance=mit_global_shap
    )

    # 6. Trade-Off Deltas (Mitigated - Baseline)
    base_acc = baseline_eval["performance"]["accuracy"]["value"]
    mit_acc = mit_perf["accuracy"]["value"]
    delta_acc = round(mit_acc - base_acc, 4) if (base_acc is not None and mit_acc is not None) else None

    base_f1 = baseline_eval["performance"]["f1_score"]["value"]
    mit_f1 = mit_perf["f1_score"]["value"]
    delta_f1 = round(mit_f1 - base_f1, 4) if (base_f1 is not None and mit_f1 is not None) else None

    base_dpd = baseline_eval["fairness"]["demographic_parity_difference"]["value"]
    mit_dpd = mit_fair["demographic_parity_difference"]["value"]
    delta_dpd = round(mit_dpd - base_dpd, 4) if (base_dpd is not None and mit_dpd is not None) else None

    base_eod = baseline_eval["fairness"]["equalized_odds_difference"]["value"]
    mit_eod = mit_fair["equalized_odds_difference"]["value"]
    delta_eod = round(mit_eod - base_eod, 4) if (base_eod is not None and mit_eod is not None) else None

    elapsed_time = round(time.time() - start_time, 2)

    # 7. Construct Machine-Readable Experiment Manifest (Correction 4)
    manifest = {
        "experiment_id": config.experiment_id,
        "git_commit_hash": git_hash,
        "timestamp_utc": timestamp_str,
        "runtime_seconds": elapsed_time,
        "dataset": {
            "name": dataset_loader.metadata.name,
            "official_title": dataset_loader.metadata.official_title,
            "source_url": dataset_loader.metadata.source_url,
            "version": dataset_loader.metadata.version_or_release,
            "license": dataset_loader.metadata.license_name,
            "is_synthetic_benchmark": dataset_loader.metadata.is_synthetic_benchmark,
            "target_column": dataset_loader.metadata.target_column,
            "sensitive_column": dataset_loader.metadata.sensitive_column,
            "split_id": splits.split_id,
            "train_samples": len(splits.X_train),
            "val_samples": len(splits.X_val),
            "test_samples": len(splits.X_test),
        },
        "model": {
            "family": config.model_name,
            "parameters": config.model_params
        },
        "mitigation": {
            "name": config.mitigation_name,
            "strategy_type": mitigation.strategy_type,
            "parameters": config.mitigation_params,
            "calibration_split": getattr(mitigation, "calibration_split_used", "train")
        },
        "random_seed": config.seed,
        "train_val_test_strategy": {
            "train_ratio": config.train_ratio,
            "val_ratio": config.val_ratio,
            "test_ratio": config.test_ratio,
            "stratified": True
        },
        "preprocessing_configuration": {
            "preprocessor_type": "ResearchPreprocessor",
            "transformed_features_count": len(proc_feature_names),
            "feature_names": proc_feature_names
        },
        "environment": {
            "python_version": sys.version.split()[0],
            "scikit_learn_version": sklearn.__version__,
            "fairlearn_version": fairlearn.__version__,
            "shap_version": shap.__version__,
            "xgboost_version": _XGB_VERSION,
            "pandas_version": pd.__version__,
            "numpy_version": np.__version__,
            "scipy_version": scipy.__version__,
        }
    }

    # 8. Complete Raw Result Payload
    raw_result = {
        "experiment_id": config.experiment_id,
        "manifest_reference": f"manifests/{config.experiment_id}.json",
        "dataset_name": config.dataset_name,
        "model_name": config.model_name,
        "mitigation_name": config.mitigation_name,
        "random_seed": config.seed,
        "is_synthetic_benchmark": dataset_loader.metadata.is_synthetic_benchmark,
        "baseline_evaluation": {
            "performance": baseline_eval["performance"],
            "fairness": baseline_eval["fairness"],
            "global_shap": baseline_eval["explainability"]["global_importance"],
            "subgroup_shap": baseline_eval["explainability"]["subgroup_importance"],
            "shap_provenance": baseline_eval["explainability"]["provenance"]
        },
        "mitigated_evaluation": {
            "performance": mit_perf,
            "fairness": mit_fair,
            "global_shap": mit_global_shap,
            "subgroup_shap": mit_subgroup_shap,
            "shap_provenance": mit_shap_provenance
        },
        "attribution_comparison": attribution_comparison,
        "trade_off_deltas": {
            "delta_accuracy": delta_acc,
            "delta_f1_score": delta_f1,
            "delta_demographic_parity_difference": delta_dpd,
            "delta_equalized_odds_difference": delta_eod
        }
    }

    # 9. Persistence to File System
    if save_artifacts:
        manifest_dir = os.path.join(results_dir, "manifests")
        raw_dir = os.path.join(results_dir, "raw")
        os.makedirs(manifest_dir, exist_ok=True)
        os.makedirs(raw_dir, exist_ok=True)

        manifest_file = os.path.join(manifest_dir, f"{config.experiment_id}.json")
        with open(manifest_file, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

        raw_filename = f"{config.dataset_name}__{config.model_name}__{config.mitigation_name}__seed{config.seed}.json"
        raw_file = os.path.join(raw_dir, raw_filename)
        with open(raw_file, "w", encoding="utf-8") as f:
            json.dump(raw_result, f, indent=2)

    return raw_result, manifest
