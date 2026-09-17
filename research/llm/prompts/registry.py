"""
Versioned Prompt Registry and Evidence Text Formatters for FairLens AI Research.
"""
import os
from typing import Dict, Any, Optional
from ...evidence.schemas import AuditEvidence, MetricType

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

AVAILABLE_PROMPTS = [
    "fairness_audit_v1",
    "fairness_comparison_v1",
    "shap_explanation_v1",
    "combined_audit_v1"
]


def load_prompt_template(prompt_id: str) -> str:
    """Loads prompt template string from disk."""
    if prompt_id not in AVAILABLE_PROMPTS:
        raise ValueError(f"Unknown prompt_id '{prompt_id}'. Available: {AVAILABLE_PROMPTS}")
    path = os.path.join(_CURRENT_DIR, f"{prompt_id}.txt")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def format_evidence_for_prompt(evidence: AuditEvidence, prompt_id: str) -> str:
    """
    Formats structured AuditEvidence into clear, authoritative text block
    to insert into the prompt template.
    """
    lines = []

    # Dataset & Model section
    lines.append("DATASET & MODEL CONFIGURATION:")
    lines.append(f"- Dataset: {evidence.dataset.dataset_name}")
    lines.append(f"- Protected Attribute: {evidence.dataset.sensitive_column} "
                 f"(Privileged: {evidence.dataset.privileged_group}, Unprivileged: {evidence.dataset.unprivileged_group})")
    lines.append(f"- Model Architecture: {evidence.model.model_family}")
    lines.append(f"- Random Seed: {evidence.model.random_seed}")
    if evidence.model.mitigation_applied:
        lines.append(f"- Mitigation Applied: {evidence.model.mitigation_applied} ({evidence.model.mitigation_strategy})")

    # Baseline section
    if prompt_id in ["fairness_audit_v1", "combined_audit_v1"]:
        lines.append("\nBASELINE AUDIT METRICS:")
        lines.append("Fairness:")
        for m_name, m in evidence.baseline_state.fairness_metrics.items():
            val_str = f"{m.value:.4f}" if m.value is not None else "undefined"
            lines.append(f"  * {m_name}: {val_str}")
        lines.append("Performance:")
        for m_name, m in evidence.baseline_state.performance_metrics.items():
            val_str = f"{m.value:.4f}" if m.value is not None else "undefined"
            lines.append(f"  * {m_name}: {val_str}")

    # Mitigation comparison section
    if prompt_id in ["fairness_comparison_v1", "combined_audit_v1"] and evidence.metric_comparisons:
        lines.append("\nPRE- VS POST-MITIGATION COMPARISON:")
        for comp in evidence.metric_comparisons:
            before_str = f"{comp.before:.4f}" if comp.before is not None else "N/A"
            after_str = f"{comp.after:.4f}" if comp.after is not None else "N/A"
            delta_str = f"{comp.absolute_change:+.4f}" if comp.absolute_change is not None else "N/A"
            lines.append(
                f"- Metric: {comp.metric_name} ({comp.metric_type.value})\n"
                f"    Baseline: {before_str} | Mitigated: {after_str} | Delta: {delta_str}\n"
                f"    Direction: {comp.direction.value} | Domain Evaluation: {comp.interpretation.value}\n"
                f"    Rationale: {comp.semantics_rationale}"
            )

    # SHAP section
    if prompt_id in ["shap_explanation_v1", "combined_audit_v1"]:
        active_state = evidence.mitigated_state or evidence.baseline_state
        if active_state.shap_evidence and active_state.shap_evidence.ranked_features:
            lines.append(f"\nSHAP FEATURE IMPORTANCE (Explainer: {active_state.shap_evidence.explainer_type}):")
            lines.append("Ranked features by mean absolute SHAP value:")
            for feat in active_state.shap_evidence.ranked_features[:10]:
                lines.append(f"  {feat.rank}. {feat.feature_name}: {feat.mean_abs_shap:.5f}")

    return "\n".join(lines)


def build_prompt(evidence: AuditEvidence, prompt_id: str = "combined_audit_v1") -> str:
    """Builds complete prompt by injecting formatted evidence into template."""
    template = load_prompt_template(prompt_id)
    evidence_text = format_evidence_for_prompt(evidence, prompt_id)
    return template.format(evidence_text=evidence_text)
