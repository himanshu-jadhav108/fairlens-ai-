#!/usr/bin/env python3
"""
CLI entrypoint to aggregate raw JSON experiment results into summary tables.
Usage:
    python research/scripts/aggregate_results.py
"""
import argparse
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from research.analysis.aggregator import aggregate_raw_results, aggregate_faithfulness_summaries


def main():
    parser = argparse.ArgumentParser(description="Aggregate FairLens AI raw results.")
    parser.add_argument("--raw-dir", "--input-dir", dest="raw_dir", type=str, default="research/results/raw", help="Directory of raw JSON results or pilot directory")
    parser.add_argument("--output-dir", type=str, default="research/results/processed", help="Directory for processed CSVs")
    parser.add_argument("--mode", type=str, default=None, help="Execution mode filter (e.g. PILOT_VALIDATION_RUN or FINAL_EMPIRICAL_RUN)")
    parser.add_argument("--inventory", type=str, default=None, help="Path to canonical inventory JSON to enforce exact condition membership")

    args = parser.parse_args()

    # Determine paths
    if os.path.isdir(os.path.join(args.raw_dir, "raw")):
        raw_target = os.path.join(args.raw_dir, "raw")
    else:
        raw_target = args.raw_dir

    if os.path.isdir(os.path.join(args.raw_dir, "summaries")):
        summaries_target = os.path.join(args.raw_dir, "summaries")
    elif os.path.isdir("research/results/summaries"):
        summaries_target = "research/results/summaries"
    else:
        summaries_target = None

    inventory_path = args.inventory
    if not inventory_path:
        # Auto-detect final_matrix_inventory.json in raw_dir if available
        candidate = os.path.join(args.raw_dir, "final_matrix_inventory.json")
        if os.path.exists(candidate):
            inventory_path = candidate

    print(f"[*] Aggregating raw experiment results from: {raw_target}")
    summary_raw = aggregate_raw_results(raw_dir=raw_target, output_dir=args.output_dir, required_execution_mode=args.mode)

    summary_faith = None
    if summaries_target and os.path.isdir(summaries_target):
        print(f"[*] Aggregating faithfulness summaries from: {summaries_target}")
        if inventory_path:
            print(f"[*] Enforcing canonical inventory from: {inventory_path}")
        summary_faith = aggregate_faithfulness_summaries(
            summaries_dir=summaries_target,
            output_dir=args.output_dir,
            required_execution_mode=args.mode,
            canonical_inventory_path=inventory_path
        )

    if summary_raw is not None or summary_faith is not None:
        print("[+] Aggregation completed successfully.")
    else:
        print("[!] Aggregation produced no output.")


if __name__ == "__main__":
    main()
