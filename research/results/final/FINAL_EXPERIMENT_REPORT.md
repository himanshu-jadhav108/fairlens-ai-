# Confirmatory Final Experiment Report: Faithfulness of LLM Explanations for ML Fairness Audits

**Topic:** Quantitative Faithfulness of LLM-Generated Natural-Language Explanations for Machine Learning Fairness Audits: An Empirical Study  
**Execution Mode:** `FINAL_EMPIRICAL_RUN`  
**Primary Model Tested:** `gemini-2.5-flash` (`combined_audit_v1`, temperature=0.2, top_p=0.95, max_output_tokens=1500)  
**Control Baseline:** Deterministic `TemplateExplainer` (rule-based natural language template)  
**Benchmark Datasets:** Adult Census Income ($N=48,842$), COMPAS Recidivism ($N=7,214$), German Credit ($N=1,000$) — 100% Real Benchmark Data  
**Experimental Design:** $3 \times 2 \times 2 \times 3 = 36$ canonical conditions (72 explanation runs)  

---

## 1. Executive Summary

This confirmatory empirical experiment evaluated 36 paired experimental conditions across 3 benchmark datasets, 2 predictive model families (Logistic Regression, Random Forest), 2 fairness mitigations (Correlation Remover, Threshold Optimizer), and 3 random seeds (42, 123, 456), generating 72 explanations (36 Template Baseline + 36 Gemini 2.5 Flash).

### Key Empirical Findings:
- **Template Baseline Control ($N=36$):** Guaranteed **100.00% ± 0.00%** Numerical Faithfulness and **100.00% ± 0.00%** Directional Faithfulness with **0.00% ± 0.00%** Unsupported Claims.
- **LLM (`gemini-2.5-flash`) Faithfulness ($N=36$):**
  - Mean Numerical Faithfulness: **88.13% ± 10.82%** (mean degradation: -11.87 percentage points, Cohen's $d = -1.097$, paired $t = -6.581, p = 1.34 \times 10^{-7}$).
  - Mean Directional Faithfulness ($N=23$ evaluable pairs): **94.18% ± 21.02%** (mean difference: -5.82 percentage points, Cohen's $d = -0.277$, paired $t = -1.328, p = 0.1979$, Wilcoxon $W = 0.0, p = 0.0679$; not statistically significant at $\alpha = 0.05$).
  - Mean Unsupported Claim Rate: **8.51% ± 8.72%** (paired $t = 5.854, p = 1.20 \times 10^{-6}$).
- **Data & Artifact Integrity:** 100% authentic benchmark distributions; zero synthetic fallback; legacy retries quarantined in `research/results/legacy_retries/`.

---

## 2. Canonical Experimental Matrix Inventory ($N=36$)

Total Planned Conditions: **36**  
Successfully Completed: **36**  
Failed Conditions: **0**  

| Index | Dataset | Model | Mitigation | Seed | Template Num Faith | Gemini Num Faith | Gemini Dir Faith | Gemini Unsup Rate |
|---|---|---|---|---|---|---|---|---|
| 01 | adult | logistic_regression | correlation_remover | 123 | 100.0% | 81.6% | 92.9% | 15.1% |
| 02 | adult | logistic_regression | correlation_remover | 42 | 100.0% | 100.0% | N/A | 0.0% |
| 03 | adult | logistic_regression | correlation_remover | 456 | 100.0% | 100.0% | N/A | 0.0% |
| 04 | adult | logistic_regression | threshold_optimizer | 123 | 100.0% | 73.9% | 100.0% | 21.4% |
| 05 | adult | logistic_regression | threshold_optimizer | 42 | 100.0% | 91.7% | 100.0% | 3.1% |
| 06 | adult | logistic_regression | threshold_optimizer | 456 | 100.0% | 100.0% | N/A | 0.0% |
| 07 | adult | random_forest | correlation_remover | 123 | 100.0% | 91.4% | 100.0% | 4.8% |
| 08 | adult | random_forest | correlation_remover | 42 | 100.0% | 94.1% | N/A | 3.1% |
| 09 | adult | random_forest | correlation_remover | 456 | 100.0% | 90.6% | 100.0% | 6.7% |
| 10 | adult | random_forest | threshold_optimizer | 123 | 100.0% | 87.5% | N/A | 8.7% |
| 11 | adult | random_forest | threshold_optimizer | 42 | 100.0% | 100.0% | 100.0% | 0.0% |
| 12 | adult | random_forest | threshold_optimizer | 456 | 100.0% | 100.0% | 100.0% | 0.0% |
| 13 | compas | logistic_regression | correlation_remover | 123 | 100.0% | 93.1% | 100.0% | 5.0% |
| 14 | compas | logistic_regression | correlation_remover | 42 | 100.0% | 95.2% | 100.0% | 3.5% |
| 15 | compas | logistic_regression | correlation_remover | 456 | 100.0% | 70.6% | 0.0% | 10.5% |
| 16 | compas | logistic_regression | threshold_optimizer | 123 | 100.0% | 83.9% | 100.0% | 12.2% |
| 17 | compas | logistic_regression | threshold_optimizer | 42 | 100.0% | 78.3% | 100.0% | 14.7% |
| 18 | compas | logistic_regression | threshold_optimizer | 456 | 100.0% | 100.0% | N/A | 0.0% |
| 19 | compas | random_forest | correlation_remover | 123 | 100.0% | 100.0% | 100.0% | 0.0% |
| 20 | compas | random_forest | correlation_remover | 42 | 100.0% | 100.0% | N/A | 0.0% |
| 21 | compas | random_forest | correlation_remover | 456 | 100.0% | 100.0% | N/A | 0.0% |
| 22 | compas | random_forest | threshold_optimizer | 123 | 100.0% | 68.2% | N/A | 24.1% |
| 23 | compas | random_forest | threshold_optimizer | 42 | 100.0% | 74.2% | 80.0% | 23.7% |
| 24 | compas | random_forest | threshold_optimizer | 456 | 100.0% | 88.0% | 100.0% | 7.1% |
| 25 | german | logistic_regression | correlation_remover | 123 | 100.0% | 70.6% | N/A | 27.8% |
| 26 | german | logistic_regression | correlation_remover | 42 | 100.0% | 73.9% | 100.0% | 12.2% |
| 27 | german | logistic_regression | correlation_remover | 456 | 100.0% | 81.2% | 100.0% | 11.1% |
| 28 | german | logistic_regression | threshold_optimizer | 123 | 100.0% | 83.9% | 93.3% | 14.1% |
| 29 | german | logistic_regression | threshold_optimizer | 42 | 100.0% | 63.6% | N/A | 33.3% |
| 30 | german | logistic_regression | threshold_optimizer | 456 | 100.0% | 84.1% | 100.0% | 11.9% |
| 31 | german | random_forest | correlation_remover | 123 | 100.0% | 88.9% | 100.0% | 7.6% |
| 32 | german | random_forest | correlation_remover | 42 | 100.0% | 100.0% | 100.0% | 0.0% |
| 33 | german | random_forest | correlation_remover | 456 | 100.0% | 91.4% | 100.0% | 6.4% |
| 34 | german | random_forest | threshold_optimizer | 123 | 100.0% | 94.4% | 100.0% | 4.3% |
| 35 | german | random_forest | threshold_optimizer | 42 | 100.0% | 84.6% | N/A | 8.7% |
| 36 | german | random_forest | threshold_optimizer | 456 | 100.0% | 93.8% | N/A | 5.3% |
