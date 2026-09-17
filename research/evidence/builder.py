"""
Structured Audit Evidence Builder.
Transforms raw experiment outputs into authoritative, canonical AuditEvidence payloads
with explicit metric interpretation semantics.
"""
from typing import Dict, Any, List, Optional
import math
from .schemas import (
    AuditEvidence,
    AuditStateEvidence,
    DatasetEvidence,
    ModelEvidence,
    ObservedMetric,
    MetricComparison,
    FeatureImportanceEvidence,
    SHAPAuditEvidence,
    MetricType,
    Direction,
    SemanticInterpretation
)


def compute_direction_and_interpretation(
    metric_name: str,
    metric_type: MetricType,
    before: Optional[float],
    after: Optional[float],
    tolerance: float = 1e-4
) -> Dict[str, Any]:
    """
    Computes mathematical direction and domain-specific semantic interpretation.
    Enforces strict mathematical definitions rather than simplistic 'lower is better' assumptions.
    """
    if before is None or after is None or math.isnan(before) or math.isnan(after):
        return {
            "absolute_change": None,
            "relative_change": None,
            "direction": Direction.UNCHANGED,
            "interpretation": SemanticInterpretation.AMBIGUOUS,
            "ideal_target": 0.0,
            "semantics_rationale": "One or both metric values are undefined or NaN."
        }

    abs_change = round(after - before, 4)
    rel_change = round((after - before) / abs(before), 4) if abs(before) > 1e-6 else None

    # Determine mathematical direction
    if abs(abs_change) < tolerance:
        direction = Direction.UNCHANGED
    elif abs_change > 0:
        direction = Direction.INCREASE
    else:
        direction = Direction.DECREASE

    # Metric-specific interpretation logic
    if metric_name in ["demographic_parity_difference", "equal_opportunity_difference", "equalized_odds_difference"]:
        # Ideal parity is 0.0. Lower absolute magnitude is better.
        ideal = 0.0
        abs_before = abs(before)
        abs_after = abs(after)
        if abs(abs_after - abs_before) < tolerance:
            interpretation = SemanticInterpretation.UNCHANGED
            rationale = f"{metric_name} remained essentially unchanged (|{before:.4f}| vs |{after:.4f}|)."
        elif abs_after < abs_before:
            interpretation = SemanticInterpretation.IMPROVEMENT
            rationale = f"Absolute {metric_name} decreased from {abs_before:.4f} to {abs_after:.4f}, moving closer to ideal parity (0.0)."
        else:
            interpretation = SemanticInterpretation.DEGRADATION
            rationale = f"Absolute {metric_name} increased from {abs_before:.4f} to {abs_after:.4f}, moving further from ideal parity (0.0)."

    elif metric_name == "disparate_impact":
        # Ideal parity is 1.0. Distance to 1.0 determines fairness.
        ideal = 1.0
        dist_before = abs(before - 1.0)
        dist_after = abs(after - 1.0)
        if abs(dist_after - dist_before) < tolerance:
            interpretation = SemanticInterpretation.UNCHANGED
            rationale = f"Disparate impact distance to parity remained unchanged (|{before:.4f}-1.0| vs |{after:.4f}-1.0|)."
        elif dist_after < dist_before:
            interpretation = SemanticInterpretation.IMPROVEMENT
            rationale = f"Disparate impact moved from {before:.4f} to {after:.4f} (closer to ideal ratio 1.0)."
        else:
            interpretation = SemanticInterpretation.DEGRADATION
            rationale = f"Disparate impact moved from {before:.4f} to {after:.4f} (further from ideal ratio 1.0)."

    elif metric_type == MetricType.PERFORMANCE:
        # Standard performance metrics: higher is better (ideal: 1.0)
        ideal = 1.0
        if direction == Direction.UNCHANGED:
            interpretation = SemanticInterpretation.UNCHANGED
            rationale = f"{metric_name} remained stable ({before:.4f} vs {after:.4f})."
        elif direction == Direction.INCREASE:
            interpretation = SemanticInterpretation.IMPROVEMENT
            rationale = f"{metric_name} increased from {before:.4f} to {after:.4f}."
        else:
            interpretation = SemanticInterpretation.DEGRADATION
            rationale = f"{metric_name} decreased from {before:.4f} to {after:.4f}."

    else:
        ideal = 0.0
        interpretation = SemanticInterpretation.AMBIGUOUS
        rationale = f"No predefined domain interpretation rule for {metric_name}."

    return {
        "absolute_change": abs_change,
        "relative_change": rel_change,
        "direction": direction,
        "interpretation": interpretation,
        "ideal_target": ideal,
        "semantics_rationale": rationale
    }


