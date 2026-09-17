"""
Empirical Pilot Experiment Runner for FairLens AI Research (Phase 2).
Executes a focused pilot matrix designed for method validation and failure inspection:
2 Datasets x 2 Models x 2 Mitigations x 3 Seeds = 24 conditions.

Outputs are written to: research/results/pilot/
Tagged with execution_mode: "PILOT_VALIDATION_RUN"
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
from typing import Dict, Any, List

from research.scripts.run_llm_experiment import run_experiment


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run Empirical Pilot Experiment for LLM Fairness Explanation Faithfulness"
    )
    parser.add_argument("--config", type=str, default="research/configs/pilot_config.yaml",
                        help="Path to pilot configuration YAML")
    parser.add_argument("--provider", type=str, default=None, choices=["mock", "gemini"],
                        help="LLM provider: overrides config setting ('mock' for dry testing, 'gemini' for real API)")
    parser.add_argument("--limit", type=int, default=None,
                        help="Limit number of pilot runs to execute (e.g. --limit 2)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print the planned pilot matrix without executing")
    parser.add_argument("--use-synthetic", action="store_true", default=True,
                        help="Use synthetic benchmark data for fast execution (default: True)")
    return parser.parse_args()


def load_pilot_config(config_path: str) -> Dict[str, Any]:
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main():
    args = parse_args()
    cfg = load_pilot_config(args.config)

    matrix = cfg["matrix"]
    datasets = matrix["datasets"]
    models = matrix["models"]
    mitigations = matrix["mitigations"]
    seeds = matrix["seeds"]

    llm_cfg = cfg.get("llm_configuration", {})
    provider = args.provider or llm_cfg.get("provider", "gemini")
    temperature = float(llm_cfg.get("temperature", 0.2))
    prompt_id = llm_cfg.get("prompts", ["combined_audit_v1"])[0]
    output_dir = cfg.get("pilot_metadata", {}).get("output_dir", "research/results/pilot")

    # Generate all condition tuples
    all_conditions = list(itertools.product(datasets, models, mitigations, seeds))
    if args.limit:
        all_conditions = all_conditions[:args.limit]

    print("=" * 75)
    print("FAIRLENS AI RESEARCH — EMPIRICAL PILOT EXPERIMENT (PHASE 2)")
    print(f"Target Output:   {output_dir}")
    print(f"Provider:        {provider}")
    print(f"Total Runs:      {len(all_conditions)}")
    print(f"Datasets:        {datasets}")
    print(f"Models:          {models}")
    print(f"Mitigations:     {mitigations}")
    print(f"Seeds:           {seeds}")
    print(f"Use Synthetic:   {args.use_synthetic}")
    print("=" * 75)

    if args.dry_run:
        print("\n[DRY RUN] Planned Experimental Conditions:")
        for idx, (d, m, mit, s) in enumerate(all_conditions, 1):
            print(f"  [{idx:02d}/{len(all_conditions):02d}] Dataset={d:<8} | Model={m:<20} | Mitigation={mit:<22} | Seed={s}")
        print("\nDry run complete. No experiments were executed.")
        sys.exit(0)

    os.makedirs(output_dir, exist_ok=True)
    results = []
    failures = []

    start_time = datetime.datetime.now(datetime.timezone.utc)

    for idx, (d, m, mit, s) in enumerate(all_conditions, 1):
        print(f"\n>>> Executing Pilot Run [{idx}/{len(all_conditions)}]: {d} | {m} | {mit} | seed={s}")
        try:
            res = run_experiment(
                dataset_name=d,
                model_name=m,
                mitigation_name=mit,
                seed=s,
                provider_name=provider,
                prompt_id=prompt_id,
                temperature=temperature,
                output_dir=output_dir,
                use_synthetic=args.use_synthetic,
                is_smoke_test=False,
                execution_mode="PILOT_VALIDATION_RUN"
            )
            results.append({
                "condition": {"dataset": d, "model": m, "mitigation": mit, "seed": s},
                "experiment_id": res["experiment_id"],
                "evidence_hash": res["evidence_hash"],
                "status": "SUCCESS",
                "template_faithfulness": res["template_report"]["numerical_faithfulness"],
                "llm_faithfulness": res["llm_report"]["numerical_faithfulness"]
            })
        except Exception as e:
            print(f"[!] FAILED: Pilot run for {d}-{m}-{mit}-s{s} failed: {e}")
            failures.append({
                "condition": {"dataset": d, "model": m, "mitigation": mit, "seed": s},
                "error": str(e),
                "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat()
            })

    end_time = datetime.datetime.now(datetime.timezone.utc)
    duration_secs = (end_time - start_time).total_seconds()

    # Save summary report
    summary = {
        "pilot_timestamp_utc": start_time.isoformat(),
        "duration_seconds": round(duration_secs, 2),
        "total_planned": len(all_conditions),
        "successful_runs": len(results),
        "failed_runs": len(failures),
        "provider": provider,
        "results": results,
        "failures": failures
    }

    summary_file = os.path.join(output_dir, "pilot_execution_summary.json")
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    if failures:
        fail_file = os.path.join(output_dir, "pilot_failures.json")
        with open(fail_file, "w", encoding="utf-8") as f:
            json.dump(failures, f, indent=2)

    print("\n" + "=" * 75)
    print("PILOT EXECUTION COMPLETE")
    print(f"Successes: {len(results)} / {len(all_conditions)}")
    print(f"Failures:  {len(failures)} / {len(all_conditions)}")
    print(f"Summary written to: {summary_file}")
    print("=" * 75)


if __name__ == "__main__":
    main()
