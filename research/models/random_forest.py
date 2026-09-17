"""
Random Forest Classifier Research Model Implementation.
"""
from typing import Optional
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from .base import BaseResearchModel


class RandomForestModel(BaseResearchModel):
    """Non-linear bagged ensemble."""

    def __init__(
        self,
        random_state: int = 42,
        n_estimators: int = 100,
        max_depth: Optional[int] = 10,
        min_samples_split: int = 5,
        **kwargs
    ):
        super().__init__(
            "random_forest",
            random_state=random_state,
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            **kwargs
        )
        self.estimator = RandomForestClassifier(
            random_state=self.random_state,
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_split=min_samples_split
        )

    def fit(self, X: pd.DataFrame, y: pd.Series, sample_weight: Optional[np.ndarray] = None) -> "RandomForestModel":
        self.estimator.fit(X, y, sample_weight=sample_weight)
        self.is_fitted = True
        return self
