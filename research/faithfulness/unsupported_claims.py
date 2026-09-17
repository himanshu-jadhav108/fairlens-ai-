"""
Unsupported Claims and Causal Assertion Detector.
Identifies:
1. Unevidenced causal assertions (correlation != causation)
2. Absolute fairness declarations ("completely fair")
3. Overgeneralization claims ("fair for everyone")
4. Certainty claims ("guarantees fairness")
5. Comparative optimality claims ("best mitigation algorithm")
6. Unsupported performance claims (claiming performance improved when evidence shows degradation)
7. Sociotechnical assertions requiring human annotation (UNDETERMINABLE)
"""
import re
from typing import List, Dict, Any
from .taxonomy import ClaimType, ClaimClassification, ExtractedClaim, split_into_sentences
from ..evidence.schemas import AuditEvidence, Direction, SemanticInterpretation

CAUSAL_PATTERNS = [
    r"(?:directly\s+)?caused\s+(?:the\s+)?(?:model\s+to\s+[a-z]+|disparity|bias|discrimination|lower\s+rates|outcomes|improvement)",
    r"(?:is|was)\s+the\s+direct\s+cause\s+of",
    r"proves\s+(?:systemic\s+)?discriminatory\s+intent",
    r"leads\s+directly\s+to\s+discriminatory\s+outcomes",
    r"because\s+of\s+(?:their|the\s+applicant[']?s?)\s+(?:age|race|sex|gender),?\s+the\s+model\s+(?:rejected|discriminated)",
    r"(?:removing|mitigating)\s+[a-zA-Z0-9_]+\s+caused\s+the\s+fairness"
]

ABSOLUTE_FAIRNESS_PATTERNS = [
    r"(?:is|was|became)\s+completely\s+fair",
    r"(?:is|was|became)\s+entirely\s+unbiased",
    r"(?:guarantees|ensures)\s+perfect\s+fairness",
    r"eliminates\s+all\s+(?:possible\s+)?bias",
    r"free\s+of\s+(?:all\s+)?bias",
    r"achieved\s+complete\s+parity"
]

OVERGENERALIZATION_PATTERNS = [
    r"fair\s+for\s+(?:everyone|all\s+individuals|all\s+users)",
    r"fair\s+across\s+all\s+(?:demographics|groups|subpopulations)",
    r"unbiased\s+across\s+all\s+(?:demographics|subgroups)",
    r"universally\s+(?:fair|equitable|unbiased)",
    r"equally\s+fair\s+to\s+every\s+(?:group|applicant|person)"
]

CERTAINTY_PATTERNS = [
    r"guarantees\s+(?:that\s+)?fairness",
    r"guarantees\s+equitable\s+outcomes",
    r"ensures\s+no\s+(?:disparity|bias)\s+can\s+occur",
    r"certified\s+(?:as\s+)?bias[- ]free",
    r"permanent\s+fix\s+for\s+algorithmic\s+bias"
]

OPTIMALITY_PATTERNS = [
    r"(?:is|was)\s+the\s+best\s+mitigation",
    r"(?:is|was)\s+the\s+optimal\s+(?:mitigation|debiasing|algorithm)",
    r"superior\s+to\s+all\s+other\s+mitigations",
    r"most\s+effective\s+possible\s+mitigation"
]

UNSUPPORTED_PERFORMANCE_PATTERNS = [
    r"(?:improved|enhanced|increased|boosted)\s+(?:model\s+)?performance",
    r"performance\s+(?:was\s+)?(?:improved|enhanced|increased|better)",
    r"without\s+any\s+(?:loss|reduction|degradation)\s+in\s+(?:accuracy|performance|predictive\s+power)"
]

AMBIGUOUS_COMPLEX_PATTERNS = [
    r"(?:appears\s+to\s+suggest|might\s+indicate|could\s+reflect)\s+underlying\s+societal",
    r"structural\s+inequalities\s+inherent\s+in",
    r"ethical\s+implications\s+of\s+deploying",
    r"morally\s+(?:acceptable|unacceptable|problematic)"
]


