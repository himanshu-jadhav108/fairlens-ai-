#!/usr/bin/env python3
"""
Confirmatory Final Experiment Runner for FairLens AI Research.
Executes the locked 36-condition experimental matrix:
3 Datasets (Adult, COMPAS, German) x 2 Models (Logistic Regression, Random Forest)
x 2 Mitigations (Correlation Remover, Threshold Optimizer) x 3 Seeds (42, 123, 456)
= Exactly 36 paired conditions (36 Template Baseline + 36 Gemini 2.5 Flash = 72 explanations).

Strict protocol requirements:
- Execution mode: FINAL_EMPIRICAL_RUN
- 100% Real benchmark data (use_synthetic: False)
- Strictly gemini-2.5-flash
- Automatic credential rotation across 4 accounts
- Zero API keys logged, committed, or persisted in output files
"""
import os
import sys

# Ensure workspace root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import json
import yaml
import argparse
import datetime
import itertools
from typing import Dict, Any, List, Optional

from research.scripts.run_llm_experiment import run_experiment
from research.analysis.aggregator import aggregate_raw_results, aggregate_faithfulness_summaries
from research.statistics.faithfulness_analysis import compute_paired_faithfulness_comparison


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run Confirmatory Final Experiment for FairLens AI Research"
    )
    parser.add_argument("--config", type=str, default="research/configs/final_protocol_config.yaml",
                        help="Path to final protocol configuration YAML")
    parser.add_argument("--provider", type=str, default=None, choices=["mock", "gemini"],
                        help="LLM provider: 'gemini' (production) or 'mock' (offline dry test)")
    parser.add_argument("--limit", type=int, default=None,
                        help="Limit number of conditions to execute (for test verification)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print planned experimental matrix without executing")
    parser.add_argument("--no-resume", action="store_true", default=False,
                        help="Disable resuming and re-execute conditions even if complete")
    return parser.parse_args()


def load_config(config_path: str) -> Dict[str, Any]:
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def find_completed_condition(
    output_dir: str,
    dataset: str,
    model: str,
    mitigation: str,
    seed: int,
    provider: str
) -> Optional[Dict[str, Any]]:
    """
    Checks if a valid, non-synthetic final empirical run for this condition already exists.
    Requires:
      - Faithfulness summary with execution_mode == 'FINAL_EMPIRICAL_RUN'
      - Matching manifest with execution_mode == 'FINAL_EMPIRICAL_RUN' and is_synthetic_benchmark == False
      - Matching raw explanation with non-empty text
      - Non-empty claims
    """
    summaries_dir = os.path.join(output_dir, "summaries")
    raw_dir = os.path.join(output_dir, "raw")
    manifests_dir = os.path.join(output_dir, "manifests")

    if not os.path.exists(summaries_dir):
        return None

    prefix = f"summary__{dataset}__{model}__{mitigation}__seed{seed}__"
    for fname in os.listdir(summaries_dir):
        if fname.startswith(prefix) and (f"__{provider}" in fname or f"_{provider}" in fname):
            summary_path = os.path.join(summaries_dir, fname)
            try:
                with open(summary_path, "r", encoding="utf-8") as f:
                    summ = json.load(f)
                if summ.get("execution_mode") != "FINAL_EMPIRICAL_RUN":
                    continue
                if summ.get("total_claims_count", 0) <= 0:
                    continue

                exp_id = summ.get("experiment_id")
                if not exp_id:
                    continue

                # Check manifest for non-synthetic benchmark
                man_path = os.path.join(manifests_dir, f"{exp_id}.json")
                if not os.path.exists(man_path):
                    continue
                with open(man_path, "r", encoding="utf-8") as mf:
                    man_data = json.load(mf)
                if man_data.get("execution_mode") != "FINAL_EMPIRICAL_RUN":
                    continue
                is_syn = man_data.get("dataset", {}).get("is_synthetic_benchmark", man_data.get("is_synthetic_benchmark", False))
                if is_syn:
                    continue  # Synthetic data rejected from final results

                # Check raw explanation
                raw_files = [f for f in os.listdir(raw_dir) if f.startswith(f"explanation__{exp_id}") and f.endswith(".json")]
                if not raw_files:
                    continue
                with open(os.path.join(raw_dir, raw_files[0]), "r", encoding="utf-8") as rf:
                    raw_exp = json.load(rf)
                if not raw_exp.get("output_text"):
                    continue

                # Check template baseline summary
                suffix = exp_id.split("__")[-1]
                tmpl_name = f"summary__{dataset}__{model}__{mitigation}__seed{seed}__{suffix}__template_baseline.json"
                tmpl_path = os.path.join(summaries_dir, tmpl_name)
                tmpl_faith = None
                if os.path.exists(tmpl_path):
                    with open(tmpl_path, "r", encoding="utf-8") as tf:
                        tmpl_faith = json.load(tf).get("numerical_faithfulness")

                return {
                    "experiment_id": exp_id,
                    "evidence_hash": raw_exp.get("input_evidence_hash"),
                    "template_faithfulness": tmpl_faith,
                    "llm_faithfulness": summ.get("numerical_faithfulness"),
                    "summary_file": summary_path
                }
            except Exception:
                continue
    return None


