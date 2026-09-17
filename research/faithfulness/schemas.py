"""
Faithfulness Evaluation Schemas and Aggregates.
"""
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from .taxonomy import ExtractedClaim


@dataclass
class FaithfulnessReport:
    """Complete quantitative faithfulness evaluation report for an explanation."""
    experiment_id: str
    explanation_source: str  # e.g., "gemini-2.5-flash", "mock", "template_baseline"
    prompt_id: Optional[str]
    timestamp_utc: str

    # Primary Faithfulness Metrics (Rates in [0.0, 1.0])
    numerical_faithfulness: float
    directional_faithfulness: float
    attribution_faithfulness: float
    unsupported_claim_rate: float

    # Raw counts
    numeric_claim_count: int
    numeric_match_count: int
    numeric_error_count: int

    directional_claim_count: int
    directional_match_count: int
    directional_error_count: int

    attribution_claim_count: int
    attribution_match_count: int
    attribution_error_count: int

    unsupported_claim_count: int
    undeterminable_claim_count: int
    total_claims_count: int

    # Mean Absolute Error for numerical claims
    numerical_mean_absolute_error: Optional[float]

    # Detailed claims
    claims: List[ExtractedClaim] = field(default_factory=list)

    # Configuration used
    evaluation_config: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["claims"] = [c.to_dict() for c in self.claims]
        return d