class UnsupportedClaimsDetector:
    """
    Scans explanations for unevidenced causal claims, absolute fairness declarations,
    overgeneralizations, unwarranted certainty, comparative optimality, and unsupported
    performance claims.
    """

    def evaluate(self, evidence: AuditEvidence, text: str) -> List[ExtractedClaim]:
        claims: List[ExtractedClaim] = []
        sentences = split_into_sentences(text)
        claim_idx = 1

        prov = {
            "experiment_id": evidence.experiment_id,
            "dataset": evidence.dataset.dataset_name if evidence.dataset else None,
            "model": evidence.model.model_family if evidence.model else None,
            "mitigation": evidence.model.mitigation_applied if evidence.model else None
        }
        ev_hash = getattr(evidence, "evidence_hash", None)



        for sent in sentences:
            sent_lower = sent.lower()

            # 1. Detect ungrounded causal claims
            for pattern in CAUSAL_PATTERNS:
                if re.search(pattern, sent_lower):
                    claims.append(ExtractedClaim(
                        claim_id=f"causal_{claim_idx}",
                        experiment_id=evidence.experiment_id,
                        claim_type=ClaimType.CAUSAL,
                        claim_text=sent,
                        ground_truth={
                            "causal_evidence_available": False,
                            "audit_type": "observational_statistical"
                        },
                        predicted_claim={
                            "pattern_matched": pattern,
                            "nature": "unsupported_causal_mechanism"
                        },
                        classification=ClaimClassification.UNSUPPORTED,
                        rationale=(
                            "Explanation asserts a causal mechanism or discriminatory intent, "
                            "which is ungrounded because observational fairness audits evaluate statistical associations, "
                            "not causal mechanisms."
                        ),
                        referenced_evidence="methodology.audit_type.observational",
                        extracted_values={"statement": sent, "pattern": pattern},
                        expected_values={"causal_inference_supported": False},
                        evidence_hash=ev_hash,
                        provenance=prov
                    ))
                    claim_idx += 1
                    break

            # 2. Detect ungrounded absolute fairness claims
            for pattern in ABSOLUTE_FAIRNESS_PATTERNS:
                if re.search(pattern, sent_lower):
                    claims.append(ExtractedClaim(
                        claim_id=f"abs_fair_{claim_idx}",
                        experiment_id=evidence.experiment_id,
                        claim_type=ClaimType.FAIRNESS_INTERPRETATION,
                        claim_text=sent,
                        ground_truth={"absolute_zero_bias_proven": False},
                        predicted_claim={
                            "pattern_matched": pattern,
                            "nature": "absolute_fairness_assertion"
                        },
                        classification=ClaimClassification.UNSUPPORTED,
                        rationale=(
                            "Explanation claims complete fairness or total elimination of bias, "
                            "which contradicts empirical audit realities where disparities remain non-zero."
                        ),
                        referenced_evidence="baseline_state.fairness_metrics",
                        extracted_values={"statement": sent, "pattern": pattern},
                        expected_values={"absolute_zero_bias_proven": False},
                        evidence_hash=ev_hash,
                        provenance=prov
                    ))
                    claim_idx += 1
                    break

            # 3. Detect overgeneralizations
            for pattern in OVERGENERALIZATION_PATTERNS:
                if re.search(pattern, sent_lower):
                    claims.append(ExtractedClaim(
                        claim_id=f"overgen_{claim_idx}",
                        experiment_id=evidence.experiment_id,
                        claim_type=ClaimType.FAIRNESS_INTERPRETATION,
                        claim_text=sent,
                        ground_truth={
                            "subgroups_evaluated_only": True,
                            "universal_fairness_evaluated": False
                        },
                        predicted_claim={
                            "pattern_matched": pattern,
                            "nature": "overgeneralization_to_all_populations"
                        },
                        classification=ClaimClassification.UNSUPPORTED,
                        rationale=(
                            "Explanation generalizes fairness to all groups or individuals, "
                            "whereas the audit only evaluated specific pre-defined demographic subgroups."
                        ),
                        referenced_evidence="dataset.subgroups_evaluated",
                        extracted_values={"statement": sent, "pattern": pattern},
                        expected_values={"evaluated_subgroups_only": True},
                        evidence_hash=ev_hash,
                        provenance=prov
                    ))
                    claim_idx += 1
                    break

            # 4. Detect certainty claims
            for pattern in CERTAINTY_PATTERNS:
                if re.search(pattern, sent_lower):
                    claims.append(ExtractedClaim(
                        claim_id=f"cert_{claim_idx}",
                        experiment_id=evidence.experiment_id,
                        claim_type=ClaimType.OTHER,
                        claim_text=sent,
                        ground_truth={"guarantees_possible": False},
                        predicted_claim={
                            "pattern_matched": pattern,
                            "nature": "unsupported_fairness_guarantee"
                        },
                        classification=ClaimClassification.UNSUPPORTED,
                        rationale=(
                            "Explanation asserts that fairness is guaranteed or certified, "
                            "which is scientifically ungrounded for empirical machine learning estimators."
                        ),
                        referenced_evidence="methodology.statistical_uncertainty",
                        extracted_values={"statement": sent, "pattern": pattern},
                        expected_values={"guarantee_possible": False},
                        evidence_hash=ev_hash,
                        provenance=prov
                    ))
                    claim_idx += 1
                    break

            # 5. Detect comparative optimality claims
            for pattern in OPTIMALITY_PATTERNS:
                if re.search(pattern, sent_lower):
                    claims.append(ExtractedClaim(
                        claim_id=f"opt_{claim_idx}",
                        experiment_id=evidence.experiment_id,
                        claim_type=ClaimType.OTHER,
                        claim_text=sent,
                        ground_truth={"cross_mitigation_ranking_performed": False},
                        predicted_claim={
                            "pattern_matched": pattern,
                            "nature": "unsupported_optimality_claim"
                        },
                        classification=ClaimClassification.UNSUPPORTED,
                        rationale=(
                            "Explanation claims that the mitigation is 'best' or 'optimal', "
                            "which is ungrounded as this experiment evaluates single interventions, "
                            "not an exhaustive search over all possible mitigations."
                        ),
                        referenced_evidence="mitigation.method_name",
                        extracted_values={"statement": sent, "pattern": pattern},
                        expected_values={"optimality_proven": False},
                        evidence_hash=ev_hash,
                        provenance=prov
                    ))
                    claim_idx += 1
                    break

            # 6. Detect unsupported performance claims
            for pattern in UNSUPPORTED_PERFORMANCE_PATTERNS:
                if re.search(pattern, sent_lower):
                    # Check if evidence actually showed performance degradation
                    perf_degraded = False
                    for comp in evidence.metric_comparisons:
                        if comp.metric_name in ["accuracy", "f1_score", "roc_auc"]:
                            if comp.direction == Direction.DECREASE:
                                perf_degraded = True
                                break
                    if perf_degraded:
                        claims.append(ExtractedClaim(
                            claim_id=f"unsup_perf_{claim_idx}",
                            experiment_id=evidence.experiment_id,
                            claim_type=ClaimType.PERFORMANCE,
                            claim_text=sent,
                            ground_truth={"performance_degraded": True},
                            predicted_claim={
                                "pattern_matched": pattern,
                                "nature": "claimed_performance_improvement_or_preservation"
                            },
                            classification=ClaimClassification.UNSUPPORTED,
                            rationale=(
                                "Explanation claims model performance improved or was preserved without loss, "
                                "contradicting empirical evidence where predictive accuracy/F1 decreased."
                            ),
                            referenced_evidence="metric_comparisons.accuracy",
                            extracted_values={"statement": sent, "pattern": pattern},
                            expected_values={"performance_degraded": True},
                            evidence_hash=ev_hash,
                            provenance=prov
                        ))
                        claim_idx += 1
                        break

            # 7. Detect complex sociotechnical claims requiring human annotation (UNDETERMINABLE)
            for pattern in AMBIGUOUS_COMPLEX_PATTERNS:
                if re.search(pattern, sent_lower):
                    claims.append(ExtractedClaim(
                        claim_id=f"undet_{claim_idx}",
                        experiment_id=evidence.experiment_id,
                        claim_type=ClaimType.OTHER,
                        claim_text=sent,
                        ground_truth={"requires_human_annotation": True},
                        predicted_claim={"pattern_matched": pattern},
                        classification=ClaimClassification.UNDETERMINABLE,
                        rationale=(
                            "Claim involves qualitative societal or ethical interpretation that cannot be "
                            "deterministically resolved against quantitative evidence. Flagged for human annotation."
                        ),
                        referenced_evidence="sociotechnical_context",
                        extracted_values={"statement": sent, "pattern": pattern},
                        expected_values={"human_adjudication_required": True},
                        evidence_hash=ev_hash,
                        provenance=prov
                    ))
                    claim_idx += 1
                    break

        return claims

