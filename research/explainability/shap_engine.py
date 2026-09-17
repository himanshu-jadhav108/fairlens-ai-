"""
Reproducible SHAP Explainability Engine for FairLens AI Research.
Handles model-aware explainer selection, background reference sampling,
and complete provenance recording.
"""
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
import shap
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

try:
    from xgboost import XGBClassifier
    _XGB_AVAILABLE = True
except ImportError:
    _XGB_AVAILABLE = False


class SHAPEngine:
    """
    Model-aware SHAP explanation generator.
    Enforces complete provenance recording for scientific auditability.
    """

    def __init__(
        self,
        estimator: Any,
        X_train: pd.DataFrame,
        X_test: pd.DataFrame,
        feature_names: List[str],
        sensitive_test: Optional[np.ndarray] = None,
        explainer_type: str = "auto",
        n_eval_samples: int = 150,
        n_background_samples: int = 100,
        random_seed: int = 42
    ):
        self.estimator = estimator
        self.feature_names = list(feature_names)
        self.sensitive_test = np.asarray(sensitive_test) if sensitive_test is not None else None
        self.explainer_type_requested = explainer_type
        self.n_eval_samples = min(len(X_test), n_eval_samples)
        self.n_background_samples = min(len(X_train), n_background_samples)
        self.random_seed = random_seed
        
        # Subsample evaluation data deterministically
        rng = np.random.default_rng(self.random_seed)
        test_indices = rng.choice(len(X_test), size=self.n_eval_samples, replace=False)
        self.X_test_sample = X_test.iloc[test_indices].copy()
        self.sensitive_eval_sample = (
            self.sensitive_test[test_indices] if self.sensitive_test is not None else None
        )
        
        # Subsample background reference dataset
        bg_indices = rng.choice(len(X_train), size=self.n_background_samples, replace=False)
        self.background_data = X_train.iloc[bg_indices].copy()

        # Initialize explainer
        self.explainer, self.actual_explainer_type = self._init_explainer()
        self.shap_values = self._compute_shap_values()

    def _init_explainer(self):
        """Select appropriate SHAP explainer family based on underlying model architecture."""
        target_model = self.estimator
        # Unwrap if encapsulated in a reduction or pipeline
        if hasattr(target_model, "get_raw_estimator"):
            target_model = target_model.get_raw_estimator()

        req = self.explainer_type_requested.lower()
        if req == "linear" or (req == "auto" and isinstance(target_model, LogisticRegression)):
            explainer = shap.LinearExplainer(target_model, self.background_data)
            return explainer, "LinearExplainer"

        is_tree = isinstance(target_model, RandomForestClassifier)
        if _XGB_AVAILABLE and isinstance(target_model, XGBClassifier):
            is_tree = True

        if req == "tree" or (req == "auto" and is_tree):
            try:
                explainer = shap.TreeExplainer(target_model, data=self.background_data)
                return explainer, "TreeExplainer"
            except Exception:
                # TreeExplainer without background data fallback
                explainer = shap.TreeExplainer(target_model)
                return explainer, "TreeExplainer"

        # Model-agnostic fallback
        predict_fn = getattr(target_model, "predict_proba", target_model.predict)
        explainer = shap.KernelExplainer(predict_fn, self.background_data)
        return explainer, "KernelExplainer"

    def _compute_shap_values(self) -> np.ndarray:
        """Compute attribution matrix with proper handling of binary classification output shapes."""
        raw_values = self.explainer.shap_values(self.X_test_sample)
        
        # Handle SHAP output format discrepancies across versions and explainer types:
        # If list of arrays (e.g. [class_0, class_1]), select positive class (index 1)
        if isinstance(raw_values, list):
            if len(raw_values) == 2:
                values = np.asarray(raw_values[1])
            else:
                values = np.asarray(raw_values[0])
        elif isinstance(raw_values, np.ndarray):
            if raw_values.ndim == 3 and raw_values.shape[2] == 2:
                values = raw_values[:, :, 1]
            else:
                values = raw_values
        elif hasattr(raw_values, "values"):
            values = np.asarray(raw_values.values)
            if values.ndim == 3 and values.shape[2] == 2:
                values = values[:, :, 1]
        else:
            values = np.asarray(raw_values)
            
        return values

    def get_global_importance(self) -> List[Dict[str, Any]]:
        """Mean absolute SHAP value across evaluation sample."""
        mean_abs = np.abs(self.shap_values).mean(axis=0)
        importance = []
        for i, fname in enumerate(self.feature_names):
            importance.append({
                "feature": fname,
                "importance": round(float(mean_abs[i]), 6)
            })
        importance.sort(key=lambda x: x["importance"], reverse=True)
        return importance

    def get_subgroup_importance(self) -> Dict[str, List[Dict[str, Any]]]:
        """Mean absolute SHAP value partitioned by sensitive demographic group."""
        if self.sensitive_eval_sample is None:
            return {}

        unique_groups = np.unique(self.sensitive_eval_sample)
        group_results = {}
        
        for g in unique_groups:
            mask = (self.sensitive_eval_sample == g)
            if mask.sum() == 0:
                continue
            group_shap = self.shap_values[mask]
            group_mean_abs = np.abs(group_shap).mean(axis=0)
            
            group_list = []
            for i, fname in enumerate(self.feature_names):
                group_list.append({
                    "feature": fname,
                    "importance": round(float(group_mean_abs[i]), 6)
                })
            group_list.sort(key=lambda x: x["importance"], reverse=True)
            group_results[str(g)] = group_list

        return group_results

    def get_provenance_metadata(self) -> Dict[str, Any]:
        """Detailed SHAP audit provenance metadata (Correction 3)."""
        return {
            "explainer_type": self.actual_explainer_type,
            "explainer_selection_mode": self.explainer_type_requested,
            "shap_version": str(shap.__version__),
            "background_reference_description": f"Random sample of {self.n_background_samples} training instances.",
            "evaluation_sample_description": f"Random sample of {self.n_eval_samples} test instances.",
            "feature_representation_order": self.feature_names,
            "number_of_features": len(self.feature_names),
            "n_eval_samples": self.n_eval_samples,
            "n_background_samples": self.n_background_samples,
            "random_seed": self.random_seed
        }
