"""
Logistic Regression Research Model Implementation.
"""
from typing import Optional
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from .base import BaseResearchModel


class LogisticRegressionModel(BaseResearchModel):
    """Linear classification baseline."""

    def __init__(self, random_state: int = 42, max_iter: int = 500, solver: str = "liblinear", C: float = 1.0, **kwargs):
        super().__init__("logistic_regression", random_state=random_state, max_iter=max_iter, solver=solver, C=C, **kwargs)
        self.estimator = LogisticRegression(
            random_state=self.random_state,
            max_iter=max_iter,
            solver=solver,
            C=C
        )

    def fit(self, X: pd.DataFrame, y: pd.Series, sample_weight: Optional[np.ndarray] = None) -> "LogisticRegressionModel":
        self.estimator.fit(X, y, sample_weight=sample_weight)
        self.is_fitted = True
        return self
