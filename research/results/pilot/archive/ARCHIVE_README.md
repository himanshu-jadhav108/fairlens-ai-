# Pilot Artifacts Archive

This directory contains historical exploratory pilot artifacts segregated from active experimental analysis:

## 1. `lite_model_runs/`
- **Exclusion Classification:** `EXCLUDED_FROM_FINAL_CONFIRMATORY_ANALYSIS`
- **Reason:** Generated using `gemini-flash-lite-latest` rather than the locked primary model `gemini-2.5-flash`.
- **Count:** 5 experimental runs (and matching template records).

## 2. `duplicate_runs/`
- **Exclusion Classification:** `DUPLICATE_EXCLUDED_FROM_FINAL_ANALYSIS`
- **Reason:** Duplicate execution of condition `compas__logistic_regression__correlation_remover__seed456` (`e61a33c9`).
- **Count:** 1 experimental run (and matching template record).

All raw files are preserved intact for complete provenance tracking.
