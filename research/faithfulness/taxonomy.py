"""
Taxonomy of Claims and Classifications for ML Fairness Explanation Faithfulness.
"""
import re
from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional, List


class ClaimType(str, Enum):
    NUMERICAL = "numerical"
    DIRECTIONAL = "directional"
    ATTRIBUTION = "attribution"
    PERFORMANCE = "performance"
    FAIRNESS_INTERPRETATION = "fairness_interpretation"
    CAUSAL = "causal"
    OTHER = "other"


class ClaimClassification(str, Enum):
    SUPPORTED = "SUPPORTED"
    PARTIALLY_SUPPORTED = "PARTIALLY_SUPPORTED"
    UNSUPPORTED = "UNSUPPORTED"
    UNDETERMINABLE = "UNDETERMINABLE"


@dataclass
class ExtractedClaim:
    """A single atomic factual or semantic claim extracted from an explanation."""
    claim_id: str
    experiment_id: str
    claim_type: ClaimType
    claim_text: str
    ground_truth: Dict[str, Any]
    predicted_claim: Dict[str, Any]
    classification: ClaimClassification
    rationale: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["claim_type"] = self.claim_type.value
        d["classification"] = self.classification.value
        return d


def split_into_sentences(text: str) -> List[str]:
    """
    Splits natural language text into sentences without breaking decimal numbers (e.g. 0.4200).
    A sentence boundary is a period NOT followed by a digit, or newline/semicolon.
    """
    cleaned = text.replace("\r\n", "\n").replace("\r", "\n")
    # Split on period followed by whitespace or end of string (and NOT followed by digit), or on newlines/semicolons
    sentences = re.split(r"\.(?!\d)(?:\s+|$)|[\n;]+", cleaned)
    return [s.strip() for s in sentences if s.strip()]
