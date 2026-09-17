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

# Automatically load environment variables from backend/.env or .env if needed
try:
    import dotenv
    workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    dotenv.load_dotenv(os.path.join(workspace_root, "backend", ".env"))
    dotenv.load_dotenv(os.path.join(workspace_root, ".env"))
except Exception:
    pass

if not os.environ.get("GEMINI_API_KEY"):
    for rel_path in ["backend/.env", ".env"]:
        env_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "../..", rel_path))
        if os.path.exists(env_file):
            try:
                with open(env_file, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("GEMINI_API_KEY="):
                            os.environ["GEMINI_API_KEY"] = line.split("=", 1)[1].strip().strip('"').strip("'")
                            break
            except Exception:
                pass
        if os.environ.get("GEMINI_API_KEY"):
            break

import json
import yaml
import argparse
import datetime
import itertools
from typing import Dict, Any, List, Optional

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
                        help="Limit total number of conditions from matrix to consider (e.g. --limit 2)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print the planned pilot matrix without executing")
    parser.add_argument("--no-resume", action="store_true", default=False,
                        help="Disable resuming and re-execute conditions even if complete")
    parser.add_argument("--use-synthetic", action="store_true", default=True,
                        help="Use synthetic benchmark data for fast execution (default: True)")
    return parser.parse_args()


def load_pilot_config(config_path: str) -> Dict[str, Any]:
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def find_completed_pilot_condition(
    output_dir: str,
    dataset: str,
    model: str,
    mitigation: str,
    seed: int,
    provider: str
) -> Optional[Dict[str, Any]]:
    """
    Inspects output_dir to see if a valid pilot run for this condition already exists.
    Requires:
      - Faithfulness summary with execution_mode == 'PILOT_VALIDATION_RUN'
      - Valid explanation_source matching provider
      - Matching raw explanation with non-empty output_text
      - Matching manifest with execution_mode == 'PILOT_VALIDATION_RUN'
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
                if summ.get("execution_mode") != "PILOT_VALIDATION_RUN":
                    continue
                if summ.get("total_claims_count", 0) <= 0:
                    continue

                exp_id = summ.get("experiment_id")
                if not exp_id:
                    continue

                # Check raw explanation
                if not os.path.exists(raw_dir):
                    continue
                raw_files = [f for f in os.listdir(raw_dir) if f.startswith(f"explanation__{exp_id}") and f.endswith(".json")]
                if not raw_files:
                    continue
                with open(os.path.join(raw_dir, raw_files[0]), "r", encoding="utf-8") as rf:
                    raw_exp = json.load(rf)
                if not raw_exp.get("output_text"):
                    continue

                # Check manifest
                man_path = os.path.join(manifests_dir, f"{exp_id}.json")
                if not os.path.exists(man_path):
                    continue

                suffix = exp_id.split("__")[-1]
                tmpl_name = f"summary__{dataset}__{model}__{mitigation}__seed{seed}__{suffix}__template_baseline.json"
                tmpl_path = os.path.join(summaries_dir, tmpl_name)
                tmpl_faith = None
                if os.path.exists(tmpl_path):
                    with open(tmpl_path, "r", encoding="utf-8") as tf:
                        tmpl_data = json.load(tf)
                        tmpl_faith = tmpl_data.get("numerical_faithfulness")

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
    print(f"Total Conditions In Scope: {len(all_conditions)}")
    print(f"Resume Enabled:  {not args.no_resume}")
    print(f"Datasets:        {datasets}")
    print(f"Models:          {models}")
    print(f"Mitigations:     {mitigations}")
    print(f"Seeds:           {seeds}")
    print(f"Use Synthetic:   {args.use_synthetic}")
    print("=" * 75)

    if args.dry_run:
        print("\n[DRY RUN] Planned Experimental Conditions:")
        for idx, (d, m, mit, s) in enumerate(all_conditions, 1):
            completed = find_completed_pilot_condition(output_dir, d, m, mit, s, provider) if not args.no_resume else None
            status_tag = f"ALREADY COMPLETE ({completed['experiment_id']})" if completed else "PENDING"
            print(f"  [{idx:02d}/{len(all_conditions):02d}] {d:<8} | {m:<20} | {mit:<22} | s={s} | {status_tag}")
        print("\nDry run complete. No experiments were executed.")
        sys.exit(0)

    os.makedirs(output_dir, exist_ok=True)
    results = []
    failures = []
    skipped = []
    inventory = []

    start_time = datetime.datetime.now(datetime.timezone.utc)

    for idx, (d, m, mit, s) in enumerate(all_conditions, 1):
        cond_id = f"{d}__{m}__{mit}__s{s}"
        print(f"\n>>> Checking Pilot Run [{idx}/{len(all_conditions)}]: {d} | {m} | {mit} | seed={s}")

        # Check for completed condition if resume is active
        if not args.no_resume:
            existing = find_completed_pilot_condition(output_dir, d, m, mit, s, provider)
            if existing:
                print(f"    [SKIP] Condition already completed: {existing['experiment_id']}. Skipping duplicate execution.")
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
                    "execution_mode": "PILOT_VALIDATION_RUN",
                    "experiment_id": existing["experiment_id"]
                })
                results.append(skipped[-1])
                continue

        try:
            print(f"    [EXECUTE] Running experiment for {d} | {m} | {mit} | seed={s}...")
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
                "execution_mode": "PILOT_VALIDATION_RUN",
                "experiment_id": res["experiment_id"]
            })
        except Exception as e:
            print(f"[!] FAILED: Pilot run for {d}-{m}-{mit}-s{s} failed: {e}")
            fail_entry = {
                "condition": {"dataset": d, "model": m, "mitigation": mit, "seed": s},
                "error": str(e),
                "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat()
            }
            failures.append(fail_entry)
            inventory.append({
                "condition_id": cond_id,
                "dataset": d,
                "model": m,
                "mitigation": mit,
                "seed": s,
                "status": "FAILED",
                "execution_mode": "PILOT_VALIDATION_RUN",
                "error": str(e)
            })

    end_time = datetime.datetime.now(datetime.timezone.utc)
    duration_secs = (end_time - start_time).total_seconds()

    successful_runs = [r for r in results if r.get("status") == "SUCCESS"]

    # Save summary report
    summary = {
        "pilot_timestamp_utc": start_time.isoformat(),
        "duration_seconds": round(duration_secs, 2),
        "total_planned": len(all_conditions),
        "attempted_runs": len(all_conditions) - len(skipped),
        "successful_runs": len(successful_runs),
        "failed_runs": len(failures),
        "skipped_as_already_complete": len(skipped),
        "provider": provider,
        "results": results,
        "failures": failures,
        "inventory": inventory
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
    print(f"Total Conditions in Scope:    {len(all_conditions)}")
    print(f"Skipped (Already Complete):   {len(skipped)}")
    print(f"Attempted:                    {len(all_conditions) - len(skipped)}")
    print(f"Successful Newly Executed:    {len(successful_runs)}")
    print(f"Failed:                       {len(failures)}")
    print(f"Summary written to: {summary_file}")
    print("=" * 75)


if __name__ == "__main__":
    main()
