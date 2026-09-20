# Confirmatory Final Experiment Report: Faithfulness of LLM Explanations for ML Fairness Audits

**Topic:** Quantitative Faithfulness of LLM-Generated Natural-Language Explanations for Machine Learning Fairness Audits: An Empirical Study  
**Execution Mode:** `FINAL_EMPIRICAL_RUN`  
**Model Tested:** `gemini-2.5-flash`  
**Control Baseline:** Deterministic `TemplateExplainer`  
**Benchmark Datasets:** Adult Census Income, COMPAS Recidivism, German Credit (100% Real Data)  

---

## 1. Executive Summary

This confirmatory empirical experiment evaluated 36 paired experimental conditions across 3 benchmark datasets, 2 predictive model families (Logistic Regression, Random Forest), 2 fairness mitigations (Correlation Remover, Threshold Optimizer), and 3 random seeds (42, 123, 456), generating 72 explanations (36 Template Baseline + 36 Gemini 2.5 Flash).

### Key Empirical Findings:
- **Template Baseline Control:** Guaranteed **100.0%** Numerical Faithfulness and **100.0%** Directional Faithfulness with **0.0%** Unsupported Claims.
- **LLM (`gemini-2.5-flash`) Faithfulness:**
  - Mean Numerical Faithfulness: **88.1%** (demonstrating quantitative drift / numerical distortion).
  - Mean Directional Faithfulness: **94.2%**.
  - Mean Unsupported Claim Rate: **8.5%**.
- **Data Integrity:** **0% synthetic benchmark data**; 100% real benchmark CSV distributions.

---

## 2. Experimental Matrix Inventory

Total Planned Conditions: **36**  
Successfully Completed: **36**  
Failed Conditions: **0**  

| Condition Index | Dataset | Model | Mitigation | Seed | Template Num Faith | Gemini Num Faith | Gemini Dir Faith |
|---|---|---|---|---|---|---|---|
| 01 | adult | logistic_regression | correlation_remover | 123 | 100.0% | 81.6% | 92.9% |
| 02 | adult | logistic_regression | correlation_remover | 42 | 100.0% | 100.0% | N/A |
| 03 | adult | logistic_regression | correlation_remover | 456 | 100.0% | 100.0% | N/A |
| 04 | adult | logistic_regression | threshold_optimizer | 123 | 100.0% | 73.9% | 100.0% |
| 05 | adult | logistic_regression | threshold_optimizer | 42 | 100.0% | 91.7% | 100.0% |
| 06 | adult | logistic_regression | threshold_optimizer | 456 | 100.0% | 100.0% | N/A |
| 07 | adult | random_forest | correlation_remover | 123 | 100.0% | 91.4% | 100.0% |
| 08 | adult | random_forest | correlation_remover | 42 | 100.0% | 94.1% | N/A |
| 09 | adult | random_forest | correlation_remover | 456 | 100.0% | 90.6% | 100.0% |
| 10 | adult | random_forest | threshold_optimizer | 123 | 100.0% | 87.5% | N/A |
| 11 | adult | random_forest | threshold_optimizer | 42 | 100.0% | 100.0% | 100.0% |
| 12 | adult | random_forest | threshold_optimizer | 456 | 100.0% | 100.0% | 100.0% |
| 13 | compas | logistic_regression | correlation_remover | 123 | 100.0% | 93.1% | 100.0% |
| 14 | compas | logistic_regression | correlation_remover | 42 | 100.0% | 95.2% | 100.0% |
| 15 | compas | logistic_regression | correlation_remover | 456 | 100.0% | 70.6% | 0.0% |
| 16 | compas | logistic_regression | threshold_optimizer | 123 | 100.0% | 83.9% | 100.0% |
| 17 | compas | logistic_regression | threshold_optimizer | 42 | 100.0% | 78.3% | 100.0% |
| 18 | compas | logistic_regression | threshold_optimizer | 456 | 100.0% | 100.0% | N/A |
| 19 | compas | random_forest | correlation_remover | 123 | 100.0% | 100.0% | 100.0% |
| 20 | compas | random_forest | correlation_remover | 42 | 100.0% | 100.0% | N/A |
| 21 | compas | random_forest | correlation_remover | 456 | 100.0% | 100.0% | N/A |
| 22 | compas | random_forest | threshold_optimizer | 123 | 100.0% | 68.2% | N/A |
| 23 | compas | random_forest | threshold_optimizer | 42 | 100.0% | 74.2% | 80.0% |
| 24 | compas | random_forest | threshold_optimizer | 456 | 100.0% | 88.0% | 100.0% |
| 25 | german | logistic_regression | correlation_remover | 123 | 100.0% | 70.6% | N/A |
| 26 | german | logistic_regression | correlation_remover | 42 | 100.0% | 73.9% | 100.0% |
| 27 | german | logistic_regression | correlation_remover | 456 | 100.0% | 81.2% | 100.0% |
| 28 | german | logistic_regression | threshold_optimizer | 123 | 100.0% | 83.9% | 93.3% |
| 29 | german | logistic_regression | threshold_optimizer | 42 | 100.0% | 63.6% | N/A |
| 30 | german | logistic_regression | threshold_optimizer | 456 | 100.0% | 84.1% | 100.0% |
| 31 | german | random_forest | correlation_remover | 123 | 100.0% | 88.9% | 100.0% |
| 32 | german | random_forest | correlation_remover | 42 | 100.0% | 100.0% | 100.0% |
| 33 | german | random_forest | correlation_remover | 456 | 100.0% | 91.4% | 100.0% |
| 34 | german | random_forest | threshold_optimizer | 123 | 100.0% | 94.4% | 100.0% |
| 35 | german | random_forest | threshold_optimizer | 42 | 100.0% | 84.6% | N/A |
| 36 | german | random_forest | threshold_optimizer | 456 | 100.0% | 93.8% | N/A |
