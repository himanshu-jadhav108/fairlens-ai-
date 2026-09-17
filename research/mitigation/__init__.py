"""
Mitigation abstractions, implementations, and registry.
"""
from .base import BaseMitigation
from .correlation_remover import CorrelationRemoverMitigation
from .exponentiated_gradient import ExponentiatedGradientMitigation
from .threshold_optimizer import ThresholdOptimizerMitigation
from .registry import get_mitigation, list_mitigations

__all__ = [
    "BaseMitigation",
    "CorrelationRemoverMitigation",
    "ExponentiatedGradientMitigation",
    "ThresholdOptimizerMitigation",
    "get_mitigation",
    "list_mitigations",
]
