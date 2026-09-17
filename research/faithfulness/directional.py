"""
Directional Faithfulness Evaluator.
Evaluates both mathematical directional claims (increased / decreased / unchanged)
and semantic interpretation claims (improved / worsened) against authoritative audit evidence.
"""
import re
from typing import List, Dict, Any, Optional
from .taxonomy import ClaimType, ClaimClassification, ExtractedClaim, split_into_sentences
from .numerical import METRIC_ALIASES
from ..evidence.schemas import AuditEvidence, Direction, SemanticInterpretation

INCREASE_TERMS = ["increase", "increased", "increasing", "rose", "risen", "higher", "grew", "surged", "elevated"]
DECREASE_TERMS = ["decrease", "decreased", "decreasing", "dropped", "fell", "lower", "reduced", "reduction", "declined", "diminished"]
UNCHANGED_TERMS = ["unchanged", "constant", "stable", "persisted", "remained the same", "plateaued"]

IMPROVED_TERMS = ["improved", "improvement", "better", "enhanced", "gained", "more equitable", "more fair"]
WORSENED_TERMS = ["worsened", "worse", "degraded", "degradation", "deteriorated", "suffered", "less fair", "less equitable"]


class DirectionalFaithfulnessEvaluator:
    """
    Evaluates directional claims in natural language against authoritative comparative audit evidence.
    """

    def evaluate(self, evidence: AuditEvidence, text: str) -> List[ExtractedClaim]:
        claims: List[ExtractedClaim] = []
        if not evidence.metric_comparisons:
            return claims

        # Build lookup table for comparisons
        comp_map = {c.metric_name: c for c in evidence.metric_comparisons}
        sentences = split_into_sentences(text)

        claim_idx = 1
        for sent in sentences:
            sent_lower = sent.lower()

            for canonical_metric, aliases in METRIC_ALIASES.items():
                if canonical_metric not in comp_map:
                    continue

                comp = comp_map[canonical_metric]

                # Check if metric alias is in sentence
                matched_alias = None
                for alias in aliases:
                    if re.search(rf"\b{re.escape(alias)}\b", sent_lower):
                        matched_alias = alias
                        break

                if not matched_alias:
                    continue

                # 1. Check for Mathematical Directional claims
                found_math_direction = None
                matched_term = None

                for term in DECREASE_TERMS:
                    if re.search(rf"\b{re.escape(term)}\b", sent_lower):
                        found_math_direction = Direction.DECREASE
                        matched_term = term
                        break
                if not found_math_direction:
                    for term in INCREASE_TERMS:
                        if re.search(rf"\b{re.escape(term)}\b", sent_lower):
                            found_math_direction = Direction.INCREASE
                            matched_term = term
                            break
                if not found_math_direction:
                    for term in UNCHANGED_TERMS:
                        if re.search(rf"\b{re.escape(term)}\b", sent_lower):
                            found_math_direction = Direction.UNCHANGED
                            matched_term = term
                            break

                if found_math_direction is not None:
                    is_correct = (found_math_direction == comp.direction)
                    classification = ClaimClassification.SUPPORTED if is_correct else ClaimClassification.UNSUPPORTED
                    rationale = (
                        f"Claim that {canonical_metric} '{matched_term}' matches ground truth direction: {comp.direction.value}."
                        if is_correct else
                        f"Claim that {canonical_metric} '{matched_term}' contradicts ground truth direction: "
                        f"{comp.direction.value} (delta: {comp.absolute_change})."
                    )

                    claims.append(ExtractedClaim(
                        claim_id=f"dir_math_{claim_idx}",
                        experiment_id=evidence.experiment_id,
                        claim_type=ClaimType.DIRECTIONAL,
                        claim_text=sent,
                        ground_truth={
                            "metric_name": canonical_metric,
                            "direction": comp.direction.value,
                            "before": comp.before,
                            "after": comp.after,
                            "absolute_change": comp.absolute_change
                        },
                        predicted_claim={
                            "direction": found_math_direction.value,
                            "term": matched_term,
                            "metric_alias": matched_alias
                        },
                        classification=classification,
                        rationale=rationale
                    ))
                    claim_idx += 1

                # 2. Check for Domain Semantic Interpretation claims (improvement vs worsening)
                found_interpretation = None
                matched_interp_term = None

                for term in IMPROVED_TERMS:
                    if re.search(rf"\b{re.escape(term)}\b", sent_lower):
                        found_interpretation = SemanticInterpretation.IMPROVEMENT
                        matched_interp_term = term
                        break
                if not found_interpretation:
                    for term in WORSENED_TERMS:
                        if re.search(rf"\b{re.escape(term)}\b", sent_lower):
                            found_interpretation = SemanticInterpretation.DEGRADATION
                            matched_interp_term = term
                            break

                if found_interpretation is not None:
                    is_correct_interp = (found_interpretation == comp.interpretation)
                    classification_interp = (
                        ClaimClassification.SUPPORTED if is_correct_interp else ClaimClassification.UNSUPPORTED
                    )
                    rationale_interp = (
                        f"Claim of fairness/performance '{matched_interp_term}' matches domain interpretation: "
                        f"{comp.interpretation.value}."
                        if is_correct_interp else
                        f"Claim of fairness/performance '{matched_interp_term}' contradicts domain interpretation: "
                        f"{comp.interpretation.value} ({comp.semantics_rationale})."
                    )

                    claims.append(ExtractedClaim(
                        claim_id=f"dir_interp_{claim_idx}",
                        experiment_id=evidence.experiment_id,
                        claim_type=ClaimType.FAIRNESS_INTERPRETATION if "fair" in canonical_metric or "parity" in canonical_metric or "disparate" in canonical_metric else ClaimType.PERFORMANCE,
                        claim_text=sent,
                        ground_truth={
                            "metric_name": canonical_metric,
                            "interpretation": comp.interpretation.value,
                            "semantics_rationale": comp.semantics_rationale
                        },
                        predicted_claim={
                            "interpretation": found_interpretation.value,
                            "term": matched_interp_term,
                            "metric_alias": matched_alias
                        },
                        classification=classification_interp,
                        rationale=rationale_interp
                    ))
                    claim_idx += 1

        return claims
