"""
Statistics module exports.
"""
from .hypothesis_testing import (
    check_normality,
    compute_paired_differences,
    compute_bonferroni_correction,
    PROVISIONAL_DISCLAIMER
)
from .faithfulness_analysis import (
    compute_paired_faithfulness_comparison,
    compute_explanation_bootstrap_ci
)

__all__ = [
    "check_normality",
    "compute_paired_differences",
    "compute_bonferroni_correction",
    "PROVISIONAL_DISCLAIMER",
    "compute_paired_faithfulness_comparison",
    "compute_explanation_bootstrap_ci"
]
