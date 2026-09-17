"""
Base Mitigation Interface and Taxonomy for FairLens AI Research.
Classifies methods cleanly into Pre-processing, In-processing, and Post-processing.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import numpy as np
import pandas as pd


class BaseMitigation(ABC):
    """Abstract interface for all bias mitigation strategies."""

    def __init__(self, name: str, strategy_type: str, **hyperparameters):
        assert strategy_type in ["preprocessing", "inprocessing", "postprocessing"], \
            f"Invalid strategy_type: {strategy_type}"
        self.name = name
        self.strategy_type = strategy_type
        self.hyperparameters = hyperparameters
        self.is_fitted = False

    @abstractmethod
    def fit(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        s_train: pd.Series,
        X_val: Optional[pd.DataFrame] = None,
        y_val: Optional[pd.Series] = None,
        s_val: Optional[pd.Series] = None
    ) -> "BaseMitigation":
        """
        Fit mitigation intervention.
        Post-processing strategies may use validation partition for calibration
        to prevent threshold overfitting and test leakage.
        """
        pass

    @abstractmethod
    def predict(self, X: pd.DataFrame, s: Optional[pd.Series] = None) -> np.ndarray:
        """Generate mitigated binary predictions."""
        pass

    def predict_proba(self, X: pd.DataFrame, s: Optional[pd.Series] = None) -> Optional[np.ndarray]:
        """Generate prediction probabilities if supported by the mitigation method."""
        return None

    def get_params(self) -> Dict[str, Any]:
        """Return mitigation hyperparameters and configuration."""
        params = {"name": self.name, "strategy_type": self.strategy_type}
        params.update(self.hyperparameters)
        return params

    @abstractmethod
    def get_mitigated_estimator(self) -> Any:
        """Return the underlying model or composite estimator."""
        pass
