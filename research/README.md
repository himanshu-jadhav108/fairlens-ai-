# FairLens AI — Empirical Research Infrastructure

> **LOCKED RESEARCH TOPIC:**  
> **Quantitative Faithfulness of LLM-Generated Natural-Language Explanations for Machine Learning Fairness Audits: An Empirical Study**

> [!IMPORTANT]
> **ARCHIVAL / PROPOSAL DOCUMENT:** This infrastructure README reflects an early exploratory research planning phase (which outlined provisional concepts such as XGBoost, SHAP feature attribution, and a 5-RQ structure).
> 
> **AUTHORITATIVE FROZEN BENCHMARK:** The finalized, frozen empirical study is documented exclusively in [`research/paper/PAPER_DRAFT.md`](./paper/PAPER_DRAFT.md) and [`research/results/final/`](./results/final/):
> - **Factorial Design:** 3 Datasets (Adult, COMPAS, German Credit) × 2 Models (Logistic Regression, Random Forest) × 2 Mitigations (Correlation Remover, Threshold Optimizer) × 3 Seeds (42, 123, 456) = **36 canonical conditions** (72 paired runs with deterministic template reference controls).
> - **Generative Model:** Google Gemini 2.5 Flash ($T=0.2$, $top\_p=0.95$, max output tokens = 1500, SHA-256 evidence input parity).
> - **Research Questions:** Consolidated to 3 core RQs ($RQ_1$: Numerical Faithfulness, $RQ_2$: Directional Robustness, $RQ_3$: Unsupported/Causal Assertions).
> - **Claim Taxonomy:** 5 categories (Numerical, Directional, Fairness Interpretation, Performance, Subjective Magnitude).
> - **Human Annotation:** Not performed; sensitivity evaluated via secondary automated adjudication (`llama3:latest`, 8B parameters).

---

## 1. Core Scientific Direction & Contribution

This branch (`research/fairness-xai-study`) houses the experimental research pipeline investigating the fidelity and reliability of generative language models when synthesizing quantitative algorithmic fairness audit evidence.

### Core Research Question
> **How faithfully do LLM-generated natural-language explanations represent quantitative machine-learning fairness-audit evidence?**

### The Empirical Pipeline
```text
Benchmark Dataset (Adult, COMPAS, German)
       ↓
Predictive Model (Logistic Regression, Random Forest, XGBoost)
       ↓
Fairness Audit (DPD, EOD, EODiff, DI) & Mitigation (Pre, In, Post)
       ↓
SHAP Explainability Engine (Mean |SHAP|, Feature Rankings)
       ↓
Structured Audit Evidence (Observed, Derived, Semantic Interpretation)
       ↓
Explanation Generation (LLMProvider vs Deterministic Template Baseline)
       ↓
Quantitative Faithfulness Evaluation (Numerical, Directional, Attribution, Unsupported Claims)
       ↓
Hierarchical Statistical Analysis & Visualization
       ↓
Empirical Research Findings
```

### Scientific Scope Clarification
- The primary contribution is **NOT** a new fairness mitigation algorithm or model.
- The primary contribution is **NOT** simply integrating Google Gemini.
- The primary contribution **IS** the rigorous quantitative evaluation of whether LLMs faithfully communicate empirical machine learning fairness audit findings to stakeholders without numerical distortion, directional inversion, or unwarranted causal extrapolation.

---

## 2. Research Questions (Permanently Locked)

1. **RQ1:** How accurately do LLM-generated explanations reproduce the quantitative results of machine-learning fairness audits?
2. **RQ2:** How accurately do LLM-generated explanations represent the direction and magnitude of fairness changes following bias-mitigation interventions?
3. **RQ3:** How faithfully do LLM-generated explanations represent feature-importance information derived from SHAP-based explanations?
4. **RQ4:** What types of faithfulness errors occur most frequently in LLM-generated explanations of fairness audits?
5. **RQ5:** How does explanation faithfulness vary across datasets, predictive models, fairness metrics, mitigation methods, and LLM configurations?


---

## 3. Modular Architecture

```text
research/
├── DECISIONS.md              # Research decision log (topic LOCKED, experimental details provisional)
├── REPOSITORY_AUDIT.md       # Audit of existing product, tech debt, and safety guarantees
├── requirements-research.txt # Pinned Python dependencies (including google-generativeai)
├── configs/                  # Experiment configurations (YAML)
├── datasets/                 # Abstract BaseDataset, loaders for Adult, COMPAS, German
├── preprocessing/            # Leak-free train-fitted preprocessors
├── models/                   # Common interfaces for Logistic Regression, RF, XGBoost
├── mitigation/               # Fairlearn Pre, In, and Post-processing interventions
├── fairness_metrics/         # Metric evaluators with explicit NaN/undefined tracking
├── performance_metrics/      # Classification performance evaluators
├── explainability/           # Model-aware SHAP engine with full provenance metadata
├── evidence/                 # Structured audit evidence schemas & canonical builder
├── baselines/                # Deterministic TemplateExplainer control baseline
├── llm/                      # Replaceable LLMProvider (GeminiProvider, MockLLMProvider), versioned prompts, generator
├── faithfulness/             # Evaluators for Numerical, Directional, Attribution, and Unsupported Claims
├── annotation/               # Human annotation protocol, guidelines, and Cohen's Kappa agreement tooling
├── experiments/              # Single runner, batch runner, paired baseline comparisons
├── statistics/               # Hierarchical statistical analysis (explanation-level pairing, bootstrap CIs)
├── analysis/                 # Result aggregator and candidate scientific visualization generator
├── results/
│   ├── manifests/            # Machine-readable JSON manifests tracking Git commit and environment
│   ├── raw/                  # Full experimental results and raw LLM output records
│   ├── claims/               # Atomic claim-level verification records
│   ├── summaries/            # Faithfulness evaluation summary reports
│   ├── processed/            # Summary tables with mean ± std across runs
│   └── figures/              # Generated scientific figures
├── notebooks/                # Reproducible Jupyter inspection and analysis notebooks
├── scripts/                  # CLI runners: run_llm_experiment.py, run_experiment.py, aggregate.py
├── tests/                    # Fast, self-contained unit tests using synthetic benchmarks and mock LLM
└── paper/                    # Academic paper scaffold (12 chapters conforming to locked topic)
```

---

## 4. Quickstart & Verification

### Running the Offline Deterministic Smoke Test (Zero API key required)
```bash
python research/scripts/run_llm_experiment.py --smoke-test
```

### Running Real LLM Experiments with Google Gemini
```bash
# Requires setting GEMINI_API_KEY in your environment (never commit .env or API keys!)
export GEMINI_API_KEY="your-api-key"

python research/scripts/run_llm_experiment.py \
  --dataset adult \
  --model logistic_regression \
  --mitigation correlation_remover \
  --provider gemini \
  --prompt combined_audit_v1
```

### Running the Full Test Suite
```bash
pytest research/tests/ -v
```
