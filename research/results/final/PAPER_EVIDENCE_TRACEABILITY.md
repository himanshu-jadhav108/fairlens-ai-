# Paper Evidence Traceability & Provenance Ledger

**Study Title:** Quantitative Faithfulness of LLM-Generated Natural-Language Explanations for Machine Learning Fairness Audits: An Empirical Study  
**Branch:** `research/fairness-xai-study`  
**Base Commit Hash:** `2e47573`  
**Ledger Date:** 2026-09-20  
**Status:** **FROZEN EMPIRICAL EVIDENCE**  

---

## 1. Traceability Matrix: Paper Claims to Empirical Data Sources

Every empirical number, statistical comparison, and metric cited in the research paper is mapped directly to its canonical underlying data artifact below:

| Paper Claim / Metric | Value Cited in Paper Draft | Exact Source File | Line / Key / Calculation |
|---|---|---|---|
| **Canonical Experimental Conditions** | $N = 36$ conditions | `research/results/final/final_matrix_inventory.json` | Key: `"completed_count": 36` |
| **Total Evaluated Explanations** | 72 (36 Template + 36 Gemini) | `research/results/final/processed/faithfulness_runs.csv` | Exactly 72 rows |
| **Template Numerical Faithfulness** | $100.00\% \pm 0.00\%$ ($N=36$) | `research/results/final/processed/final_paired_comparison.csv` | Row 0, Col: `mean_template` |
| **Gemini Numerical Faithfulness** | $88.13\% \pm 10.82\%$ ($N=36$) | `research/results/final/processed/final_paired_comparison.csv` | Row 0, Col: `mean_llm`, `std_difference` |
| **Numerical Degradation Delta** | $-11.87$ percentage points | `research/results/final/processed/final_paired_comparison.csv` | Row 0, Col: `mean_difference` |
| **Numerical Effect Size (Cohen's $d$)** | $-1.097$ (Large negative effect) | `research/results/final/processed/final_paired_comparison.csv` | Row 0, Col: `cohens_d` |
| **Numerical Paired $t$-test** | $t = -6.581, p = 1.34 \times 10^{-7}$ | `research/results/final/processed/final_paired_comparison.csv` | Row 0, Col: `t_statistic`, `t_p_value` |
| **Numerical Wilcoxon Signed-Rank** | $W = 0.0, p = 8.28 \times 10^{-6}$ | `research/results/final/processed/final_paired_comparison.csv` | Row 0, Col: `wilcoxon_w`, `wilcoxon_p_value` |
| **Evaluable Directional Pairs** | $N = 23$ condition pairs | `research/results/final/processed/final_paired_comparison.csv` | Row 1, Col: `n_pairs` |
| **Template Directional Faithfulness** | $100.00\% \pm 0.00\%$ ($N=23$) | `research/results/final/processed/final_paired_comparison.csv` | Row 1, Col: `mean_template` |
| **Gemini Directional Faithfulness** | $94.18\% \pm 21.02\%$ ($N=23$) | `research/results/final/processed/final_paired_comparison.csv` | Row 1, Col: `mean_llm`, `std_difference` |
| **Directional Degradation Delta** | $-5.82$ percentage points | `research/results/final/processed/final_paired_comparison.csv` | Row 1, Col: `mean_difference` |
| **Directional Effect Size (Cohen's $d$)** | $-0.277$ (Small effect size) | `research/results/final/processed/final_paired_comparison.csv` | Row 1, Col: `cohens_d` |
| **Directional Paired $t$-test** | $t = -1.328, p = 0.1979$ (Non-significant) | `research/results/final/processed/final_paired_comparison.csv` | Row 1, Col: `t_statistic`, `t_p_value` |
| **Directional Wilcoxon Signed-Rank** | $W = 0.0, p = 0.0679$ | `research/results/final/processed/final_paired_comparison.csv` | Row 1, Col: `wilcoxon_w`, `wilcoxon_p_value` |
| **Template Unsupported Claim Rate** | $0.00\% \pm 0.00\%$ | `research/results/final/processed/final_paired_comparison.csv` | Row 3, Col: `mean_template` |
| **Gemini Unsupported Claim Rate** | $8.51\% \pm 8.72\%$ | `research/results/final/processed/final_paired_comparison.csv` | Row 3, Col: `mean_llm`, `std_difference` |
| **Unsupported Claim Paired $t$-test** | $t = 5.854, p = 1.20 \times 10^{-6}$ | `research/results/final/processed/final_paired_comparison.csv` | Row 3, Col: `t_statistic`, `t_p_value` |
| **Adult Census Benchmark Size** | 48,842 instances, 15 attributes | `research/data/adult.csv` | `shape = (48842, 15)` |
| **COMPAS Benchmark Size** | 7,214 instances, 53 attributes | `research/data/compas.csv` | `shape = (7214, 53)` |
| **German Credit Benchmark Size** | 1,000 instances, 21 attributes | `research/data/german.csv` | `shape = (1000, 21)` |
| **Synthetic Fallback Instances** | 0 instances (0.0% synthetic) | `research/results/final/manifests/*.json` | `is_synthetic_benchmark: false` |
| **Evidence Cryptographic Parity** | 36 / 36 conditions (100% match) | `research/results/final/raw/*.json` | `input_evidence_hash` parity |
| **Secondary Adjudication Queue** | 100 stratified claims | `research/results/final/human_annotation_sample.json` | Key: `"claims": [100 items]` |
| **Adjudication Overall Agreement** | 77.0% concordance (77/100) | `research/results/final/INDEPENDENT_LLM_ADJUDICATION_REPORT.md` | Section 2, Table 1 |
| **Adjudication Directional Agreement**| 100.0% concordance (21/21) | `research/results/final/INDEPENDENT_LLM_ADJUDICATION_REPORT.md` | Section 3, Table 2 |
| **Adjudication Interpretation Agreement**| 100.0% concordance (20/20) | `research/results/final/INDEPENDENT_LLM_ADJUDICATION_REPORT.md` | Section 3, Table 2 |
| **Adjudication Performance Agreement**| 100.0% concordance (20/20) | `research/results/final/INDEPENDENT_LLM_ADJUDICATION_REPORT.md` | Section 3, Table 2 |
| **Adjudication Numerical Agreement** | 80.0% concordance (16/20) | `research/results/final/INDEPENDENT_LLM_ADJUDICATION_REPORT.md` | Section 3, Table 2 |
| **Adjudication Magnitude Agreement** | 0.0% (evaluator routes to UNDETERMINABLE) | `research/results/final/INDEPENDENT_LLM_ADJUDICATION_REPORT.md` | Section 3, Table 2 |
| **Adjudication Cohen's Kappa** | $\kappa = 0.063$ | `research/results/final/INDEPENDENT_LLM_ADJUDICATION_REPORT.md` | Section 2, Table 1 |
| **Evaluator False Positives (Fabricated Values)** | 0 cases (0.0%) | `research/results/final/adjudication/adjudication_records.json` | Zero hallucinated numbers accepted |

---

## 2. Canonical Experimental Matrix Ledger (36 Unique Conditions)

| Index | Condition Identifier | Dataset | Predictive Model | Mitigation Technique | Seed | Canonical Experiment UUID | Evidence SHA-256 Hash Prefix |
|---|---|---|---|---|---|---|---|
| 01 | `adult__logistic_regression__correlation_remover__seed42` | Adult | Logistic Regression | Correlation Remover | 42 | `3e772ca6` | `4322883f` |
| 02 | `adult__logistic_regression__correlation_remover__seed123` | Adult | Logistic Regression | Correlation Remover | 123 | `6581c502` | `dbbcbe0e` |
| 03 | `adult__logistic_regression__correlation_remover__seed456` | Adult | Logistic Regression | Correlation Remover | 456 | `462a71d8` | `a3915bc6` |
| 04 | `adult__logistic_regression__threshold_optimizer__seed42` | Adult | Logistic Regression | Threshold Optimizer | 42 | `10ea6787` | `f0a35ee7` |
| 05 | `adult__logistic_regression__threshold_optimizer__seed123` | Adult | Logistic Regression | Threshold Optimizer | 123 | `021be82b` | `5c371aa4` |
| 06 | `adult__logistic_regression__threshold_optimizer__seed456` | Adult | Logistic Regression | Threshold Optimizer | 456 | `0b77b9aa` | `105a81e9` |
| 07 | `adult__random_forest__correlation_remover__seed42` | Adult | Random Forest | Correlation Remover | 42 | `25bcbbbf` | `e2a537f5` |
| 08 | `adult__random_forest__correlation_remover__seed123` | Adult | Random Forest | Correlation Remover | 123 | `168673a5` | `e47c16aa` |
| 09 | `adult__random_forest__correlation_remover__seed456` | Adult | Random Forest | Correlation Remover | 456 | `5a74ff90` | `8f844da0` |
| 10 | `adult__random_forest__threshold_optimizer__seed42` | Adult | Random Forest | Threshold Optimizer | 42 | `295a0928` | `eb9170e7` |
| 11 | `adult__random_forest__threshold_optimizer__seed123` | Adult | Random Forest | Threshold Optimizer | 123 | `be03eb5a` | `fefee015` |
| 12 | `adult__random_forest__threshold_optimizer__seed456` | Adult | Random Forest | Threshold Optimizer | 456 | `3d68fb06` | `bb552431` |
| 13 | `compas__logistic_regression__correlation_remover__seed42` | COMPAS | Logistic Regression | Correlation Remover | 42 | `83ef3e3d` | `6ae978bb` |
| 14 | `compas__logistic_regression__correlation_remover__seed123` | COMPAS | Logistic Regression | Correlation Remover | 123 | `bf2e8964` | `dae14cf8` |
| 15 | `compas__logistic_regression__correlation_remover__seed456` | COMPAS | Logistic Regression | Correlation Remover | 456 | `16353dbe` | `6da9a7d3` |
| 16 | `compas__logistic_regression__threshold_optimizer__seed42` | COMPAS | Logistic Regression | Threshold Optimizer | 42 | `3c87e742` | `baeb0df0` |
| 17 | `compas__logistic_regression__threshold_optimizer__seed123` | COMPAS | Logistic Regression | Threshold Optimizer | 123 | `4ca6cfa6` | `625e14cb` |
| 18 | `compas__logistic_regression__threshold_optimizer__seed456` | COMPAS | Logistic Regression | Threshold Optimizer | 456 | `4efcb06f` | `be26b5e0` |
| 19 | `compas__random_forest__correlation_remover__seed42` | COMPAS | Random Forest | Correlation Remover | 42 | `003923a1` | `b3bb748a` |
| 20 | `compas__random_forest__correlation_remover__seed123` | COMPAS | Random Forest | Correlation Remover | 123 | `167d32c0` | `f289cfeb` |
| 21 | `compas__random_forest__correlation_remover__seed456` | COMPAS | Random Forest | Correlation Remover | 456 | `6c471ee6` | `e56f4d54` |
| 22 | `compas__random_forest__threshold_optimizer__seed42` | COMPAS | Random Forest | Threshold Optimizer | 42 | `9ea96695` | `ebc9f6a7` |
| 23 | `compas__random_forest__threshold_optimizer__seed123` | COMPAS | Random Forest | Threshold Optimizer | 123 | `6451e50f` | `41555543` |
| 24 | `compas__random_forest__threshold_optimizer__seed456` | COMPAS | Random Forest | Threshold Optimizer | 456 | `a40ebfdc` | `9b3ff898` |
| 25 | `german__logistic_regression__correlation_remover__seed42` | German Credit | Logistic Regression | Correlation Remover | 42 | `aa9dfae8` | `f60fe884` |
| 26 | `german__logistic_regression__correlation_remover__seed123` | German Credit | Logistic Regression | Correlation Remover | 123 | `7b7a6616` | `6cf87d46` |
| 27 | `german__logistic_regression__correlation_remover__seed456` | German Credit | Logistic Regression | Correlation Remover | 456 | `5a9fc272` | `295a9a5f` |
| 28 | `german__logistic_regression__threshold_optimizer__seed42` | German Credit | Logistic Regression | Threshold Optimizer | 42 | `ea1ca740` | `82f91523` |
| 29 | `german__logistic_regression__threshold_optimizer__seed123` | German Credit | Logistic Regression | Threshold Optimizer | 123 | `5d804245` | `5c4786fc` |
| 30 | `german__logistic_regression__threshold_optimizer__seed456` | German Credit | Logistic Regression | Threshold Optimizer | 456 | `54fe66b8` | `6aa688cb` |
| 31 | `german__random_forest__correlation_remover__seed42` | German Credit | Random Forest | Correlation Remover | 42 | `ad818d3d` | `6788ecab` |
| 32 | `german__random_forest__correlation_remover__seed123` | German Credit | Random Forest | Correlation Remover | 123 | `03ff8403` | `be256a1b` |
| 33 | `german__random_forest__correlation_remover__seed456` | German Credit | Random Forest | Correlation Remover | 456 | `ab650bb6` | `451c0ee1` |
| 34 | `german__random_forest__threshold_optimizer__seed42` | German Credit | Random Forest | Threshold Optimizer | 42 | `60a63aa6` | `7486f06b` |
| 35 | `german__random_forest__threshold_optimizer__seed123` | German Credit | Random Forest | Threshold Optimizer | 123 | `6aebe310` | `b53fca9d` |
| 36 | `german__random_forest__threshold_optimizer__seed456` | German Credit | Random Forest | Threshold Optimizer | 456 | `66878347` | `f287ee3b` |

---

## 3. Provenance of Quarantined Artifacts

Total quarantined artifacts: **44 files** located in `research/results/legacy_retries/`.
Complete inventory and exclusion justifications are cataloged in `research/results/legacy_retries/QUARANTINE_PROVENANCE.json`.
- `manifests/`: 11 quarantined files (7 duplicate retries + 4 orphan pilot manifests)
- `raw/`: 5 quarantined explanation files
- `claims/`: 14 quarantined claims files (7 template + 7 gemini)
- `summaries/`: 14 quarantined summary files (7 template + 7 gemini)

None of these 44 quarantined artifacts are included in any summary table, CSV, or inferential test reported in the paper.

---

## 4. Evaluator & Adjudicator Model Provenance

### Automated Evaluator:
- **Location:** `research/faithfulness/`
- **Module:** `faithfulness_evaluator.py`, `claim_extractor.py`, `candidate_filter.py`
- **Mathematical Tolerances:**
  $$\text{Match} \iff |v_{\text{extracted}} - v_{\text{true}}| \le 0.015 \quad\lor\quad \frac{|v_{\text{extracted}} - v_{\text{true}}|}{|v_{\text{true}}|} \le 0.05$$
- **Evaluator Test Suite:** 100/100 tests passed (`pytest research/tests`, 13.18s).

### Primary Generation Model:
- **Model Name:** `gemini-2.5-flash`
- **SDK:** `google-generativeai==0.8.6`
- **Prompt:** `combined_audit_v1`
- **Generation Parameters:** $T = 0.2$, $\text{top\_p} = 0.95$, $\text{max\_output\_tokens} = 1500$, condition random seed.

### Secondary Independent Adjudicator:
- **Model Name:** `llama3:latest` (Meta Llama 3 8B Instruct)
- **Host Engine:** Ollama 0.32.4 local server on NVIDIA GeForce RTX 4060 Laptop GPU (8GB VRAM).
- **Execution Mode:** Offline local inference ($0$ cloud tokens).
- **Generation Parameters:** $T = 0.0$ (deterministic), seed $42$, format `json`.
- **Adjudication Blindness:** Strictly blinded to automated evaluator classifications.