def build_audit_state(
    state_name: str,
    perf_dict: Dict[str, Any],
    fair_dict: Dict[str, Any],
    shap_global: Optional[Dict[str, float]] = None,
    shap_subgroup: Optional[Dict[str, Dict[str, float]]] = None,
    shap_provenance: Optional[Dict[str, Any]] = None,
    top_k: int = 5
) -> AuditStateEvidence:
    """Build an AuditStateEvidence container for a given state (baseline or mitigated)."""
    NON_SCALAR_METADATA_KEYS = {
        "sensitive_attribute", "groups", "privileged_group", "unprivileged_group", "subgroup_statistics"
    }

    def _safe_float(val: Any) -> Optional[float]:
        if val is None:
            return None
        try:
            f = float(val)
            return None if math.isnan(f) else f
        except (ValueError, TypeError):
            return None

    fairness_metrics = {}
    for metric_name, m_data in fair_dict.items():
        if metric_name in NON_SCALAR_METADATA_KEYS:
            continue
        # Normalize metric name if needed
        norm_name = "disparate_impact" if metric_name == "disparate_impact_ratio" else metric_name

        if isinstance(m_data, dict):
            raw_val = m_data.get("value")
            is_def = bool(m_data.get("defined", m_data.get("is_defined", True)))
        else:
            raw_val = m_data
            is_def = True

        float_val = _safe_float(raw_val)
        if float_val is None:
            is_def = False

        fairness_metrics[norm_name] = ObservedMetric(
            metric_name=norm_name,
            metric_type=MetricType.FAIRNESS,
            value=round(float_val, 4) if float_val is not None else None,
            is_defined=is_def,
            details=m_data if isinstance(m_data, dict) else {}
        )

    performance_metrics = {}
    for metric_name, m_data in perf_dict.items():
        if metric_name in NON_SCALAR_METADATA_KEYS:
            continue
        if isinstance(m_data, dict):
            raw_val = m_data.get("value")
            is_def = bool(m_data.get("defined", m_data.get("is_defined", True)))
        else:
            raw_val = m_data
            is_def = True

        float_val = _safe_float(raw_val)
        if float_val is None:
            is_def = False

        performance_metrics[metric_name] = ObservedMetric(
            metric_name=metric_name,
            metric_type=MetricType.PERFORMANCE,
            value=round(float_val, 4) if float_val is not None else None,
            is_defined=is_def,
            details=m_data if isinstance(m_data, dict) else {}
        )

    shap_ev = None
    if shap_global:
        if isinstance(shap_global, list):
            sorted_features = [
                (item["feature"], float(item["importance"]))
                for item in shap_global if isinstance(item, dict) and "feature" in item
            ]
        elif isinstance(shap_global, dict):
            sorted_features = sorted(shap_global.items(), key=lambda x: x[1], reverse=True)
        else:
            sorted_features = []

        ranked = [
            FeatureImportanceEvidence(
                feature_name=feat,
                mean_abs_shap=round(val, 5),
                rank=idx + 1
            )
            for idx, (feat, val) in enumerate(sorted_features)
        ]
        top_k_names = [feat for feat, _ in sorted_features[:top_k]]

        subgroup_tops = {}
        if shap_subgroup and isinstance(shap_subgroup, dict):
            for grp, grp_data in shap_subgroup.items():
                if isinstance(grp_data, list):
                    subgroup_tops[str(grp)] = [
                        item["feature"] for item in grp_data[:top_k]
                        if isinstance(item, dict) and "feature" in item
                    ]
                elif isinstance(grp_data, dict):
                    sorted_grp = sorted(grp_data.items(), key=lambda x: x[1], reverse=True)
                    subgroup_tops[str(grp)] = [feat for feat, _ in sorted_grp[:top_k]]

        prov = shap_provenance or {}
        shap_ev = SHAPAuditEvidence(
            explainer_type=prov.get("explainer_type", "SHAPEngine"),
            n_eval_samples=prov.get("n_eval_samples", 0),
            n_background_samples=prov.get("n_background_samples", 0),
            ranked_features=ranked,
            top_k_features=top_k_names,
            subgroup_top_features=subgroup_tops
        )

    return AuditStateEvidence(
        state_name=state_name,
        fairness_metrics=fairness_metrics,
        performance_metrics=performance_metrics,
        shap_evidence=shap_ev
    )


