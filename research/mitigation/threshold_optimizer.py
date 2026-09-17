"""
ThresholdOptimizer Post-Processing Mitigation Implementation.
Calibrates group-specific decision thresholds post-training.
Guarantees strict separation between training/calibration and final test evaluation.
"""
from typing import Optional, Any
import numpy as np
import pandas as pd
from fairlearn.postprocessing import ThresholdOptimizer
from .base import BaseMitigation
from ..models.base import BaseResearchModel


class ThresholdOptimizerMitigation(BaseMitigation):
    """
    Post-processing intervention: adjusts decision thresholds per demographic subgroup
    to equalize selection rates or error rates.
    """

    def __init__(
        self,
        base_model: BaseResearchModel,
        constraint: str = "demographic_parity",
        predict_method: str = "predict_proba",
        **kwargs
    ):
        super().__init__(
            "threshold_optimizer",
            "postprocessing",
            constraint=constraint,
            predict_method=predict_method,
            **kwargs
        )
        self.base_model = base_model
        self.constraint = constraint
        self.predict_method = predict_method
        self.optimizer = None
        self.calibration_split_used = "train"

    def fit(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        s_train: pd.Series,
        X_val: Optional[pd.DataFrame] = None,
        y_val: Optional[pd.Series] = None,
        s_val: Optional[pd.Series] = None
    ) -> "ThresholdOptimizerMitigation":
        # Step 1: Fit underlying base model on training partition
        self.base_model.fit(X_train, y_train)

        # Step 2: Initialize postprocessing optimizer
        raw_estimator = self.base_model.get_raw_estimator()
        self.optimizer = ThresholdOptimizer(
            estimator=raw_estimator,
            constraints=self.constraint,
            predict_method=self.predict_method,
            prefit=True
        )

        # Step 3: Calibrate thresholds
        # To prevent threshold overfitting, calibrate on validation partition if supplied and non-degenerate.
        # Under NO circumstances is test data permitted during threshold fitting.
        calibrated = False
        if X_val is not None and y_val is not None and s_val is not None and len(X_val) >= 4:
            try:
                # Check if each group has at least one positive and one negative label
                valid_groups = True
                for g in np.unique(s_val):
                    g_mask = (s_val == g)
                    g_labels = y_val[g_mask]
                    if len(np.unique(g_labels)) < 2:
                        valid_groups = False
                        break
                if valid_groups:
                    self.optimizer.fit(X_val, y_val, sensitive_features=s_val.values)
                    self.calibration_split_used = "validation"
                    calibrated = True
            except Exception:
                calibrated = False

        if not calibrated:
            self.optimizer.fit(X_train, y_train, sensitive_features=s_train.values)
            self.calibration_split_used = "train"

        self.is_fitted = True
        return self

    def predict(self, X: pd.DataFrame, s: Optional[pd.Series] = None) -> np.ndarray:
        if not self.is_fitted:
            raise RuntimeError("ThresholdOptimizerMitigation must be fitted before predict().")
        if s is None:
            raise ValueError("ThresholdOptimizer requires sensitive_features series 's' for inference.")
        return self.optimizer.predict(X, sensitive_features=s.values)

    def predict_proba(self, X: pd.DataFrame, s: Optional[pd.Series] = None) -> Optional[np.ndarray]:
        # Post-processed thresholding outputs discrete calibrated decisions
        return None

    def get_mitigated_estimator(self) -> Any:
        return self.optimizer
