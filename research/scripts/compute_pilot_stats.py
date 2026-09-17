"""
Compute exact pilot statistical analysis comparing Template Baseline vs LLM Explanations.
Outputs markdown tables for PILOT_RESULTS_REPORT.md and PILOT_STATISTICAL_REPORT.md.
"""
import pandas as pd
import numpy as np
from scipy import stats

def compute_pilot_statistics():
    df = pd.read_csv("research/results/pilot/processed/faithfulness_runs.csv")
    
    # Split into template vs LLM
    template_df = df[df["explanation_source"] == "template_baseline"].copy()
    llm_df = df[df["explanation_source"] != "template_baseline"].copy()
    
    metrics = [
        ("numerical_faithfulness", "Numerical Faithfulness"),
        ("directional_faithfulness", "Directional Faithfulness"),
        ("attribution_faithfulness", "Attribution Faithfulness"),
        ("unsupported_claim_rate", "Unsupported Claim Rate"),
        ("total_claims_count", "Total Claims Count"),
        ("numerical_mae", "Numerical MAE")
    ]
    
    print("=== SUMMARY METRICS (MEAN ± STD, MEDIAN, IQR) ===")
    results = {}
    for col, name in metrics:
        t_vals = template_df[col].dropna()
        l_vals = llm_df[col].dropna()
        
        t_mean, t_std = t_vals.mean(), t_vals.std()
        l_mean, l_std = l_vals.mean(), l_vals.std()
        
        t_med, t_iqr = t_vals.median(), stats.iqr(t_vals)
        l_med, l_iqr = l_vals.median(), stats.iqr(l_vals)
        
        # Paired test where experiment_ids match
        merged = pd.merge(template_df[["experiment_id", col]], llm_df[["experiment_id", col]], on="experiment_id", suffixes=('_tmpl', '_llm'))
        merged = merged.drop_duplicates(subset=["experiment_id"]).dropna()
        
        diff = merged[f"{col}_llm"] - merged[f"{col}_tmpl"]
        cohen_d = (l_mean - t_mean) / np.sqrt((t_std**2 + l_std**2) / 2) if (t_std**2 + l_std**2) > 0 else 0.0
        
        try:
            w_stat, p_val = stats.wilcoxon(merged[f"{col}_llm"], merged[f"{col}_tmpl"])
        except Exception:
            w_stat, p_val = 0.0, 1.0
            
        # 95% CI for difference in means
        se_diff = np.sqrt((t_std**2 / len(t_vals)) + (l_std**2 / len(l_vals))) if len(t_vals) > 0 and len(l_vals) > 0 else 0
        ci_lower = (l_mean - t_mean) - 1.96 * se_diff
        ci_upper = (l_mean - t_mean) + 1.96 * se_diff
        
        results[col] = {
            "name": name,
            "t_mean": t_mean, "t_std": t_std, "t_med": t_med, "t_iqr": t_iqr,
            "l_mean": l_mean, "l_std": l_std, "l_med": l_med, "l_iqr": l_iqr,
            "delta_mean": l_mean - t_mean,
            "ci_95": (ci_lower, ci_upper),
            "cohen_d": cohen_d,
            "wilcoxon_stat": w_stat,
            "p_val": p_val
        }
        
        print(f"\nMetric: {name}")
        print(f"  Template: {t_mean:.4f} ± {t_std:.4f} (Med: {t_med:.4f}, IQR: {t_iqr:.4f})")
        print(f"  LLM:      {l_mean:.4f} ± {l_std:.4f} (Med: {l_med:.4f}, IQR: {l_iqr:.4f})")
        print(f"  Delta:    {l_mean - t_mean:.4f} [95% CI: {ci_lower:.4f}, {ci_upper:.4f}]")
        print(f"  Cohen's d: {cohen_d:.4f} | Wilcoxon W: {w_stat} (p = {p_val:.4e})")

if __name__ == "__main__":
    compute_pilot_statistics()
