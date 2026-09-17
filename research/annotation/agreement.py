"""
Inter-Annotator Agreement Utilities for Human Faithfulness Annotations.
Computes Cohen's Kappa, percentage agreement, and confusion matrices.
"""
from typing import List, Dict, Any, Tuple, Optional
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
        "sample_size": n,
        "scale_type": "nominal",
        "methodological_note": (
            "Unweighted Cohen's Kappa applies to nominal categorical schemes (e.g. including UNDETERMINABLE). "
            "It penalizes all disagreements equally."
        )
    }


def compute_weighted_cohen_kappa(
    labels_a: List[str],
    labels_b: List[str],
    ordered_categories: Optional[List[str]] = None,
    weight_type: str = "quadratic"
) -> Dict[str, Any]:
    """
    Computes Weighted Cohen's Kappa for ordinal classifications.
    
    METHODOLOGICAL RATIONALE (Section 16):
    When evaluating factual faithfulness on the ordered continuum:
      SUPPORTED (2) > PARTIALLY_SUPPORTED (1) > UNSUPPORTED (0)
    a disagreement between SUPPORTED and PARTIALLY_SUPPORTED is less severe
    than a full inversion between SUPPORTED and UNSUPPORTED. Weighted kappa
    penalizes disagreements according to their distance on the ordinal scale.
    
    Weights:
      linear:    w_ij = 1 - |i - j| / (k - 1)
      quadratic: w_ij = 1 - (i - j)^2 / (k - 1)^2
    
    If labels contain non-ordinal categories (such as UNDETERMINABLE), unweighted
    kappa MUST be used instead or UNDETERMINABLE cases partitioned first.
    """
    if len(labels_a) != len(labels_b):
        raise ValueError("Annotator label lists must have identical length.")
    if not labels_a:
        return {"weighted_kappa": 1.0, "observed_agreement": 1.0, "expected_agreement": 1.0}

    if ordered_categories is None:
        ordered_categories = ["UNSUPPORTED", "PARTIALLY_SUPPORTED", "SUPPORTED"]

    # Verify all labels belong to the ordered categories
    all_present = set(labels_a) | set(labels_b)
    invalid = all_present - set(ordered_categories)
    if invalid:
        raise ValueError(
            f"Labels contain non-ordinal categories {invalid}. "
            f"Use unweighted compute_cohen_kappa() for nominal data including UNDETERMINABLE."
        )

    cat_to_idx = {c: i for i, c in enumerate(ordered_categories)}
    k = len(ordered_categories)
    n = len(labels_a)

    if k <= 1:
        return {"weighted_kappa": 1.0, "observed_agreement": 1.0, "expected_agreement": 1.0}

    # Weight matrix
    weights = np.zeros((k, k), dtype=float)
    for i in range(k):
        for j in range(k):
            if weight_type == "linear":
                weights[i, j] = 1.0 - abs(i - j) / (k - 1)
            elif weight_type == "quadratic":
                weights[i, j] = 1.0 - ((i - j) ** 2) / ((k - 1) ** 2)
            else:
                raise ValueError(f"Unsupported weight_type '{weight_type}'. Choose 'linear' or 'quadratic'.")

    # Observed confusion matrix
    conf_mat = np.zeros((k, k), dtype=float)
    for a, b in zip(labels_a, labels_b):
        conf_mat[cat_to_idx[a], cat_to_idx[b]] += 1.0

    p_observed_mat = conf_mat / n
    row_margins = p_observed_mat.sum(axis=1)
    col_margins = p_observed_mat.sum(axis=0)
    p_expected_mat = np.outer(row_margins, col_margins)

    p_o = np.sum(weights * p_observed_mat)
    p_e = np.sum(weights * p_expected_mat)

    if abs(1.0 - p_e) < 1e-9:
        kappa_w = 1.0
    else:
        kappa_w = (p_o - p_e) / (1.0 - p_e)

    return {
        "weighted_kappa": round(float(kappa_w), 4),
        "observed_weighted_agreement": round(float(p_o), 4),
        "expected_weighted_agreement": round(float(p_e), 4),
        "sample_size": n,
        "weight_type": weight_type,
        "ordered_scale": ordered_categories
    }

