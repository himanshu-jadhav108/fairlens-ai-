"""
Core ML pipeline for FairLens AI.
Handles model training, fairness metric computation, SHAP, and mitigation.
"""
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from typing import Tuple, Dict, Any, Optional
import warnings

from .ml.fairness_engine import FairnessEngine

warnings.filterwarnings("ignore")


# ─── Data Preparation ────────────────────────────────────────────────────────

def prepare_dataset(
    df: pd.DataFrame,
    target_col: str,
    sensitive_col: str,
    drop_sensitive: bool = False
) -> Tuple[pd.DataFrame, pd.Series, pd.Series]:
    """
    Prepare dataset for ML training.
    Returns: X (features), y (target), sensitive (sensitive attribute series)
    """
    df = df.copy()

    # Fill NaNs for target and sensitive columns
    df[target_col] = df[target_col].fillna(df[target_col].mode()[0] if not df[target_col].mode().empty else 0)
    df[sensitive_col] = df[sensitive_col].fillna(df[sensitive_col].mode()[0] if not df[sensitive_col].mode().empty else 0)

    # Force sensitive to be string so it is categorically encoded properly
    df[sensitive_col] = df[sensitive_col].astype(str)

    # Encode target if categorical
    le_y = LabelEncoder()
    df[target_col] = le_y.fit_transform(df[target_col].astype(str) if df[target_col].dtype == object else df[target_col])

    # Encode sensitive attribute
    le_s = LabelEncoder()
    df[sensitive_col] = le_s.fit_transform(df[sensitive_col])
    sensitive = pd.Series(df[sensitive_col], name=sensitive_col)

    # Encode all remaining categorical columns
    for col in df.select_dtypes(include=["object", "category"]).columns:
        if col not in [target_col, sensitive_col]:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype(str))

    y = df[target_col]

    if drop_sensitive:
        X = df.drop(columns=[target_col, sensitive_col], errors="ignore")
    else:
        X = df.drop(columns=[target_col], errors="ignore")

    # Fill NaN for X
    X = X.fillna(X.median(numeric_only=True))
    X = X.fillna(0)

    return X, y, sensitive


def train_logistic_model(
    X_train: pd.DataFrame,
    y_train: pd.Series,
) -> Tuple[LogisticRegression, StandardScaler]:
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_train)
    model = LogisticRegression(max_iter=1000, random_state=42)
    model.fit(X_scaled, y_train)
    return model, scaler


# ─── Fairness Scoring ────────────────────────────────────────────────────────

def compute_fairness_score(metrics: Dict[str, Any]) -> Tuple[float, str]:
    """
    Score formula: starts at 100.
    Penalty for DPD, EOD, and DI, plus Accuracy thresholding.
    """
    dpd = metrics.get('demographic_parity_difference', 0.0)
    eod = metrics.get('equalized_odds_difference', 0.0)
    di = metrics.get('disparate_impact_ratio', 1.0)
    acc = metrics.get('accuracy', 0.0)
    
    dpd_penalty = min(dpd * 150, 30) # Max 30
    eod_penalty = min(eod * 150, 30) # Max 30
    di_penalty = max((0.8 - di) * 100, 0) # Penalty if DI < 0.8
    acc_penalty = max((0.8 - acc) * 100, 0) # Penalty if acc < 0.8
    
    score = 100.0 - dpd_penalty - eod_penalty - di_penalty - acc_penalty
    score = max(0.0, min(100.0, score))
    
    if score >= 80:
        label = "Fair"
    elif score >= 50:
        label = "Moderate Risk"
    else:
        label = "High Risk"
        
    return round(score, 1), label


# ─── Pipeline Execution ──────────────────────────────────────────────────────

