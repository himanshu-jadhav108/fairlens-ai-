"""
Baseline Model Evaluation Module for FairLens AI Research.
Guarantees identical splits, preprocessing, and metrics for baseline vs mitigated comparisons.
"""
from typing import Dict, Any
import numpy as np
import pandas as pd
from ..models.base import BaseResearchModel
from ..fairness_metrics.evaluator import FairnessEvaluator
from ..performance_metrics.evaluator import PerformanceEvaluator
from ..explainability.shap_engine import SHAPEngine


def evaluate_baseline_model(
    model: BaseResearchModel,
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    s_test: pd.Series,
    feature_names: list,
    sensitive_col_name: str,
    privileged_group: Any = None,
    unprivileged_group: Any = None,
    n_eval_samples: int = 150,
    n_background_samples: int = 100,
    explainer_type: str = "auto",
    seed: int = 42
) -> Dict[str, Any]:
    """Fit baseline model and compute performance, fairness, and SHAP attributions."""
    # 1. Fit baseline model on training partition
    model.fit(X_train, y_train)
    
    # 2. Generate predictions on test partition
    y_pred = model.predict(X_test)
    try:
        y_prob = model.predict_proba(X_test)
    except Exception:
        y_prob = None

    # 3. Evaluate performance metrics
    perf_eval = PerformanceEvaluator(y_true=y_test.values, y_pred=y_pred, y_prob=y_prob)
    performance_metrics = perf_eval.evaluate_all()

    # 4. Evaluate fairness metrics
    fair_eval = FairnessEvaluator(
        y_true=y_test.values,
        y_pred=y_pred,
        sensitive_features=s_test.values,
        sensitive_col_name=sensitive_col_name,
        privileged_group=privileged_group,
        unprivileged_group=unprivileged_group
    )
    fairness_metrics = fair_eval.evaluate_all()

    # 5. Compute SHAP explanations
    shap_engine = SHAPEngine(
        estimator=model.get_raw_estimator(),
        X_train=X_train,
        X_test=X_test,
        feature_names=feature_names,
        sensitive_test=s_test.values,
        explainer_type=explainer_type,
        n_eval_samples=n_eval_samples,
        n_background_samples=n_background_samples,
        random_seed=seed
    )
    
    return {
        "model_name": model.name,
        "model_parameters": model.get_params(),
        "performance": performance_metrics,
        "fairness": fairness_metrics,
        "explainability": {
            "global_importance": shap_engine.get_global_importance(),
            "subgroup_importance": shap_engine.get_subgroup_importance(),
            "provenance": shap_engine.get_provenance_metadata()
        },
        "raw_predictions": y_pred.tolist(),
        "raw_probabilities": y_prob[:, 1].tolist() if (y_prob is not None and y_prob.ndim == 2) else None
    }
