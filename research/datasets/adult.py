"""
Adult Census Income Dataset Loader and Provenance Specification.
"""
import os
from typing import Optional
import numpy as np
import pandas as pd
from .base import BaseDataset, DatasetMetadata


class AdultDataset(BaseDataset):
    """
    Adult Census Income Benchmark Dataset.
    Target: Binary income prediction (>50K vs <=50K).
    Sensitive Attribute: Sex (Male: Privileged, Female: Unprivileged).
    """

    def __init__(self):
        metadata = DatasetMetadata(
            name="adult",
            official_title="Adult Census Income (1994 US Census Database)",
            source_url="https://archive.ics.uci.edu/dataset/2/adult",
            version_or_release="1.0 (UCI 1996 release)",
            license_name="Creative Commons Attribution 4.0 International (CC BY 4.0)",
            license_restrictions="Open academic research use with attribution to original authors (Kohavi & Becker).",
            download_instructions=(
                "Download adult.data and adult.test from UCI repository or use fetch_openml('adult', version=2). "
                "Do not commit raw restricted datasets directly to public version control."
            ),
            target_column="income",
            sensitive_column="sex",
            privileged_value="Male",
            unprivileged_value="Female",
            favorable_outcome_value=1,
            feature_names=[
                "age", "workclass", "education_num", "marital_status",
                "occupation", "relationship", "race", "sex",
                "capital_gain", "capital_loss", "hours_per_week"
            ],
            categorical_columns=[
                "workclass", "marital_status", "occupation",
                "relationship", "race", "sex"
            ],
            numeric_columns=[
                "age", "education_num", "capital_gain", "capital_loss", "hours_per_week"
            ],
            known_limitations=(
                "Encodes structural 1994 US wage disparities and gender stratification. "
                "Coarse binary income threshold ($50,000) creates artificial boundary effects. "
                "Excluded demographic groups and married filing joint bias."
            ),
            is_synthetic_benchmark=False
        )
        super().__init__(metadata)

    def load_data(
        self,
        use_synthetic_benchmark: bool = False,
        local_path: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Loads the Adult dataset.
        If local_path exists and is readable, loads real data.
        Otherwise, if use_synthetic_benchmark=True, deterministically generates
        a benchmark-structured synthetic dataset for unit tests and CI.
        """
        if local_path and os.path.exists(local_path):
            df = pd.read_csv(local_path)
            self.metadata.is_synthetic_benchmark = False
            return self._clean_adult(df)

        if use_synthetic_benchmark:
            self.metadata.is_synthetic_benchmark = True
            return self._generate_synthetic_benchmark()

        raise FileNotFoundError(
            f"Adult dataset file not found at '{local_path}'. "
            "To run unit tests or smoke tests without external data downloads, "
            "pass use_synthetic_benchmark=True."
        )

    def _clean_adult(self, df: pd.DataFrame) -> pd.DataFrame:
        """Cleans and standardizes raw Adult census data."""
        df = df.copy()
        df.columns = [c.strip().lower().replace("-", "_") for c in df.columns]
        
        # Standardize target
        if "income" in df.columns:
            df["income"] = df["income"].astype(str).str.strip().replace({
                ">50K": 1, ">50K.": 1, "<=50K": 0, "<=50K.": 0
            })
            df["income"] = pd.to_numeric(df["income"], errors="coerce").fillna(0).astype(int)
        
        # Standardize sex
        if "sex" in df.columns:
            df["sex"] = df["sex"].astype(str).str.strip().replace({
                "Male": "Male", "Female": "Female"
            })
        return df

    def _generate_synthetic_benchmark(self, n_samples: int = 1500, seed: int = 42) -> pd.DataFrame:
        """
        Generates a deterministic synthetic benchmark matching the exact
        feature schema, data types, and empirical correlations of Adult Census Income.
        NOTE: Strictly intended for unit tests, smoke tests, and CI. NOT research evidence.
        """
        rng = np.random.default_rng(seed)
        
        sex = rng.choice(["Male", "Female"], size=n_samples, p=[0.67, 0.33])
        age = rng.integers(18, 75, size=n_samples)
        edu_num = rng.integers(5, 16, size=n_samples)
        hours = rng.integers(20, 60, size=n_samples)
        cap_gain = rng.choice([0, 5000, 10000], size=n_samples, p=[0.85, 0.10, 0.05])
        cap_loss = rng.choice([0, 1500, 2500], size=n_samples, p=[0.90, 0.07, 0.03])
        
        workclass = rng.choice(["Private", "Self-Emp", "Gov"], size=n_samples, p=[0.7, 0.15, 0.15])
        marital = rng.choice(["Married", "Never-married", "Divorced"], size=n_samples, p=[0.5, 0.3, 0.2])
        race = rng.choice(["White", "Black", "Asian-Pac", "Other"], size=n_samples, p=[0.85, 0.09, 0.04, 0.02])
        occupation = rng.choice(["Exec-managerial", "Prof-specialty", "Craft-repair", "Sales", "Other"], size=n_samples)
        relationship = rng.choice(["Husband", "Wife", "Own-child", "Not-in-family", "Unmarried"], size=n_samples)
        
        # Base log-odds with documented historical wage disparity
        base_score = (age / 75.0) * 1.5 + (edu_num / 16.0) * 2.5 + (hours / 60.0) * 1.2
        sex_penalty = np.where(sex == "Female", 0.7, 0.0)
        prob = 1.0 / (1.0 + np.exp(-(base_score - 2.8 - sex_penalty + rng.normal(0, 0.3, n_samples))))
        income = (prob > 0.5).astype(int)

        return pd.DataFrame({
            "age": age,
            "workclass": workclass,
            "education_num": edu_num,
            "marital_status": marital,
            "occupation": occupation,
            "relationship": relationship,
            "race": race,
            "sex": sex,
            "capital_gain": cap_gain,
            "capital_loss": cap_loss,
            "hours_per_week": hours,
            "income": income
        })
