"""
Dataset Registry for FairLens AI Research.
"""
from typing import Dict, Type, List
from .base import BaseDataset
from .adult import AdultDataset
from .compas import COMPASDataset
from .german import GermanCreditDataset


_DATASET_REGISTRY: Dict[str, Type[BaseDataset]] = {
    "adult": AdultDataset,
    "compas": COMPASDataset,
    "german": GermanCreditDataset,
}


def get_dataset(name: str) -> BaseDataset:
    """Instantiate dataset loader by canonical name."""
    clean_name = name.strip().lower()
    if clean_name not in _DATASET_REGISTRY:
        available = list(_DATASET_REGISTRY.keys())
        raise ValueError(f"Unknown dataset '{name}'. Available candidate datasets: {available}")
    return _DATASET_REGISTRY[clean_name]()


def list_datasets() -> List[str]:
    """List all registered candidate datasets."""
    return list(_DATASET_REGISTRY.keys())
