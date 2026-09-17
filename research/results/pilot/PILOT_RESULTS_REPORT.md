# FairLens AI: Empirical Pilot Results Report (Phase 2)

**Study Title:** Quantitative Faithfulness of LLM-Generated Natural-Language Explanations for Machine Learning Fairness Audits: An Empirical Study  
**Execution Mode:** `PILOT_VALIDATION_RUN`  
**Evaluation Date:** 2026-09-17  
**Status:** Completed (24/24 Planned Matrix Conditions Executed)

---

## 1. Executive Summary

This empirical pilot study executes a 24-condition factorial matrix designed to quantitatively evaluate the faithfulness of Large Language Model (LLM) explanations against deterministic ground-truth Structured Audit Evidence.

The pilot evaluates:
- **2 Datasets:** `adult` (Adult Census Income), `compas` (ProPublica COMPAS Recidivism)
- **2 ML Classifiers:** `logistic_regression`, `random_forest`
- **2 Fairness Mitigations:** `correlation_remover` (preprocessing), `threshold_optimizer` (postprocessing)
- **3 Random Seeds:** `42`, `123`, `456`
- **LLM Evaluated:** Google Gemini via live API calls (`gemini-2.5-flash` / `gemini-flash-lite-latest` fallback)
- **Baseline Comparator:** Deterministic rule-based template generator (`template_baseline`)

All 24 experimental conditions were successfully executed with zero errors, producing 24 complete evidence manifests, raw explanations, and fine-grained NLI claim evaluations.

---

## 2. Core Quantitative Findings

| Metric | Deterministic Template | Live LLM (Gemini) | Paired Difference ($\Delta$) | 95% Confidence Interval | Effect Size (Cohen's $d$) | Statistical Significance |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Numerical Faithfulness** | **83.56%** $\pm$ 0.69% | 54.59% $\pm$ 23.19% | **-28.97%** | [-38.06%, -19.87%] | $d = -1.77$ (Large) | $p = 1.97 \times 10^{-6}$ (***) |
| **Directional Faithfulness** | **100.00%** $\pm$ 0.00% | 64.77% $\pm$ 37.61% | **-35.23%** | [-49.98%, -20.49%] | $d = -1.32$ (Large) | $p = 2.79 \times 10^{-4}$ (***) |
| **Attribution Faithfulness** | **100.00%** $\pm$ 0.00% | **100.00%** $\pm$ 0.00% | 0.00% | [0.00%, 0.00%] | $d = 0.00$ | $p = \text{N/A}$ |
| **Unsupported Claim Rate** | **0.00%** $\pm$ 0.00% | 6.31% $\pm$ 5.38% | **+6.31%** | [+4.20%, +8.42%] | $d = +1.66$ (Large) | $p = 1.31 \times 10^{-4}$ (***) |
| **Numerical MAE** | **0.0000** $\pm$ 0.0000 | 0.0132 $\pm$ 0.0184 | **+0.0132** | [+0.0055, +0.0209] | $d = +1.02$ (Large) | $p = 2.93 \times 10^{-4}$ (***) |
| **Total Claims Extracted** | 52.12 $\pm$ 3.44 | 29.68 $\pm$ 20.35 | -22.44 | [-30.53, -14.35] | $d = -1.54$ (Large) | $p = 4.20 \times 10^{-4}$ (***) |

*(***) denotes statistical significance at $p < 0.001$ via two-tailed Wilcoxon signed-rank test.*

---

## 3. Key Observations & Failure Modes

### 3.1 Hallucinated and Inaccurate Numbers
- The LLM explanation achieved an average numerical faithfulness of **54.59%**, failing on nearly half of numerical assertions.
- Common failure pattern: Rounding discrepancies exceeding tolerance, attributing post-mitigation fairness metrics to baseline models, or citing group-specific base rates instead of global metric differences.

### 3.2 Directional Inversion
- In **35.23%** of directional comparisons, the LLM misstated the direction of mitigation impact (e.g. stating that demographic parity difference decreased when it actually increased or remained static).
- In contrast, the deterministic template maintained **100.00%** directional fidelity.

### 3.3 Hallucinated External Context (Unsupported Claims)
- The LLM exhibited an unsupported claim rate of **6.31%**.
- Qualitative analysis indicates the model frequently introduced ungrounded claims regarding external legal thresholds ("violating the 80% four-fifths rule") or sociodemographic causal explanations not provided in the Structured Audit Evidence JSON.

### 3.4 Robust Feature Attribution
- Both the deterministic template and LLM explanations achieved **100.00%** attribution faithfulness whenever feature attributions were cited, confirming that top SHAP features were reported accurately when explicitly referenced.

---

## 4. Condition-by-Condition Matrix Breakdown

The 24 conditions span:
1. `adult` | `logistic_regression` | `correlation_remover` (Seeds 42, 123, 456)
2. `adult` | `logistic_regression` | `threshold_optimizer` (Seeds 42, 123, 456)
3. `adult` | `random_forest` | `correlation_remover` (Seeds 42, 123, 456)
4. `adult` | `random_forest` | `threshold_optimizer` (Seeds 42, 123, 456)
5. `compas` | `logistic_regression` | `correlation_remover` (Seeds 42, 123, 456)
6. `compas` | `logistic_regression` | `threshold_optimizer` (Seeds 42, 123, 456)
7. `compas` | `random_forest` | `correlation_remover` (Seeds 42, 123, 456)
8. `compas` | `random_forest` | `threshold_optimizer` (Seeds 42, 123, 456)

Detailed individual metrics for each run are recorded canonically in:
- [`faithfulness_runs.csv`](file:///d:/Projects/fairlens-ai/research/results/pilot/processed/faithfulness_runs.csv)
- [`faithfulness_summary.csv`](file:///d:/Projects/fairlens-ai/research/results/pilot/processed/faithfulness_summary.csv)
- [`pilot_execution_summary.json`](file:///d:/Projects/fairlens-ai/research/results/pilot/pilot_execution_summary.json)
