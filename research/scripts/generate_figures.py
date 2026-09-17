#!/usr/bin/env python3
"""
CLI entrypoint to generate candidate research visualization figures.
Usage:
    python research/scripts/generate_figures.py
"""
import argparse
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from research.analysis.visualization import generate_candidate_figures


def main():
    parser = argparse.ArgumentParser(description="Generate candidate figures for FairLens AI research.")
    parser.add_argument("--processed-dir", type=str, default="research/results/processed", help="Path to processed CSVs")
    parser.add_argument("--figures-dir", type=str, default="research/results/figures", help="Path to output figures")

    args = parser.parse_args()
    generate_candidate_figures(processed_dir=args.processed_dir, figures_dir=args.figures_dir)


if __name__ == "__main__":
    main()
