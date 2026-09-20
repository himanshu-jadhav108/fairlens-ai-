"""
Result Aggregator Module for FairLens AI Research.
Compiles raw single-experiment and faithfulness outputs into machine-readable summary tables
with means, standard deviations, paired trade-off deltas, and missing run detection.

Evidence Classification Guarantees:
1. Pilot aggregation REQUIRES execution_mode == PILOT_VALIDATION_RUN
2. Final aggregation REQUIRES execution_mode == FINAL_EMPIRICAL_RUN
3. Mock results (MockLLMProvider, software validation) are NEVER admitted to either
4. Smoke/test artifacts are NEVER admitted to empirical aggregation
5. Deduplication prevents double-counting
6. Missing condition reporting maintained

Evidence classes (as per research protocol):
  SOFTWARE_VALIDATION_ONLY  - unit tests, mock runs, smoke tests
  PILOT_VALIDATION_RUN      - real Gemini pilot (24 conditions)
  FINAL_EMPIRICAL_RUN       - confirmatory experiment (135 conditions)
"""
import os
import glob
import json
from typing import List, Dict, Any, Optional, Set, Tuple
import numpy as np
import pandas as pd

# --- Evidence Mode Constants ---
PILOT_MODE = "PILOT_VALIDATION_RUN"
FINAL_MODE = "FINAL_EMPIRICAL_RUN"
SMOKE_MODE = "SOFTWARE_VALIDATION_ONLY"

# Provider names that indicate non-empirical (mock) runs
_MOCK_PROVIDER_NAMES = {"mock", "mock_gemini-2.5-flash", "mock_provider", "software_validation"}


def _is_mock_source(source_str: str) -> bool:
    """Returns True if explanation_source indicates a mock or software validation run."""
    if not source_str:
        return True
    s = source_str.lower().strip()
    return s.startswith("mock") or s == "software_validation"


