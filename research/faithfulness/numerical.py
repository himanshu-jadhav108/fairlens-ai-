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
        Identifies sentences containing metrics and numbers, matching them to evidence.
        """
        claims: List[ExtractedClaim] = []
        sentences = split_into_sentences(text)

        # Collect ground truth numbers
        ground_truth_map = self._build_ground_truth_map(evidence)

        claim_idx = 1
        for sent in sentences:
            sent_lower = sent.lower()

            # 1. Locate all metric mentions in this sentence
            metric_mentions = []
            for canonical_metric, aliases in METRIC_ALIASES.items():
                for alias in aliases:
                    for m in re.finditer(rf"\b{re.escape(alias)}\b", sent_lower):
                        metric_mentions.append({
                            "canonical_metric": canonical_metric,
                            "alias": alias,
                            "start": m.start(),
                            "end": m.end()
                        })

            if not metric_mentions:
                continue

            # 2. Locate all numbers in this sentence
            number_matches = list(re.finditer(r"([+-]?\d+(?:\.\d+)?|\.\d+)\s*(%)?", sent))

            for num_match in number_matches:
                raw_val_str = num_match.group(1)
                is_pct = bool(num_match.group(2))
                try:
                    extracted_val = float(raw_val_str)
                    if is_pct:
                        extracted_val = extracted_val / 100.0
                except ValueError:
                    continue

                if extracted_val > 10.0 and "sample" not in sent_lower:
                    continue

                num_start = num_match.start()

                # Find closest metric mention (preferring one that precedes the number)
                preceding = [m for m in metric_mentions if m["end"] <= num_start]
                if preceding:
                    best_mention = min(preceding, key=lambda m: num_start - m["end"])
                else:
                    following = [m for m in metric_mentions if m["start"] >= num_match.end()]
                    if following:
                        best_mention = min(following, key=lambda m: m["start"] - num_match.end())
                    else:
                        best_mention = None

                if not best_mention:
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
                    rationale = (
                        f"Reported value {extracted_val} matches ground truth {best_match['candidate']['value']} "
                        f"for '{canonical_metric}' within tolerance (abs diff: {best_match['abs_diff']})."
                        if is_match else
                        f"Reported value {extracted_val} contradicts ground truth "
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
                        evidence_hash=getattr(evidence, "evidence_hash", None),

                        provenance={
                            "experiment_id": evidence.experiment_id,
                            "dataset": evidence.dataset.dataset_name if evidence.dataset else None,
                            "model": evidence.model.model_family if evidence.model else None,
                            "mitigation": evidence.model.mitigation_applied if evidence.model else None
                        },

                        metadata={
                            "abs_diff": best_match["abs_diff"],
                            "rel_diff": best_match["rel_diff"],
                            "absolute_tolerance": self.absolute_tolerance,
                            "relative_tolerance": self.relative_tolerance
                        }
                    ))
                    claim_idx += 1

        return claims

    def _build_ground_truth_map(self, evidence: AuditEvidence) -> Dict[str, List[Dict[str, Any]]]:
        """Collects all valid numerical values from baseline, mitigated, and comparisons."""
        gt: Dict[str, List[Dict[str, Any]]] = {}

        def add_gt(metric_name: str, val: Optional[float], state: str, path: str):
            if val is None:
                return
            if metric_name not in gt:
                gt[metric_name] = []
            gt[metric_name].append({"state": state, "value": val, "path": path})

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

