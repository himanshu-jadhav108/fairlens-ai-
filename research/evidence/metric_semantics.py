"""
Centralized Machine-Readable Metric Semantics Registry for FairLens AI Research.

Authoritative source of truth for:
1. Mathematical definitions and valid domain ranges
2. Parity targets and reference values
3. Directional interpretation semantics (Fairness vs Performance)
4. Standard textual aliases for natural language processing

Both evidence builders and faithfulness evaluators MUST reference this registry
to prevent semantic divergence or hard-coded ad-hoc assumptions.
"""
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum


class MetricDomainType(str, Enum):
    FAIRNESS = "fairness"
    PERFORMANCE = "performance"


class DisparityDirection(str, Enum):
    ZERO_PARITY = "zero_parity"          # Ideal value is 0.0; lower absolute magnitude = less disparity
    RATIO_PARITY = "ratio_parity"        # Ideal value is 1.0; distance to 1.0 = disparity
    NOT_APPLICABLE = "not_applicable"    # For performance metrics


@dataclass(frozen=True)
class MetricSemantics:
    """Rigorous mathematical and semantic specification for a metric."""
    canonical_name: str
    display_name: str
    domain_type: MetricDomainType
    mathematical_definition: str
    valid_range: Tuple[float, float]
    ideal_target: float
    disparity_type: DisparityDirection
    higher_is_better: Optional[bool]
    lower_is_better: Optional[bool]
    distance_to_target_applies: bool
    aliases: List[str] = field(default_factory=list)
    interpretation_rationale: str = ""

    def evaluate_change(
        self,
        before: Optional[float],
        after: Optional[float],
        tolerance: float = 1e-4
    ) -> Dict[str, Any]:
        """
        Computes exact mathematical direction and domain semantic interpretation
        according to the formalized metric definition.
        """
        if before is None or after is None:
            return {
                "absolute_change": None,
                "relative_change": None,
                "direction": "unchanged",
                "interpretation": "ambiguous",
                "ideal_target": self.ideal_target,
                "rationale": "One or both metric values are undefined."
            }

        abs_change = round(after - before, 4)
        rel_change = round((after - before) / abs(before), 4) if abs(before) > 1e-6 else None

        # Mathematical direction
        if abs(abs_change) < tolerance:
            math_dir = "unchanged"
        elif abs_change > 0:
            math_dir = "increase"
        else:
            math_dir = "decrease"

        # Domain semantic interpretation
        if self.disparity_type == DisparityDirection.ZERO_PARITY:
            # Ideal is 0.0. Closer to 0 is an improvement.
            abs_before = abs(before)
            abs_after = abs(after)
            if abs(abs_after - abs_before) < tolerance:
                interp = "unchanged"
                rationale = f"{self.display_name} disparity remained stable (|{before:.4f}| vs |{after:.4f}|)."
            elif abs_after < abs_before:
                interp = "improvement"
                rationale = (
                    f"Absolute {self.display_name} decreased from {abs_before:.4f} to {abs_after:.4f}, "
                    f"moving closer to ideal parity (0.0)."
                )
            else:
                interp = "degradation"
                rationale = (
                    f"Absolute {self.display_name} increased from {abs_before:.4f} to {abs_after:.4f}, "
                    f"moving further from ideal parity (0.0)."
                )

        elif self.disparity_type == DisparityDirection.RATIO_PARITY:
            # Ideal is 1.0. Distance to 1.0 determines equity.
            dist_before = abs(before - 1.0)
            dist_after = abs(after - 1.0)
            if abs(dist_after - dist_before) < tolerance:
                interp = "unchanged"
                rationale = f"{self.display_name} distance to parity (1.0) remained unchanged."
            elif dist_after < dist_before:
                interp = "improvement"
                rationale = (
                    f"{self.display_name} moved from {before:.4f} to {after:.4f}, "
                    f"closer to ideal parity ratio (1.0)."
                )
            else:
                interp = "degradation"
                rationale = (
                    f"{self.display_name} moved from {before:.4f} to {after:.4f}, "
                    f"further from ideal parity ratio (1.0)."
                )

        elif self.domain_type == MetricDomainType.PERFORMANCE:
            if math_dir == "unchanged":
                interp = "unchanged"
                rationale = f"{self.display_name} remained stable ({before:.4f} vs {after:.4f})."
            elif math_dir == "increase":
                interp = "improvement"
                rationale = f"{self.display_name} increased from {before:.4f} to {after:.4f}."
            else:
                interp = "degradation"
                rationale = f"{self.display_name} decreased from {before:.4f} to {after:.4f}."
        else:
            interp = "ambiguous"
            rationale = f"No defined interpretation rule for {self.canonical_name}."

        return {
            "absolute_change": abs_change,
            "relative_change": rel_change,
            "direction": math_dir,
            "interpretation": interp,
            "ideal_target": self.ideal_target,
            "rationale": rationale
        }


