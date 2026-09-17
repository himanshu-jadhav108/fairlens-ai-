"""
Batch Experiment Runner for FairLens AI Research.
Executes configured subsets or matrices of experiments while guaranteeing full manifest logging.
NOTE: Does NOT automatically execute the full 135+ candidate matrix unless explicitly invoked.
"""
import os
import sys
from typing import List, Dict, Any, Optional
import yaml

from .experiment_config import ExperimentConfig
from .runner import run_single_experiment


class BatchExperimentRunner:
    """Orchestrates sequential execution of configured research experiments."""

    def __init__(
        self,
        config_path: str = "research/configs/default_config.yaml",
        results_dir: str = "research/results"
    ):
        self.config_path = config_path
        self.results_dir = results_dir

    def run_matrix(
        self,
        datasets: Optional[List[str]] = None,
        models: Optional[List[str]] = None,
        mitigations: Optional[List[str]] = None,
        seeds: Optional[List[int]] = None,
        use_synthetic_benchmark: bool = True,
        smoke_test: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Executes an experiment matrix.
        If smoke_test is True, runs a single representative experiment to verify pipeline health.
        """
        if smoke_test:
            target_datasets = ["adult"]
            target_models = ["logistic_regression"]
            target_mitigations = ["correlation_remover"]
            target_seeds = [42]
        else:
            target_datasets = datasets or ["adult"]
            target_models = models or ["logistic_regression"]
            target_mitigations = mitigations or ["correlation_remover"]
            target_seeds = seeds or [42]

        total_experiments = len(target_datasets) * len(target_models) * len(target_mitigations) * len(target_seeds)
        print(f"[*] Starting Batch Execution: {total_experiments} experiment(s) queued.")
        
        results = []
        for d in target_datasets:
            for m in target_models:
                for mit in target_mitigations:
                    for s in target_seeds:
                        print(f" -> Running: dataset={d}, model={m}, mitigation={mit}, seed={s}")
                        cfg = ExperimentConfig(
                            dataset_name=d,
                            model_name=m,
                            mitigation_name=mit,
                            seed=s,
                            use_synthetic_benchmark=use_synthetic_benchmark
                        )
                        try:
                            raw_res, manifest = run_single_experiment(
                                config=cfg,
                                results_dir=self.results_dir,
                                save_artifacts=True
                            )
                            results.append({
                                "experiment_id": cfg.experiment_id,
                                "status": "SUCCESS",
                                "dataset": d,
                                "model": m,
                                "mitigation": mit,
                                "seed": s,
                                "manifest_file": f"manifests/{cfg.experiment_id}.json"
                            })
                        except Exception as e:
                            print(f" [!] Experiment failed ({d}, {m}, {mit}, seed={s}): {e}")
                            results.append({
                                "experiment_id": cfg.experiment_id,
                                "status": "FAILED",
                                "error": str(e),
                                "dataset": d,
                                "model": m,
                                "mitigation": mit,
                                "seed": s
                            })

        success_count = sum(1 for r in results if r.get("status") == "SUCCESS")
        print(f"[*] Batch Execution Completed: {success_count}/{len(results)} successful.")
        return results
