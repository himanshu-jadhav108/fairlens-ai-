# FairLens AI Research — Data Leakage & Split Isolation Audit

**Branch:** `research/fairness-xai-study`  
**Date:** 2026-09-17  
**Auditor:** Automated Reproducibility & Integrity Verification  
**Status:** `VERIFIED — 0 DATA LEAKAGE PATHWAYS DETECTED`

---

## 1. Executive Summary

A comprehensive line-by-line audit of the experimental pipeline (`research/experiments/runner.py`, `research/preprocessing/preprocessor.py`, `research/explainability/shap_engine.py`) confirms that strict partition isolation is maintained across all training, validation, testing, and explanation stages. No information from validation or test splits is exposed during feature scaling, categorical encoding, model fitting, threshold calibration, or SHAP background sampling.

---

## 2. Preprocessing Isolation Audit

### 2.1 Fit Call Sites
- **Source Location:** `research/experiments/runner.py`, lines 78–86
- **Code Execution:**
  ```python
  preprocessor = ResearchPreprocessor(
      categorical_columns=dataset_loader.metadata.categorical_columns,
      numeric_columns=dataset_loader.metadata.numeric_columns,
      drop_sensitive_from_features=False,
      sensitive_col=dataset_loader.metadata.sensitive_column
  )
  X_train_proc = preprocessor.fit_transform(splits.X_train)
  X_val_proc = preprocessor.transform(splits.X_val)
  X_test_proc = preprocessor.transform(splits.X_test)
  ```
- **Verification:**
  - `fit()` / `fit_transform()` is invoked **strictly** on `splits.X_train`.
  - Imputation statistics (mean/median/mode) and `StandardScaler` parameters ($\mu, \sigma$) are computed exclusively on the training partition.
  - `OneHotEncoder` categories are established from the training set; unseen categories in `val` or `test` are handled using `handle_unknown="ignore"`.
  - `X_val` and `X_test` are strictly transformed via `.transform()` without re-fitting.

---

## 3. Train / Validation / Test Split Integrity

### 3.1 Partitioning Logic
- **Source Location:** `research/datasets/base.py` (`BaseDataset.create_splits`)
- **Default Ratios:** 60% Training, 20% Validation, 20% Testing (`train_ratio=0.6, val_ratio=0.2, test_ratio=0.2`).
- **Stratification:** Splits are stratified by the target label $y$ and sensitive attribute $s$ jointly, ensuring identical demographic and outcome proportions across splits.
- **Split Hash:** Every `DatasetSplit` computes a deterministic SHA-256 fingerprint of the data indices to guarantee exact reproducibility under identical random seeds.

### 3.2 Partition Role Separation Matrix
| Split | Permitted Operations | Forbidden Operations |
|:---|:---|:---|
| **Train (`X_train, y_train, s_train`)** | Preprocessor fitting, Base model training, In-processing mitigation fitting, SHAP background distribution | Threshold tuning, Final fairness evaluation, Final performance evaluation |
| **Validation (`X_val, y_val, s_val`)** | Post-processing threshold calibration (e.g. ThresholdOptimizer), Hyperparameter selection | Preprocessor fitting, Model fitting, Final evaluation reporting |
| **Test (`X_test, y_test, s_test`)** | Final model scoring (`predict`, `predict_proba`), Final fairness metrics, Final performance metrics, SHAP evaluation instances | Preprocessor fitting, Model training, Threshold calibration |

---

## 4. Mitigation Threshold Calibration Verification

### 4.1 Post-Processing Split Isolation
- **Source Location:** `research/experiments/runner.py`, lines 116–124
- **Code Execution:**
  ```python
  mitigation.fit(
      X_train=X_train_proc,
      y_train=splits.y_train,
      s_train=splits.s_train,
      X_val=X_val_proc,
      y_val=splits.y_val,
      s_val=splits.s_val
  )
  ```
- **Verification:**
  - For `ThresholdOptimizer` (`research/mitigation/threshold_optimizer.py`), decision thresholds are tuned exclusively using `X_val_proc` and `y_val, s_val`.
  - The test split (`X_test_proc, y_test, s_test`) is never supplied to `fit()`.
  - Testing is performed strictly via `predict()` and `predict_proba()` at line 127.

---

## 5. SHAP Background Distribution Audit

### 5.1 Explainability Sampling Isolation
- **Source Location:** `research/experiments/runner.py`, lines 153–165
- **Code Execution:**
  ```python
  mit_shap_engine = SHAPEngine(
      estimator=mitigation.get_mitigated_estimator(),
      X_train=X_train_proc,
      X_test=X_test_proc,
      feature_names=proc_feature_names,
      sensitive_test=splits.s_test.values,
      explainer_type=config.explainer_type,
      n_eval_samples=config.n_eval_samples,
      n_background_samples=config.n_background_samples,
      random_seed=config.seed
  )
  ```
- **Verification:**
  - `SHAPEngine` background reference distribution uses k-means or random sampling drawn **strictly** from `X_train_proc`.
  - The test set (`X_test_proc`) is used exclusively as evaluation instances to explain test predictions.
  - No baseline reference values are computed from test data, preventing attribution data leakage.

---

## 6. Synthetic Benchmark Split Verification

### 6.1 Benchmark Parity
- **Source Location:** `research/datasets/adult.py`, `compas.py`, `german.py` (`load_data(use_synthetic_benchmark=True)`)
- **Verification:**
  - Synthetic benchmark datasets generate dataframes matching the exact feature schema, data types, and sensitive attribute encodings of real datasets.
  - The synthetic data flows through the identical `create_splits()` logic, producing valid, non-overlapping train/val/test splits.
  - Verified by tests: `test_synthetic_benchmark_loading[adult]`, `test_synthetic_benchmark_loading[compas]`, and `test_synthetic_benchmark_loading[german]` in `test_datasets.py`.
