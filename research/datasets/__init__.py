"""
Dataset abstractions, provenance metadata, and candidate loaders.
"""
from .base import BaseDataset, DatasetMetadata, DatasetSplit
from .adult import AdultDataset
from .compas import COMPASDataset
from .german import GermanCreditDataset
from .registry import get_dataset, list_datasets

__all__ = [
    "BaseDataset",
    "DatasetMetadata",
    "DatasetSplit",
    "AdultDataset",
    "COMPASDataset",
    "GermanCreditDataset",
    "get_dataset",
    "list_datasets",
]
