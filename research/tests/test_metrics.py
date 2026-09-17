"""
Unit tests for fairness and performance metric evaluators.
"""
import pytest
import numpy as np
from research.fairness_metrics.evaluator import FairnessEvaluator
from research.performance_metrics.evaluator import PerformanceEvaluator


def test_fairness_evaluator_standard():
    y_true = np.array([1, 0, 1, 0, 1, 0, 1, 0])
    y_pred = np.array([1, 0, 0, 0, 1, 1, 1, 0])
    sensitive = np.array(["M", "M", "M", "M", "F", "F", "F", "F"])
    
    evaluator = FairnessEvaluator(
        y_true=y_true,
        y_pred=y_pred,
        sensitive_features=sensitive,
        sensitive_col_name="sex",
        privileged_group="M",
        unprivileged_group="F"
    )
    res = evaluator.evaluate_all()
    
    assert res["demographic_parity_difference"]["defined"] is True
    assert res["equalized_odds_difference"]["defined"] is True
    assert res["equal_opportunity_difference"]["defined"] is True
    assert res["disparate_impact_ratio"]["defined"] is True
    assert len(res["subgroup_statistics"]) == 2


def test_fairness_evaluator_undefined_metric_recorded():
    # Only 1 group present
    y_true = np.array([1, 0, 1, 0])
    y_pred = np.array([1, 0, 0, 0])
    sensitive = np.array(["M", "M", "M", "M"])
    
    evaluator = FairnessEvaluator(
        y_true=y_true,
        y_pred=y_pred,
        sensitive_features=sensitive,
        sensitive_col_name="sex"
    )
    res = evaluator.evaluate_all()
    
    # Must record reason without crashing or silently defaulting to 0
    assert res["demographic_parity_difference"]["defined"] is False
    assert "Fewer than two" in res["demographic_parity_difference"]["reason"]


def test_performance_evaluator():
    y_true = np.array([1, 0, 1, 0])
    y_pred = np.array([1, 0, 1, 0])
    y_prob = np.array([[0.1, 0.9], [0.8, 0.2], [0.2, 0.8], [0.9, 0.1]])
    
    evaluator = PerformanceEvaluator(y_true=y_true, y_pred=y_pred, y_prob=y_prob)
    res = evaluator.evaluate_all()
    
    assert res["accuracy"]["value"] == 1.0
    assert res["precision"]["value"] == 1.0
    assert res["recall"]["value"] == 1.0
    assert res["f1_score"]["value"] == 1.0
    assert res["roc_auc"]["value"] == 1.0
