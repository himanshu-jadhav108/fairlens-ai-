"""
Deterministic Template Explainer Baseline for FairLens AI Research.

Generates rule-based, deterministic natural-language explanations directly
from structured audit evidence. Serves as the experimental control baseline
against LLM-generated explanations.
"""
from typing import Optional
from ..evidence.schemas import AuditEvidence, Direction, SemanticInterpretation


class TemplateExplainer:
    """
    Deterministic rule-based baseline explainer.
    Guaranteed to produce 100% faithful explanations matching authoritative numbers and directions.
    """

    def __init__(self, top_k_features: int = 5):
        self.top_k_features = top_k_features

    def generate_explanation(self, evidence: AuditEvidence) -> str:
        """Generates a complete structured audit explanation from evidence."""
        lines = []

        # 1. Dataset & Model Context
        lines.append(f"# Fairness Audit Report for {evidence.dataset.dataset_name.upper()}")
        lines.append(
            f"The audit evaluates a {evidence.model.model_family} model trained on "
            f"{evidence.dataset.train_samples} samples and evaluated on {evidence.dataset.test_samples} test samples. "
            f"The protected attribute audited is '{evidence.dataset.sensitive_column}'."
        )

        # 2. Baseline Audit Findings
        lines.append("\n## Baseline Audit Findings")
        base_dpd = evidence.baseline_state.fairness_metrics.get("demographic_parity_difference")
        base_eod = evidence.baseline_state.fairness_metrics.get("equalized_odds_difference")
        base_di = evidence.baseline_state.fairness_metrics.get("disparate_impact")
        base_acc = evidence.baseline_state.performance_metrics.get("accuracy")
        base_f1 = evidence.baseline_state.performance_metrics.get("f1_score")

        if base_dpd and base_dpd.value is not None:
            lines.append(f"- Baseline Demographic Parity Difference: {base_dpd.value:.4f}")
        if base_eod and base_eod.value is not None:
            lines.append(f"- Baseline Equalized Odds Difference: {base_eod.value:.4f}")
        if base_di and base_di.value is not None:
            lines.append(f"- Baseline Disparate Impact: {base_di.value:.4f}")
        if base_acc and base_acc.value is not None:
            lines.append(f"- Baseline Accuracy: {base_acc.value:.4f}")
        if base_f1 and base_f1.value is not None:
            lines.append(f"- Baseline F1 Score: {base_f1.value:.4f}")

        # 3. Mitigation Comparison (if applicable)
        if evidence.mitigated_state and evidence.metric_comparisons:
            lines.append(f"\n## Mitigation Impact: {evidence.model.mitigation_applied}")
            for comp in evidence.metric_comparisons:
                m_name = comp.metric_name.replace("_", " ").title()
                if comp.before is not None and comp.after is not None:
                    delta_str = f"{comp.absolute_change:+.4f}" if comp.absolute_change is not None else "N/A"
                    lines.append(
                        f"- {m_name}: changed from {comp.before:.4f} to {comp.after:.4f} "
                        f"(absolute change: {delta_str}, direction: {comp.direction.value}, "
                        f"evaluation: {comp.interpretation.value})."
                    )

        # 4. Feature Attribution (SHAP)
        active_state = evidence.mitigated_state or evidence.baseline_state
        if active_state.shap_evidence and active_state.shap_evidence.ranked_features:
            lines.append("\n## Feature Attribution Analysis")
            lines.append("The top influential features ranked by mean absolute SHAP value are:")
            for feat in active_state.shap_evidence.ranked_features[:self.top_k_features]:
                lines.append(f"  {feat.rank}. {feat.feature_name} (mean |SHAP|: {feat.mean_abs_shap:.5f})")

        return "\n".join(lines)
