#!/usr/bin/env python3
"""
CLI entrypoint to execute a batch or candidate matrix of experiments.
Usage:
    python research/scripts/run_matrix.py --smoke-test
"""
import argparse
import sys
import os
import yaml

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from research.experiments.batch_runner import BatchExperimentRunner


def main():
    parser = argparse.ArgumentParser(description="Execute experiment batch matrix for FairLens AI research.")
    parser.add_argument("--config", type=str, default="research/configs/matrix_config.yaml", help="Path to matrix config")
    parser.add_argument("--smoke-test", action="store_true", help="Run a single-configuration smoke test")
    parser.add_argument("--results-dir", type=str, default="research/results", help="Directory to store outputs")

    args = parser.parse_args()

    runner = BatchExperimentRunner(config_path=args.config, results_dir=args.results_dir)

    if args.smoke_test:
        print("[*] Running Smoke Test (1 experiment configuration)...")
        results = runner.run_matrix(smoke_test=True, use_synthetic_benchmark=True)
    else:
        # Load matrix configuration
        if os.path.exists(args.config):
            with open(args.config, "r", encoding="utf-8") as f:
                cfg_data = yaml.safe_load(f)
            mat = cfg_data.get("candidate_matrix", {})
            datasets = mat.get("datasets", ["adult"])
            models = mat.get("models", ["logistic_regression"])
            mitigations = mat.get("mitigations", ["correlation_remover"])
            seeds = mat.get("seeds", [42])
        else:
            datasets = ["adult"]
            models = ["logistic_regression"]
            mitigations = ["correlation_remover"]
            seeds = [42]

        results = runner.run_matrix(
            datasets=datasets,
            models=models,
            mitigations=mitigations,
            seeds=seeds,
            use_synthetic_benchmark=True,
            smoke_test=False
        )

    failures = [r for r in results if r.get("status") == "FAILED"]
    if failures:
        print(f"[!] {len(failures)} experiment(s) failed.")
        sys.exit(1)
    else:
        print("[+] All batch experiments completed successfully.")


if __name__ == "__main__":
    main()
