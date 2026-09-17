"""
Unit tests for SHAP engine and attribution comparison metrics.
"""
import pytest
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from research.explainability.shap_engine import SHAPEngine
from research.explainability.comparison import compare_attributions


@pytest.fixture
def dummy_shap_data():
    rng = np.random.default_rng(42)
    X_train = pd.DataFrame(rng.normal(0, 1, size=(50, 4)), columns=["f1", "f2", "f3", "f4"])
    y_train = pd.Series((X_train["f1"] + X_train["f2"] > 0).astype(int))
    
    X_test = pd.DataFrame(rng.normal(0, 1, size=(30, 4)), columns=["f1", "f2", "f3", "f4"])
    s_test = pd.Series(rng.choice(["A", "B"], size=30))
    
    model = LogisticRegression(random_state=42)
    model.fit(X_train, y_train)
    return model, X_train, X_test, s_test


def test_shap_engine_execution_and_provenance(dummy_shap_data):
    model, X_train, X_test, s_test = dummy_shap_data
    engine = SHAPEngine(
        estimator=model,
        X_train=X_train,
        X_test=X_test,
        feature_names=list(X_train.columns),
        sensitive_test=s_test.values,
        explainer_type="linear",
        n_eval_samples=20,
        n_background_samples=20,
        random_seed=42
    )
    
    global_imp = engine.get_global_importance()
    assert len(global_imp) == 4
    assert all("feature" in item and "importance" in item for item in global_imp)
    
    subgroup_imp = engine.get_subgroup_importance()
    assert "A" in subgroup_imp and "B" in subgroup_imp
    
    prov = engine.get_provenance_metadata()
    assert "explainer_type" in prov
    assert "shap_version" in prov
    assert "feature_representation_order" in prov
    assert prov["n_eval_samples"] == 20


def test_compare_attributions():
    base = [{"feature": "f1", "importance": 0.8}, {"feature": "f2", "importance": 0.2}]
    mit = [{"feature": "f1", "importance": 0.7}, {"feature": "f2", "importance": 0.3}]
    
    res = compare_attributions(base, mit)
    assert res["provisional_status"] == "PROVISIONAL (pending literature review)"
    assert res["cosine_similarity"] > 0.9
    assert "spearman_rank_correlation" in res
    assert "l1_attribution_difference" in res
