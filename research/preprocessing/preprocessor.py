"""
Leak-Free Preprocessing Pipeline for Machine Learning Fairness Experiments.
Guarantees that all scalers, imputers, and categorical encoders are fitted
strictly on the training split without leaking validation or test data.
"""
from typing import List, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer


class ResearchPreprocessor:
    """
    Leak-free tabular preprocessor.
    Stores fitted transformers and output feature names.
    """

    def __init__(
        self,
        categorical_columns: Optional[List[str]] = None,
        numeric_columns: Optional[List[str]] = None,
        drop_sensitive_from_features: bool = False,
        sensitive_col: Optional[str] = None
    ):
        self.categorical_columns = categorical_columns or []
        self.numeric_columns = numeric_columns or []
        self.drop_sensitive_from_features = drop_sensitive_from_features
        self.sensitive_col = sensitive_col
        
        self.num_imputer = SimpleImputer(strategy="median")
        self.scaler = StandardScaler()
        self.cat_imputer = SimpleImputer(strategy="most_frequent")
        self.encoder = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
        
        self.is_fitted = False
        self.transformed_feature_names: List[str] = []

    def fit(self, X: pd.DataFrame) -> "ResearchPreprocessor":
        """Fit transformers strictly on the training partition."""
        X_copy = X.copy()
        if self.drop_sensitive_from_features and self.sensitive_col in X_copy.columns:
            X_copy = X_copy.drop(columns=[self.sensitive_col])

        # Automatically determine numeric and categorical columns if not explicitly passed
        if not self.numeric_columns and not self.categorical_columns:
            self.numeric_columns = list(X_copy.select_dtypes(include=[np.number]).columns)
            self.categorical_columns = [c for c in X_copy.columns if c not in self.numeric_columns]
        else:
            # Filter to columns present in X_copy
            self.numeric_columns = [c for c in self.numeric_columns if c in X_copy.columns]
            self.categorical_columns = [c for c in self.categorical_columns if c in X_copy.columns]

        # Fit numeric pipeline
        if self.numeric_columns:
            num_data = X_copy[self.numeric_columns]
            num_imputed = self.num_imputer.fit_transform(num_data)
            self.scaler.fit(num_imputed)

        # Fit categorical pipeline
        if self.categorical_columns:
            cat_data = X_copy[self.categorical_columns].astype(str)
            cat_imputed = self.cat_imputer.fit_transform(cat_data)
            self.encoder.fit(cat_imputed)

        # Build feature names
        names = []
        if self.numeric_columns:
            names.extend(self.numeric_columns)
        if self.categorical_columns:
            cat_names = self.encoder.get_feature_names_out(self.categorical_columns)
            names.extend(list(cat_names))
            
        self.transformed_feature_names = names
        self.is_fitted = True
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """Transform partition using previously fitted statistics."""
        if not self.is_fitted:
            raise RuntimeError("Preprocessor must be fitted on training data before calling transform.")
            
        X_copy = X.copy()
        if self.drop_sensitive_from_features and self.sensitive_col in X_copy.columns:
            X_copy = X_copy.drop(columns=[self.sensitive_col])

        parts = []
        if self.numeric_columns:
            num_data = X_copy[self.numeric_columns]
            num_imputed = self.num_imputer.transform(num_data)
            num_scaled = self.scaler.transform(num_imputed)
            parts.append(pd.DataFrame(num_scaled, columns=self.numeric_columns))

        if self.categorical_columns:
            cat_data = X_copy[self.categorical_columns].astype(str)
            cat_imputed = self.cat_imputer.transform(cat_data)
            cat_encoded = self.encoder.transform(cat_imputed)
            cat_names = self.encoder.get_feature_names_out(self.categorical_columns)
            parts.append(pd.DataFrame(cat_encoded, columns=cat_names))

        if not parts:
            raise ValueError("No features available after preprocessing.")

        transformed_df = pd.concat(parts, axis=1)
        return transformed_df

    def fit_transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """Fit on training data and transform in a single step."""
        return self.fit(X).transform(X)
