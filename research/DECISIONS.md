# FairLens AI Research — Decision Log & Methodological Registry

**Repository:** `fairlens-ai-`  
**Branch:** `research/fairness-xai-study`  
**Last Updated:** September 17, 2026  

---

## 1. Non-Negotiable Core Research Direction

### PERMANENTLY LOCKED RESEARCH TOPIC
> **Quantitative Faithfulness of LLM-Generated Natural-Language Explanations for Machine Learning Fairness Audits: An Empirical Study**

### Core Research Question
> **How faithfully do LLM-generated natural-language explanations represent quantitative machine-learning fairness-audit evidence?**

### Foundational Paradigm Shift
The original fairness, mitigation, and SHAP explainability infrastructure is **not** the primary scientific contribution. Instead, it serves as the **rigorous experimental ground-truth evidence generator** supporting the core empirical inquiry into LLM explanation faithfulness.
- The scientific contribution is **NOT** a new fairness mitigation algorithm.
- The scientific contribution is **NOT** a new predictive ML model.
- The scientific contribution is **NOT** simply integrating Google Gemini.
- **The scientific contribution IS the empirical evaluation of the quantitative faithfulness of LLM-generated natural-language explanations of machine learning fairness audits.**

---

## 2. Locked vs. Provisional Decision Index

| ID | Decision Area | Status | Date Logged | Scientific Rationale |
| :--- | :--- | :---: | :---: | :--- |
| **DEC-001** | **Core Research Topic** | **`LOCKED`** | 2026-09-17 | Permanently locked to *"Quantitative Faithfulness of LLM-Generated Natural-Language Explanations for Machine Learning Fairness Audits: An Empirical Study"*. |
| **DEC-002** | **Core Pipeline Architecture** | **`LOCKED`** | 2026-09-17 | Pipeline: `Dataset -> ML Model -> Fairness Audit -> Mitigation -> SHAP Evidence -> Structured Audit Evidence -> LLM Explanation -> Faithfulness Evaluation -> Statistics -> Results`. |
| **DEC-003** | **Evaluation Philosophy** | **`LOCKED`** | 2026-09-17 | Deterministic evaluation against authoritative structured evidence is the primary judge. Do NOT use another LLM as primary judge. Human annotation protocol governs semantic edge cases. |
| **DEC-004** | **Primary Faithfulness Dimensions**| **`LOCKED`** | 2026-09-17 | Four foundational dimensions: Numerical Faithfulness, Directional Faithfulness, Attribution Faithfulness, and Unsupported Claim Rate. |
| **DEC-005** | **Evidence Separation Principle** | **`LOCKED`** | 2026-09-17 | Structured evidence strictly separates *Observed Values*, *Derived Values*, and *Metric Interpretations*. Domain semantics are explicit. |
| **DEC-006** | **Deterministic Baseline** | **`LOCKED`** | 2026-09-17 | TemplateExplainer generates deterministic text from structured evidence as the experimental control baseline. |
| **DEC-007** | **LLM Provider Replaceability** | **`LOCKED`** | 2026-09-17 | Abstract `BaseLLMProvider` decouples the research from Gemini; Gemini is an experimental provider, not the subject of the paper. |
| **DEC-008** | **Production Code Isolation** | **`LOCKED`** | 2026-09-17 | `backend/`, `frontend/`, and `main` remain completely untouched. All research lives isolated under `research/`. |
| **DEC-009** | **Reproducibility & Security** | **`LOCKED`** | 2026-09-17 | `GEMINI_API_KEY` is never committed. Deterministic mock smoke-tests run offline without credentials. Raw outputs are cryptographically hashed and saved. |
| **DEC-010** | **Exact Gemini Model & Versions** | **`LOCKED`** | 2026-09-17 | Strictly locked to `gemini-2.5-flash`. No silent fallbacks to Lite or other versions allowed. |
| **DEC-011** | **Prompt Variants** | `PROVISIONAL` | 2026-09-17 | Four versioned templates implemented (`combined_audit_v1`, `fairness_audit_v1`, `fairness_comparison_v1`, `shap_explanation_v1`). Ablations may test variant phrasing. |
| **DEC-012** | **Full Experiment Matrix** | `PROVISIONAL` | 2026-09-17 | Configurable matrix over datasets × models × mitigations × seeds × prompts. Computational scale will be calibrated for statistical power. |
| **DEC-013** | **Statistical Analysis Details** | `PROVISIONAL` | 2026-09-17 | Hierarchical nesting (claims nested in explanations) enforced. Paired non-parametric tests and bootstrap CIs implemented. |
| **DEC-014** | **Human Annotation Sample Size** | `PROVISIONAL` | 2026-09-17 | Protocol and Cohen's Kappa tooling established. Sample size for human adjudication (target: 100-300 claims) to be finalized with annotator availability. |

