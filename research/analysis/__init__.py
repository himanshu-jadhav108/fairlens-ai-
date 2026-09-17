"""
Analysis, aggregation, and candidate visualization module.
"""
from .aggregator import aggregate_raw_results
from .visualization import generate_candidate_figures

__all__ = ["aggregate_raw_results", "generate_candidate_figures"]
