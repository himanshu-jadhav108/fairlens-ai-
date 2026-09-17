"""
Numerical Faithfulness Evaluator.
Extracts quantitative claims from generated text and rigorously verifies them
against authoritative structured audit evidence using pre-defined tolerances.
"""
import re
from typing import List, Dict, Any, Tuple, Optional
from .taxonomy import ClaimType, ClaimClassification, ExtractedClaim, split_into_sentences
from ..evidence.schemas import AuditEvidence
from ..evidence.metric_semantics import METRIC_REGISTRY

# Derive authoritative aliases directly from centralized Metric Registry
METRIC_ALIASES: Dict[str, List[str]] = {
    canonical_name: sem.aliases
    for canonical_name, sem in METRIC_REGISTRY.items()
}

# Unit words that indicate non-metric counts
NON_METRIC_COUNT_UNITS = re.compile(
    r"\b(?:samples?|records?|rows?|instances?|observations?|trees?|estimators?|features?|"
    r"dimensions?|epochs?|iterations?|seeds?|splits?|folds?|participants?|applicants?|"
    r"years?|months?|days?|seconds?|minutes?)\b",
    re.IGNORECASE
)

CLAUSE_DELIMITER_PATTERN = re.compile(
    r"(?:;\s*|,\s*(?:and|while|whereas|but|however)\s*|\s+(?:while|whereas|but|however)\s*|\s+and\s+)",
    re.IGNORECASE
)


def canonicalize_metric_name(metric_name: str) -> str:
    """Resolves any metric alias or variant to its canonical METRIC_REGISTRY key."""
    if metric_name in METRIC_REGISTRY:
        return metric_name
    m_clean = metric_name.replace("_", " ").lower()
    for canon, sem in METRIC_REGISTRY.items():
        if metric_name == canon:
            return canon
        if m_clean in [a.lower() for a in sem.aliases]:
            return canon
        if metric_name.lower() in [a.lower().replace(" ", "_") for a in sem.aliases]:
            return canon
    return metric_name


