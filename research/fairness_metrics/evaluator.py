"""
Fairness Evaluation Module for FairLens AI Research.
Implements standardized demographic and error-rate fairness metrics.
Guarantees transparent recording of undefined metrics and edge cases without silent fallbacks.
"""
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix
from fairlearn.metrics import (
    MetricFrame,
    demographic_parity_difference,
    equalized_odds_difference,
    selection_rate,
    true_positive_rate,
    false_positive_rate,
    false_negative_rate
)


class FairnessEvaluator:
    """
    Evaluates group fairness metrics across sensitive attributes.
    Preserves audit trails for undefined metrics (e.g., division by zero, empty classes).
    """

    def __init__(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        sensitive_features: np.ndarray,
        sensitive_col_name: str = "sensitive",
        privileged_group: Optional[Any] = None,
        unprivileged_group: Optional[Any] = None
    ):
        self.y_true = np.asarray(y_true).astype(int)
        self.y_pred = np.asarray(y_pred).astype(int)
        self.sensitive_features = np.asarray(sensitive_features)
        self.sensitive_col_name = sensitive_col_name
        self.privileged_group = privileged_group
        self.unprivileged_group = unprivileged_group
        
        self.unique_groups = np.unique(self.sensitive_features)
        self.n_groups = len(self.unique_groups)

    def evaluate_all(self) -> Dict[str, Any]:
        """Compute the complete fairness metric suite with explicit error/undefined handling."""
        return {
            "sensitive_attribute": self.sensitive_col_name,
            "groups": [str(g) for g in self.unique_groups],
            "privileged_group": str(self.privileged_group) if self.privileged_group is not None else None,
            "unprivileged_group": str(self.unprivileged_group) if self.unprivileged_group is not None else None,
            "demographic_parity_difference": self._compute_dpd(),
            "equalized_odds_difference": self._compute_eod(),
            "equal_opportunity_difference": self._compute_eoppd(),
            "disparate_impact_ratio": self._compute_disparate_impact(),
            "false_positive_rate_difference": self._compute_fpr_difference(),
            "false_negative_rate_difference": self._compute_fnr_difference(),
            "subgroup_statistics": self._compute_subgroup_stats()
        }

    def _compute_dpd(self) -> Dict[str, Any]:
        """Difference in positive selection rates between demographic groups."""
        if self.n_groups < 2:
            return {"value": None, "defined": False, "reason": "Fewer than two demographic groups present."}
        try:
            dpd = float(demographic_parity_difference(
                self.y_true, self.y_pred, sensitive_features=self.sensitive_features
            ))
            return {"value": round(dpd, 4), "defined": True, "reason": None}
        except Exception as e:
            return {"value": None, "defined": False, "reason": str(e)}

    def _compute_eod(self) -> Dict[str, Any]:
        """Greater of the differences in FPR and TPR between groups."""
        if self.n_groups < 2:
            return {"value": None, "defined": False, "reason": "Fewer than two demographic groups present."}
        # Check if both binary classes (0 and 1) are present in y_true
        if len(np.unique(self.y_true)) < 2:
            return {
                "value": None,
                "defined": False,
                "reason": "Both positive and negative true labels must be present to evaluate Equalized Odds."
            }
        try:
            eod = float(equalized_odds_difference(
                self.y_true, self.y_pred, sensitive_features=self.sensitive_features
            ))
            return {"value": round(eod, 4), "defined": True, "reason": None}
        except Exception as e:
            return {"value": None, "defined": False, "reason": str(e)}

    def _compute_eoppd(self) -> Dict[str, Any]:
        """Difference in True Positive Rates (TPR) between groups."""
        if self.n_groups < 2:
            return {"value": None, "defined": False, "reason": "Fewer than two demographic groups present."}
        if (self.y_true == 1).sum() == 0:
            return {"value": None, "defined": False, "reason": "No positive ground-truth instances present."}
        try:
            mf = MetricFrame(
                metrics=true_positive_rate,
                y_true=self.y_true,
                y_pred=self.y_pred,
                sensitive_features=self.sensitive_features
            )
            val = float(mf.difference())
            if np.isnan(val):
                return {"value": None, "defined": False, "reason": "NaN encountered in subgroup TPR calculation."}
            return {"value": round(val, 4), "defined": True, "reason": None}
        except Exception as e:
            return {"value": None, "defined": False, "reason": str(e)}

    def _compute_disparate_impact(self) -> Dict[str, Any]:
        """
        Disparate Impact ratio: min(selection_rate) / max(selection_rate).
        If privileged and unprivileged groups are specified, computes unprivileged / privileged.
        """
        if self.n_groups < 2:
            return {"value": None, "defined": False, "reason": "Fewer than two demographic groups present."}
        try:
            mf = MetricFrame(
                metrics=selection_rate,
                y_true=self.y_true,
                y_pred=self.y_pred,
                sensitive_features=self.sensitive_features
            )
            rates = mf.by_group
            max_rate = rates.max()
            min_rate = rates.min()
            
            if max_rate == 0:
                return {
                    "value": None,
                    "defined": False,
                    "reason": "Max selection rate across all groups is zero (no positive predictions)."
                }
                
            if (self.privileged_group is not None and 
                self.unprivileged_group is not None and
                self.privileged_group in rates and
                self.unprivileged_group in rates):
                priv_rate = rates[self.privileged_group]
                unpriv_rate = rates[self.unprivileged_group]
                if priv_rate == 0:
                    return {
                        "value": None,
                        "defined": False,
                        "reason": f"Privileged group '{self.privileged_group}' selection rate is zero."
                    }
                di_ratio = float(unpriv_rate / priv_rate)
            else:
                di_ratio = float(min_rate / max_rate)

            return {"value": round(di_ratio, 4), "defined": True, "reason": None}
        except Exception as e:
            return {"value": None, "defined": False, "reason": str(e)}

    def _compute_fpr_difference(self) -> Dict[str, Any]:
        """Difference in False Positive Rates between groups."""
        if self.n_groups < 2:
            return {"value": None, "defined": False, "reason": "Fewer than two demographic groups present."}
        try:
            mf = MetricFrame(
                metrics=false_positive_rate,
                y_true=self.y_true,
                y_pred=self.y_pred,
                sensitive_features=self.sensitive_features
            )
            val = float(mf.difference())
            if np.isnan(val):
                return {"value": None, "defined": False, "reason": "NaN encountered in subgroup FPR calculation."}
            return {"value": round(val, 4), "defined": True, "reason": None}
        except Exception as e:
            return {"value": None, "defined": False, "reason": str(e)}

    def _compute_fnr_difference(self) -> Dict[str, Any]:
        """Difference in False Negative Rates between groups."""
        if self.n_groups < 2:
            return {"value": None, "defined": False, "reason": "Fewer than two demographic groups present."}
        try:
            mf = MetricFrame(
                metrics=false_negative_rate,
                y_true=self.y_true,
                y_pred=self.y_pred,
                sensitive_features=self.sensitive_features
            )
            val = float(mf.difference())
            if np.isnan(val):
                return {"value": None, "defined": False, "reason": "NaN encountered in subgroup FNR calculation."}
            return {"value": round(val, 4), "defined": True, "reason": None}
        except Exception as e:
            return {"value": None, "defined": False, "reason": str(e)}

    def _compute_subgroup_stats(self) -> List[Dict[str, Any]]:
        """Computes sample counts, base rates, selection rates, and confusion matrix per group."""
        stats = []
        for g in self.unique_groups:
            mask = (self.sensitive_features == g)
            count = int(mask.sum())
            if count == 0:
                continue
                
            y_t = self.y_true[mask]
            y_p = self.y_pred[mask]
            
            sel_rate = float(np.mean(y_p)) if count > 0 else 0.0
            base_rate = float(np.mean(y_t)) if count > 0 else 0.0
            acc = float(np.mean(y_t == y_p)) if count > 0 else 0.0
            
            # Confusion matrix
            if len(np.unique(self.y_true)) > 1:
                tn, fp, fn, tp = confusion_matrix(y_t, y_p, labels=[0, 1]).ravel()
            else:
                tp = int(((y_t == 1) & (y_p == 1)).sum())
                tn = int(((y_t == 0) & (y_p == 0)).sum())
                fp = int(((y_t == 0) & (y_p == 1)).sum())
                fn = int(((y_t == 1) & (y_p == 0)).sum())

            tpr = float(tp / (tp + fn)) if (tp + fn) > 0 else None
            fpr = float(fp / (fp + tn)) if (fp + tn) > 0 else None

            stats.append({
                "group": str(g),
                "count": count,
                "base_rate": round(base_rate, 4),
                "selection_rate": round(sel_rate, 4),
                "accuracy": round(acc, 4),
                "tpr": round(tpr, 4) if tpr is not None else None,
                "fpr": round(fpr, 4) if fpr is not None else None,
                "confusion_matrix": {
                    "tp": int(tp),
                    "tn": int(tn),
                    "fp": int(fp),
                    "fn": int(fn)
                }
            })
        return stats