def build_evidence_from_raw_result(
    raw_result: Dict[str, Any],
    manifest: Dict[str, Any],
    top_k: int = 5
) -> AuditEvidence:
    """
    Constructs canonical AuditEvidence from raw experiment outputs and manifest.
    Calculates explicit metric comparisons with strict semantics.
    """
    dataset_meta = manifest.get("dataset", {})
    dataset_evidence = DatasetEvidence(
        dataset_name=dataset_meta.get("name", raw_result.get("dataset_name", "unknown")),
        sensitive_column=dataset_meta.get("sensitive_column", "sensitive_attr"),
        privileged_group=dataset_meta.get("privileged_group", 1),
        unprivileged_group=dataset_meta.get("unprivileged_group", 0),
        target_column=dataset_meta.get("target_column", "target"),
        train_samples=dataset_meta.get("train_samples", 0),
        val_samples=dataset_meta.get("val_samples", 0),
        test_samples=dataset_meta.get("test_samples", 0),
        is_synthetic_benchmark=dataset_meta.get("is_synthetic_benchmark", False)
    )

    model_meta = manifest.get("model", {})
    mitigation_meta = manifest.get("mitigation", {})
    model_evidence = ModelEvidence(
        model_family=model_meta.get("family", raw_result.get("model_name", "unknown")),
        hyperparameters=model_meta.get("parameters", {}),
        random_seed=manifest.get("random_seed", raw_result.get("random_seed", 42)),
        mitigation_applied=mitigation_meta.get("name", raw_result.get("mitigation_name")),
        mitigation_strategy=mitigation_meta.get("strategy_type"),
        mitigation_parameters=mitigation_meta.get("parameters", {})
    )

    base_raw = raw_result.get("baseline_evaluation", {})
    baseline_state = build_audit_state(
        state_name="baseline",
        perf_dict=base_raw.get("performance", {}),
        fair_dict=base_raw.get("fairness", {}),
        shap_global=base_raw.get("global_shap"),
        shap_subgroup=base_raw.get("subgroup_shap"),
        shap_provenance=base_raw.get("shap_provenance"),
        top_k=top_k
    )

    mit_raw = raw_result.get("mitigated_evaluation")
    mitigated_state = None
    comparisons: List[MetricComparison] = []

    if mit_raw:
        mitigated_state = build_audit_state(
            state_name="mitigated",
            perf_dict=mit_raw.get("performance", {}),
            fair_dict=mit_raw.get("fairness", {}),
            shap_global=mit_raw.get("global_shap"),
            shap_subgroup=mit_raw.get("subgroup_shap"),
            shap_provenance=mit_raw.get("shap_provenance"),
            top_k=top_k
        )

        # Build pairwise comparisons for all fairness metrics
        for m_name, base_m in baseline_state.fairness_metrics.items():
            if m_name in mitigated_state.fairness_metrics:
                mit_m = mitigated_state.fairness_metrics[m_name]
                interp = compute_direction_and_interpretation(
                    metric_name=m_name,
                    metric_type=MetricType.FAIRNESS,
                    before=base_m.value,
                    after=mit_m.value
                )
                comparisons.append(MetricComparison(
                    metric_name=m_name,
                    metric_type=MetricType.FAIRNESS,
                    before=base_m.value,
                    after=mit_m.value,
                    absolute_change=interp["absolute_change"],
                    relative_change=interp["relative_change"],
                    direction=interp["direction"],
                    interpretation=interp["interpretation"],
                    ideal_target=interp["ideal_target"],
                    semantics_rationale=interp["semantics_rationale"]
                ))

        # Build pairwise comparisons for all performance metrics
        for m_name, base_m in baseline_state.performance_metrics.items():
            if m_name in mitigated_state.performance_metrics:
                mit_m = mitigated_state.performance_metrics[m_name]
                interp = compute_direction_and_interpretation(
                    metric_name=m_name,
                    metric_type=MetricType.PERFORMANCE,
                    before=base_m.value,
                    after=mit_m.value
                )
                comparisons.append(MetricComparison(
                    metric_name=m_name,
                    metric_type=MetricType.PERFORMANCE,
                    before=base_m.value,
                    after=mit_m.value,
                    absolute_change=interp["absolute_change"],
                    relative_change=interp["relative_change"],
                    direction=interp["direction"],
                    interpretation=interp["interpretation"],
                    ideal_target=interp["ideal_target"],
                    semantics_rationale=interp["semantics_rationale"]
                ))

    return AuditEvidence(
        experiment_id=raw_result.get("experiment_id", manifest.get("experiment_id", "exp_unknown")),
        dataset=dataset_evidence,
        model=model_evidence,
        baseline_state=baseline_state,
        mitigated_state=mitigated_state,
        metric_comparisons=comparisons
    )
