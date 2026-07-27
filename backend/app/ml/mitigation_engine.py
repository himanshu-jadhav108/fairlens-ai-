import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple
from sklearn.linear_model import LogisticRegression
from fairlearn.reductions import ExponentiatedGradient, DemographicParity, EqualizedOdds
from fairlearn.postprocessing import ThresholdOptimizer
from fairlearn.preprocessing import CorrelationRemover

from .fairness_engine import FairnessEngine

class MitigationEngine:
    """
    Enterprise-grade Bias Mitigation Engine.
    Implements Pre-processing, In-processing, and Post-processing strategies.
    """

    def __init__(self, X_train: pd.DataFrame, y_train: pd.Series, X_test: pd.DataFrame, y_test: pd.Series, 
                 s_train: pd.Series, s_test: pd.Series, sensitive_col: str,
                 X_full: pd.DataFrame = None, s_full: pd.Series = None):
        self.X_train = X_train
        self.y_train = y_train
        self.X_test = X_test
        self.y_test = y_test
        self.s_train = s_train
        self.s_test = s_test
        self.sensitive_col = sensitive_col
        self.X_full = X_full
        self.s_full = s_full

    def _evaluate(self, y_pred_test: np.ndarray, y_pred_full: np.ndarray) -> Tuple[Dict[str, Any], np.ndarray]:
        """Helper to evaluate predictions using FairnessEngine."""
        engine = FairnessEngine(self.y_test.values, y_pred_test, self.s_test.values, self.sensitive_col)
        return engine.compute_all_metrics(), y_pred_full

    def run_preprocessing_mitigation(self) -> Tuple[Dict[str, Any], np.ndarray]:
        try:
            from sklearn.impute import SimpleImputer
            
            X_train_corr = self.X_train.copy()
            X_train_corr[self.sensitive_col] = self.s_train
            X_test_corr = self.X_test.copy()
            X_test_corr[self.sensitive_col] = self.s_test
            
            imputer = SimpleImputer(strategy='mean')
            X_train_corr_imputed = pd.DataFrame(imputer.fit_transform(X_train_corr), columns=X_train_corr.columns)
            X_test_corr_imputed = pd.DataFrame(imputer.transform(X_test_corr), columns=X_test_corr.columns)
            
            cr = CorrelationRemover(sensitive_feature_ids=[self.sensitive_col])
            X_train_clean = cr.fit_transform(X_train_corr_imputed)
            X_test_clean = cr.transform(X_test_corr_imputed)

            model = LogisticRegression(max_iter=200, random_state=42, solver='liblinear')
            model.fit(X_train_clean, self.y_train)
            y_pred_test = model.predict(X_test_clean)

            if self.X_full is not None and self.s_full is not None:
                X_full_corr = self.X_full.copy()
                X_full_corr[self.sensitive_col] = self.s_full
                X_full_corr_imputed = pd.DataFrame(imputer.transform(X_full_corr), columns=X_full_corr.columns)
                X_full_clean = cr.transform(X_full_corr_imputed)
                y_pred_full = model.predict(X_full_clean)
            else:
                y_pred_full = np.array([])

            return self._evaluate(y_pred_test, y_pred_full)
        except Exception as e:
            print(f"Pre-processing mitigation failed: {e}")
            return {}, np.array([])

    def run_inprocessing_mitigation(self) -> Tuple[Dict[str, Any], np.ndarray]:
        try:
            base_model = LogisticRegression(max_iter=200, random_state=42, solver='liblinear')
            eg = ExponentiatedGradient(
                estimator=base_model,
                constraints=DemographicParity(),
                sample_weight_name="sample_weight",
                max_iter=5
            )
            eg.fit(self.X_train, self.y_train, sensitive_features=self.s_train)
            y_pred_test = eg.predict(self.X_test)
            
            y_pred_full = eg.predict(self.X_full) if self.X_full is not None else np.array([])
            
            return self._evaluate(y_pred_test, y_pred_full)
        except Exception as e:
            print(f"In-processing mitigation failed: {e}")
            return {}, np.array([])

    def run_postprocessing_mitigation(self) -> Tuple[Dict[str, Any], np.ndarray]:
        try:
            base_model = LogisticRegression(max_iter=200, random_state=42, solver='liblinear')
            base_model.fit(self.X_train, self.y_train)

            optimizer = ThresholdOptimizer(
                estimator=base_model,
                constraints="demographic_parity",
                predict_method="predict_proba",
                prefit=True
            )
            optimizer.fit(self.X_train, self.y_train, sensitive_features=self.s_train)
            y_pred_test = optimizer.predict(self.X_test, sensitive_features=self.s_test)
            
            if self.X_full is not None and self.s_full is not None:
                y_pred_full = optimizer.predict(self.X_full, sensitive_features=self.s_full)
            else:
                y_pred_full = np.array([])
            
            return self._evaluate(y_pred_test, y_pred_full)
        except Exception as e:
            print(f"Post-processing mitigation failed: {e}")
            return {}, np.array([])
