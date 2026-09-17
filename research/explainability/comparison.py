"""
Feature Attribution Comparison Module for FairLens AI Research.
Implements established attribution distance and rank-order comparison metrics.
NOTE: These comparison metrics are PROVISIONAL pending literature review confirmation.
"""
from typing import Dict, Any, List
import numpy as np
from scipy.stats import spearmanr


def compare_attributions(
    baseline_importance: List[Dict[str, Any]],
    mitigated_importance: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Compares global feature importance vectors between baseline and mitigated models.
    
    Metrics:
    - Cosine Similarity: Directional alignment of feature attribution vectors [-1, 1].
    - Spearman Rank Correlation: Monotonic consistency of feature ranking [-1, 1].
    - L1 Attribution Difference: Mean absolute change across feature weights.
    - L2 Attribution Difference: Euclidean norm of attribution vector difference.
    """
    # Align features by name
    base_dict = {item["feature"]: float(item["importance"]) for item in baseline_importance}
    mit_dict = {item["feature"]: float(item["importance"]) for item in mitigated_importance}
    
    common_features = [f for f in base_dict if f in mit_dict]
    if len(common_features) == 0:
        return {
            "provisional_status": "PROVISIONAL (pending literature review)",
            "defined": False,
            "reason": "No intersecting feature names between baseline and mitigated models."
        }
        
    u = np.array([base_dict[f] for f in common_features])
    v = np.array([mit_dict[f] for f in common_features])

    # 1. Cosine Similarity
    norm_u = np.linalg.norm(u)
    norm_v = np.linalg.norm(v)
    if norm_u > 0 and norm_v > 0:
        cosine_sim = float(np.dot(u, v) / (norm_u * norm_v))
    else:
        cosine_sim = 1.0 if norm_u == norm_v else 0.0

    # 2. Spearman Rank Correlation
    if len(u) > 1 and np.std(u) > 0 and np.std(v) > 0:
        res = spearmanr(u, v)
        spearman_corr = float(res.statistic) if hasattr(res, "statistic") else float(res.correlation)
        spearman_pvalue = float(res.pvalue)
    else:
        spearman_corr = 1.0 if np.array_equal(u, v) else 0.0
        spearman_pvalue = 1.0

    # 3. L1 Attribution Difference (Mean Absolute Shift)
    l1_diff = float(np.mean(np.abs(u - v)))

    # 4. L2 Attribution Difference (Euclidean Shift)
    l2_diff = float(np.linalg.norm(u - v))

    # Identify top rank shifts
    rank_shifts = []
    base_ranked = sorted(common_features, key=lambda f: base_dict[f], reverse=True)
    mit_ranked = sorted(common_features, key=lambda f: mit_dict[f], reverse=True)
    for rank_idx, f in enumerate(base_ranked):
        mit_idx = mit_ranked.index(f)
        shift = mit_idx - rank_idx
        rank_shifts.append({
            "feature": f,
            "baseline_rank": rank_idx + 1,
            "mitigated_rank": mit_idx + 1,
            "rank_shift": shift
        })

    return {
        "provisional_status": "PROVISIONAL (pending literature review)",
        "cosine_similarity": round(cosine_sim, 6),
        "spearman_rank_correlation": round(spearman_corr, 6),
        "spearman_pvalue": round(spearman_pvalue, 6),
        "l1_attribution_difference": round(l1_diff, 6),
        "l2_attribution_difference": round(l2_diff, 6),
        "features_evaluated": len(common_features),
        "top_rank_shifts": rank_shifts[:5]
    }
