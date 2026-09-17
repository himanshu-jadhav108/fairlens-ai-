"""
Unsupported Claims and Causal Assertion Detector.
Identifies unevidenced causal assertions, extreme non-empirical generalizations,
and ungrounded fairness conclusions.
"""
import re
from typing import List, Dict, Any
from .taxonomy import ClaimType, ClaimClassification, ExtractedClaim, split_into_sentences
from ..evidence.schemas import AuditEvidence

CAUSAL_PATTERNS = [
    r"(?:directly\s+)?caused\s+(?:the\s+)?(?:model\s+to\s+[a-z]+|disparity|bias|discrimination|lower\s+rates|outcomes)",
    r"(?:is|was)\s+the\s+direct\s+cause\s+of",
    r"proves\s+(?:systemic\s+)?discriminatory\s+intent",
    r"leads\s+directly\s+to\s+discriminatory\s+outcomes",
    r"because\s+of\s+(?:their|the\s+applicant[']?s?)\s+(?:age|race|sex|gender),?\s+the\s+model\s+(?:rejected|discriminated)"
]

ABSOLUTE_FAIRNESS_PATTERNS = [
    r"(?:is|was|became)\s+completely\s+fair",
    r"(?:is|was|became)\s+entirely\s+unbiased",
    r"(?:guarantees|ensures)\s+perfect\s+fairness",
    r"eliminates\s+all\s+(?:possible\s+)?bias"
]

AMBIGUOUS_COMPLEX_PATTERNS = [
    r"(?:appears\s+to\s+suggest|might\s+indicate|could\s+reflect)\s+underlying\s+societal",
    r"structural\s+inequalities\s+inherent\s+in",
    r"ethical\s+implications\s+of\s+deploying"
]


class UnsupportedClaimsDetector:
    """
    Scans explanations for unevidenced causal claims, absolute fairness declarations,
    and flags complex semantic assertions as UNDETERMINABLE for human annotation.
    """

    def evaluate(self, evidence: AuditEvidence, text: str) -> List[ExtractedClaim]:
        claims: List[ExtractedClaim] = []
        sentences = split_into_sentences(text)
        claim_idx = 1
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
                        )
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
                        ground_truth={
                            "absolute_zero_bias_proven": False
                        },
                        predicted_claim={
                            "pattern_matched": pattern,
                            "nature": "absolute_fairness_assertion"
                        },
                        classification=ClaimClassification.UNSUPPORTED,
                        rationale=(
                            "Explanation claims complete fairness or total elimination of bias, "
                            "which contradicts empirical audit realities where disparities remain non-zero."
                        )
                    ))
                    claim_idx += 1
                    break

            # 3. Detect complex sociotechnical claims requiring human annotation (UNDETERMINABLE)
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
                        )
                    ))
                    claim_idx += 1
                    break

        return claims
