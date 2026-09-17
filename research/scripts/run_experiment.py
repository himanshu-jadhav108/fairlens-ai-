#!/usr/bin/env python3
"""
CLI entrypoint to execute a single FairLens AI research experiment.
Usage:
    python research/scripts/run_experiment.py --dataset adult --model logistic_regression --mitigation correlation_remover --seed 42 --smoke-test
"""
import argparse
import sys
import os

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from research.experiments.experiment_config import ExperimentConfig
from research.experiments.runner import run_single_experiment


def main():
    parser = argparse.ArgumentParser(description="Run a single FairLens AI LLM faithfulness research experiment (fairness audit + explanation generation + evaluation).")
    parser.add_argument("--dataset", type=str, default="adult", help="Dataset name (adult, compas, german)")
    parser.add_argument("--model", type=str, default="logistic_regression", help="Model family (logistic_regression, random_forest, xgboost)")
    parser.add_argument("--mitigation", type=str, default="correlation_remover", help="Mitigation method (correlation_remover, exponentiated_gradient, threshold_optimizer)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    parser.add_argument("--smoke-test", action="store_true", help="Run in smoke-test mode with synthetic benchmark")
    parser.add_argument("--use-real-data", action="store_true", help="Attempt to load real dataset if available")
    parser.add_argument("--data-path", type=str, default=None, help="Optional local path to real dataset CSV")
    parser.add_argument("--results-dir", type=str, default="research/results", help="Directory to store outputs")

    args = parser.parse_args()

    use_synthetic = not args.use_real_data

    print(f"[*] Launching Experiment:")
    print(f"    Dataset:        {args.dataset} (Synthetic benchmark: {use_synthetic})")
    print(f"    Model:          {args.model}")
    print(f"    Mitigation:     {args.mitigation}")
    print(f"    Seed:           {args.seed}")

    config = ExperimentConfig(
        dataset_name=args.dataset,
        model_name=args.model,
        mitigation_name=args.mitigation,
        seed=args.seed,
        use_synthetic_benchmark=use_synthetic,
        local_dataset_path=args.data_path
    )

    try:
        raw_res, manifest = run_single_experiment(
            config=config,
            results_dir=args.results_dir,
            save_artifacts=True
        )
        print("\n[+] Experiment Succeeded!")
        print(f"    Experiment ID: {raw_res['experiment_id']}")
        print(f"    Manifest File: {args.results_dir}/manifests/{raw_res['experiment_id']}.json")
        
        base_acc = raw_res["baseline_evaluation"]["performance"]["accuracy"]["value"]
        mit_acc = raw_res["mitigated_evaluation"]["performance"]["accuracy"]["value"]
        base_dpd = raw_res["baseline_evaluation"]["fairness"]["demographic_parity_difference"]["value"]
        mit_dpd = raw_res["mitigated_evaluation"]["fairness"]["demographic_parity_difference"]["value"]
        cos_sim = raw_res["attribution_comparison"].get("cosine_similarity")
        
        print("\n--- Key Trade-Off Results ---")
        print(f"    Baseline Accuracy:     {base_acc:.4f} | Mitigated Accuracy: {mit_acc:.4f}")
        print(f"    Baseline DPD:          {base_dpd} | Mitigated DPD:      {mit_dpd}")
        print(f"    Attribution Cosine Sim:{cos_sim}")
        
    except Exception as e:
        print(f"\n[!] Experiment Failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