---

## 3. Detailed Decision Summaries

### DEC-001 & DEC-002: Locked Topic and Research Pipeline
- **Decision:** The research study is permanently dedicated to measuring the quantitative faithfulness of LLM-generated explanations for machine learning fairness audits.
- **Context:** The previously implemented fairness auditing, mitigation, and SHAP pipelines are not discarded; they now generate the authoritative ground-truth evidence payloads that LLMs are tasked with explaining.
- **Pipeline Flow:**
  ```text
  Raw Benchmark Dataset (Adult, COMPAS, German)
         ↓
  ML Model Training (LR, RF, XGBoost)
         ↓
  Fairness Audit (DPD, EOD, EODiff, DI) & Bias Mitigation
         ↓
  SHAP Attribution Engine (Feature Importances & Rankings)
         ↓
  Canonical Structured Evidence (Observed, Derived, Semantic Interpretation)
         ↓
  Explanation Generation (LLMProvider vs TemplateExplainer Baseline)
         ↓
  Deterministic Faithfulness Evaluator (Numerical, Directional, Attribution, Unsupported Claims)
         ↓
  Hierarchical Statistical Analysis & Visualization
  ```

### DEC-003 & DEC-004: Evaluation Philosophy & Primary Faithfulness Dimensions
- **Evaluation Philosophy:** Deterministic verification against structured evidence is the primary judge. LLM-as-a-judge is excluded from primary evaluation to avoid circular reasoning and uncalibrated LLM evaluator bias.
- **Primary Metrics:**
  1. *Numerical Faithfulness Rate:* Proportion of stated numbers matching ground-truth within scientific tolerance ($\pm 0.015$ absolute, $\pm 5\%$ relative).
  2. *Directional Faithfulness Rate:* Correctness of reported mathematical shifts ("increased", "decreased") and domain implications ("improved", "worsened").
  3. *Attribution Faithfulness Rate:* Concordance of stated top predictors with authoritative SHAP rankings (top-1 match, top-$k$ overlap).
  4. *Unsupported Claim Rate:* Frequency of ungrounded causal leaps ("feature X caused discrimination") and absolute fairness claims ("completely fair").

### DEC-005: Explicit Separation of Evidence Layers
- Structured audit evidence must never conflate raw observations with derived values or subjective interpretations:
  - **Observed Value:** Exact empirical measurement on the audit split (e.g. $DPD = 0.4222$).
  - **Derived Value:** Mathematically calculated delta or ratio (e.g. $\Delta = -0.4099$, $Relative = -97.1\%$).
  - **Interpretation:** Domain-specific semantic meaning according to pre-defined rules (e.g. $DPD$ decrease towards $0.0$ indicates *fairness improvement*; disparate impact closer to $1.0$ indicates *fairness improvement*; accuracy decrease indicates *performance degradation*).

### DEC-006: Deterministic Template Explainer Baseline
- To rigorously answer reviewer questions such as *"Why use an LLM if a deterministic template can report metrics?"*, the framework includes `TemplateExplainer` as a control baseline. This isolates the trade-off between natural language fluidity and factual precision.

### DEC-007: Provider Replaceability & Decoupling from Gemini
- The research paper does not evaluate "Gemini's fairness explanations." It evaluates "LLM-generated explanations."
- `BaseLLMProvider` enables swapping Google Gemini with local LLMs (e.g., Llama, Mistral) or deterministic mock providers.

### DEC-008 & DEC-009: Branch Isolation, Manifest Provenance, & Security
- `backend/`, `frontend/`, and `main` remain 100% untouched.
- All research artifacts live under `research/`.
- `GEMINI_API_KEY` is loaded strictly via environment variables and never committed to version control.
- Deterministic mock smoke-tests run fully offline without credentials.
