"""
Statistical Analysis Utilities for FairLens AI Research.
NOTE: All statistical procedures in this module are PROVISIONAL.
The final inferential methodology (unit of analysis, pairing structure, test selection,
multiple comparison corrections, effect sizes) will be finalized after formal literature review.
Five random seeds reflect algorithmic stochasticity across splits, NOT independent scientific observations.
"""
from typing import Dict, Any, List, Optional
import numpy as np
from scipy import stats


PROVISIONAL_DISCLAIMER = (
    "STATISTICAL METHODOLOGY IS PROVISIONAL: "
    "Random seeds capture algorithmic initialization and split variance, NOT independent sampling units. "
    "Do not cite these test statistics as finalized confirmatory p-values prior to formal experimental pre-registration."
)


def check_normality(sample: np.ndarray) -> Dict[str, Any]:
    """Evaluates normality using Shapiro-Wilk test with sample size guards."""
    arr = np.asarray(sample).astype(float)
    n = len(arr)
    if n < 3:
        return {
            "test": "Shapiro-Wilk",
            "defined": False,
            "reason": f"Sample size N={n} is too small for normality testing (minimum N=3).",
            "is_normal": None
        }
    try:
        stat, pval = stats.shapiro(arr)
        return {
            "test": "Shapiro-Wilk",
            "defined": True,
            "statistic": round(float(stat), 4),
            "p_value": round(float(pval), 4),
            "is_normal": bool(pval > 0.05),
            "n_samples": n,
            "warning": "Small sample size (N < 20) yields low statistical power." if n < 20 else None
        }
    except Exception as e:
        return {"test": "Shapiro-Wilk", "defined": False, "reason": str(e), "is_normal": None}


def compute_paired_differences(
    baseline_scores: np.ndarray,
    mitigated_scores: np.ndarray
) -> Dict[str, Any]:
    """
    Computes paired difference statistics between baseline and mitigated runs across identical seeds.
    Includes parametric (paired t) and non-parametric (Wilcoxon) candidates with sample size caveats.
    """
    base = np.asarray(baseline_scores).astype(float)
    mit = np.asarray(mitigated_scores).astype(float)
    
    if len(base) != len(mit):
        raise ValueError(f"Length mismatch: baseline has {len(base)}, mitigated has {len(mit)}.")
        
    n = len(base)
    diff = mit - base
    
    mean_diff = float(np.mean(diff))
    std_diff = float(np.std(diff, ddof=1)) if n > 1 else 0.0
    median_diff = float(np.median(diff))
    
    # Cohen's d for paired samples
    cohens_d = (mean_diff / std_diff) if std_diff > 0 else 0.0

    # Paired t-test
    if n >= 2 and std_diff > 0:
        t_stat, t_pval = stats.ttest_rel(mit, base)
        paired_t = {
            "t_statistic": round(float(t_stat), 4),
            "p_value": round(float(t_pval), 4),
            "defined": True
        }
    else:
        paired_t = {"defined": False, "reason": "Insufficient variance or sample size < 2."}

    # Wilcoxon signed-rank test
    if n >= 5 and not np.all(diff == 0):
        try:
            w_stat, w_pval = stats.wilcoxon(diff)
            wilcoxon = {
                "w_statistic": round(float(w_stat), 4),
                "p_value": round(float(w_pval), 4),
                "defined": True
            }
        except Exception as e:
            wilcoxon = {"defined": False, "reason": str(e)}
    else:
        wilcoxon = {"defined": False, "reason": "Sample size too small for Wilcoxon or all differences zero."}

    return {
        "status": "PROVISIONAL",
        "disclaimer": PROVISIONAL_DISCLAIMER,
        "n_pairs": n,
        "mean_difference": round(mean_diff, 4),
        "std_difference": round(std_diff, 4),
        "median_difference": round(median_diff, 4),
        "cohens_d": round(cohens_d, 4),
        "paired_t_test": paired_t,
        "wilcoxon_signed_rank": wilcoxon,
        "sample_size_warning": (
            "Caution: Analysis across random seeds reflects split sensitivity, not independent sampling units."
            if n <= 10 else None
        )
    }


def adjust_multiple_comparisons(p_values: List[float], method: str = "bonferroni") -> List[float]:
    """Applies standard family-wise or false-discovery-rate multiple comparison adjustment."""
    arr = np.asarray(p_values, dtype=float)
    m = len(arr)
    if m <= 1:
        return [float(p) for p in arr]

    if method.lower() == "bonferroni":
        adjusted = np.clip(arr * m, 0.0, 1.0)
        return [round(float(p), 4) for p in adjusted]
    elif method.lower() in ["fdr_bh", "benjamini_hochberg"]:
        # Benjamini-Hochberg FDR
        sorted_indices = np.argsort(arr)
        sorted_p = arr[sorted_indices]
        q_values = np.zeros(m)
        q_values[-1] = sorted_p[-1]
        for i in range(m - 2, -1, -1):
            q_values[i] = min(q_values[i + 1], sorted_p[i] * m / (i + 1))
        q_out = np.empty(m)
        q_out[sorted_indices] = np.clip(q_values, 0.0, 1.0)
        return [round(float(q), 4) for q in q_out]
    else:
        raise ValueError(f"Unsupported adjustment method '{method}'.")
