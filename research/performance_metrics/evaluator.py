"""
Performance Evaluation Module for FairLens AI Research.
Evaluates classification accuracy, precision, recall, F1, and ROC-AUC.
Strictly distinguishes between metrics requiring hard decision labels versus probabilistic outputs.
"""
from typing import Dict, Any, Optional
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score


class PerformanceEvaluator:
    """
    Evaluates standard machine learning predictive performance metrics.
    Documents data requirements (hard predictions vs probabilities) for each metric.
    """

    def __init__(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_prob: Optional[np.ndarray] = None
    ):
        self.y_true = np.asarray(y_true).astype(int)
        self.y_pred = np.asarray(y_pred).astype(int)
        
        # Format probabilities for positive class (label 1)
        if y_prob is not None:
            arr = np.asarray(y_prob)
            if arr.ndim == 2 and arr.shape[1] == 2:
                self.y_prob = arr[:, 1]
            elif arr.ndim == 1:
                self.y_prob = arr
            else:
                self.y_prob = None
        else:
            self.y_prob = None

    def evaluate_all(self) -> Dict[str, Any]:
        """Runs the complete performance metric evaluation."""
        return {
            "accuracy": self._compute_accuracy(),
            "precision": self._compute_precision(),
            "recall": self._compute_recall(),
            "f1_score": self._compute_f1(),
            "roc_auc": self._compute_roc_auc()
        }

    def _compute_accuracy(self) -> Dict[str, Any]:
        """Overall classification accuracy (requires hard labels)."""
        acc = float(accuracy_score(self.y_true, self.y_pred))
        return {"value": round(acc, 4), "requires": "labels", "defined": True}

    def _compute_precision(self) -> Dict[str, Any]:
        """Precision for positive class (label=1)."""
        prec = float(precision_score(self.y_true, self.y_pred, zero_division=0))
        return {"value": round(prec, 4), "requires": "labels", "defined": True}

    def _compute_recall(self) -> Dict[str, Any]:
        """Recall / True Positive Rate for positive class (label=1)."""
        rec = float(recall_score(self.y_true, self.y_pred, zero_division=0))
        return {"value": round(rec, 4), "requires": "labels", "defined": True}

    def _compute_f1(self) -> Dict[str, Any]:
        """Harmonic mean of precision and recall (requires hard labels)."""
        f1 = float(f1_score(self.y_true, self.y_pred, zero_division=0))
        return {"value": round(f1, 4), "requires": "labels", "defined": True}

    def _compute_roc_auc(self) -> Dict[str, Any]:
        """
        Area Under the ROC Curve.
        Requires well-calibrated continuous probabilities and presence of both binary classes.
        """
        if self.y_prob is None:
            return {
                "value": None,
                "requires": "probabilities",
                "defined": False,
                "reason": "Model or mitigation intervention did not generate continuous probabilities."
            }
            
        if len(np.unique(self.y_true)) < 2:
            return {
                "value": None,
                "requires": "probabilities",
                "defined": False,
                "reason": "ROC-AUC requires both positive and negative ground-truth labels."
            }
            
        try:
            auc = float(roc_auc_score(self.y_true, self.y_prob))
            return {"value": round(auc, 4), "requires": "probabilities", "defined": True, "reason": None}
        except Exception as e:
            return {"value": None, "requires": "probabilities", "defined": False, "reason": str(e)}
