"""
LLM Explanation and Faithfulness Experiment Runner.
Executes the full pipeline:
Dataset -> ML Model -> Fairness Audit -> Mitigation -> SHAP Evidence ->
Structured Audit Evidence -> LLM Explanation -> Faithfulness Evaluation ->
Results & Manifest Logging.

Supports:
1. --smoke-test: 100% deterministic offline verification without API key.
2. --provider gemini: Real experiment via Google Generative AI using GEMINI_API_KEY.
3. Template Baseline: Evaluates deterministic control baseline alongside LLM.
"""
import os
import sys

# Ensure workspace root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import json
import argparse
import datetime
from typing import Dict, Any, Optional

from research.experiments.experiment_config import ExperimentConfig
from research.experiments.runner import run_single_experiment
from research.evidence.builder import build_evidence_from_raw_result
from research.baselines.template_explainer import TemplateExplainer
from research.llm.providers import get_llm_provider
from research.llm.generator import ExplanationGenerator
from research.llm.config import get_default_generation_config
from research.faithfulness.evaluator import FaithfulnessEvaluator
from research.faithfulness.coverage import EvidenceCoverageEvaluator


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run LLM Explanation and Faithfulness Experiment for ML Fairness Audits"
    )
    parser.add_argument("--dataset", type=str, default="adult", choices=["adult", "compas", "german"],
                        help="Audited dataset name")
    parser.add_argument("--model", type=str, default="logistic_regression",
                        choices=["logistic_regression", "random_forest", "xgboost"],
                        help="Predictive model family")
    parser.add_argument("--mitigation", type=str, default="correlation_remover",
                        choices=["correlation_remover", "exponentiated_gradient", "threshold_optimizer"],
                        help="Fairness mitigation algorithm")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    parser.add_argument("--provider", type=str, default="mock", choices=["mock", "gemini"],
                        help="LLM provider: 'mock' for offline testing, 'gemini' for real experiments")
    parser.add_argument("--prompt", type=str, default="combined_audit_v1",
                        choices=["combined_audit_v1", "fairness_audit_v1", "fairness_comparison_v1", "shap_explanation_v1"],
                        help="Versioned prompt template ID")
    parser.add_argument("--temperature", type=float, default=0.2, help="LLM sampling temperature")
    parser.add_argument("--output-dir", type=str, default="research/results", help="Root results directory")
    parser.add_argument("--smoke-test", action="store_true", help="Run deterministic offline smoke test")
    parser.add_argument("--use-synthetic", action="store_true", help="Use fast synthetic benchmark dataset")
    return parser.parse_args()


