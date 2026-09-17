"""
Base Model Abstraction for FairLens AI Research.
Provides a uniform protocol for training, hard predictions, probability estimates,
and hyperparameter introspection across diverse model families.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import numpy as np
import pandas as pd


class BaseResearchModel(ABC):
    """Abstract interface for candidate machine learning models."""

    def __init__(self, name: str, random_state: int = 42, **hyperparameters):
        self.name = name
        self.random_state = random_state
        self.hyperparameters = hyperparameters
        self.estimator = None
        self.is_fitted = False

    @abstractmethod
    def fit(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        sample_weight: Optional[np.ndarray] = None
    ) -> "BaseResearchModel":
        """Fit model estimator with optional sample weights."""
        pass

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Generate hard binary classification predictions."""
        if not self.is_fitted:
            raise RuntimeError(f"Model '{self.name}' must be fitted before predict().")
        return self.estimator.predict(X)

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """Generate prediction probabilities [P(y=0), P(y=1)]."""
        if not self.is_fitted:
            raise RuntimeError(f"Model '{self.name}' must be fitted before predict_proba().")
        if hasattr(self.estimator, "predict_proba"):
            return self.estimator.predict_proba(X)
        raise NotImplementedError(f"Estimator '{self.name}' does not implement predict_proba.")

    def get_params(self) -> Dict[str, Any]:
        """Return hyperparameter configuration dictionary."""
        params = {"name": self.name, "random_state": self.random_state}
        params.update(self.hyperparameters)
        return params

    def get_raw_estimator(self) -> Any:
        """Access underlying Scikit-Learn or XGBoost estimator instance."""
        return self.estimator
