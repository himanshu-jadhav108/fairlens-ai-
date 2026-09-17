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

# Section 5: Qualitative magnitude terms cannot be deterministically evaluated without arbitrary thresholds.
# They must be classified as UNDETERMINABLE and routed to human annotation.
QUALITATIVE_MAGNITUDE_TERMS = [
    "substantially", "dramatically", "drastically", "significantly",
    "slightly", "marginally", "minimally", "modestly", "moderately",
    "large improvement", "small improvement", "massive reduction",
    "huge drop", "negligible change", "slight decrease", "substantial decrease"
]


class DirectionalFaithfulnessEvaluator:
    """
    Evaluates directional claims in natural language against authoritative comparative audit evidence.
    Distinguishes:
    1. Mathematical Direction (increase / decrease / unchanged)
    2. Domain Semantic Interpretation (improvement / degradation)
    3. Qualitative Magnitude Claims (routed to UNDETERMINABLE for human annotation)
    """

    def evaluate(self, evidence: AuditEvidence, text: str) -> List[ExtractedClaim]:
        claims: List[ExtractedClaim] = []
        if not evidence.metric_comparisons:
            return claims

        # Build lookup table for comparisons
        comp_map = {c.metric_name: c for c in evidence.metric_comparisons}
        sentences = split_into_sentences(text)

        prov = {
            "experiment_id": evidence.experiment_id,
            "dataset": evidence.dataset.dataset_name if evidence.dataset else None,
            "model": evidence.model.model_family if evidence.model else None,
            "mitigation": evidence.model.mitigation_applied if evidence.model else None
        }
        ev_hash = getattr(evidence, "evidence_hash", None)



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
                        rationale=rationale,
                        referenced_evidence=f"metric_comparisons.{canonical_metric}.direction",
                        extracted_values={
                            "direction": found_math_direction.value,
                            "term": matched_term,
                            "metric": canonical_metric
                        },
                        expected_values={
                            "direction": comp.direction.value,
                            "absolute_change": comp.absolute_change,
                            "before": comp.before,
                            "after": comp.after
                        },
                        evidence_hash=ev_hash,
                        provenance=prov
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

                    claim_type = (
                        ClaimType.FAIRNESS_INTERPRETATION
                        if "fair" in canonical_metric or "parity" in canonical_metric or "disparate" in canonical_metric or "equal" in canonical_metric
                        else ClaimType.PERFORMANCE
                    )

                    claims.append(ExtractedClaim(
                        claim_id=f"dir_interp_{claim_idx}",
                        experiment_id=evidence.experiment_id,
                        claim_type=claim_type,
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
                        rationale=rationale_interp,
                        referenced_evidence=f"metric_comparisons.{canonical_metric}.interpretation",
                        extracted_values={
                            "interpretation": found_interpretation.value,
                            "term": matched_interp_term,
                            "metric": canonical_metric
                        },
                        expected_values={
                            "interpretation": comp.interpretation.value,
                            "semantics_rationale": comp.semantics_rationale
                        },
                        evidence_hash=ev_hash,
                        provenance=prov
                    ))
                    claim_idx += 1

                # 3. Check for Qualitative Magnitude Claims (Section 5: must classify as UNDETERMINABLE)
                matched_mag_term = None
                for mag_term in QUALITATIVE_MAGNITUDE_TERMS:
                    if re.search(rf"\b{re.escape(mag_term)}\b", sent_lower):
                        matched_mag_term = mag_term
                        break

                if matched_mag_term is not None:
                    claims.append(ExtractedClaim(
                        claim_id=f"mag_{claim_idx}",
                        experiment_id=evidence.experiment_id,
                        claim_type=ClaimType.MAGNITUDE,
                        claim_text=sent,
                        ground_truth={
                            "metric_name": canonical_metric,
                            "absolute_change": comp.absolute_change,
                            "relative_change": comp.relative_change
                        },
                        predicted_claim={
                            "modifier": matched_mag_term,
                            "metric_alias": matched_alias
                        },
                        classification=ClaimClassification.UNDETERMINABLE,
                        rationale=(
                            f"Claim uses qualitative magnitude modifier '{matched_mag_term}' for '{canonical_metric}' "
                            f"(actual delta: {comp.absolute_change}). Subjective magnitude claims cannot be "
                            f"deterministically resolved without arbitrary thresholds and are routed to human annotation."
                        ),
                        referenced_evidence=f"metric_comparisons.{canonical_metric}.absolute_change",
                        extracted_values={
                            "modifier": matched_mag_term,
                            "metric": canonical_metric
                        },
                        expected_values={
                            "absolute_change": comp.absolute_change,
                            "relative_change": comp.relative_change
                        },
                        evidence_hash=ev_hash,
                        provenance=prov
                    ))
                    claim_idx += 1

        return claims