def run_experiment(
    dataset_name: str = "adult",
    model_name: str = "logistic_regression",
    mitigation_name: str = "correlation_remover",
    seed: int = 42,
    provider_name: str = "mock",
    prompt_id: str = "combined_audit_v1",
    temperature: float = 0.2,
    output_dir: str = "research/results",
    use_synthetic: bool = True,
    is_smoke_test: bool = False
) -> Dict[str, Any]:
    """
    Executes the end-to-end fairness audit, explanation generation, and faithfulness evaluation.
    Isolates smoke test outputs into a dedicated subdirectory with explicit software validation tags.
    """
    # Isolate smoke test outputs (Section 20)
    effective_output_dir = os.path.join(output_dir, "smoke") if is_smoke_test else output_dir
    execution_mode = "SOFTWARE_VALIDATION_ONLY" if is_smoke_test else "EMPIRICAL_RESEARCH_RUN"

    print("=" * 70)
    print("FAIRLENS AI RESEARCH: LLM EXPLANATION FAITHFULNESS PIPELINE")
    print(f"Execution Mode: {execution_mode}")
    print(f"Output Path:    {effective_output_dir}")
    print(f"Dataset:        {dataset_name} (Synthetic: {use_synthetic})")
    print(f"Model:          {model_name}")
    print(f"Mitigation:     {mitigation_name}")
    print(f"Seed:           {seed}")
    print(f"LLM:            {provider_name} | Prompt: {prompt_id} | Temp: {temperature}")
    print("=" * 70)

    # 1. Run ML Fairness Audit & Mitigation
    print("\n[Step 1/6] Running ML training, fairness auditing, and SHAP attribution...")
    config = ExperimentConfig(
        dataset_name=dataset_name,
        model_name=model_name,
        mitigation_name=mitigation_name,
        seed=seed,
        use_synthetic_benchmark=use_synthetic,
        n_eval_samples=50,
        n_background_samples=25
    )
    raw_result, manifest = run_single_experiment(
        config=config,
        results_dir=effective_output_dir,
        save_artifacts=True
    )
    manifest["execution_mode"] = execution_mode
    print(f"-> Audit completed. Experiment ID: {config.experiment_id}")

    # 2. Build Authoritative Structured Audit Evidence
    print("\n[Step 2/6] Constructing canonical Structured Audit Evidence...")
    evidence = build_evidence_from_raw_result(raw_result, manifest)
    evidence_hash = evidence.compute_evidence_hash()
    print(f"-> Evidence constructed. Canonical Hash: {evidence_hash[:16]}...")
    print(f"   Metric comparisons recorded: {len(evidence.metric_comparisons)}")

    # 3. Generate Control Baseline Explanation (Template Explainer)
    print("\n[Step 3/6] Generating deterministic Template Baseline explanation...")
    template_explainer = TemplateExplainer(top_k_features=5)
    template_text = template_explainer.generate_explanation(evidence)
    print(f"-> Template explanation generated ({len(template_text.split())} words).")

    # 4. Generate LLM Explanation
    print(f"\n[Step 4/6] Generating explanation via LLM Provider ('{provider_name}')...")
    provider = get_llm_provider(provider_name)
    gen_config = get_default_generation_config(temperature=temperature, seed=seed)
    generator = ExplanationGenerator(provider=provider, config=gen_config)
    explanation_record = generator.generate_explanation(
        evidence=evidence,
        prompt_id=prompt_id,
        audit_state="comparison",
        output_dir=os.path.join(effective_output_dir, "raw")
    )
    print(f"-> LLM explanation received ({len(explanation_record.output_text.split())} words).")

    # 5. Evaluate Faithfulness
    print("\n[Step 5/6] Performing deterministic Faithfulness Evaluation...")
    evaluator = FaithfulnessEvaluator(
        absolute_tolerance=0.015,
        relative_tolerance=0.05,
        top_k_features=5
    )
    coverage_evaluator = EvidenceCoverageEvaluator(top_k_features=5)

    # Evaluate LLM explanation
    llm_report = evaluator.evaluate(
        evidence=evidence,
        explanation_text=explanation_record.output_text,
        explanation_source=f"{provider_name}_{explanation_record.llm_model}",
        prompt_id=prompt_id,
        save_records=True,
        output_claims_dir=os.path.join(effective_output_dir, "claims"),
        output_summaries_dir=os.path.join(effective_output_dir, "summaries")
    )
    llm_coverage = coverage_evaluator.evaluate(
        evidence=evidence,
        text=explanation_record.output_text,
        explanation_source=f"{provider_name}_{explanation_record.llm_model}"
    )

    # Evaluate Template baseline explanation (as experimental control)
    template_report = evaluator.evaluate(
        evidence=evidence,
        explanation_text=template_text,
        explanation_source="template_baseline",
        prompt_id="deterministic_template",
        save_records=True,
        output_claims_dir=os.path.join(effective_output_dir, "claims"),
        output_summaries_dir=os.path.join(effective_output_dir, "summaries")
    )
    template_coverage = coverage_evaluator.evaluate(
        evidence=evidence,
        text=template_text,
        explanation_source="template_baseline"
    )

    # 6. Print Faithfulness and Coverage Summary
    print("\n[Step 6/6] Faithfulness Evaluation Complete!")
    print("-" * 75)
    print(f"{'Metric':<35} | {'Template Baseline':<17} | {'LLM (' + provider_name + ')':<17}")
    print("-" * 75)
    print(f"{'Numerical Faithfulness':<35} | {template_report.numerical_faithfulness * 100:>15.1f}% | {llm_report.numerical_faithfulness * 100:>15.1f}%")
    print(f"{'Directional Faithfulness':<35} | {template_report.directional_faithfulness * 100:>15.1f}% | {llm_report.directional_faithfulness * 100:>15.1f}%")
    print(f"{'Attribution Faithfulness':<35} | {template_report.attribution_faithfulness * 100:>15.1f}% | {llm_report.attribution_faithfulness * 100:>15.1f}%")
    print(f"{'Unsupported Claim Rate':<35} | {template_report.unsupported_claim_rate * 100:>15.1f}% | {llm_report.unsupported_claim_rate * 100:>15.1f}%")
    print(f"{'Total Extracted Claims':<35} | {template_report.total_claims_count:>16} | {llm_report.total_claims_count:>16}")
    print(f"{'[Secondary] Evidence Coverage':<35} | {template_coverage.overall_coverage_rate * 100:>15.1f}% | {llm_coverage.overall_coverage_rate * 100:>15.1f}%")
    print("-" * 75)

    return {
        "experiment_id": config.experiment_id,
        "evidence_hash": evidence_hash,
        "execution_mode": execution_mode,
        "llm_report": llm_report.to_dict(),
        "template_report": template_report.to_dict(),
        "llm_coverage": llm_coverage.to_dict(),
        "template_coverage": template_coverage.to_dict()
    }


def main():
    args = parse_args()
    if args.smoke_test:
        print("[SMOKE TEST MODE] Running fully deterministic pipeline with mock provider...")
        res = run_experiment(
            dataset_name=args.dataset,
            model_name=args.model,
            mitigation_name=args.mitigation,
            seed=args.seed,
            provider_name="mock",
            prompt_id=args.prompt,
            temperature=args.temperature,
            output_dir=args.output_dir,
            use_synthetic=True,
            is_smoke_test=True
        )
        print("\n[SUCCESS] Smoke test completed cleanly! Pipeline verified.")
        sys.exit(0)
    else:
        res = run_experiment(
            dataset_name=args.dataset,
            model_name=args.model,
            mitigation_name=args.mitigation,
            seed=args.seed,
            provider_name=args.provider,
            prompt_id=args.prompt,
            temperature=args.temperature,
            output_dir=args.output_dir,
            use_synthetic=args.use_synthetic,
            is_smoke_test=False
        )
        print("\n[SUCCESS] Experiment completed.")


if __name__ == "__main__":
    main()

