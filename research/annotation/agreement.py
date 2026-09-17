"""
Inter-Annotator Agreement Utilities for Human Faithfulness Annotations.
Computes Cohen's Kappa, percentage agreement, and confusion matrices.
"""
from typing import List, Dict, Any, Tuple
import numpy as np


def compute_cohen_kappa(labels_a: List[str], labels_b: List[str]) -> Dict[str, float]:
    """
    Computes Cohen's Kappa coefficient between two independent raters.
    Handles arbitrary categorical labels.
    """
    if len(labels_a) != len(labels_b):
        raise ValueError("Annotator label lists must have identical length.")
    if not labels_a:
        return {"cohen_kappa": 1.0, "observed_agreement": 1.0, "expected_agreement": 1.0}

    categories = sorted(list(set(labels_a) | set(labels_b)))
    cat_to_idx = {c: i for i, c in enumerate(categories)}
    n_cat = len(categories)
    n = len(labels_a)

    # Confusion matrix
    conf_mat = np.zeros((n_cat, n_cat), dtype=int)
    for a, b in zip(labels_a, labels_b):
        conf_mat[cat_to_idx[a], cat_to_idx[b]] += 1

    # Observed agreement
    p_o = np.trace(conf_mat) / n

    # Expected chance agreement
    row_sums = conf_mat.sum(axis=1) / n
    col_sums = conf_mat.sum(axis=0) / n
    p_e = np.sum(row_sums * col_sums)

    if p_e >= 1.0:
        kappa = 1.0
    else:
        kappa = (p_o - p_e) / (1.0 - p_e)

    return {
        "cohen_kappa": round(float(kappa), 4),
        "observed_agreement": round(float(p_o), 4),
        "expected_agreement": round(float(p_e), 4),
        "sample_size": n
    }