def main():
    args = parse_args()
    cfg = load_config(args.config)

    matrix = cfg["matrix"]
    datasets = matrix["datasets"]
    models = matrix["models"]
    mitigations = matrix["mitigations"]
    seeds = matrix["seeds"]

    llm_cfg = cfg.get("llm_configuration", {})
    provider = args.provider or llm_cfg.get("provider", "gemini")
    model_name = llm_cfg.get("model", "gemini-2.5-flash")
    temperature = float(llm_cfg.get("temperature", 0.2))
    prompt_id = llm_cfg.get("prompts", ["combined_audit_v1"])[0]

    output_dir = cfg.get("experiment_metadata", {}).get("output_dir", "research/results/final")
    use_synthetic = cfg.get("experiment_metadata", {}).get("use_synthetic", False)

    # STRICT PROTOCOL CHECK
    if use_synthetic:
        raise ValueError("FINAL EXPERIMENT ERROR: use_synthetic must be False for final confirmatory study.")

    all_conditions = list(itertools.product(datasets, models, mitigations, seeds))
    if args.limit:
        all_conditions = all_conditions[:args.limit]

    print("=" * 80)
    print("FAIRLENS AI RESEARCH — CONFIRMATORY FINAL EMPIRICAL EXPERIMENT")
    print("=" * 80)
    print(f"Target Output Directory:   {output_dir}")
    print(f"LLM Provider:              {provider} ({model_name})")
    print(f"Real Data Enforced:        {not use_synthetic} (100% Real Benchmark Datasets)")
    print(f"Total Conditions in Scope: {len(all_conditions)}")
    print(f"Resumability Active:       {not args.no_resume}")
    print(f"Datasets:                  {datasets}")
    print(f"Models:                    {models}")
    print(f"Mitigations:               {mitigations}")
    print(f"Seeds:                     {seeds}")
    print("=" * 80)

    if args.dry_run:
        print("\n[DRY RUN] Planned Experimental Matrix:")
        for idx, (d, m, mit, s) in enumerate(all_conditions, 1):
            completed = find_completed_condition(output_dir, d, m, mit, s, provider) if not args.no_resume else None
            status_tag = f"COMPLETED ({completed['experiment_id']})" if completed else "PENDING"
            print(f"  [{idx:02d}/{len(all_conditions):02d}] {d:<8} | {m:<20} | {mit:<22} | seed={s:<3} | {status_tag}")
        print("\nDry run completed successfully.")
        return

    # Ensure output directory structure exists
    for sub in ["raw", "manifests", "claims", "summaries", "processed"]:
        os.makedirs(os.path.join(output_dir, sub), exist_ok=True)

    results = []
    failures = []
    skipped = []
    inventory = []

    start_time = datetime.datetime.now(datetime.timezone.utc)

    for idx, (d, m, mit, s) in enumerate(all_conditions, 1):
        cond_id = f"{d}__{m}__{mit}__seed{s}"
        print(f"\n[{idx:02d}/{len(all_conditions):02d}] Condition: {d} | {m} | {mit} | seed={s}", flush=True)

        if not args.no_resume:
            existing = find_completed_condition(output_dir, d, m, mit, s, provider)
            if existing:
                print(f"    [SKIP] Condition already completed: {existing['experiment_id']}", flush=True)
                skipped.append({
                    "condition": {"dataset": d, "model": m, "mitigation": mit, "seed": s},
                    "experiment_id": existing["experiment_id"],
                    "evidence_hash": existing["evidence_hash"],
                    "status": "SKIPPED_AS_ALREADY_COMPLETE",
                    "template_faithfulness": existing["template_faithfulness"],
                    "llm_faithfulness": existing["llm_faithfulness"]
                })
                inventory.append({
                    "condition_id": cond_id,
                    "dataset": d,
                    "model": m,
                    "mitigation": mit,
                    "seed": s,
                    "status": "SKIPPED_AS_ALREADY_COMPLETE",
                    "execution_mode": "FINAL_EMPIRICAL_RUN",
                    "experiment_id": existing["experiment_id"]
                })
                results.append(skipped[-1])
                continue

        try:
            print(f"    [EXECUTE] Running full pipeline for condition...", flush=True)
            res = run_experiment(
                dataset_name=d,
                model_name=m,
                mitigation_name=mit,
                seed=s,
                provider_name=provider,
                prompt_id=prompt_id,
                temperature=temperature,
                output_dir=output_dir,
                use_synthetic=False,
                is_smoke_test=False,
                execution_mode="FINAL_EMPIRICAL_RUN",
                llm_model_name=model_name
            )
            entry = {
                "condition": {"dataset": d, "model": m, "mitigation": mit, "seed": s},
                "experiment_id": res["experiment_id"],
                "evidence_hash": res["evidence_hash"],
                "status": "SUCCESS",
                "template_faithfulness": res["template_report"]["numerical_faithfulness"],
                "llm_faithfulness": res["llm_report"]["numerical_faithfulness"]
            }
            results.append(entry)
            inventory.append({
                "condition_id": cond_id,
                "dataset": d,
                "model": m,
                "mitigation": mit,
                "seed": s,
                "status": "SUCCESS",
                "execution_mode": "FINAL_EMPIRICAL_RUN",
                "experiment_id": res["experiment_id"]
            })
            print(f"    [SUCCESS] Condition {res['experiment_id']} completed.", flush=True)
        except Exception as e:
            print(f"    [ERROR] Condition {cond_id} failed: {e}", flush=True)
            failures.append({
                "condition": {"dataset": d, "model": m, "mitigation": mit, "seed": s},
                "error": str(e),
                "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat()
            })
            inventory.append({
                "condition_id": cond_id,
                "dataset": d,
                "model": m,
                "mitigation": mit,
                "seed": s,
                "status": "FAILED",
                "error": str(e)
            })

    end_time = datetime.datetime.now(datetime.timezone.utc)
    duration_s = (end_time - start_time).total_seconds()

    print("\n" + "=" * 80)
    print("FINAL EXPERIMENTAL MATRIX EXECUTION SUMMARY")
    print("=" * 80)
    print(f"Total Conditions in Matrix: {len(all_conditions)}")
    print(f"Successfully Completed:     {len(results)}")
    print(f"  - Reused from Prior Runs: {len(skipped)}")
    print(f"  - Newly Executed:         {len(results) - len(skipped)}")
    print(f"Failed Conditions:          {len(failures)}")
    print(f"Total Elapsed Time:         {duration_s:.1f}s ({duration_s/60:.2f} min)")
    print("=" * 80)

    # Save manifest inventory
    inventory_path = os.path.join(output_dir, "final_matrix_inventory.json")
    with open(inventory_path, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp_utc": end_time.isoformat(),
            "total_planned": len(all_conditions),
            "completed_count": len(results),
            "failed_count": len(failures),
            "inventory": inventory,
            "failures": failures
        }, f, indent=2)
    print(f"[+] Final matrix inventory saved to: {inventory_path}")

    # Trigger Aggregations
    proc_dir = os.path.join(output_dir, "processed")
    raw_target = os.path.join(output_dir, "raw")
    summaries_target = os.path.join(output_dir, "summaries")

    print("\n[*] Aggregating raw results and faithfulness summaries...")
    aggregate_raw_results(raw_dir=raw_target, output_dir=proc_dir, required_execution_mode="FINAL_EMPIRICAL_RUN")
    aggregate_faithfulness_summaries(summaries_dir=summaries_target, output_dir=proc_dir, required_execution_mode="FINAL_EMPIRICAL_RUN")

    # Paired Statistical Comparison
    faith_runs_csv = os.path.join(proc_dir, "faithfulness_runs.csv")
    if os.path.exists(faith_runs_csv):
        print("[*] Computing paired statistical comparison (Template Baseline vs LLM)...")
        import pandas as pd
        import numpy as np
        df_runs = pd.read_csv(faith_runs_csv)
        base_source = "template_baseline"
        llm_source = f"{provider}__{model_name}"

        df_base = df_runs[df_runs["explanation_source"] == base_source].set_index("experiment_id")
        df_llm = df_runs[df_runs["explanation_source"] == llm_source].set_index("experiment_id")
        common_ids = sorted(list(set(df_base.index).intersection(set(df_llm.index))))

        paired_rows = []
        metrics = ["numerical_faithfulness", "directional_faithfulness", "attribution_faithfulness", "unsupported_claim_rate"]
        for m in metrics:
            t_vals = []
            l_vals = []
            for exp_id in common_ids:
                if m in df_base.columns and m in df_llm.columns:
                    bv = df_base.loc[exp_id, m]
                    lv = df_llm.loc[exp_id, m]
                    if pd.notna(bv) and pd.notna(lv):
                        t_vals.append(float(bv))
                        l_vals.append(float(lv))

            if len(t_vals) >= 3:
                comp = compute_paired_faithfulness_comparison(t_vals, l_vals, metric_name=m)
                paired_rows.append({
                    "metric": m,
                    "n_pairs": comp["n_pairs"],
                    "mean_template": comp["mean_template"],
                    "mean_llm": comp["mean_llm"],
                    "mean_difference": comp["mean_difference"],
                    "std_difference": comp["std_difference"],
                    "cohens_d": comp["cohens_d"],
                    "t_statistic": comp.get("paired_t_test", {}).get("t_statistic"),
                    "t_p_value": comp.get("paired_t_test", {}).get("p_value"),
                    "wilcoxon_w": comp.get("wilcoxon_signed_rank", {}).get("w_statistic"),
                    "wilcoxon_p_value": comp.get("wilcoxon_signed_rank", {}).get("p_value"),
                })
            else:
                paired_rows.append({
                    "metric": m,
                    "n_pairs": len(t_vals),
                    "mean_template": round(float(np.mean(t_vals)), 4) if t_vals else None,
                    "mean_llm": round(float(np.mean(l_vals)), 4) if l_vals else None,
                    "mean_difference": None,
                    "std_difference": None,
                    "cohens_d": None,
                    "t_statistic": None,
                    "t_p_value": None,
                    "wilcoxon_w": None,
                    "wilcoxon_p_value": None,
                })
        paired_df = pd.DataFrame(paired_rows)
        paired_csv = os.path.join(proc_dir, "final_paired_comparison.csv")
        paired_df.to_csv(paired_csv, index=False)
        print(f"[+] Paired comparison saved to: {paired_csv}")


if __name__ == "__main__":
    main()
