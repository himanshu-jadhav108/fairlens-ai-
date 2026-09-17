# FairLens AI: Complete Research Artifact Index & Master Directory

**Study Title:** Quantitative Faithfulness of LLM-Generated Natural-Language Explanations for Machine Learning Fairness Audits: An Empirical Study  
**Document Classification:** Master Comprehensive Research Guide (Sections A through K)  
**Status:** Certified Ready for Confirmatory Phase  

---

## Table of Contents
- [Section A: Locked Research Question & Scope](#section-a-locked-research-question--scope)
- [Section B: Core Methodology & Mathematical Formulations](#section-b-core-methodology--mathematical-formulations)
- [Section C: Evidence Classification & Anti-Contamination Rules](#section-c-evidence-classification--anti-contamination-rules)
- [Section D: Pilot Study Architecture & Matrix (24 Conditions)](#section-d-pilot-study-architecture--matrix-24-conditions)
- [Section E: Pilot Empirical Findings & Statistical Significance](#section-e-pilot-empirical-findings--statistical-significance)
- [Section F: Human Annotation Protocol & Queue](#section-f-human-annotation-protocol--queue)
- [Section G: Evaluator Validation & Adversarial Testing](#section-g-evaluator-validation--adversarial-testing)
- [Section H: Confirmatory Experiment Protocol (135 Conditions)](#section-h-confirmatory-experiment-protocol-135-conditions)
- [Section I: Software Architecture & Codebase Map](#section-i-software-architecture--codebase-map)
- [Section J: Security, API Key, and Secret Isolation](#section-j-security-api-key-and-secret-isolation)
- [Section K: Complete Artifact Directory & File Registry](#section-k-complete-artifact-directory--file-registry)

---

## Section A: Locked Research Question & Scope

The research topic is permanently locked:
> **Quantitative Faithfulness of LLM-Generated Natural-Language Explanations for Machine Learning Fairness Audits: An Empirical Study**

### Core Research Inquiry
When Large Language Models are tasked with explaining complex machine learning fairness audits and mitigation trade-offs, to what degree do their generated natural-language explanations faithfully represent the underlying ground-truth numerical performance metrics, directional parity changes, and feature attribution values?

---

## Section B: Core Methodology & Mathematical Formulations

The research framework establishes an end-to-end evaluation pipeline:
1. **Model Training & Auditing:** Trains ML classifiers on tabular fairness datasets and applies fairness mitigation algorithms.
2. **Canonical Evidence Construction:** Compiles all evaluation metrics, group-level discrepancies, and SHAP attribution values into an immutable `StructuredAuditEvidence` JSON schema with a cryptographic SHA-256 hash.
3. **Dual Generation:**
   - Deterministic Grounded Template Explanation (`template_baseline`)
   - LLM Natural-Language Explanation via Google Gemini API (`gemini-2.5-flash` / `gemini-flash-lite-latest`)
4. **NLI Claim Extraction & Verification:**
   - Numerical Faithfulness: $F_{\text{num}} = \frac{N_{\text{matched}}}{N_{\text{total\_num}}}$ (tolerance $|\Delta| \le 0.005$)
   - Directional Faithfulness: $F_{\text{dir}} = \frac{N_{\text{correct\_direction}}}{N_{\text{total\_dir}}}$
   - Attribution Faithfulness: $F_{\text{attr}} = \frac{N_{\text{top\_features\_correct}}}{N_{\text{top\_features\_cited}}}$
   - Unsupported Claim Rate: $U = \frac{N_{\text{unsupported}}}{N_{\text{total\_claims}}}$
   - Numerical MAE: $\text{MAE} = \frac{1}{N_{\text{claims}}} \sum |v_{\text{extracted}} - v_{\text{ground\_truth}}|$

---

## Section C: Evidence Classification & Anti-Contamination Rules

All generated outputs are rigorously segregated into three evidence classes:
- **`SOFTWARE_VALIDATION_ONLY`:** Mocks, unit tests, and smoke test outputs. Located strictly under `research/results/smoke/`.
- **`PILOT_VALIDATION_RUN`:** Live empirical pilot runs ($N = 24$). Located strictly under `research/results/pilot/`.
- **`FINAL_EMPIRICAL_RUN`:** Confirmatory 135-condition matrix runs. Located strictly under `research/results/final/` (pre-registered protocol, not yet executed).

---

## Section D: Pilot Study Architecture & Matrix (24 Conditions)

The pilot matrix tests a $2 \times 2 \times 2 \times 3 = 24$ condition design:
- **Datasets (2):** `adult`, `compas`
- **Models (2):** `logistic_regression`, `random_forest`
- **Mitigations (2):** `correlation_remover`, `threshold_optimizer`
- **Seeds (3):** `42`, `123`, `456`

**Execution Status:** 24/24 conditions completed successfully with live Google Gemini API calls. Zero failures.

---

## Section E: Pilot Empirical Findings & Statistical Significance

Paired comparisons ($N = 24$) between deterministic templates and Gemini LLM explanations:
- **Numerical Faithfulness:** Template: $83.56\% \pm 0.69\%$ vs LLM: $54.59\% \pm 23.19\%$ ($\Delta = -28.97\%$, Cohen's $d = -1.77$, Wilcoxon $W = 9.0$, $p = 1.97 \times 10^{-6}$).
- **Directional Faithfulness:** Template: $100.00\% \pm 0.00\%$ vs LLM: $64.77\% \pm 37.61\%$ ($\Delta = -35.23\%$, Cohen's $d = -1.32$, Wilcoxon $W = 0.0$, $p = 2.79 \times 10^{-4}$).
- **Attribution Faithfulness:** Both systems achieved $100.00\%$ fidelity.
- **Unsupported Claim Rate:** Template: $0.00\%$ vs LLM: $6.31\% \pm 5.38\%$ ($\Delta = +6.31\%$, Cohen's $d = +1.66$, Wilcoxon $W = 0.0$, $p = 1.31 \times 10^{-4}$).

---

## Section F: Human Annotation Protocol & Queue

- **Artifact:** [`ANNOTATION_QUEUE.json`](file:///d:/Projects/fairlens-ai/research/results/pilot/ANNOTATION_QUEUE.json)
- **Status:** 742 claims extracted across all 24 pilot conditions.
- **Human Annotation State:** `QUEUED_PENDING_HUMAN_ANNOTATION` (no labels synthetically imputed).
- **Guidelines:** Detailed in [`ANNOTATION_README.md`](file:///d:/Projects/fairlens-ai/research/results/pilot/ANNOTATION_README.md).

---

## Section G: Evaluator Validation & Adversarial Testing

The automated claim extraction and verification pipeline is validated by:
- Comprehensive unit tests: `test_evaluator.py`, `test_schemas.py`, `test_evidence.py`
- Adversarial test suite: `test_adversarial.py` (28/28 tests passing), covering sign flips, hallucinated metrics, percentage-point confusions, and out-of-bounds floating-point claims.
- Formal documentation in [`EVALUATOR_VALIDATION.md`](file:///d:/Projects/fairlens-ai/research/EVALUATOR_VALIDATION.md).

---

## Section H: Confirmatory Experiment Protocol (135 Conditions)

- **Artifact:** [`FINAL_EXPERIMENT_PROTOCOL.md`](file:///d:/Projects/fairlens-ai/research/FINAL_EXPERIMENT_PROTOCOL.md)
- **Matrix:** 3 Datasets (`adult`, `compas`, `german`) $\times$ 3 Models (`logistic_regression`, `random_forest`, `xgboost`) $\times$ 3 Mitigations (`reweighing`, `correlation_remover`, `threshold_optimizer`) $\times$ 5 Seeds (`42`, `123`, `456`, `789`, `1011`) = 135 conditions.
- **Status:** Protocol locked, pre-registered, and frozen. Execution reserved for Phase 4.

---

## Section I: Software Architecture & Codebase Map

- `research/data/`: Tabular dataset split loaders and synthetically generated benchmark mirrors.
- `research/models/`: Model training wrappers with scikit-learn and XGBoost support.
- `research/fairness/`: Mitigations (`Reweighing`, `CorrelationRemover`, `ThresholdOptimizer`).
- `research/xai/`: SHAP tree and kernel feature attribution explainers.
- `research/faithfulness/`: NLI claim extraction, evidence schemas, and evaluation engines.
- `research/llm/`: LLM provider interfaces (`gemini.py`, `mock.py`) with deterministic seeding.
- `research/scripts/`: Reproducible experiment drivers and aggregation CLI utilities.
- `research/tests/`: Complete pytest verification suite.

---

## Section J: Security, API Key, and Secret Isolation

- No API keys, credentials, or secrets are hardcoded in any tracked source file or git commit.
- `GeminiProvider` extracts `GEMINI_API_KEY` dynamically from environment variables or `backend/.env`.
- Production code (`backend/`, `frontend/`) remains 100% untouched.

---

## Section K: Complete Artifact Directory & File Registry

| File Path | Description | Evidence Class |
| :--- | :--- | :--- |
| [`research/PILOT_GO_NO_GO.md`](file:///d:/Projects/fairlens-ai/research/PILOT_GO_NO_GO.md) | Formal Pilot Gate Review | Governance |
| [`research/FINAL_EXPERIMENT_PROTOCOL.md`](file:///d:/Projects/fairlens-ai/research/FINAL_EXPERIMENT_PROTOCOL.md) | Confirmatory 135-Condition Protocol | Protocol |
| [`research/PAPER_EVIDENCE_PACKAGE.md`](file:///d:/Projects/fairlens-ai/research/PAPER_EVIDENCE_PACKAGE.md) | Evidence Tier Classification | Governance |
| [`research/FINAL_RESEARCH_STATUS.md`](file:///d:/Projects/fairlens-ai/research/FINAL_RESEARCH_STATUS.md) | Research Milestone Summary | Governance |
| [`research/results/pilot/PILOT_RESULTS_REPORT.md`](file:///d:/Projects/fairlens-ai/research/results/pilot/PILOT_RESULTS_REPORT.md) | Pilot Empirical Findings Report | `PILOT_VALIDATION_RUN` |
| [`research/results/pilot/PILOT_STATISTICAL_REPORT.md`](file:///d:/Projects/fairlens-ai/research/results/pilot/PILOT_STATISTICAL_REPORT.md) | Statistical Significance & Tests | `PILOT_VALIDATION_RUN` |
| [`research/results/pilot/ANNOTATION_QUEUE.json`](file:///d:/Projects/fairlens-ai/research/results/pilot/ANNOTATION_QUEUE.json) | 742 Queued Pilot Claims | `PILOT_VALIDATION_RUN` |
| [`research/results/pilot/ANNOTATION_README.md`](file:///d:/Projects/fairlens-ai/research/results/pilot/ANNOTATION_README.md) | Human Annotation Protocol | Protocol |
| [`research/results/pilot/pilot_execution_summary.json`](file:///d:/Projects/fairlens-ai/research/results/pilot/pilot_execution_summary.json) | Pilot Condition Inventory (24/24) | `PILOT_VALIDATION_RUN` |
| [`research/results/pilot/processed/faithfulness_runs.csv`](file:///d:/Projects/fairlens-ai/research/results/pilot/processed/faithfulness_runs.csv) | Processed Condition Runs | `PILOT_VALIDATION_RUN` |
| [`research/results/pilot/processed/faithfulness_summary.csv`](file:///d:/Projects/fairlens-ai/research/results/pilot/processed/faithfulness_summary.csv) | Processed Group Summaries | `PILOT_VALIDATION_RUN` |
