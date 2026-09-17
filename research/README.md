# FairLens AI — Empirical Research Infrastructure

> **FOUNDATIONAL DIRECTIVE:**  
> The research questions and final scientific claims are provisional and must be validated against the literature before the paper is finalized.  
> The implementation infrastructure is prepared for empirical investigation; the final research question, gap, contribution, experiment matrix, and statistical methodology remain subject to literature-based validation.

---

## 1. Overview & Working Research Direction

This branch (`research/fairness-xai-study`) contains the isolated machine-learning research framework for FairLens AI. It establishes an end-to-end experimental pipeline investigating the multi-dimensional interplay between fairness intervention algorithms, predictive classification performance, and Shapley feature attribution stability.

**Working Research Direction (PROVISIONAL):**  
*"Evaluating fairness–performance–explainability trade-offs in machine-learning bias mitigation."*

All production application components (`backend/`, `frontend/`, and deployment configs) remain unaltered on `main`.

---

## 2. Provisional Research Questions

The following questions serve as orienting inquiries for empirical pipeline design and will be formalized following systematic literature review:

1. **RQ1 (Provisional):** To what extent do diverse mitigation interventions (pre-processing, in-processing, post-processing) impact out-of-sample predictive accuracy relative to their reduction in demographic bias?
2. **RQ2 (Provisional):** How do bias mitigation interventions perturb global and subgroup-level Shapley feature attributions (measured via cosine similarity, Spearman rank correlation, and attribution distance)?
3. **RQ3 (Provisional):** Does post-processing decision thresholding decouple predictive fairness from model explanation consistency compared to representation-level pre-processing?

---

## 3. Modular Architecture

```
research/
├── REPOSITORY_AUDIT.md       # Audit of existing product, tech debt, and safety guarantees
├── DECISIONS.md              # Research decision log (provisional vs locked choices)
├── requirements-research.txt # Pinned Python dependencies
├── configs/                  # YAML experiment configurations
│   ├── default_config.yaml
│   └── matrix_config.yaml
├── datasets/                 # Abstract BaseDataset, loaders for Adult, COMPAS, German
├── preprocessing/            # Leak-free train-fitted preprocessors
├── models/                   # Common interfaces for Logistic Regression, RF, XGBoost
├── mitigation/               # Common interfaces for Pre, In, and Post-processing Fairlearn interventions
├── fairness_metrics/         # Metric evaluators with explicit NaN/undefined tracking
├── performance_metrics/      # Classification performance evaluators
├── explainability/           # Model-aware SHAP engine with full provenance metadata
├── experiments/              # Single runner, batch runner, paired baseline comparisons
├── statistics/               # Provisional inferential testing utilities
├── analysis/                 # Result aggregator and candidate visualization generator
├── results/
│   ├── manifests/            # Machine-readable JSON manifests tracking Git commit and environment
│   ├── raw/                  # Full experimental results per configuration
│   ├── processed/            # Summary tables with mean ± std across seeds
│   └── figures/              # Candidate visualization figures
├── notebooks/                # 6 reproducible Jupyter inspection and analysis notebooks
├── scripts/                  # CLI tools: run_experiment, run_matrix, aggregate, generate_figures
├── tests/                    # Fast, self-contained unit tests using synthetic benchmarks
└── paper/                    # Academic paper scaffold (10 chapters + references)
```

---

## 4. Experimental Suite & Provenance

### Candidate Benchmark Datasets
- **Adult Census Income:** US Census Bureau 1994 via UCI ML Repository. Sensitive attribute: `sex`.
- **ProPublica COMPAS:** Broward County recidivism risk assessment. Sensitive attribute: `race`.
- **Statlog German Credit:** UCI ML Repository. Sensitive attribute: `age_group`.
*Data Provenance Protocol:* Real datasets are not committed if subject to access constraints. Synthetic benchmark generators are included strictly for unit tests, smoke tests, and CI.

### Candidate Model Families
- **Logistic Regression:** Linear classification baseline (`max_iter=500`, `solver=liblinear`).
- **Random Forest:** Bagged non-linear ensemble (`n_estimators=100`, `max_depth=10`).
- **XGBoost:** Gradient boosted decision trees (`n_estimators=100`, `max_depth=5`, `learning_rate=0.1`).

### Candidate Mitigation Interventions
- **Pre-processing:** `CorrelationRemover` (Fairlearn).
- **In-processing:** `ExponentiatedGradient` with Demographic Parity constraints (Fairlearn).
- **Post-processing:** `ThresholdOptimizer` (Fairlearn), calibrated strictly on training/validation partitions to prevent test leakage.

### End-to-End Auditability (Manifest Guarantee)
Every experiment automatically generates a manifest in `results/manifests/` recording:
$$\text{Paper Result} \longrightarrow \text{Processed Table} \longrightarrow \text{Raw JSON} \longrightarrow \text{Experiment ID} \longrightarrow \text{Manifest} \longrightarrow \text{Git Commit Hash}$$

---

## 5. Getting Started & Execution Guide

### Dependency Installation
```bash
# Using Python 3.10 - 3.13
pip install -r research/requirements-research.txt
```

### Run Fast Unit Tests
```bash
pytest research/tests/ -v
```

### Run a Fast Smoke Test (Single Experiment)
```bash
python research/scripts/run_experiment.py --dataset adult --model logistic_regression --mitigation correlation_remover --seed 42 --smoke-test
```

### Run Configurable Batch Execution
```bash
python research/scripts/run_matrix.py --smoke-test
```

### Aggregate Results & Generate Candidate Visualizations
```bash
python research/scripts/aggregate_results.py
python research/scripts/generate_figures.py
```

---

## 6. Known Limitations
- The initial 3×3×3×5 experiment matrix is PROVISIONAL and does not imply that all 135 combinations are scientifically necessary.
- Random seeds represent algorithmic split sensitivity and initialization variance; they must NOT be interpreted as independent statistical observations.
- Synthetic benchmark datasets are strictly for testing and must never be reported as empirical findings.
