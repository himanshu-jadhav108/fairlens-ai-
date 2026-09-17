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
    explanation_source: str  # e.g., "gemini__gemini-2.5-flash", "template_baseline"
    prompt_id: Optional[str]
    timestamp_utc: str

    # Evidence classification — REQUIRED for aggregation guards
    # Must be one of: SOFTWARE_VALIDATION_ONLY | PILOT_VALIDATION_RUN | FINAL_EMPIRICAL_RUN
    execution_mode: Optional[str] = None

    # Primary Faithfulness Metrics (Rates in [0.0, 1.0])
    numerical_faithfulness: float = 0.0
    directional_faithfulness: float = 0.0
    attribution_faithfulness: float = 0.0
    unsupported_claim_rate: float = 0.0

    # Raw counts
    numeric_claim_count: int = 0
    numeric_match_count: int = 0
    numeric_error_count: int = 0

    directional_claim_count: int = 0
    directional_match_count: int = 0
    directional_error_count: int = 0

    attribution_claim_count: int = 0
    attribution_match_count: int = 0
    attribution_error_count: int = 0

    unsupported_claim_count: int = 0
    undeterminable_claim_count: int = 0
    total_claims_count: int = 0

    # Mean Absolute Error for numerical claims
    numerical_mean_absolute_error: Optional[float] = None

    # Detailed claims
    claims: List[ExtractedClaim] = field(default_factory=list)

    # Configuration used
    evaluation_config: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["claims"] = [c.to_dict() for c in self.claims]
        return d
