"""
Mitigation Registry for FairLens AI Research.
"""
from typing import Dict, Type, List, Any
from .base import BaseMitigation
from .correlation_remover import CorrelationRemoverMitigation
from .exponentiated_gradient import ExponentiatedGradientMitigation
from .threshold_optimizer import ThresholdOptimizerMitigation
from ..models.base import BaseResearchModel


_MITIGATION_REGISTRY: Dict[str, Type[BaseMitigation]] = {
    "correlation_remover": CorrelationRemoverMitigation,
    "exponentiated_gradient": ExponentiatedGradientMitigation,
    "threshold_optimizer": ThresholdOptimizerMitigation,
}


def get_mitigation(name: str, base_model: BaseResearchModel, **kwargs: Any) -> BaseMitigation:
    """Instantiate a mitigation intervention wrapping a specified base model."""
    clean_name = name.strip().lower()
    if clean_name not in _MITIGATION_REGISTRY:
        available = list(_MITIGATION_REGISTRY.keys())
        raise ValueError(f"Unknown mitigation method '{name}'. Available mitigations: {available}")
    return _MITIGATION_REGISTRY[clean_name](base_model=base_model, **kwargs)


def list_mitigations() -> List[str]:
    """List all registered candidate mitigation algorithms."""
    return list(_MITIGATION_REGISTRY.keys())
