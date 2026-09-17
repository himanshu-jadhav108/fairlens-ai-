"""
Attribution Faithfulness Evaluator.
Evaluates LLM statements about feature importance, top-ranked predictors, and relative
influence against authoritative SHAP evidence.
"""
import re
from typing import List, Dict, Any, Optional, Set
from .taxonomy import ClaimType, ClaimClassification, ExtractedClaim, split_into_sentences
from ..evidence.schemas import AuditEvidence

MOST_IMPORTANT_PATTERNS = [
    r"most\s+(?:important|influential|significant|predictive|critical)\s+feature\s+(?:is|was|remains)?\s*[:]?\s*([a-zA-Z0-9_]+)",
    r"([a-zA-Z0-9_]+)\s+(?:was|is)\s+the\s+most\s+(?:important|influential|significant|predictive|dominant)",
    r"top\s+predictor\s+(?:is|was)\s*[:]?\s*([a-zA-Z0-9_]+)",
    r"highest\s+feature\s+importance\s+(?:belonged\s+to|was)?\s*[:]?\s*([a-zA-Z0-9_]+)",
    r"([a-zA-Z0-9_]+)\s+had\s+the\s+largest\s+(?:impact|effect|shap\s+value)"
]


class AttributionFaithfulnessEvaluator:
    """
    Evaluates statements regarding feature importance against authoritative SHAP rankings.
    """

    def __init__(self, top_k: int = 5):
        self.top_k = top_k

    def evaluate(self, evidence: AuditEvidence, text: str) -> List[ExtractedClaim]:
        claims: List[ExtractedClaim] = []

        # Ground truth SHAP from mitigated (if present) or baseline state
        active_state = evidence.mitigated_state or evidence.baseline_state
        if not active_state.shap_evidence or not active_state.shap_evidence.ranked_features:
            return claims

        shap_ev = active_state.shap_evidence
        ranked_features = shap_ev.ranked_features
        top_1_feature = ranked_features[0].feature_name if ranked_features else None
        top_k_features = set(shap_ev.top_k_features[:self.top_k])
        all_features = {f.feature_name for f in ranked_features}
        feature_rank_map = {f.feature_name: f.rank for f in ranked_features}

        sentences = split_into_sentences(text)
        claim_idx = 1

        for sent in sentences:
            sent_lower = sent.lower()

            # 1. Check for top-1 / most important feature claim
            for pattern in MOST_IMPORTANT_PATTERNS:
                m = re.search(pattern, sent, re.IGNORECASE)
                if m:
                    claimed_feature = m.group(1).strip()
                    # Resolve to actual feature name if case-insensitive match
                    matched_gt_name = self._resolve_feature_name(claimed_feature, all_features)

                    if matched_gt_name is None:
                        # Hallucinated feature not even in dataset!
                        claims.append(ExtractedClaim(
                            claim_id=f"attr_top1_{claim_idx}",
                            experiment_id=evidence.experiment_id,
                            claim_type=ClaimType.ATTRIBUTION,
                            claim_text=sent,
                            ground_truth={
                                "true_top_1": top_1_feature,
                                "top_k": list(top_k_features)
                            },
                            predicted_claim={
                                "claimed_feature": claimed_feature,
                                "claim_role": "top_1_most_important"
                            },
                            classification=ClaimClassification.UNSUPPORTED,
                            rationale=f"Claimed feature '{claimed_feature}' does not exist in audited features."
                        ))
                        claim_idx += 1
                    else:
                        true_rank = feature_rank_map.get(matched_gt_name, 999)
                        is_top1 = (true_rank == 1)
                        is_in_top_k = (true_rank <= self.top_k)

                        classification = (
                            ClaimClassification.SUPPORTED if is_top1
                            else (ClaimClassification.PARTIALLY_SUPPORTED if is_in_top_k else ClaimClassification.UNSUPPORTED)
                        )
                        rationale = (
                            f"Claimed top feature '{matched_gt_name}' is indeed rank 1 with mean |SHAP| {ranked_features[0].mean_abs_shap}."
                            if is_top1 else
                            f"Claimed top feature '{matched_gt_name}' is rank {true_rank} (true rank 1 is '{top_1_feature}')."
                        )

                        claims.append(ExtractedClaim(
                            claim_id=f"attr_top1_{claim_idx}",
                            experiment_id=evidence.experiment_id,
                            claim_type=ClaimType.ATTRIBUTION,
                            claim_text=sent,
                            ground_truth={
                                "true_top_1": top_1_feature,
                                "feature_rank": true_rank,
                                "top_k": list(top_k_features)
                            },
                            predicted_claim={
                                "claimed_feature": matched_gt_name,
                                "claim_role": "top_1_most_important"
                            },
                            classification=classification,
                            rationale=rationale,
                            metadata={"rank": true_rank}
                        ))
                        claim_idx += 1
                    break

            # 2. Check for explicit rank statements (e.g. "feature X ranked second", "ranked 3rd")
            rank_match = re.search(r"([a-zA-Z0-9_]+)\s+(?:ranked|was\s+ranked|placed)\s+(?:#|number\s+)?(\d+)(?:st|nd|rd|th)?", sent, re.IGNORECASE)
            if rank_match:
                claimed_feat = rank_match.group(1).strip()
                claimed_rank = int(rank_match.group(2))
                matched_name = self._resolve_feature_name(claimed_feat, all_features)

                if matched_name is not None:
                    actual_rank = feature_rank_map.get(matched_name)
                    is_correct_rank = (actual_rank == claimed_rank)
                    classification = ClaimClassification.SUPPORTED if is_correct_rank else ClaimClassification.UNSUPPORTED

                    claims.append(ExtractedClaim(
                        claim_id=f"attr_rank_{claim_idx}",
                        experiment_id=evidence.experiment_id,
                        claim_type=ClaimType.ATTRIBUTION,
                        claim_text=sent,
                        ground_truth={
                            "feature_name": matched_name,
                            "actual_rank": actual_rank
                        },
                        predicted_claim={
                            "feature_name": matched_name,
                            "claimed_rank": claimed_rank
                        },
                        classification=classification,
                        rationale=f"Claimed rank {claimed_rank} for '{matched_name}' (actual rank: {actual_rank})."
                    ))
                    claim_idx += 1

        return claims

    def _resolve_feature_name(self, candidate: str, valid_features: Set[str]) -> Optional[str]:
        cand_lower = candidate.lower().strip()
        for f in valid_features:
            if f.lower() == cand_lower or cand_lower in f.lower():
                return f
        return None
