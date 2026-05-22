import shap
import pandas as pd
import numpy as np
from typing import Dict, Any, List

class ExplainabilityEngine:
    """
    Enterprise SHAP Explainability Engine.
    Handles Global, Demographic, and Local interpretability.
    """
    def __init__(self, model, X_train_scaled: pd.DataFrame, X_test_scaled: pd.DataFrame, 
                 feature_names: List[str], sensitive_test: np.ndarray, y_test: np.ndarray = None):
        self.model = model
        self.X_train_scaled = X_train_scaled
        
        # In production, we limit the test background size to prevent API timeouts
        # SHAP calculation is O(N * F), so we cap at 150 samples unless otherwise needed
        max_samples = min(len(X_test_scaled), 150)
        
        # Sample uniformly
        np.random.seed(42)
        indices = np.random.choice(len(X_test_scaled), max_samples, replace=False)
        
        self.X_test_sample = X_test_scaled.iloc[indices]
        self.sensitive_sample = sensitive_test[indices] if sensitive_test is not None else None
        
        if y_test is not None:
            if isinstance(y_test, pd.Series):
                y_test = y_test.values
            self.y_test_sample = y_test[indices]
        else:
            self.y_test_sample = None

        self.feature_names = feature_names
        
        # Initialize explainer
        # We use LinearExplainer because we enforce Logistic Regression for the MVP
        self.explainer = shap.LinearExplainer(self.model, self.X_train_scaled)
        self.shap_values = self.explainer.shap_values(self.X_test_sample)

    def compute_global_shap(self) -> List[Dict[str, Any]]:
        """
        Computes overall global feature importance (mean absolute SHAP).
        """
        mean_abs_shap = np.abs(self.shap_values).mean(axis=0)
        
        importance = []
        for i, f_name in enumerate(self.feature_names):
            importance.append({
                "feature": f_name,
                "importance": float(mean_abs_shap[i])
            })
            
        # Sort descending
        importance.sort(key=lambda x: x["importance"], reverse=True)
        return importance

    def compute_demographic_shap(self) -> Dict[str, Any]:
        """
        Computes average feature importance broken down by demographic group.
        Also calculates 'disparity' (which features penalize groups differently).
        """
        if self.sensitive_sample is None:
            return {}

        unique_groups = np.unique(self.sensitive_sample)
        group_attributions = {}
        
        # Calculate mean absolute SHAP for each group
        for g in unique_groups:
            mask = (self.sensitive_sample == g)
            if mask.sum() == 0:
                continue
                
            group_shap = self.shap_values[mask]
            mean_abs_group_shap = np.abs(group_shap).mean(axis=0)
            
            group_dict = {}
            for i, f_name in enumerate(self.feature_names):
                group_dict[f_name] = float(mean_abs_group_shap[i])
            
            group_attributions[str(g)] = group_dict

        # Calculate feature disparity (Max Importance - Min Importance across groups)
        disparities = []
        for f_name in self.feature_names:
            group_vals = [group_attributions[str(g)][f_name] for g in unique_groups if str(g) in group_attributions]
            if len(group_vals) > 1:
                disp = max(group_vals) - min(group_vals)
                disparities.append({
                    "feature": f_name,
                    "disparity": float(disp)
                })
        
        disparities.sort(key=lambda x: x["disparity"], reverse=True)

        return {
            "group_importance": group_attributions,
            "top_disparities": disparities[:5]
        }

    def compute_local_shap(self) -> Dict[str, Any]:
        """
        Finds the 'most unfairly rejected' individual (a False Negative if y_test is provided,
        or just the lowest probability prediction) and explains exactly why they were rejected.
        """
        preds = self.model.predict(self.X_test_sample)
        probs = self.model.predict_proba(self.X_test_sample)[:, 1]
        
        target_idx = 0
        if self.y_test_sample is None:
            # If no truth labels, find the lowest probability prediction
            target_idx = np.argmin(probs)
        else:
            # Find a False Negative (y_true=1, y_pred=0) with the lowest probability
            fn_mask = (self.y_test_sample == 1) & (preds == 0)
            if fn_mask.sum() > 0:
                fn_indices = np.where(fn_mask)[0]
                # Out of false negatives, find the one the model was most confident rejecting
                target_idx = fn_indices[np.argmin(probs[fn_indices])]
            else:
                # Fallback to lowest probability overall
                target_idx = np.argmin(probs)
        
        local_shap = self.shap_values[target_idx]
        local_features = self.X_test_sample.iloc[target_idx].to_dict()
        
        contributions = []
        for i, f_name in enumerate(self.feature_names):
            contributions.append({
                "feature": f_name,
                "value": local_features[f_name],
                "shap_impact": float(local_shap[i])
            })
            
        # Sort by absolute impact to show the most important drivers first
        contributions.sort(key=lambda x: abs(x["shap_impact"]), reverse=True)
        
        return {
            "row_index_in_sample": int(target_idx),
            "prediction_probability": float(probs[target_idx]),
            "true_label": int(self.y_test_sample[target_idx]) if self.y_test_sample is not None else None,
            "demographic_group": str(self.sensitive_sample[target_idx]) if self.sensitive_sample is not None else "Unknown",
            "feature_contributions": contributions[:10]  # Top 10 reasons
        }