def run_full_analysis(
    df: pd.DataFrame,
    target_col: str,
    sensitive_col: str,
    drop_sensitive: bool = False
) -> Dict[str, Any]:
    """
    Full pipeline: prepare → split → train → predict → metrics.
    Returns all artifacts needed by the API.
    """
    X, y, sensitive = prepare_dataset(df, target_col, sensitive_col, drop_sensitive)

    X_train, X_test, y_train, y_test, s_train, s_test = train_test_split(
        X, y, sensitive, test_size=0.3, random_state=42, stratify=y if y.nunique() <= 10 else None
    )

    model, scaler = train_logistic_model(X_train, y_train)
    X_test_scaled = scaler.transform(X_test)
    y_pred = model.predict(X_test_scaled)

    # Instantiate FairnessEngine instead of manual math
    engine = FairnessEngine(y_test.values, y_pred, s_test.values, sensitive_col)
    metrics_payload = engine.compute_all_metrics()
    
    score, label = compute_fairness_score(metrics_payload)
    metrics_payload["fairness_score"] = score
    metrics_payload["fairness_label"] = label

    return {
        "model": model,
        "scaler": scaler,
        "X_train": X_train,
        "X_test": X_test,
        "X_test_scaled": X_test_scaled,
        "y_train": y_train,
        "y_test": y_test,
        "s_test": s_test,
        "y_pred": y_pred,
        "feature_names": list(X.columns),
        "metrics": metrics_payload,
    }


# ─── SHAP Explainability ──────────────────────────────────────────────────────

# Legacy compute_shap_values removed. SHAP is now handled by ExplainabilityEngine.


from .ml.mitigation_engine import MitigationEngine

def apply_advanced_mitigation(
    df: pd.DataFrame,
    target_col: str,
    sensitive_col: str
) -> Dict[str, Any]:
    """
    Advanced Multi-Strategy Mitigation Engine using Fairlearn.
    Evaluates Pre-processing, In-processing, and Post-processing strategies.
    Returns the strategy with the best fairness score tradeoffs.
    """
    X, y, sensitive = prepare_dataset(df, target_col, sensitive_col, drop_sensitive=True)
    X_train, X_test, y_train, y_test, s_train, s_test = train_test_split(
        X, y, sensitive, test_size=0.3, random_state=42,
        stratify=y if y.nunique() <= 10 else None
    )

    # Scale the data first (Fairlearn models require scaled numericals for convergence)
    scaler = StandardScaler()
    X_train_scaled = pd.DataFrame(scaler.fit_transform(X_train), columns=X_train.columns)
    X_test_scaled = pd.DataFrame(scaler.transform(X_test), columns=X_test.columns)
    X_full_scaled = pd.DataFrame(scaler.transform(X), columns=X.columns)

    engine = MitigationEngine(
        X_train=X_train_scaled, y_train=y_train, 
        X_test=X_test_scaled, y_test=y_test, 
        s_train=s_train, s_test=s_test, 
        sensitive_col=sensitive_col,
        X_full=X_full_scaled, s_full=sensitive
    )

    results = {}

    # 1. Pre-processing
    pre_metrics, pre_y_pred_full = engine.run_preprocessing_mitigation()
    if pre_metrics:
        score, _ = compute_fairness_score(pre_metrics)
        pre_metrics["fairness_score"] = score
        results["CorrelationRemover (Pre-processing)"] = {
            "metrics": pre_metrics,
            "y_pred_full": pre_y_pred_full
        }

    # 2. In-processing
    in_metrics, in_y_pred_full = engine.run_inprocessing_mitigation()
    if in_metrics:
        score, _ = compute_fairness_score(in_metrics)
        in_metrics["fairness_score"] = score
        results["ExponentiatedGradient (In-processing)"] = {
            "metrics": in_metrics,
            "y_pred_full": in_y_pred_full
        }

    # 3. Post-processing
    post_metrics, post_y_pred_full = engine.run_postprocessing_mitigation()
    if post_metrics:
        score, _ = compute_fairness_score(post_metrics)
        post_metrics["fairness_score"] = score
        results["ThresholdOptimizer (Post-processing)"] = {
            "metrics": post_metrics,
            "y_pred_full": post_y_pred_full
        }

    if not results:
        raise RuntimeError("All mitigation strategies failed.")

    # Select best strategy based on highest fairness_score
    best_strategy = max(results.items(), key=lambda x: x[1]["metrics"]["fairness_score"])[0]

    return {
        "metrics": results[best_strategy]["metrics"],
        "strategy": best_strategy,
        "y_pred_full": results[best_strategy]["y_pred_full"],
        "all_results": {k: v["metrics"] for k, v in results.items()}
    }