def aggregate_raw_results(
    raw_dir: str = "research/results/raw",
    output_dir: str = "research/results/processed",
    required_execution_mode: Optional[str] = None
) -> Optional[pd.DataFrame]:
    """
    Parses all raw JSON result files in raw_dir and builds an aggregated summary table.

    Args:
        raw_dir: Directory containing raw experiment JSON files.
        output_dir: Where to write summary CSV/JSON outputs.
        required_execution_mode: If set, only files with this execution_mode are admitted.
            Use PILOT_MODE for pilot aggregation, FINAL_MODE for final aggregation.
            If None, admits any non-smoke, non-mock file (legacy behavior — use with caution).

    Contamination controls:
        - Files under any /smoke/ path component are always excluded.
        - Files with execution_mode == SOFTWARE_VALIDATION_ONLY are always excluded.
        - Files lacking execution_mode field are classified as non-empirical and excluded.
        - If required_execution_mode is set, files with any other mode are excluded.
    """
    json_pattern = os.path.join(raw_dir, "*.json")
    files = glob.glob(json_pattern)

    if not files:
        print(f"[!] No raw result files found in '{raw_dir}'.")
        return None

    rows = []
    seen_experiments: Set[str] = set()
    excluded_counts = {"smoke_path": 0, "no_mode": 0, "wrong_mode": 0, "software_only": 0, "failed": 0, "duplicate": 0}

    for fp in files:
        # Guard 1: Path isolation — never admit files under a smoke directory
        norm_fp = fp.replace("\\", "/").lower()
        if "/smoke/" in norm_fp or norm_fp.endswith("/.gitkeep"):
            excluded_counts["smoke_path"] += 1
            continue

        # Skip explanation records (handled by aggregate_faithfulness_summaries)
        if os.path.basename(fp).startswith("explanation__"):
            continue

        try:
            with open(fp, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"[!] Warning: Failed parsing result file '{fp}': {e}")
            continue

        # Guard 2: Software validation mode — always excluded from empirical aggregation
        exec_mode = data.get("execution_mode")
        if exec_mode == SMOKE_MODE:
            excluded_counts["software_only"] += 1
            continue

        # Guard 3: Missing execution_mode — classify conservatively as non-empirical
        if exec_mode is None:
            print(f"[!] Excluding '{os.path.basename(fp)}': missing execution_mode field. "
                  "Conservatively classified as non-empirical.")
            excluded_counts["no_mode"] += 1
            continue

        # Guard 4: Required mode enforcement
        if required_execution_mode is not None and exec_mode != required_execution_mode:
            excluded_counts["wrong_mode"] += 1
            continue

        # Guard 5: Failed/errored runs
        if data.get("status") == "FAILED" or "error" in data:
            print(f"[!] Skipping failed run in '{fp}'.")
            excluded_counts["failed"] += 1
            continue

        exp_id = data.get("experiment_id")
        if not exp_id:
            continue

        # Guard 6: Deduplication
        if exp_id in seen_experiments:
            print(f"[!] Warning: Duplicate experiment_id '{exp_id}' in '{fp}'. Skipping.")
            excluded_counts["duplicate"] += 1
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
            "execution_mode": exec_mode,
            "dataset": dataset,
            "model": model,
            "mitigation": mitigation,
            "seed": seed,
            "is_synthetic_benchmark": is_synthetic,
            "baseline_accuracy": base_perf.get("accuracy", {}).get("value"),
            "mitigated_accuracy": mit_perf.get("accuracy", {}).get("value"),
            "delta_accuracy": deltas.get("delta_accuracy"),
            "baseline_f1": base_perf.get("f1_score", {}).get("value"),
            "mitigated_f1": mit_perf.get("f1_score", {}).get("value"),
            "delta_f1": deltas.get("delta_f1_score"),
            "baseline_roc_auc": base_perf.get("roc_auc", {}).get("value"),
            "mitigated_roc_auc": mit_perf.get("roc_auc", {}).get("value"),
            "baseline_dpd": base_fair.get("demographic_parity_difference", {}).get("value"),
            "mitigated_dpd": mit_fair.get("demographic_parity_difference", {}).get("value"),
            "delta_dpd": deltas.get("delta_demographic_parity_difference"),
            "baseline_eod": base_fair.get("equalized_odds_difference", {}).get("value"),
            "mitigated_eod": mit_fair.get("equalized_odds_difference", {}).get("value"),
            "delta_eod": deltas.get("delta_equalized_odds_difference"),
            "baseline_di": base_fair.get("disparate_impact_ratio", {}).get("value"),
            "mitigated_di": mit_fair.get("disparate_impact_ratio", {}).get("value"),
            "cosine_similarity": attr_comp.get("cosine_similarity"),
            "spearman_rank_correlation": attr_comp.get("spearman_rank_correlation"),
            "l1_attribution_difference": attr_comp.get("l1_attribution_difference"),
            "l2_attribution_difference": attr_comp.get("l2_attribution_difference"),
        }
        rows.append(row)

    print(f"[Aggregator] Admitted: {len(rows)} | "
          f"Excluded smoke-path: {excluded_counts['smoke_path']} | "
          f"No execution_mode: {excluded_counts['no_mode']} | "
          f"Wrong mode: {excluded_counts['wrong_mode']} | "
          f"Software-only: {excluded_counts['software_only']} | "
          f"Failed: {excluded_counts['failed']} | "
          f"Duplicate: {excluded_counts['duplicate']}")

    if not rows:
        print("[Aggregator] No admissible raw results found.")
        return None

    df_raw = pd.DataFrame(rows)

    os.makedirs(output_dir, exist_ok=True)
    runs_csv = os.path.join(output_dir, "individual_runs.csv")
    df_raw.to_csv(runs_csv, index=False)

    group_cols = ["dataset", "model", "mitigation", "execution_mode", "is_synthetic_benchmark"]
    metric_cols = [c for c in df_raw.columns if c not in group_cols + ["experiment_id", "seed"]]
    for col in metric_cols:
        df_raw[col] = pd.to_numeric(df_raw[col], errors="coerce")

    summary_df = df_raw.groupby(group_cols)[metric_cols].agg(["mean", "std", "count"]).reset_index()
    summary_df.columns = [
        f"{c[0]}_{c[1]}" if c[1] and c[0] not in group_cols else c[0]
        for c in summary_df.columns
    ]

    summary_csv = os.path.join(output_dir, "summary_table.csv")
    summary_df.to_csv(summary_csv, index=False)
    summary_json = os.path.join(output_dir, "summary_table.json")
    summary_df.to_json(summary_json, orient="records", indent=2)

    print(f"[Aggregator] Summary written: {runs_csv} ({len(df_raw)} runs)")
    return summary_df


