"""
German Credit Dataset Loader and Provenance Specification.
"""
import os
from typing import Optional
import numpy as np
import pandas as pd
from .base import BaseDataset, DatasetMetadata


class GermanCreditDataset(BaseDataset):
    """
    Statlog German Credit Benchmark Dataset.
    Target: credit_risk (1: Good Credit [Favorable], 0: Bad Credit).
    Sensitive Attribute: age_group (Adult >= 25 vs Young < 25).
    """

    def __init__(self):
        metadata = DatasetMetadata(
            name="german",
            official_title="Statlog (German Credit Data) Data Set",
            source_url="https://archive.ics.uci.edu/dataset/144/statlog+german+credit+data",
            version_or_release="1.0 (UCI 1994 Release)",
            license_name="Open Access / Academic Public Domain via UCI ML Repository",
            license_restrictions="Open academic research use with attribution to Prof. Dr. Hans Hofmann.",
            download_instructions=(
                "Obtain german.data from the UCI ML Repository. "
                "The 21st column represents credit risk (1 = Good, 2 = Bad). "
                "Recode target to 1 (Good) and 0 (Bad). Sensitive attribute is Age binned at 25 years."
            ),
            target_column="credit_risk",
            sensitive_column="age_group",
            privileged_value="Adult",
            unprivileged_value="Young",
            favorable_outcome_value=1,
            feature_names=[
                "duration_months", "credit_amount", "installment_rate", "age",
                "age_group", "existing_credits", "checking_status", "credit_history", "savings_status"
            ],
            categorical_columns=["checking_status", "credit_history", "savings_status", "age_group"],
            numeric_columns=["duration_months", "credit_amount", "installment_rate", "age", "existing_credits"],
            known_limitations=(
                "Small sample size (exactly 1,000 instances) limits statistical power for subgroup analysis. "
                "Asymmetric cost structure (cost matrix 5:1 for false positives) frequently ignored in standard benchmarks. "
                "Originates from 1970s West German bank credit scoring practices."
            ),
            is_synthetic_benchmark=False
        )
        super().__init__(metadata)

    def load_data(
        self,
        use_synthetic_benchmark: bool = False,
        local_path: Optional[str] = None
    ) -> pd.DataFrame:
        """Loads German Credit dataset or generates deterministic benchmark."""
        if use_synthetic_benchmark:
            self.metadata.is_synthetic_benchmark = True
            return self._generate_synthetic_benchmark()

        target_path = local_path or os.path.join("research", "data", f"{self.metadata.name}.csv")
        if target_path and os.path.exists(target_path):
            df = pd.read_csv(target_path)
            self.metadata.is_synthetic_benchmark = False
            return self._clean_german(df)

        raise FileNotFoundError(
            f"FINAL EXPERIMENT BLOCKED: German credit dataset file not found at '{target_path}'. "
            "Synthetic fallback is strictly prohibited in final confirmatory experiment mode. "
            "Pass use_synthetic_benchmark=True strictly for unit/smoke tests."
        )

    def _clean_german(self, df: pd.DataFrame) -> pd.DataFrame:
        """Cleans and recodes German credit dataset."""
        df = df.copy()
        # Recode target if raw format (1=Good, 2=Bad or 'good'/'bad')
        if "credit_risk" in df.columns:
            if df["credit_risk"].dtype == object or isinstance(df["credit_risk"].iloc[0], str):
                df["credit_risk"] = df["credit_risk"].astype(str).str.lower().map({"good": 1, "bad": 0}).fillna(df["credit_risk"])
            elif set(df["credit_risk"].dropna().unique()).issubset({1, 2}):
                df["credit_risk"] = df["credit_risk"].replace({1: 1, 2: 0})
            df["credit_risk"] = df["credit_risk"].astype(int)
        
        # Ensure age_group exists
        if "age" in df.columns and "age_group" not in df.columns:
            df["age_group"] = np.where(df["age"] >= 25, "Adult", "Young")
            
        return df

    def _generate_synthetic_benchmark(self, n_samples: int = 1000, seed: int = 42) -> pd.DataFrame:
        """
        Generates deterministic benchmark reflecting Statlog German Credit.
        Strictly for unit tests and CI. NOT empirical evidence.
        """
        rng = np.random.default_rng(seed)
        
        age = rng.integers(19, 75, size=n_samples)
        age_group = np.where(age >= 25, "Adult", "Young")
        duration = rng.integers(6, 60, size=n_samples)
        credit_amount = rng.integers(500, 15000, size=n_samples)
        installment = rng.integers(1, 5, size=n_samples)
        existing_credits = rng.integers(1, 4, size=n_samples)
        
        checking = rng.choice(["<0 DM", "0-200 DM", ">=200 DM", "no checking"], size=n_samples)
        history = rng.choice(["critical", "good", "all paid", "delayed"], size=n_samples)
        savings = rng.choice(["<100 DM", "100-500 DM", ">=1000 DM", "unknown"], size=n_samples)
        
        # Creditworthiness calculation with documented disparity against younger borrowers
        score = (age / 75.0) * 1.5 - (duration / 60.0) * 1.8 - (credit_amount / 15000.0) * 1.0
        age_bias = np.where(age_group == "Young", 0.4, 0.0)
        prob = 1.0 / (1.0 + np.exp(-(score - age_bias + rng.normal(0, 0.3, n_samples))))
        credit_risk = (prob > 0.45).astype(int)

        return pd.DataFrame({
            "duration_months": duration,
            "credit_amount": credit_amount,
            "installment_rate": installment,
            "age": age,
            "age_group": age_group,
            "existing_credits": existing_credits,
            "checking_status": checking,
            "credit_history": history,
            "savings_status": savings,
            "credit_risk": credit_risk
        })
