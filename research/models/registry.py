"""
Model Registry for FairLens AI Research.
"""
from typing import Dict, Type, List, Any
from .base import BaseResearchModel
from .logistic_regression import LogisticRegressionModel
from .random_forest import RandomForestModel
from .xgboost_model import XGBoostModel


_MODEL_REGISTRY: Dict[str, Type[BaseResearchModel]] = {
    "logistic_regression": LogisticRegressionModel,
    "random_forest": RandomForestModel,
    "xgboost": XGBoostModel,
}


def get_model(name: str, random_state: int = 42, **kwargs: Any) -> BaseResearchModel:
    """Instantiate a candidate research model by name with random state."""
    clean_name = name.strip().lower()
    if clean_name not in _MODEL_REGISTRY:
        available = list(_MODEL_REGISTRY.keys())
        raise ValueError(f"Unknown model '{name}'. Available models: {available}")
    return _MODEL_REGISTRY[clean_name](random_state=random_state, **kwargs)


def list_models() -> List[str]:
    """List all registered candidate model families."""
    return list(_MODEL_REGISTRY.keys())
