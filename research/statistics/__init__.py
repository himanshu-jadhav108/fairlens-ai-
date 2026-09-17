"""
Statistical procedures and hypothesis testing utilities (PROVISIONAL).
"""
from .hypothesis_testing import (
    check_normality,
    compute_paired_differences,
    adjust_multiple_comparisons,
    PROVISIONAL_DISCLAIMER
)

__all__ = [
    "check_normality",
    "compute_paired_differences",
    "adjust_multiple_comparisons",
    "PROVISIONAL_DISCLAIMER"
]
