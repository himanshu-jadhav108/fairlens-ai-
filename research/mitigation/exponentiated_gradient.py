"""
ExponentiatedGradient In-Processing Mitigation Implementation.
Uses Fairlearn's reduction framework to optimize empirical loss subject to fairness constraints.
"""
from typing import Optional, Any
import numpy as np
import pandas as pd
from fairlearn.reductions import ExponentiatedGradient, DemographicParity, EqualizedOdds
from .base import BaseMitigation
from ..models.base import BaseResearchModel


class ExponentiatedGradientMitigation(BaseMitigation):
    """
    In-processing intervention: reduces fair classification to a sequence of
    cost-sensitive learning problems solved via game-theoretic optimization.
    """

    def __init__(
        self,
        base_model: BaseResearchModel,
        constraint: str = "demographic_parity",
        eps: float = 0.01,
        max_iter: int = 20,
        **kwargs
    ):
        super().__init__(
            "exponentiated_gradient",
            "inprocessing",
            constraint=constraint,
            eps=eps,
            max_iter=max_iter,
            **kwargs
        )
        self.base_model = base_model
        self.constraint_name = constraint
        self.eps = eps
        self.max_iter = max_iter
        
        if constraint.lower() in ["demographic_parity", "dp"]:
            self.constraint_obj = DemographicParity()
        elif constraint.lower() in ["equalized_odds", "eo"]:
            self.constraint_obj = EqualizedOdds()
        else:
            raise ValueError(f"Unsupported constraint '{constraint}'. Use 'demographic_parity' or 'equalized_odds'.")
            
        self.reduction_model = None

    def fit(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        s_train: pd.Series,
        X_val: Optional[pd.DataFrame] = None,
        y_val: Optional[pd.Series] = None,
        s_val: Optional[pd.Series] = None
    ) -> "ExponentiatedGradientMitigation":
        # Extract base estimator
        estimator = self.base_model.get_raw_estimator()
        
        self.reduction_model = ExponentiatedGradient(
            estimator=estimator,
            constraints=self.constraint_obj,
            eps=self.eps,
            max_iter=self.max_iter,
            sample_weight_name="sample_weight"
        )
        
        self.reduction_model.fit(
            X_train,
            y_train,
            sensitive_features=s_train.values
        )
        self.is_fitted = True
        return self

    def predict(self, X: pd.DataFrame, s: Optional[pd.Series] = None) -> np.ndarray:
        if not self.is_fitted:
            raise RuntimeError("ExponentiatedGradientMitigation must be fitted before predict().")
        return self.reduction_model.predict(X)

    def predict_proba(self, X: pd.DataFrame, s: Optional[pd.Series] = None) -> Optional[np.ndarray]:
        if not self.is_fitted:
            raise RuntimeError("ExponentiatedGradientMitigation must be fitted before predict_proba().")
        if hasattr(self.reduction_model, "_pmf_predict"):
            pmf = self.reduction_model._pmf_predict(X)
            # Binary PMF: column 0 is P(0), column 1 is P(1)
            return pmf
        return None

    def get_mitigated_estimator(self) -> Any:
        return self.reduction_model
