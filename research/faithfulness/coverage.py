"""
Evidence Coverage and Omission Evaluator.
Computes orthogonal secondary metrics evaluating how much of the canonical
audit evidence was communicated in the generated explanation.

CRITICAL METHODOLOGICAL DISTINCTION (Section 19):
- Faithfulness measures factual veracity: are the statements made supported by evidence?
- Coverage measures communicative completeness: how much relevant evidence was reported?
Coverage MUST NEVER penalize or dilute the primary Faithfulness score.
An explanation that mentions only one metric with 100% precision is completely faithful,
even if its evidence coverage is low.
"""
import re
from typing import Dict, Any, List, Set, Optional
from dataclasses import dataclass, asdict

from ..evidence.schemas import AuditEvidence
from ..evidence.metric_semantics import METRIC_REGISTRY


@dataclass
class EvidenceCoverageReport:
    """Secondary evaluation report for evidence coverage and omission."""
    experiment_id: str
    explanation_source: str
    fairness_metrics_total: List[str]
    fairness_metrics_covered: List[str]
    fairness_coverage_rate: float
    performance_metrics_total: List[str]
    performance_metrics_covered: List[str]
    performance_coverage_rate: float
    top_k_features_total: List[str]
    top_k_features_covered: List[str]
    feature_coverage_rate: float
    overall_coverage_rate: float
    methodological_note: str = (
        "Evidence Coverage is an orthogonal secondary metric measuring informational breadth. "
        "It does not affect or dilute primary faithfulness metrics."
    )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class EvidenceCoverageEvaluator:
    """
    Evaluates evidence coverage across fairness metrics, performance metrics,
    and top-k SHAP feature attributions.
    """

    def __init__(self, top_k_features: int = 5):
        self.top_k_features = top_k_features

    def evaluate(
        self,
        evidence: AuditEvidence,
        text: str,
        explanation_source: str = "llm"
    ) -> EvidenceCoverageReport:
        text_lower = text.lower()

        # 1. Fairness Metrics Coverage
        fairness_total = list(evidence.baseline_state.fairness_metrics.keys())
        fairness_covered = []
        for metric_name in fairness_total:
            sem = METRIC_REGISTRY.get(metric_name)
            aliases = sem.aliases if sem else [metric_name]
            for alias in aliases:
                if re.search(rf"\b{re.escape(alias.lower())}\b", text_lower):
                    fairness_covered.append(metric_name)
                    break
        fair_cov_rate = (len(fairness_covered) / len(fairness_total)) if fairness_total else 1.0

        # 2. Performance Metrics Coverage
        perf_total = list(evidence.baseline_state.performance_metrics.keys())
        perf_covered = []
        for metric_name in perf_total:
            sem = METRIC_REGISTRY.get(metric_name)
            aliases = sem.aliases if sem else [metric_name]
            for alias in aliases:
                if re.search(rf"\b{re.escape(alias.lower())}\b", text_lower):
                    perf_covered.append(metric_name)
                    break
        perf_cov_rate = (len(perf_covered) / len(perf_total)) if perf_total else 1.0

        # 3. Top-k Feature Attributions Coverage
        active_state = evidence.mitigated_state or evidence.baseline_state
        feat_total = []
        feat_covered = []
        if active_state.shap_evidence and active_state.shap_evidence.top_k_features:
            feat_total = active_state.shap_evidence.top_k_features[:self.top_k_features]
            for feat in feat_total:
                if re.search(rf"\b{re.escape(feat.lower())}\b", text_lower):
                    feat_covered.append(feat)
        feat_cov_rate = (len(feat_covered) / len(feat_total)) if feat_total else 1.0

        # 4. Overall Weighted Coverage (40% Fairness, 30% Performance, 30% Features)
        overall = round(
            0.4 * fair_cov_rate + 0.3 * perf_cov_rate + 0.3 * feat_cov_rate,
            4
        )

        return EvidenceCoverageReport(
            experiment_id=evidence.experiment_id,
            explanation_source=explanation_source,
            fairness_metrics_total=fairness_total,
            fairness_metrics_covered=fairness_covered,
            fairness_coverage_rate=round(fair_cov_rate, 4),
            performance_metrics_total=perf_total,
            performance_metrics_covered=perf_covered,
            performance_coverage_rate=round(perf_cov_rate, 4),
            top_k_features_total=feat_total,
            top_k_features_covered=feat_covered,
            feature_coverage_rate=round(feat_cov_rate, 4),
            overall_coverage_rate=overall
        )
