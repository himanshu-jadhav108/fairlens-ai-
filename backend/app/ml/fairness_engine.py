import numpy as np
import pandas as pd
from typing import Dict, Any, List
from sklearn.metrics import accuracy_score, confusion_matrix
from fairlearn.metrics import (
    MetricFrame,
    demographic_parity_difference,
    equalized_odds_difference,
    false_positive_rate,
    false_negative_rate,
    selection_rate,
    true_positive_rate
)

class FairnessEngine:
    """
    Production-grade Fairness Engine leveraging Microsoft's Fairlearn.
    Separates fairness evaluation concerns from ML training pipelines.
    """
    
    def __init__(self, y_true: np.ndarray, y_pred: np.ndarray, sensitive_features: np.ndarray, sensitive_col_name: str = "group"):
        self.y_true = np.array(y_true)
        self.y_pred = np.array(y_pred)
        self.sensitive_features = np.array(sensitive_features)
        self.sensitive_col_name = sensitive_col_name
        self.groups = np.unique(self.sensitive_features)

    def compute_demographic_parity_difference(self) -> float:
        """Difference in selection rates between groups."""
        return float(demographic_parity_difference(
            self.y_true, self.y_pred, sensitive_features=self.sensitive_features
        ))

    def compute_equalized_odds_difference(self) -> float:
        """Greater of the differences in FPR and TPR between groups."""
        return float(equalized_odds_difference(
            self.y_true, self.y_pred, sensitive_features=self.sensitive_features
        ))

    def compute_equal_opportunity_difference(self) -> float:
        """Difference in True Positive Rates (TPR) between groups."""
        mf = MetricFrame(metrics=true_positive_rate,
                         y_true=self.y_true,
                         y_pred=self.y_pred,
                         sensitive_features=self.sensitive_features)
        return float(mf.difference())

    def compute_disparate_impact_ratio(self) -> float:
        """Ratio of selection rates (min / max). Commonly evaluated against the 80% rule."""
        mf = MetricFrame(metrics=selection_rate,
                         y_true=self.y_true,
                         y_pred=self.y_pred,
                         sensitive_features=self.sensitive_features)
        rates = mf.by_group
        if rates.max() == 0:
            return 0.0
        return float(rates.min() / rates.max())

    def compute_fpr_difference(self) -> float:
        """Difference in False Positive Rates between groups."""
        mf = MetricFrame(metrics=false_positive_rate,
                         y_true=self.y_true,
                         y_pred=self.y_pred,
                         sensitive_features=self.sensitive_features)
        return float(mf.difference())

    def compute_fnr_difference(self) -> float:
        """Difference in False Negative Rates between groups."""
        mf = MetricFrame(metrics=false_negative_rate,
                         y_true=self.y_true,
                         y_pred=self.y_pred,
                         sensitive_features=self.sensitive_features)
        return float(mf.difference())

    def compute_group_stats(self) -> List[Dict[str, Any]]:
        """
        Computes detailed stats (Accuracy, Selection Rate, Confusion Matrix elements) 
        for each demographic group. Used for frontend Calibration and Matrix visualization.
        """
        group_stats = []
        for g in self.groups:
            mask = self.sensitive_features == g
            if mask.sum() == 0:
                continue
                
            y_t = self.y_true[mask]
            y_p = self.y_pred[mask]
            
            count = len(y_t)
            acc = float(accuracy_score(y_t, y_p))
            pos_rate = float(np.mean(y_p))
            
            # Confusion matrix
            tn, fp, fn, tp = confusion_matrix(y_t, y_p, labels=[0, 1]).ravel() if len(np.unique(y_t)) > 1 else (0,0,0,0)
            
            group_stats.append({
                "group": str(g),
                "count": count,
                "accuracy": round(acc, 4),
                "positive_rate": round(pos_rate, 4),
                "confusion_matrix": {
                    "tp": int(tp),
                    "tn": int(tn),
                    "fp": int(fp),
                    "fn": int(fn)
                }
            })
        return group_stats

    def compute_all_metrics(self) -> Dict[str, Any]:
        """Runs the full fairness evaluation suite."""
        dpd = self.compute_demographic_parity_difference()
        eod = self.compute_equalized_odds_difference()
        eoppd = self.compute_equal_opportunity_difference()
        di = self.compute_disparate_impact_ratio()
        fprd = self.compute_fpr_difference()
        fnrd = self.compute_fnr_difference()
        
        # Overall Accuracy
        acc = float(accuracy_score(self.y_true, self.y_pred))
        
        # Standardized Payload
        return {
            "accuracy": round(acc, 4),
            "demographic_parity_difference": round(dpd, 4),
            "equalized_odds_difference": round(eod, 4),
            "equal_opportunity_difference": round(eoppd, 4),
            "disparate_impact_ratio": round(di, 4),
            "false_positive_rate_difference": round(fprd, 4),
            "false_negative_rate_difference": round(fnrd, 4),
            "group_stats": self.compute_group_stats()
        }
