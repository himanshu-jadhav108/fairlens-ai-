# 5. Experimental Setup

<!-- PROVISIONAL SCAFFOLD ONLY -->

## 5.1 Benchmark Datasets
- **Adult Census Income:** Source UCI; Target: `income` (>50K); Sensitive: `sex`.
- **COMPAS Recidivism:** Source ProPublica; Target: `two_year_recid`; Sensitive: `race`.
- **Statlog German Credit:** Source UCI; Target: `credit_risk`; Sensitive: `age_group`.

## 5.2 Model Architectures
- **Logistic Regression:** Linear baseline (`max_iter=500`, `solver=liblinear`).
- **Random Forest:** Bagged ensemble (`n_estimators=100`, `max_depth=10`).
- **XGBoost:** Gradient boosted trees (`n_estimators=100`, `max_depth=5`, `learning_rate=0.1`).

## 5.3 Data Partitioning & Leakage Prevention
- 60% Train (model fitting), 20% Validation (threshold calibration / tuning), 20% Test (final evaluation).
- Stratification across labels; sensitive feature alignment preserved.
- All transformers (StandardScaler, OneHotEncoder, SimpleImputer) fitted strictly on training data.

## 5.4 Random Seeds & Experimental Replications
- Evaluated across 5 random seeds: `42, 123, 456, 789, 2026`.
- *Caveat:* Seeds reflect split variance, not independent sampling observations.

## 5.5 Provenance & Manifest Tracking
- Every run logged to `research/results/manifests/` with Git commit hash, environment metadata, and timestamps.