def aggregate_faithfulness_summaries(
    summaries_dir: str = "research/results/summaries",
    output_dir: str = "research/results/processed",
    required_execution_mode: Optional[str] = None,
    expected_conditions: Optional[List[Dict[str, Any]]] = None,
    canonical_inventory_path: Optional[str] = None
) -> Optional[pd.DataFrame]:
    """
    Parses faithfulness summary JSON files and builds aggregated faithfulness tables.

    Contamination controls:
        - Files under /smoke/ are always excluded.
        - Files with execution_mode == SOFTWARE_VALIDATION_ONLY are always excluded.
        - Files from mock providers (explanation_source starts with 'mock') are excluded.
        - Files missing execution_mode are conservatively excluded.
        - If required_execution_mode is set, only matching files are admitted.
        - If canonical_inventory_path or expected_conditions is set, only canonical condition IDs are admitted.
    """
    json_pattern = os.path.join(summaries_dir, "*.json")
    files = glob.glob(json_pattern)

    if not files:
        print(f"[!] No summary files found in '{summaries_dir}'.")
        return None

    canonical_exp_ids: Set[str] = set()
    if canonical_inventory_path and os.path.exists(canonical_inventory_path):
        try:
            with open(canonical_inventory_path, "r", encoding="utf-8") as f:
                inv_data = json.load(f)
                canonical_exp_ids = {c.get("experiment_id") for c in inv_data.get("inventory", []) if c.get("experiment_id")}
        except Exception as e:
            print(f"[!] Warning: Failed parsing canonical inventory at '{canonical_inventory_path}': {e}")
    elif expected_conditions:
        canonical_exp_ids = {c.get("experiment_id") for c in expected_conditions if c.get("experiment_id")}

    rows = []
    seen_keys: Set[Tuple[str, str, str]] = set()
    excluded_counts = {"smoke_path": 0, "mock_source": 0, "no_mode": 0, "wrong_mode": 0,
                       "software_only": 0, "duplicate": 0, "non_canonical": 0}

    for fp in files:
        norm_fp = fp.replace("\\", "/").lower()
        if "/smoke/" in norm_fp or norm_fp.endswith("/.gitkeep"):
            excluded_counts["smoke_path"] += 1
            continue

        try:
            with open(fp, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"[!] Warning: Failed parsing summary file '{fp}': {e}")
            continue

        # Guard: Software validation mode
        exec_mode = data.get("execution_mode")
        if exec_mode == SMOKE_MODE:
            excluded_counts["software_only"] += 1
            continue

        # Guard: Mock provider source — never admit mock results to empirical aggregation
        source = data.get("explanation_source", "")
        if _is_mock_source(source):
            excluded_counts["mock_source"] += 1
            continue

        # Guard: Missing execution_mode — conservative exclusion
        if exec_mode is None:
            print(f"[!] Excluding faithfulness summary '{os.path.basename(fp)}': "
                  "missing execution_mode. Conservatively classified as non-empirical.")
            excluded_counts["no_mode"] += 1
            continue

        # Guard: Required mode enforcement
        if required_execution_mode is not None and exec_mode != required_execution_mode:
            excluded_counts["wrong_mode"] += 1
            continue

        exp_id = data.get("experiment_id")
        # Guard: Canonical condition enforcement
        if canonical_exp_ids and exp_id not in canonical_exp_ids:
            excluded_counts["non_canonical"] += 1
            continue

        prompt_id = data.get("prompt_id", "unknown")

        dedup_key = (exp_id, source, prompt_id)
        if dedup_key in seen_keys:
            print(f"[!] Warning: Duplicate faithfulness summary {dedup_key} in '{fp}'. Skipping.")
            excluded_counts["duplicate"] += 1
            continue
        seen_keys.add(dedup_key)

        row = {
            "experiment_id": exp_id,
            "execution_mode": exec_mode,
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
            "numerical_mae": data.get("numerical_mean_absolute_error"),
        }
        rows.append(row)

    print(f"[FaithAggregator] Admitted: {len(rows)} | "
          f"Smoke-path: {excluded_counts['smoke_path']} | "
          f"Mock-source: {excluded_counts['mock_source']} | "
          f"No mode: {excluded_counts['no_mode']} | "
          f"Wrong mode: {excluded_counts['wrong_mode']} | "
          f"Software-only: {excluded_counts['software_only']} | "
          f"Duplicate: {excluded_counts['duplicate']} | "
          f"Non-canonical: {excluded_counts['non_canonical']}")

    if not rows:
        print("[FaithAggregator] No admissible faithfulness summaries found.")
        return None

    df_faith = pd.DataFrame(rows)
    os.makedirs(output_dir, exist_ok=True)
    runs_csv = os.path.join(output_dir, "faithfulness_runs.csv")
    df_faith.to_csv(runs_csv, index=False)

    metric_cols = [
        "numerical_faithfulness", "directional_faithfulness",
        "attribution_faithfulness", "unsupported_claim_rate",
        "total_claims_count", "numerical_mae"
    ]
    for col in metric_cols:
        df_faith[col] = pd.to_numeric(df_faith[col], errors="coerce")

    summary_df = df_faith.groupby(["explanation_source", "prompt_id", "execution_mode"])[metric_cols].agg(
        ["mean", "std", "count"]
    ).reset_index()
    summary_df.columns = [
        f"{c[0]}_{c[1]}" if c[1] and c[0] not in ["explanation_source", "prompt_id", "execution_mode"] else c[0]
        for c in summary_df.columns
    ]
    out_csv = os.path.join(output_dir, "faithfulness_summary.csv")
    summary_df.to_csv(out_csv, index=False)

    if expected_conditions:
        recorded_exp_ids = set(df_faith["experiment_id"].dropna())
        missing = [c for c in expected_conditions if c.get("experiment_id") not in recorded_exp_ids]
        if missing:
            print(f"[!] Warning: {len(missing)} expected experimental conditions missing from summaries:")
            for m in missing[:5]:
                print(f"    - Missing: {m}")
            if len(missing) > 5:
                print(f"    ... and {len(missing) - 5} more.")

    return summary_df
