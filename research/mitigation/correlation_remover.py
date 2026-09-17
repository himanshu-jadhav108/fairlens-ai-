"""
CorrelationRemover Pre-Processing Mitigation Implementation.
Leverages Fairlearn's CorrelationRemover to project features into a subspace
orthogonal to the sensitive attribute.
"""
from typing import Optional, Any
import numpy as np
import pandas as pd
from fairlearn.preprocessing import CorrelationRemover
from .base import BaseMitigation
from ..models.base import BaseResearchModel


class CorrelationRemoverMitigation(BaseMitigation):
    """
    Pre-processing intervention: decorrelates non-sensitive features
    from protected characteristics using linear projection.
    """

    def __init__(self, base_model: BaseResearchModel, alpha: float = 1.0, sensitive_col: str = "sensitive"):
        super().__init__("correlation_remover", "preprocessing", alpha=alpha, sensitive_col=sensitive_col)
        self.base_model = base_model
        self.alpha = alpha
        self.sensitive_col = sensitive_col
        self.remover = None
        self.feature_columns_ = []

    def fit(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        s_train: pd.Series,
        X_val: Optional[pd.DataFrame] = None,
        y_val: Optional[pd.Series] = None,
        s_val: Optional[pd.Series] = None
    ) -> "CorrelationRemoverMitigation":
        # Create joint feature matrix including sensitive attribute for projection
        X_corr = X_train.copy()
        sensitive_name = s_train.name if s_train.name else self.sensitive_col
        
        # Ensure sensitive attribute is numeric for CorrelationRemover
        if s_train.dtype == object or isinstance(s_train.iloc[0], str):
            s_codes, self.categories_ = pd.factorize(s_train)
            X_corr[sensitive_name] = s_codes.astype(float)
        else:
            self.categories_ = None
            X_corr[sensitive_name] = s_train.values.astype(float)

        # Initialize and fit Fairlearn CorrelationRemover
        self.remover = CorrelationRemover(sensitive_feature_ids=[sensitive_name], alpha=self.alpha)
        X_clean = self.remover.fit_transform(X_corr)
        
        # Determine cleaned column count
        self.feature_columns_ = [f"f_{i}" for i in range(X_clean.shape[1])]
        X_clean_df = pd.DataFrame(X_clean, columns=self.feature_columns_)

        # Fit underlying base model on decorrelated features
        self.base_model.fit(X_clean_df, y_train)
        self.is_fitted = True
        return self

    def _transform_features(self, X: pd.DataFrame, s: Optional[pd.Series] = None) -> pd.DataFrame:
        """Helper to project incoming features with fitted CorrelationRemover."""
        X_corr = X.copy()
        sensitive_name = s.name if (s is not None and s.name) else self.sensitive_col
        if s is not None:
            if hasattr(self, "categories_") and self.categories_ is not None:
                # Map using categories_ if available, else factorize
                cat_map = {cat: idx for idx, cat in enumerate(self.categories_)}
                s_numeric = s.map(cat_map).fillna(0).values.astype(float)
            else:
                try:
                    s_numeric = s.values.astype(float)
                except Exception:
                    s_numeric, _ = pd.factorize(s)
                    s_numeric = s_numeric.astype(float)
            X_corr[sensitive_name] = s_numeric
        elif sensitive_name not in X_corr.columns:
            # Fallback zero if sensitive feature series not passed
            X_corr[sensitive_name] = 0.0

        X_clean = self.remover.transform(X_corr)
        return pd.DataFrame(X_clean, columns=self.feature_columns_)

    def predict(self, X: pd.DataFrame, s: Optional[pd.Series] = None) -> np.ndarray:
        if not self.is_fitted:
            raise RuntimeError("CorrelationRemoverMitigation must be fitted before predict().")
        X_clean_df = self._transform_features(X, s)
        return self.base_model.predict(X_clean_df)

    def predict_proba(self, X: pd.DataFrame, s: Optional[pd.Series] = None) -> Optional[np.ndarray]:
        if not self.is_fitted:
            raise RuntimeError("CorrelationRemoverMitigation must be fitted before predict_proba().")
        X_clean_df = self._transform_features(X, s)
        return self.base_model.predict_proba(X_clean_df)

    def get_mitigated_estimator(self) -> Any:
        return self.base_model.get_raw_estimator()
