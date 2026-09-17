"""
Result Aggregator Module for FairLens AI Research.
Compiles raw single-experiment outputs into machine-readable summary tables
with means, standard deviations, and paired trade-off deltas.
"""
import os
import glob
import json
from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd


def aggregate_raw_results(
    raw_dir: str = "research/results/raw",
    output_dir: str = "research/results/processed"
) -> Optional[pd.DataFrame]:
    """
    Parses all raw JSON result files in raw_dir and builds an aggregated summary table.
    Groups by (dataset_name, model_name, mitigation_name) and computes mean/std across seeds.
    """
    json_pattern = os.path.join(raw_dir, "*.json")
    files = glob.glob(json_pattern)
    
    if not files:
        print(f"[!] No raw result files found in '{raw_dir}'.")
        return None

    rows = []
    for fp in files:
        try:
            with open(fp, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            exp_id = data.get("experiment_id")
            dataset = data.get("dataset_name")
            model = data.get("model_name")
            mitigation = data.get("mitigation_name")
            seed = data.get("random_seed")
            is_synthetic = data.get("is_synthetic_benchmark", False)

            base_perf = data.get("baseline_evaluation", {}).get("performance", {})
            mit_perf = data.get("mitigated_evaluation", {}).get("performance", {})
            base_fair = data.get("baseline_evaluation", {}).get("fairness", {})
            mit_fair = data.get("mitigated_evaluation", {}).get("fairness", {})
            attr_comp = data.get("attribution_comparison", {})
            deltas = data.get("trade_off_deltas", {})

            row = {
                "experiment_id": exp_id,
                "dataset": dataset,
                "model": model,
                "mitigation": mitigation,
                "seed": seed,
                "is_synthetic_benchmark": is_synthetic,
                
                # Performance
                "baseline_accuracy": base_perf.get("accuracy", {}).get("value"),
                "mitigated_accuracy": mit_perf.get("accuracy", {}).get("value"),
                "delta_accuracy": deltas.get("delta_accuracy"),
                
                "baseline_f1": base_perf.get("f1_score", {}).get("value"),
                "mitigated_f1": mit_perf.get("f1_score", {}).get("value"),
                "delta_f1": deltas.get("delta_f1_score"),
                
                "baseline_roc_auc": base_perf.get("roc_auc", {}).get("value"),
                "mitigated_roc_auc": mit_perf.get("roc_auc", {}).get("value"),

                # Fairness
                "baseline_dpd": base_fair.get("demographic_parity_difference", {}).get("value"),
                "mitigated_dpd": mit_fair.get("demographic_parity_difference", {}).get("value"),
                "delta_dpd": deltas.get("delta_demographic_parity_difference"),

                "baseline_eod": base_fair.get("equalized_odds_difference", {}).get("value"),
                "mitigated_eod": mit_fair.get("equalized_odds_difference", {}).get("value"),
                "delta_eod": deltas.get("delta_equalized_odds_difference"),

                "baseline_di": base_fair.get("disparate_impact_ratio", {}).get("value"),
                "mitigated_di": mit_fair.get("disparate_impact_ratio", {}).get("value"),

                # Explainability attribution comparison
                "cosine_similarity": attr_comp.get("cosine_similarity"),
                "spearman_rank_correlation": attr_comp.get("spearman_rank_correlation"),
                "l1_attribution_difference": attr_comp.get("l1_attribution_difference"),
                "l2_attribution_difference": attr_comp.get("l2_attribution_difference")
            }
            rows.append(row)
        except Exception as e:
            print(f"[!] Warning: Failed parsing result file '{fp}': {e}")

    if not rows:
        return None

    df_raw = pd.DataFrame(rows)
    
    # Save individual run table
    os.makedirs(output_dir, exist_ok=True)
    runs_csv = os.path.join(output_dir, "individual_runs.csv")
    df_raw.to_csv(runs_csv, index=False)

    # Compute summary group metrics (mean and std across seeds)
    group_cols = ["dataset", "model", "mitigation", "is_synthetic_benchmark"]
    metric_cols = [c for c in df_raw.columns if c not in group_cols + ["experiment_id", "seed"]]
    
    # Convert metric columns to float
    for col in metric_cols:
        df_raw[col] = pd.to_numeric(df_raw[col], errors="coerce")

    summary_df = df_raw.groupby(group_cols)[metric_cols].agg(["mean", "std", "count"]).reset_index()
    
    # Flatten hierarchical columns
    summary_df.columns = [
        f"{c[0]}_{c[1]}" if c[1] and c[0] not in group_cols else c[0]
        for c in summary_df.columns
    ]
    
    summary_csv = os.path.join(output_dir, "summary_table.csv")
    summary_df.to_csv(summary_csv, index=False)
    
    summary_json = os.path.join(output_dir, "summary_table.json")
    summary_df.to_json(summary_json, orient="records", indent=2)

    print(f"[*] Aggregated {len(df_raw)} runs into '{summary_csv}'.")
    return summary_df
