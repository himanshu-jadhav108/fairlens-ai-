"""
Unit tests for candidate research models.
"""
import pytest
import numpy as np
import pandas as pd
from research.models.registry import get_model, list_models


@pytest.fixture
def dummy_train_data():
    X = pd.DataFrame({
        "f1": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0],
        "f2": [0.5, 0.2, 0.9, 0.1, 0.8, 0.3, 0.7, 0.4]
    })
    y = pd.Series([0, 0, 0, 0, 1, 1, 1, 1])
    return X, y


def test_list_models():
    models = list_models()
    assert "logistic_regression" in models
    assert "random_forest" in models
    assert "xgboost" in models


@pytest.mark.parametrize("mname", ["logistic_regression", "random_forest", "xgboost"])
def test_model_training_and_predict(mname, dummy_train_data):
    X, y = dummy_train_data
    model = get_model(mname, random_state=42)
    model.fit(X, y)
    
    preds = model.predict(X)
    assert len(preds) == len(X)
    assert set(preds).issubset({0, 1})
    
    probs = model.predict_proba(X)
    assert probs.shape == (len(X), 2)
    assert np.all((probs >= 0.0) & (probs <= 1.0))
