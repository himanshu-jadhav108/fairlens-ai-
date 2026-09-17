"""
Unit tests for research dataset loaders and split partitioning.
"""
import pytest
import pandas as pd
from research.datasets.registry import get_dataset, list_datasets
from research.datasets.base import DatasetSplit


def test_list_datasets():
    datasets = list_datasets()
    assert "adult" in datasets
    assert "compas" in datasets
    assert "german" in datasets


@pytest.mark.parametrize("dname", ["adult", "compas", "german"])
def test_synthetic_benchmark_loading(dname):
    loader = get_dataset(dname)
    df = loader.load_data(use_synthetic_benchmark=True)
    assert isinstance(df, pd.DataFrame)
    assert len(df) >= 100
    assert loader.metadata.target_column in df.columns
    assert loader.metadata.sensitive_column in df.columns
    assert loader.metadata.is_synthetic_benchmark is True


def test_dataset_split_partitioning():
    loader = get_dataset("adult")
    df = loader.load_data(use_synthetic_benchmark=True)
    splits = loader.create_splits(df, train_ratio=0.60, val_ratio=0.20, test_ratio=0.20, random_seed=42)
    
    assert isinstance(splits, DatasetSplit)
    total_len = len(splits.X_train) + len(splits.X_val) + len(splits.X_test)
    assert total_len == len(df)
    assert len(splits.y_train) == len(splits.X_train)
    assert len(splits.s_train) == len(splits.X_train)
    assert len(splits.y_val) == len(splits.X_val)
    assert len(splits.y_test) == len(splits.X_test)
    assert splits.random_seed == 42