# Canonical Registry Definitions
METRIC_REGISTRY: Dict[str, MetricSemantics] = {
    "demographic_parity_difference": MetricSemantics(
        canonical_name="demographic_parity_difference",
        display_name="Demographic Parity Difference",
        domain_type=MetricDomainType.FAIRNESS,
        mathematical_definition="max(P(Y_hat=1|A=a)) - min(P(Y_hat=1|A=a)) across demographic groups",
        valid_range=(0.0, 1.0),
        ideal_target=0.0,
        disparity_type=DisparityDirection.ZERO_PARITY,
        higher_is_better=False,
        lower_is_better=True,
        distance_to_target_applies=True,
        aliases=[
            "demographic parity difference", "dpd", "demographic parity", "statistical parity difference"
        ],
        interpretation_rationale="Zero indicates equal positive selection rates across groups. Values closer to 0 indicate greater fairness."
    ),
    "equalized_odds_difference": MetricSemantics(
        canonical_name="equalized_odds_difference",
        display_name="Equalized Odds Difference",
        domain_type=MetricDomainType.FAIRNESS,
        mathematical_definition="max(|FPR_a - FPR_b|, |TPR_a - TPR_b|) across demographic groups",
        valid_range=(0.0, 1.0),
        ideal_target=0.0,
        disparity_type=DisparityDirection.ZERO_PARITY,
        higher_is_better=False,
        lower_is_better=True,
        distance_to_target_applies=True,
        aliases=[
            "equalized odds difference", "equalized odds", "eod"
        ],
        interpretation_rationale="Zero indicates identical TPR and FPR across groups. Values closer to 0 indicate greater fairness."
    ),
    "equal_opportunity_difference": MetricSemantics(
        canonical_name="equal_opportunity_difference",
        display_name="Equal Opportunity Difference",
        domain_type=MetricDomainType.FAIRNESS,
        mathematical_definition="|TPR_privileged - TPR_unprivileged|",
        valid_range=(0.0, 1.0),
        ideal_target=0.0,
        disparity_type=DisparityDirection.ZERO_PARITY,
        higher_is_better=False,
        lower_is_better=True,
        distance_to_target_applies=True,
        aliases=[
            "equal opportunity difference", "equal opportunity", "eodiff"
        ],
        interpretation_rationale="Zero indicates equal True Positive Rates across groups. Values closer to 0 indicate greater fairness."
    ),
    "disparate_impact": MetricSemantics(
        canonical_name="disparate_impact",
        display_name="Disparate Impact",
        domain_type=MetricDomainType.FAIRNESS,
        mathematical_definition="P(Y_hat=1|A=unprivileged) / P(Y_hat=1|A=privileged)",
        valid_range=(0.0, 10.0),
        ideal_target=1.0,
        disparity_type=DisparityDirection.RATIO_PARITY,
        higher_is_better=None,  # Distance to 1.0 determines equity; neither higher nor lower is universally better
        lower_is_better=None,
        distance_to_target_applies=True,
        aliases=[
            "disparate impact", "disparate impact ratio", "adverse impact ratio", "disparate_impact_ratio"
        ],
        interpretation_rationale="A ratio of 1.0 indicates exact parity. Moving closer to 1.0 indicates improvement; moving further indicates worsening."
    ),
    "false_positive_rate_difference": MetricSemantics(
        canonical_name="false_positive_rate_difference",
        display_name="False Positive Rate Difference",
        domain_type=MetricDomainType.FAIRNESS,
        mathematical_definition="|FPR_privileged - FPR_unprivileged| across demographic groups",
        valid_range=(0.0, 1.0),
        ideal_target=0.0,
        disparity_type=DisparityDirection.ZERO_PARITY,
        higher_is_better=False,
        lower_is_better=True,
        distance_to_target_applies=True,
        aliases=[
            "false positive rate difference", "fpr difference", "fprd", "predictive equality difference"
        ],
        interpretation_rationale="Zero indicates identical False Positive Rates across groups. Values closer to 0 indicate greater fairness."
    ),
    "false_negative_rate_difference": MetricSemantics(
        canonical_name="false_negative_rate_difference",
        display_name="False Negative Rate Difference",
        domain_type=MetricDomainType.FAIRNESS,
        mathematical_definition="|FNR_privileged - FNR_unprivileged| across demographic groups",
        valid_range=(0.0, 1.0),
        ideal_target=0.0,
        disparity_type=DisparityDirection.ZERO_PARITY,
        higher_is_better=False,
        lower_is_better=True,
        distance_to_target_applies=True,
        aliases=[
            "false negative rate difference", "fnr difference", "fnrd"
        ],
        interpretation_rationale="Zero indicates identical False Negative Rates across groups. Values closer to 0 indicate greater fairness."
    ),
    "accuracy": MetricSemantics(
        canonical_name="accuracy",
        display_name="Accuracy",
        domain_type=MetricDomainType.PERFORMANCE,
        mathematical_definition="Fraction of correct predictions: (TP + TN) / (P + N)",
        valid_range=(0.0, 1.0),
        ideal_target=1.0,
        disparity_type=DisparityDirection.NOT_APPLICABLE,
        higher_is_better=True,
        lower_is_better=False,
        distance_to_target_applies=False,
        aliases=[
            "accuracy", "overall accuracy", "classification accuracy"
        ],
        interpretation_rationale="Standard predictive performance metric. Higher is better."
    ),
    "f1_score": MetricSemantics(
        canonical_name="f1_score",
        display_name="F1 Score",
        domain_type=MetricDomainType.PERFORMANCE,
        mathematical_definition="Harmonic mean of precision and recall: 2 * (Prec * Rec) / (Prec + Rec)",
        valid_range=(0.0, 1.0),
        ideal_target=1.0,
        disparity_type=DisparityDirection.NOT_APPLICABLE,
        higher_is_better=True,
        lower_is_better=False,
        distance_to_target_applies=False,
        aliases=[
            "f1 score", "f1", "f-measure"
        ],
        interpretation_rationale="Balances precision and recall. Higher is better."
    ),
    "precision": MetricSemantics(
        canonical_name="precision",
        display_name="Precision",
        domain_type=MetricDomainType.PERFORMANCE,
        mathematical_definition="Positive predictive value: TP / (TP + FP)",
        valid_range=(0.0, 1.0),
        ideal_target=1.0,
        disparity_type=DisparityDirection.NOT_APPLICABLE,
        higher_is_better=True,
        lower_is_better=False,
        distance_to_target_applies=False,
        aliases=["precision", "positive predictive value"],
        interpretation_rationale="Higher is better."
    ),
    "recall": MetricSemantics(
        canonical_name="recall",
        display_name="Recall",
        domain_type=MetricDomainType.PERFORMANCE,
        mathematical_definition="True positive rate: TP / (TP + FN)",
        valid_range=(0.0, 1.0),
        ideal_target=1.0,
        disparity_type=DisparityDirection.NOT_APPLICABLE,
        higher_is_better=True,
        lower_is_better=False,
        distance_to_target_applies=False,
        aliases=["recall", "true positive rate", "sensitivity"],
        interpretation_rationale="Higher is better."
    ),
    "roc_auc": MetricSemantics(
        canonical_name="roc_auc",
        display_name="ROC-AUC",
        domain_type=MetricDomainType.PERFORMANCE,
        mathematical_definition="Area under the receiver operating characteristic curve",
        valid_range=(0.0, 1.0),
        ideal_target=1.0,
        disparity_type=DisparityDirection.NOT_APPLICABLE,
        higher_is_better=True,
        lower_is_better=False,
        distance_to_target_applies=False,
        aliases=["roc auc", "roc-auc", "auc"],
        interpretation_rationale="Threshold-independent classification capability. Higher is better."
    )
}


def get_metric_semantics(metric_name: str) -> Optional[MetricSemantics]:
    """Retrieves authoritative semantics for a metric by canonical name or alias."""
    name_clean = metric_name.lower().strip()
    if name_clean in METRIC_REGISTRY:
        return METRIC_REGISTRY[name_clean]
    # Check aliases
    for semantics in METRIC_REGISTRY.values():
        if name_clean in [a.lower() for a in semantics.aliases]:
            return semantics
    return None
