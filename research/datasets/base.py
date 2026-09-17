"""
Base Dataset Abstractions and Provenance Schema for FairLens AI Research.
Provides unified dataset interfaces, strict train/validation/test splits,
and documentation requirements for ethical ML benchmarks.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split


@dataclass
class DatasetMetadata:
    """Rigorous documentation of dataset provenance, licensing, and limitations."""
    name: str
    official_title: str
    source_url: str
    version_or_release: str
    license_name: str
    license_restrictions: str
    download_instructions: str
    target_column: str
    sensitive_column: str
    privileged_value: Any
    unprivileged_value: Any
    favorable_outcome_value: Any
    feature_names: List[str]
    categorical_columns: List[str]
    numeric_columns: List[str]
    known_limitations: str
    is_synthetic_benchmark: bool = False
    access_date: Optional[str] = "2026-09-17"


@dataclass
class DatasetSplit:
    """Strictly partitioned train, validation, and test splits."""
    X_train: pd.DataFrame
    y_train: pd.Series
    s_train: pd.Series
    
    X_val: pd.DataFrame
    y_val: pd.Series
    s_val: pd.Series
    
    X_test: pd.DataFrame
    y_test: pd.Series
    s_test: pd.Series
    
    feature_names: List[str]
    target_name: str
    sensitive_name: str
    split_id: str
    random_seed: int
    is_synthetic_benchmark: bool = False


class BaseDataset(ABC):
    """Abstract interface for all candidate research datasets."""

    def __init__(self, metadata: DatasetMetadata):
        self.metadata = metadata

    @abstractmethod
    def load_data(
        self,
        use_synthetic_benchmark: bool = False,
        local_path: Optional[str] = None
    ) -> pd.DataFrame:
        """Load or deterministically generate dataset following exact schema."""
        pass

    def create_splits(
        self,
        df: pd.DataFrame,
        train_ratio: float = 0.60,
        val_ratio: float = 0.20,
        test_ratio: float = 0.20,
        random_seed: int = 42
    ) -> DatasetSplit:
        """
        Partition dataframe into Train (60%), Validation (20%), and Test (20%).
        Guarantees:
        - Stratification across target label to preserve base rates.
        - Sensitive feature alignment with corresponding feature rows.
        - Deterministic reproducibility keyed by random_seed.
        """
        assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-5, "Ratios must sum to 1.0"
        
        target_col = self.metadata.target_column
        sensitive_col = self.metadata.sensitive_column
        
        y = df[target_col].copy()
        s = df[sensitive_col].copy()
        X = df.drop(columns=[target_col]).copy()
        
        # Step 1: Separate Train vs Temp (Val + Test)
        temp_ratio = val_ratio + test_ratio
        stratify_col = y if y.nunique() <= 10 else None
        
        X_train, X_temp, y_train, y_temp, s_train, s_temp = train_test_split(
            X, y, s,
            test_size=temp_ratio,
            random_state=random_seed,
            stratify=stratify_col
        )
        
        # Step 2: Separate Val vs Test from Temp
        val_share_of_temp = val_ratio / temp_ratio
        stratify_temp = y_temp if y_temp.nunique() <= 10 else None
        
        X_val, X_test, y_val, y_test, s_val, s_test = train_test_split(
            X_temp, y_temp, s_temp,
            test_size=(1.0 - val_share_of_temp),
            random_state=random_seed,
            stratify=stratify_temp
        )
        
        split_id = f"{self.metadata.name}__split_{random_seed}_t{int(train_ratio*100)}_v{int(val_ratio*100)}_te{int(test_ratio*100)}"
        
        return DatasetSplit(
            X_train=X_train.reset_index(drop=True),
            y_train=y_train.reset_index(drop=True),
            s_train=s_train.reset_index(drop=True),
            X_val=X_val.reset_index(drop=True),
            y_val=y_val.reset_index(drop=True),
            s_val=s_val.reset_index(drop=True),
            X_test=X_test.reset_index(drop=True),
            y_test=y_test.reset_index(drop=True),
            s_test=s_test.reset_index(drop=True),
            feature_names=list(X.columns),
            target_name=target_col,
            sensitive_name=sensitive_col,
            split_id=split_id,
            random_seed=random_seed,
            is_synthetic_benchmark=self.metadata.is_synthetic_benchmark
        )
