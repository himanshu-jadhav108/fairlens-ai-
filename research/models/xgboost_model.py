"""
XGBoost Classifier Research Model Implementation.
"""
from typing import Optional
import numpy as np
import pandas as pd
from .base import BaseResearchModel

try:
    from xgboost import XGBClassifier
    _XGB_AVAILABLE = True
except ImportError:
    _XGB_AVAILABLE = False


class XGBoostModel(BaseResearchModel):
    """Gradient boosted decision trees implementation."""

    def __init__(
        self,
        random_state: int = 42,
        n_estimators: int = 100,
        max_depth: int = 5,
        learning_rate: float = 0.1,
        **kwargs
    ):
        super().__init__(
            "xgboost",
            random_state=random_state,
            n_estimators=n_estimators,
            max_depth=max_depth,
            learning_rate=learning_rate,
            **kwargs
        )
        if not _XGB_AVAILABLE:
            raise ImportError("xgboost package is required for XGBoostModel. Please install xgboost.")
            
        self.estimator = XGBClassifier(
            random_state=self.random_state,
            n_estimators=n_estimators,
            max_depth=max_depth,
            learning_rate=learning_rate,
            eval_metric="logloss"
        )

    def fit(self, X: pd.DataFrame, y: pd.Series, sample_weight: Optional[np.ndarray] = None) -> "XGBoostModel":
        self.estimator.fit(X, y, sample_weight=sample_weight)
        self.is_fitted = True
        return self
