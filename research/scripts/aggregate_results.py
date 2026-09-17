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

from research.analysis.aggregator import aggregate_raw_results


def main():
    parser = argparse.ArgumentParser(description="Aggregate FairLens AI raw results.")
    parser.add_argument("--raw-dir", type=str, default="research/results/raw", help="Directory of raw JSON results")
    parser.add_argument("--output-dir", type=str, default="research/results/processed", help="Directory for processed CSVs")

    args = parser.parse_args()
    summary = aggregate_raw_results(raw_dir=args.raw_dir, output_dir=args.output_dir)
    if summary is not None:
        print("[+] Aggregation completed successfully.")
    else:
        print("[!] Aggregation produced no output.")


if __name__ == "__main__":
    main()