class NumericalFaithfulnessEvaluator:
    """
    Extracts numerical claims from natural-language text and verifies them
    against ground-truth values in AuditEvidence.
    """

    def __init__(
        self,
        absolute_tolerance: float = 0.015,
        relative_tolerance: float = 0.05
    ):
        """
        Args:
            absolute_tolerance: Maximum allowable absolute numerical discrepancy (e.g. 0.015).
            relative_tolerance: Maximum allowable relative error (e.g. 5% = 0.05).
        """
        self.absolute_tolerance = absolute_tolerance
        self.relative_tolerance = relative_tolerance

    def evaluate(self, evidence: AuditEvidence, text: str) -> List[ExtractedClaim]:
        """
        Identifies sentences and clauses containing metrics and numbers, matching them to evidence.
        Unassociated numbers are classified as UNDETERMINABLE.
        """
        claims: List[ExtractedClaim] = []
        sentences = split_into_sentences(text)

        # Collect ground truth numbers
        ground_truth_map = self._build_ground_truth_map(evidence)

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

            # Attribution sections (e.g. SHAP values / feature importance ranks)
            # are evaluated by AttributionFaithfulnessEvaluator, not NumericalFaithfulnessEvaluator
            if "shap" in sent_lower or ("feature" in sent_lower and ("importance" in sent_lower or "ranked" in sent_lower)):
                continue

            # Split sentence into clauses to prevent cross-clause metric bleed
            clauses = self._split_clauses(sent)

            for clause_text, clause_start_offset in clauses:
                clause_lower = clause_text.lower()

                # 1. Locate all metric mentions in this clause
                metric_mentions = []
                for canonical_metric, aliases in METRIC_ALIASES.items():
                    for alias in aliases:
                        for m in re.finditer(rf"\b{re.escape(alias)}\b", clause_lower):
                            metric_mentions.append({
                                "canonical_metric": canonical_metric,
                                "alias": alias,
                                "start": m.start(),
                                "end": m.end()
                            })

                # 2. Locate all numbers in this clause
                number_matches = list(re.finditer(
                    r"(?<![a-zA-Z_])([+-\u2212]?\d+(?:\.\d+)?|\.\d+)\s*(%|\bpercent\b|\bpercentage\b)?",
                    clause_text,
                    re.IGNORECASE
                ))

                for num_match in number_matches:
                    raw_val_str = num_match.group(1).replace("\u2212", "-")
                    pct_str = num_match.group(2)
                    is_pct = bool(pct_str)
                    try:
                        extracted_val = float(raw_val_str)
                        if is_pct:
                            extracted_val = extracted_val / 100.0
                    except ValueError:
                        continue

                    # Check if number is preceded/followed immediately by non-metric count units
                    post_context = clause_text[num_match.end():num_match.end() + 20]
                    if NON_METRIC_COUNT_UNITS.match(post_context.strip()):
                        continue

                    num_start = num_match.start()
                    num_end = num_match.end()

                    # Find best metric mention within the clause
                    best_mention = None
                    if metric_mentions:
                        def distance_to_mention(m):
                            if m["end"] <= num_start:
                                return num_start - m["end"]
                            elif m["start"] >= num_end:
                                return m["start"] - num_end
                            return 0

                        # Preceding metrics have slight preference when distance is equal
                        best_mention = min(
                            metric_mentions,
                            key=lambda m: (distance_to_mention(m), 0 if m["end"] <= num_start else 1)
                        )

                    # Case H: Number with no metric association
                    if not best_mention:
                        if "." in raw_val_str or is_pct:
                            claims.append(ExtractedClaim(
                                claim_id=f"num_{claim_idx}",
                                experiment_id=evidence.experiment_id,
                                claim_type=ClaimType.NUMERICAL,
                                claim_text=sent,
                                ground_truth={"canonical_metric": None, "reason": "no_associated_metric"},
                                predicted_claim={
                                    "extracted_value": extracted_val,
                                    "raw_string": num_match.group(0),
                                    "metric_alias": None
                                },
                                classification=ClaimClassification.UNDETERMINABLE,
                                rationale=(
                                    f"Numerical value '{num_match.group(0)}' has no clear metric association "
                                    f"in clause/sentence and cannot be deterministically evaluated against audit evidence."
                                ),
                                referenced_evidence="unassociated_numerical_value",
                                extracted_values={
                                    "value": extracted_val,
                                    "raw_string": num_match.group(0),
                                    "is_percentage": is_pct
                                },
                                expected_values={"metric_associated": False},
                                evidence_hash=ev_hash,
                                provenance=prov,
                                metadata={"is_orphan_number": True}
                            ))
                            claim_idx += 1
                        continue

                    canonical_metric = best_mention["canonical_metric"]
                    matched_alias = best_mention["alias"]

                    gt_candidates = ground_truth_map.get(canonical_metric, [])
                    if not gt_candidates:
                        continue

                    best_match = None
                    best_abs_diff = float("inf")

                    for cand in gt_candidates:
                        true_val = cand["value"]
                        if true_val is None:
                            continue
                        abs_diff = abs(extracted_val - true_val)
                        rel_diff = abs_diff / abs(true_val) if abs(true_val) > 1e-6 else abs_diff

                        if abs_diff < best_abs_diff:
                            best_abs_diff = abs_diff
                            best_match = {
                                "candidate": cand,
                                "abs_diff": round(abs_diff, 5),
                                "rel_diff": round(rel_diff, 5)
                            }

                    if best_match is not None:
                        is_match = (
                            best_match["abs_diff"] <= self.absolute_tolerance or
                            best_match["rel_diff"] <= self.relative_tolerance
                        )

                        classification = ClaimClassification.SUPPORTED if is_match else ClaimClassification.UNSUPPORTED
                        conversion_note = f" (converted from {num_match.group(0).strip()} -> {extracted_val})" if is_pct else ""
                        rationale = (
                            f"Reported value {extracted_val}{conversion_note} matches ground truth {best_match['candidate']['value']} "
                            f"for '{canonical_metric}' within tolerance (abs diff: {best_match['abs_diff']})."
                            if is_match else
                            f"Reported value {extracted_val}{conversion_note} contradicts ground truth "
                            f"{[c['value'] for c in gt_candidates]} for '{canonical_metric}' "
                            f"(min abs diff: {best_match['abs_diff']} > tol {self.absolute_tolerance})."
                        )

                        ref_path = best_match["candidate"].get("path", f"evidence.{canonical_metric}")
                        claims.append(ExtractedClaim(
                            claim_id=f"num_{claim_idx}",
                            experiment_id=evidence.experiment_id,
                            claim_type=ClaimType.NUMERICAL,
                            claim_text=sent,
                            ground_truth={
                                "canonical_metric": canonical_metric,
                                "matched_candidate": best_match["candidate"],
                                "all_candidates": [c["value"] for c in gt_candidates]
                            },
                            predicted_claim={
                                "extracted_value": extracted_val,
                                "metric_alias": matched_alias,
                                "raw_string": num_match.group(0)
                            },
                            classification=classification,
                            rationale=rationale,
                            referenced_evidence=ref_path,
                            extracted_values={
                                "value": extracted_val,
                                "raw_string": num_match.group(0),
                                "is_percentage": is_pct
                            },
                            expected_values={
                                "matched_value": best_match["candidate"]["value"],
                                "all_candidate_values": [c["value"] for c in gt_candidates]
                            },
                            evidence_hash=ev_hash,
                            provenance=prov,
                            metadata={
                                "abs_diff": best_match["abs_diff"],
                                "rel_diff": best_match["rel_diff"],
                                "absolute_tolerance": self.absolute_tolerance,
                                "relative_tolerance": self.relative_tolerance,
                                "is_percentage_converted": is_pct
                            }
                        ))
                        claim_idx += 1

        return claims

    def _split_clauses(self, sentence: str) -> List[Tuple[str, int]]:
        """
        Splits a sentence into constituent clauses using conjunctions and punctuation.
        Returns a list of (clause_text, start_offset) tuples.
        """
        splits = []
        last_end = 0
        for m in CLAUSE_DELIMITER_PATTERN.finditer(sentence):
            clause = sentence[last_end:m.start()].strip()
            if clause:
                splits.append((clause, last_end))
            last_end = m.end()
        remainder = sentence[last_end:].strip()
        if remainder:
            splits.append((remainder, last_end))
        return splits if splits else [(sentence, 0)]

    def _build_ground_truth_map(self, evidence: AuditEvidence) -> Dict[str, List[Dict[str, Any]]]:
        """Collects all valid numerical values from baseline, mitigated, and comparisons."""
        gt: Dict[str, List[Dict[str, Any]]] = {}

        def add_gt(raw_metric_name: str, val: Optional[float], state: str, path: str):
            if val is None:
                return
            canon_name = canonicalize_metric_name(raw_metric_name)
            for name in {raw_metric_name, canon_name}:
                if name not in gt:
                    gt[name] = []
                gt[name].append({"state": state, "value": val, "path": path})

        # Baseline
        for k, v in evidence.baseline_state.fairness_metrics.items():
            add_gt(k, v.value, "baseline", f"baseline_state.fairness_metrics.{k}.value")
        for k, v in evidence.baseline_state.performance_metrics.items():
            add_gt(k, v.value, "baseline", f"baseline_state.performance_metrics.{k}.value")

        # Mitigated
        if evidence.mitigated_state:
            for k, v in evidence.mitigated_state.fairness_metrics.items():
                add_gt(k, v.value, "mitigated", f"mitigated_state.fairness_metrics.{k}.value")
            for k, v in evidence.mitigated_state.performance_metrics.items():
                add_gt(k, v.value, "mitigated", f"mitigated_state.performance_metrics.{k}.value")

        # Comparisons
        for comp in evidence.metric_comparisons:
            add_gt(comp.metric_name, comp.before, "comparison_before", f"metric_comparisons.{comp.metric_name}.before")
            add_gt(comp.metric_name, comp.after, "comparison_after", f"metric_comparisons.{comp.metric_name}.after")
            add_gt(comp.metric_name, comp.absolute_change, "absolute_change", f"metric_comparisons.{comp.metric_name}.absolute_change")
            add_gt(comp.metric_name, comp.relative_change, "relative_change", f"metric_comparisons.{comp.metric_name}.relative_change")

        return gt
