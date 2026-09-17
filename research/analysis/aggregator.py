"""
Result Aggregator Module for FairLens AI Research.
Compiles raw single-experiment and faithfulness outputs into machine-readable summary tables
with means, standard deviations, paired trade-off deltas, and missing run detection.

Guarantees:
1. Strict isolation of smoke test outputs (SOFTWARE_VALIDATION_ONLY).
2. Explicit filtering of failed or corrupt runs.
3. Deduplication to prevent double-counting.
4. Reporting of missing experimental conditions.
"""
import os
import glob
import json
from typing import List, Dict, Any, Optional, Set, Tuple
import numpy as np
import pandas as pd


def aggregate_raw_results(
    raw_dir: str = "research/results/raw",
    output_dir: str = "research/results/processed"
) -> Optional[pd.DataFrame]:
    """
    Parses all raw JSON result files in raw_dir and builds an aggregated summary table.
    Excludes smoke tests, failed runs, and duplicate records.
    """
    json_pattern = os.path.join(raw_dir, "*.json")
    files = glob.glob(json_pattern)
    
    if not files:
        print(f"[!] No raw result files found in '{raw_dir}'.")
        return None

    rows = []
    seen_experiments: Set[str] = set()

    for fp in files:
        # Check path for smoke isolation
        norm_fp = fp.replace("\\", "/").lower()
        if "/smoke/" in norm_fp:
            continue

        try:
            with open(fp, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Check explicit execution mode
            if data.get("execution_mode") == "SOFTWARE_VALIDATION_ONLY":
                continue
            if data.get("status") == "FAILED" or "error" in data:
                print(f"[!] Skipping failed run in '{fp}'.")
                continue

            exp_id = data.get("experiment_id")
            if not exp_id:
                continue

            # Deduplication
            if exp_id in seen_experiments:
                print(f"[!] Warning: Duplicate experiment_id '{exp_id}' encountered in '{fp}'. Skipping.")
                continue
            seen_experiments.add(exp_id)

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


def aggregate_faithfulness_summaries(
    summaries_dir: str = "research/results/summaries",
    output_dir: str = "research/results/processed",
    expected_conditions: Optional[List[Dict[str, Any]]] = None
) -> Optional[pd.DataFrame]:
    """
    Parses FaithfulnessReport JSON files in summaries_dir and builds aggregated tables.
    Excludes smoke validations, deduplicates entries, and detects missing experimental conditions.
    """
    json_pattern = os.path.join(summaries_dir, "*.json")
    files = glob.glob(json_pattern)

    if not files:
        print(f"[!] No summary files found in '{summaries_dir}'.")
        return None

    rows = []
    seen_keys: Set[Tuple[str, str, str]] = set()

    for fp in files:
        norm_fp = fp.replace("\\", "/").lower()
        if "/smoke/" in norm_fp:
            continue

        try:
            with open(fp, "r", encoding="utf-8") as f:
                data = json.load(f)

            if data.get("execution_mode") == "SOFTWARE_VALIDATION_ONLY":
                continue

            exp_id = data.get("experiment_id")
            source = data.get("explanation_source", "unknown")
            prompt_id = data.get("prompt_id", "unknown")

            dedup_key = (exp_id, source, prompt_id)
            if dedup_key in seen_keys:
                print(f"[!] Warning: Duplicate faithfulness summary {dedup_key} in '{fp}'. Skipping.")
                continue
            seen_keys.add(dedup_key)

            row = {
                "experiment_id": exp_id,
                "explanation_source": source,
                "prompt_id": prompt_id,
                "timestamp_utc": data.get("timestamp_utc"),
                "numerical_faithfulness": data.get("numerical_faithfulness"),
                "directional_faithfulness": data.get("directional_faithfulness"),
                "attribution_faithfulness": data.get("attribution_faithfulness"),
                "unsupported_claim_rate": data.get("unsupported_claim_rate"),
                "total_claims_count": data.get("total_claims_count", 0),
                "numeric_claim_count": data.get("numeric_claim_count", 0),
                "directional_claim_count": data.get("directional_claim_count", 0),
                "attribution_claim_count": data.get("attribution_claim_count", 0),
                "unsupported_claim_count": data.get("unsupported_claim_count", 0),
                "undeterminable_claim_count": data.get("undeterminable_claim_count", 0),
                "numerical_mae": data.get("numerical_mean_absolute_error")
            }
            rows.append(row)
        except Exception as e:
            print(f"[!] Warning: Failed parsing summary file '{fp}': {e}")

    if not rows:
        return None

    df_faith = pd.DataFrame(rows)

    # Save individual faithfulness runs
    os.makedirs(output_dir, exist_ok=True)
    runs_csv = os.path.join(output_dir, "faithfulness_runs.csv")
    df_faith.to_csv(runs_csv, index=False)

    # Compute group statistics across explanation sources
    metric_cols = [
        "numerical_faithfulness", "directional_faithfulness",
        "attribution_faithfulness", "unsupported_claim_rate",
        "total_claims_count", "numerical_mae"
    ]
    for col in metric_cols:
        df_faith[col] = pd.to_numeric(df_faith[col], errors="coerce")

    summary_df = df_faith.groupby(["explanation_source", "prompt_id"])[metric_cols].agg(
        ["mean", "std", "count"]
    ).reset_index()

    summary_df.columns = [
        f"{c[0]}_{c[1]}" if c[1] and c[0] not in ["explanation_source", "prompt_id"] else c[0]
        for c in summary_df.columns
    ]

    out_csv = os.path.join(output_dir, "faithfulness_summary.csv")
    summary_df.to_csv(out_csv, index=False)

    # Report missing conditions if expected matrix supplied
    if expected_conditions:
        recorded_exp_ids = set(df_faith["experiment_id"].dropna())
        missing = [c for c in expected_conditions if c.get("experiment_id") not in recorded_exp_ids]
        if missing:
            print(f"[!] Warning: {len(missing)} expected experimental conditions are missing from summaries:")
            for m in missing[:5]:
                print(f"    - Missing: {m}")
            if len(missing) > 5:
                print(f"    ... and {len(missing) - 5} more.")

    return summary_df
