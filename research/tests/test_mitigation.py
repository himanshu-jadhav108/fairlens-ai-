"""
Unit tests for mitigation strategies.
"""
import pytest
import numpy as np
import pandas as pd
from research.models.registry import get_model
from research.mitigation.registry import get_mitigation, list_mitigations


@pytest.fixture
def dummy_mitigation_data():
    X_train = pd.DataFrame({
        "f1": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0],
        "f2": [0.5, 0.2, 0.9, 0.1, 0.8, 0.3, 0.7, 0.4, 0.6, 0.5, 0.8, 0.2]
    })
    y_train = pd.Series([0, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0])
    s_train = pd.Series(["A", "A", "A", "A", "A", "A", "B", "B", "B", "B", "B", "B"])
    
    X_val = pd.DataFrame({
        "f1": [2.5, 3.5, 6.5, 7.5],
        "f2": [0.3, 0.7, 0.6, 0.2]
    })
    y_val = pd.Series([0, 1, 0, 1])
    s_val = pd.Series(["A", "A", "B", "B"])
    
    return X_train, y_train, s_train, X_val, y_val, s_val


def test_list_mitigations():
    mits = list_mitigations()
    assert "correlation_remover" in mits
    assert "exponentiated_gradient" in mits
    assert "threshold_optimizer" in mits


@pytest.mark.parametrize("mit_name", ["correlation_remover", "exponentiated_gradient", "threshold_optimizer"])
def test_mitigation_fit_predict(mit_name, dummy_mitigation_data):
    X_tr, y_tr, s_tr, X_v, y_v, s_v = dummy_mitigation_data
    base = get_model("logistic_regression", random_state=42)
    
    mit = get_mitigation(mit_name, base_model=base)
    mit.fit(X_tr, y_tr, s_tr, X_v, y_v, s_v)
    
    preds = mit.predict(X_tr, s=s_tr)
    assert len(preds) == len(X_tr)
    assert set(preds).issubset({0, 1})
