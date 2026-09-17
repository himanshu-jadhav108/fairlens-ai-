"""
Statistical Analysis for LLM Explanation Faithfulness.

Primary Dependent Variables:
- Numerical Faithfulness Rate
- Directional Faithfulness Rate
- Attribution Faithfulness Rate
- Unsupported Claim Rate

Hierarchical Structure:
Claims (Level 1) -> Explanations (Level 2) -> Experiments / Conditions (Level 3).
Claims generated within the same explanation are NOT statistically independent.
The primary experimental unit of analysis is the EXPLANATION or PAIRED RUN.
"""
from typing import Dict, Any, List, Optional
import numpy as np
from scipy import stats


def compute_paired_faithfulness_comparison(
    template_scores: List[float],
    llm_scores: List[float],
    metric_name: str = "faithfulness"
) -> Dict[str, Any]:
    """
    Evaluates paired difference between deterministic Template baseline and LLM explanations
    evaluated on identical structured audit evidence.
    Unit of analysis: Explanation (paired by experiment_id).
    """
    t_arr = np.asarray(template_scores, dtype=float)
    l_arr = np.asarray(llm_scores, dtype=float)

    if len(t_arr) != len(l_arr):
        raise ValueError(f"Pairing mismatch: template has {len(t_arr)}, llm has {len(l_arr)} observations.")

    n = len(t_arr)
    if n < 3:
        return {
            "metric": metric_name,
            "n_pairs": n,
            "defined": False,
            "reason": f"Sample size N={n} is insufficient for inferential hypothesis testing."
        }

    deltas = l_arr - t_arr
    mean_diff = float(np.mean(deltas))
    std_diff = float(np.std(deltas, ddof=1)) if n > 1 else 0.0

    # Paired t-test
    t_stat, t_pval = stats.ttest_rel(l_arr, t_arr)

    # Non-parametric Wilcoxon signed-rank test
    try:
        w_stat, w_pval = stats.wilcoxon(l_arr, t_arr)
    except Exception as e:
        w_stat, w_pval = None, None

    # Cohen's d for paired samples
    cohens_d = (mean_diff / std_diff) if std_diff > 1e-6 else 0.0

    return {
        "metric": metric_name,
        "n_pairs": n,
        "unit_of_analysis": "explanation_run",
        "mean_template": round(float(np.mean(t_arr)), 4),
        "mean_llm": round(float(np.mean(l_arr)), 4),
        "mean_difference": round(mean_diff, 4),
        "std_difference": round(std_diff, 4),
        "cohens_d": round(float(cohens_d), 4),
        "paired_t_test": {
            "t_statistic": round(float(t_stat), 4) if not np.isnan(t_stat) else None,
            "p_value": round(float(t_pval), 4) if not np.isnan(t_pval) else None
        },
        "wilcoxon_signed_rank": {
            "w_statistic": round(float(w_stat), 4) if w_stat is not None else None,
            "p_value": round(float(w_pval), 4) if w_pval is not None else None
        },
        "methodological_note": (
            "Statistical test assumes explanations paired on identical structured evidence. "
            "Claims within an explanation are nested and should not be pooled as i.i.d. observations."
        )
    }


def compute_explanation_bootstrap_ci(
    scores: List[float],
    n_bootstraps: int = 1000,
    confidence_level: float = 0.95,
    seed: int = 42
) -> Dict[str, Any]:
    """
    Computes non-parametric bootstrap confidence intervals over explanation-level scores.
    """
    arr = np.asarray(scores, dtype=float)
    n = len(arr)
    if n == 0:
        return {"defined": False, "reason": "Empty score array."}

    rng = np.random.default_rng(seed)
    boot_means = []
    for _ in range(n_bootstraps):
        sample = rng.choice(arr, size=n, replace=True)
        boot_means.append(np.mean(sample))

    alpha = 1.0 - confidence_level
    ci_lower = float(np.percentile(boot_means, (alpha / 2.0) * 100))
    ci_upper = float(np.percentile(boot_means, (1.0 - alpha / 2.0) * 100))

    return {
        "defined": True,
        "n_samples": n,
        "mean": round(float(np.mean(arr)), 4),
        "ci_lower": round(ci_lower, 4),
        "ci_upper": round(ci_upper, 4),
        "confidence_level": confidence_level,
        "n_bootstraps": n_bootstraps
    }
