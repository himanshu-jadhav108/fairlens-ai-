"""
ProPublica COMPAS Dataset Loader and Provenance Specification.
"""
import os
from typing import Optional
import numpy as np
import pandas as pd
from .base import BaseDataset, DatasetMetadata


class COMPASDataset(BaseDataset):
    """
    ProPublica COMPAS Recidivism Benchmark Dataset.
    Target: two_year_recid (0: No Recidivism [Favorable], 1: Recidivism).
    Sensitive Attribute: race (Caucasian vs African-American).
    """

    def __init__(self):
        metadata = DatasetMetadata(
            name="compas",
            official_title="ProPublica COMPAS Recidivism Risk Assessment Dataset",
            source_url="https://github.com/propublica/compas-analysis",
            version_or_release="2016 Broward County Release",
            license_name="Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)",
            license_restrictions="Academic non-commercial research use. Derived from Broward County public records.",
            download_instructions=(
                "Download compas-scores-two-years.csv from ProPublica's GitHub repository. "
                "Apply ProPublica standard filtering (days_b_screening_arrest between -30 and 30, "
                "is_recid != -1, c_charge_degree != 'O'). Do not commit to public VCS without license review."
            ),
            target_column="two_year_recid",
            sensitive_column="race",
            privileged_value="Caucasian",
            unprivileged_value="African-American",
            favorable_outcome_value=0,
            feature_names=[
                "age", "priors_count", "c_charge_degree", "race", "sex", "decile_score"
            ],
            categorical_columns=["c_charge_degree", "race", "sex"],
            numeric_columns=["age", "priors_count", "decile_score"],
            known_limitations=(
                "Recidivism is operationalized as re-arrest within two years, which reflects policing "
                "surveillance intensity rather than pure underlying criminal behavior. "
                "Well-documented false positive rate disparities between African-American and Caucasian defendants."
            ),
            is_synthetic_benchmark=False
        )
        super().__init__(metadata)

    def load_data(
        self,
        use_synthetic_benchmark: bool = False,
        local_path: Optional[str] = None
    ) -> pd.DataFrame:
        """Loads COMPAS dataset from local file or generates deterministic benchmark."""
        target_path = local_path or os.path.join("research", "data", f"{self.metadata.name}.csv")
        if target_path and os.path.exists(target_path):
            df = pd.read_csv(target_path)
            self.metadata.is_synthetic_benchmark = False
            return self._clean_compas(df)

        if use_synthetic_benchmark or local_path is None:
            self.metadata.is_synthetic_benchmark = True
            return self._generate_synthetic_benchmark()

        raise FileNotFoundError(
            f"COMPAS dataset file not found at '{local_path}'. "
            "Pass use_synthetic_benchmark=True for unit/smoke tests."
        )

    def _clean_compas(self, df: pd.DataFrame) -> pd.DataFrame:
        """Applies standard ProPublica cleaning criteria."""
        df = df.copy()
        if "days_b_screening_arrest" in df.columns:
            df = df[(df["days_b_screening_arrest"] <= 30) & (df["days_b_screening_arrest"] >= -30)]
        if "is_recid" in df.columns:
            df = df[df["is_recid"] != -1]
        if "c_charge_degree" in df.columns:
            df = df[df["c_charge_degree"] != "O"]
        if "race" in df.columns:
            df = df[df["race"].isin(["African-American", "Caucasian"])]
            
        required_cols = ["age", "priors_count", "c_charge_degree", "race", "sex", "two_year_recid"]
        available = [c for c in required_cols if c in df.columns]
        return df[available].reset_index(drop=True)

    def _generate_synthetic_benchmark(self, n_samples: int = 1500, seed: int = 42) -> pd.DataFrame:
        """
        Generates deterministic benchmark reflecting COMPAS schema and documented disparities.
        Strictly for unit tests and CI. NOT empirical evidence.
        """
        rng = np.random.default_rng(seed)
        
        race = rng.choice(["African-American", "Caucasian"], size=n_samples, p=[0.55, 0.45])
        sex = rng.choice(["Male", "Female"], size=n_samples, p=[0.80, 0.20])
        age = rng.integers(18, 70, size=n_samples)
        
        # Priors count
        priors_rate = np.where(race == "African-American", 4.2, 2.8)
        priors_count = rng.poisson(priors_rate, size=n_samples)
        c_charge = rng.choice(["F", "M"], size=n_samples, p=[0.65, 0.35])
        
        # Score and recidivism risk
        risk_score = (age / 70.0) * -1.5 + (priors_count / 10.0) * 2.0
        disparity = np.where(race == "African-American", 0.4, 0.0)
        prob = 1.0 / (1.0 + np.exp(-(risk_score + disparity + rng.normal(0, 0.4, n_samples))))
        two_year_recid = (prob > 0.5).astype(int)
        
        decile_score = np.clip((prob * 10).astype(int) + 1, 1, 10)

        return pd.DataFrame({
            "age": age,
            "priors_count": priors_count,
            "c_charge_degree": c_charge,
            "race": race,
            "sex": sex,
            "decile_score": decile_score,
            "two_year_recid": two_year_recid
        })
