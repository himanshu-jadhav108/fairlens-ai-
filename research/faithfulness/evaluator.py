"""
Master Faithfulness Evaluator Orchestrator for FairLens AI Research.
Runs numerical, directional, attribution, and unsupported claim evaluations
against structured audit evidence, producing both summary reports and claim-level records.
"""
import os
import json
import datetime
from typing import List, Dict, Any, Optional
import numpy as np

from .taxonomy import ClaimType, ClaimClassification, ExtractedClaim
from .schemas import FaithfulnessReport
from .numerical import NumericalFaithfulnessEvaluator
from .directional import DirectionalFaithfulnessEvaluator
from .attribution import AttributionFaithfulnessEvaluator
from .unsupported_claims import UnsupportedClaimsDetector
from ..evidence.schemas import AuditEvidence


class FaithfulnessEvaluator:
    """
    Orchestrates quantitative faithfulness evaluation across all taxonomy dimensions.
    Enforces deterministic evaluation against authoritative AuditEvidence.
    """

    def __init__(
        self,
        absolute_tolerance: float = 0.015,
        relative_tolerance: float = 0.05,
        top_k_features: int = 5
    ):
        self.num_evaluator = NumericalFaithfulnessEvaluator(
            absolute_tolerance=absolute_tolerance,
            relative_tolerance=relative_tolerance
        )
        self.dir_evaluator = DirectionalFaithfulnessEvaluator()
        self.attr_evaluator = AttributionFaithfulnessEvaluator(top_k=top_k_features)
        self.unsupported_evaluator = UnsupportedClaimsDetector()

        self.config = {
            "absolute_tolerance": absolute_tolerance,
            "relative_tolerance": relative_tolerance,
            "top_k_features": top_k_features
        }

    def evaluate(
        self,
        evidence: AuditEvidence,
        explanation_text: str,
        explanation_source: str = "llm",
        prompt_id: Optional[str] = None,
        execution_mode: Optional[str] = None,
        save_records: bool = True,
        output_claims_dir: str = "research/results/claims",
        output_summaries_dir: str = "research/results/summaries"
    ) -> FaithfulnessReport:
        """
        Evaluates an explanation against structured evidence.
        Computes rate metrics and saves claim-level records.

        Args:
            execution_mode: Evidence classification tag.
                Must be one of: SOFTWARE_VALIDATION_ONLY | PILOT_VALIDATION_RUN | FINAL_EMPIRICAL_RUN
                This field is required for the aggregator to correctly identify evidence class.
        """
        all_claims: List[ExtractedClaim] = []

        # 1. Run sub-evaluators
        num_claims = self.num_evaluator.evaluate(evidence, explanation_text)
        dir_claims = self.dir_evaluator.evaluate(evidence, explanation_text)
        attr_claims = self.attr_evaluator.evaluate(evidence, explanation_text)
        unsup_claims = self.unsupported_evaluator.evaluate(evidence, explanation_text)

        all_claims.extend(num_claims)
        all_claims.extend(dir_claims)
        all_claims.extend(attr_claims)
        all_claims.extend(unsup_claims)

        # 2. Compute Numerical Metrics
        num_count = len(num_claims)
        num_matches = sum(1 for c in num_claims if c.classification == ClaimClassification.SUPPORTED)
        num_errors = sum(1 for c in num_claims if c.classification == ClaimClassification.UNSUPPORTED)
        num_evaluable_count = num_matches + num_errors
        num_evaluable = num_evaluable_count > 0
        num_faithfulness = round(num_matches / num_evaluable_count, 4) if num_evaluable else None

        abs_diffs = [
            c.metadata.get("abs_diff") for c in num_claims
            if c.metadata.get("abs_diff") is not None and c.classification in (ClaimClassification.SUPPORTED, ClaimClassification.UNSUPPORTED)
        ]
        mean_abs_err = round(float(np.mean(abs_diffs)), 5) if abs_diffs else None

        # 3. Compute Directional Metrics
        dir_count = len(dir_claims)
        dir_matches = sum(1 for c in dir_claims if c.classification == ClaimClassification.SUPPORTED)
        dir_errors = sum(1 for c in dir_claims if c.classification == ClaimClassification.UNSUPPORTED)
        dir_evaluable_count = dir_matches + dir_errors
        dir_evaluable = dir_evaluable_count > 0
        dir_faithfulness = round(dir_matches / dir_evaluable_count, 4) if dir_evaluable else None

        # 4. Compute Attribution Metrics
        attr_count = len(attr_claims)
        attr_matches = sum(1 for c in attr_claims if c.classification == ClaimClassification.SUPPORTED)
        attr_errors = sum(1 for c in attr_claims if c.classification == ClaimClassification.UNSUPPORTED)
        attr_evaluable_count = attr_matches + attr_errors
        attr_evaluable = attr_evaluable_count > 0
        attr_faithfulness = round(attr_matches / attr_evaluable_count, 4) if attr_evaluable else None

        # 5. Unsupported and Undeterminable Claims
        unsupported_count = sum(1 for c in all_claims if c.classification == ClaimClassification.UNSUPPORTED)
        undeterminable_count = sum(1 for c in all_claims if c.classification == ClaimClassification.UNDETERMINABLE)
        total_claims = len(all_claims)
        unsupported_rate = round(unsupported_count / total_claims, 4) if total_claims > 0 else 0.0

        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

        report = FaithfulnessReport(
            experiment_id=evidence.experiment_id,
            explanation_source=explanation_source,
            prompt_id=prompt_id,
            timestamp_utc=timestamp,
            execution_mode=execution_mode,
            numerical_faithfulness=num_faithfulness,
            directional_faithfulness=dir_faithfulness,
            attribution_faithfulness=attr_faithfulness,
            numerical_evaluable=num_evaluable,
            directional_evaluable=dir_evaluable,
            attribution_evaluable=attr_evaluable,
            unsupported_claim_rate=unsupported_rate,
            numeric_claim_count=num_count,
            numeric_match_count=num_matches,
            numeric_error_count=num_errors,
            directional_claim_count=dir_count,
            directional_match_count=dir_matches,
            directional_error_count=dir_errors,
            attribution_claim_count=attr_count,
            attribution_match_count=attr_matches,
            attribution_error_count=attr_errors,
            unsupported_claim_count=unsupported_count,
            undeterminable_claim_count=undeterminable_count,
            total_claims_count=total_claims,
            numerical_mean_absolute_error=mean_abs_err,
            claims=all_claims,
            evaluation_config=self.config
        )

        # 6. Save claim-level and summary records if requested
        if save_records:
            os.makedirs(output_claims_dir, exist_ok=True)
            os.makedirs(output_summaries_dir, exist_ok=True)

            # Save claims
            claims_file = os.path.join(
                output_claims_dir,
                f"claims__{evidence.experiment_id}__{explanation_source}.json"
            )
            with open(claims_file, "w", encoding="utf-8") as f:
                json.dump([c.to_dict() for c in all_claims], f, indent=2)

            # Save summary report
            summary_file = os.path.join(
                output_summaries_dir,
                f"summary__{evidence.experiment_id}__{explanation_source}.json"
            )
            with open(summary_file, "w", encoding="utf-8") as f:
                json.dump(report.to_dict(), f, indent=2)

        return report
