# FairLens AI Research — Decision Log & Methodological Registry

**Repository:** `fairlens-ai-`  
**Branch:** `research/fairness-xai-study`  
**Last Updated:** September 17, 2026  

---

## Methodological Scope Statement

> **Foundational Principle:**  
> The implementation infrastructure is prepared for empirical investigation; the final research question, gap, contribution, experiment matrix, and statistical methodology remain subject to literature-based validation.

This document logs all methodological and architectural design decisions made during the setup and evolution of the FairLens AI research framework. Decisions are explicitly tagged as either **`PROVISIONAL`** (open to modification based on literature review, theoretical analysis, or pilot empirical results) or **`LOCKED`** (core engineering or scientific integrity constraints that must be preserved).

---

## Decision Index

| ID | Decision Area | Status | Date Logged | Summary |
| :--- | :--- | :---: | :---: | :--- |
| **DEC-001** | Core Research Topic & Title | `PROVISIONAL` | 2026-09-17 | Working direction: fairness–performance–explainability trade-offs in bias mitigation. |
| **DEC-002** | Scientific Research Gap | `PROVISIONAL` | 2026-09-17 | Research gap will be formulated only after formal literature review; no claims of novelty hardcoded. |
| **DEC-003** | Candidate Experiment Matrix | `PROVISIONAL` | 2026-09-17 | 3 datasets × 3 models × 3 mitigations × 5 seeds is a configuration capability, not a mandatory publication matrix. |
| **DEC-004** | Inferential Statistical Methodology | `PROVISIONAL` | 2026-09-17 | Tests (paired t-test, Wilcoxon), CIs, and multiple testing corrections deferred to experimental design phase. Random seeds are not independent observations. |
| **DEC-005** | Candidate Benchmark Datasets | `PROVISIONAL` | 2026-09-17 | Adult Income, COMPAS, and German Credit selected as candidate tabular benchmarks. Real data not committed if restricted. |
| **DEC-006** | Candidate Model Families | `PROVISIONAL` | 2026-09-17 | Logistic Regression, Random Forest, and XGBoost selected to contrast linear vs non-linear/tree structures. |
| **DEC-007** | Mitigation Taxonomy | `LOCKED` | 2026-09-17 | Standard taxonomy: Pre-processing (CorrelationRemover), In-processing (ExponentiatedGradient), Post-processing (ThresholdOptimizer). |
| **DEC-008** | Branch Isolation & Code Protection | `LOCKED` | 2026-09-17 | Research branch `research/fairness-xai-study` remains completely isolated. Main and production code remain untouched. |
| **DEC-009** | Synthetic Data Protocol | `LOCKED` | 2026-09-17 | Synthetic datasets are strictly for unit tests, smoke tests, and CI. Prohibited from being presented as empirical research findings. |
| **DEC-010** | End-to-End Manifest Provenance | `LOCKED` | 2026-09-17 | Every experiment generates a machine-readable manifest linking results directly to Git commit, seeds, hyperparams, and environment. |
| **DEC-011** | Attribution Comparison Metrics | `PROVISIONAL` | 2026-09-17 | Cosine similarity, Spearman rank correlation, and L1/L2 distance implemented as candidate metrics; final choice depends on literature review. |
| **DEC-012** | Gemini / LLM Role in Research | `PROVISIONAL` | 2026-09-17 | Gemini API explanations remain active in the product app, but are excluded from the initial research scientific claims. |
| **DEC-013** | Paper Visualizations | `PROVISIONAL` | 2026-09-17 | Radar charts removed. Candidate figures focus on Pareto trade-offs, fairness deltas, performance deltas, and attribution shifts. |

---

## Detailed Decision Entries

### DEC-001: Core Research Topic & Direction
- **Status:** `PROVISIONAL`
- **Decision:** Adopt the working research title and direction: *"Evaluating fairness–performance–explainability trade-offs in machine-learning bias mitigation."*
- **Rationale:** Provides an orienting direction to build a multi-dimensional evaluation pipeline assessing three interrelated dimensions: statistical fairness, predictive accuracy, and feature attribution stability.
- **Alternatives Considered:** Focusing solely on accuracy–fairness Pareto frontiers without explainability; focusing solely on SHAP attribution fidelity without mitigation.
- **Review Trigger:** Literature survey completion.

---

### DEC-002: Scientific Research Gap
- **Status:** `PROVISIONAL`
- **Decision:** Do NOT assert a finalized research gap or claim algorithmic novelty at this stage.
- **Rationale:** Claiming novelty or a verified literature gap prior to a structured literature search violates scientific integrity. The infrastructure is built to support whatever specific empirical hypothesis emerges from the literature.
- **Alternatives Considered:** Pre-specifying a gap around post-processing attribution instability. Rejected as premature.
- **Review Trigger:** Systematic review of NeurIPS, ICML, FAccT, and AIES papers (2020–2026).

---

### DEC-003: Candidate Experiment Matrix
- **Status:** `PROVISIONAL`
- **Decision:** Build a flexible configuration runner capable of executing up to 3 datasets × 3 models × 3 mitigations × 5 seeds (135 configurations), but explicitly state that not all cells are required for publication.
- **Rationale:** A modular matrix runner ensures technical flexibility. However, pilot experiments or literature alignment may reveal that certain combinations (e.g. CorrelationRemover on tree models) are scientifically uninformative or redundant.
- **Alternatives Considered:** Hardcoding the full 135-experiment matrix as a non-negotiable benchmark. Rejected.
- **Review Trigger:** Evaluation of preliminary smoke tests and research question narrowing.

---

### DEC-004: Inferential Statistical Methodology
- **Status:** `PROVISIONAL`
- **Decision:** Implement reusable statistical functions (normality tests, paired differences, effect sizes) while explicitly documenting that the final statistical inferential protocol is provisional.
- **Rationale:** Multiple random seeds represent algorithmic stochasticity across data splits/initializations, NOT independent real-world sampling units. The exact unit of analysis, choice between parametric and non-parametric tests, correction for multiple comparisons (e.g., Benjamini-Hochberg), and confidence interval estimation must align with established empirical standards in ML.
- **Alternatives Considered:** Automatically computing and reporting p-values across 5 seeds. Rejected as statistically flawed.
- **Review Trigger:** Experimental design finalization.

---

### DEC-005: Candidate Benchmark Datasets
- **Status:** `PROVISIONAL`
- **Decision:** Support Adult Census Income, ProPublica COMPAS, and Statlog German Credit through a standardized `BaseDataset` interface. Real datasets are loaded via documented paths/APIs and never committed if access conditions apply.
- **Rationale:** These three tabular datasets represent the most widely scrutinized benchmarks in algorithmic fairness literature, allowing direct contextualization against prior studies.
- **Alternatives Considered:** Introducing proprietary or synthetic-only datasets. Rejected for real-world empirical validity.
- **Review Trigger:** Verification of licensing terms and subgroup sample size viability.

---

### DEC-006: Candidate Model Families
- **Status:** `PROVISIONAL`
- **Decision:** Support Logistic Regression (linear baseline), Random Forest (bagged non-linear ensemble), and XGBoost (boosted trees).
- **Rationale:** Covers diverse functional classes with differing inductive biases and explainability mechanisms (LinearExplainer vs TreeExplainer).
- **Alternatives Considered:** Neural Networks (MLP), SVMs. Deferred to avoid unnecessary complexity in tabular settings.
- **Review Trigger:** Model training latency and convergence verification on benchmark splits.

---

### DEC-007: Mitigation Taxonomy
- **Status:** `LOCKED`
- **Decision:** Strictly categorize mitigation techniques according to the established ML fairness taxonomy:
  - *Pre-processing:* Fairlearn `CorrelationRemover` (modifies feature representation prior to training).
  - *In-processing:* Fairlearn `ExponentiatedGradient` (modifies objective function during training via reduction).
  - *Post-processing:* Fairlearn `ThresholdOptimizer` (modifies decision boundaries on predictions post-training).
- **Rationale:** Standardizes the experimental comparisons and prevents conflation of distinct intervention stages.
- **Alternatives Considered:** Ad-hoc reweighing or bespoke threshold heuristics. Rejected in favor of Fairlearn's mathematically established algorithms.

---

### DEC-008: Branch Isolation & Code Protection
- **Status:** `LOCKED`
- **Decision:** All research scripts, models, configurations, tests, notebooks, and results must reside strictly in `research/` on branch `research/fairness-xai-study`. Production code in `backend/`, `frontend/`, and root deployment manifests must remain 100% untouched.
- **Rationale:** Guarantees zero regression on the live hackathon-winning application deployed on Vercel and Render.
- **Alternatives Considered:** Refactoring existing `backend/app/ml/` in place. Rejected to avoid production downtime or configuration drift.

---

### DEC-009: Synthetic Data Protocol
- **Status:** `LOCKED`
- **Decision:** Synthetic data generation is strictly restricted to unit tests, smoke tests, and CI environments. Synthetic datasets must NEVER be reported as empirical research findings.
- **Rationale:** Prevents fabricated or pseudo-empirical results from contaminating scientific literature.
- **Alternatives Considered:** Using synthetic data for main experiments. Rejected.

---

### DEC-010: End-to-End Manifest Provenance
- **Status:** `LOCKED`
- **Decision:** Every experiment run must automatically generate a machine-readable JSON manifest stored in `research/results/manifests/` capturing: `experiment_id`, `git_commit_hash`, dataset version/metadata, model hyperparameters, mitigation configuration, random seed, data split sizes, Python/dependency versions, and timestamp. Raw result files must cross-reference this `experiment_id`.
- **Rationale:** Enables full auditability: any table, chart, or paper claim can be traced back to the exact code commit and run parameters.
- **Alternatives Considered:** Relying on filename conventions alone. Rejected as insufficient for strict reproducibility.

---

### DEC-011: Attribution Comparison Metrics
- **Status:** `PROVISIONAL`
- **Decision:** Provide candidate SHAP attribution comparison metrics: Cosine Similarity (directional alignment), Spearman Rank Correlation (ordering consistency), and L1/L2 Euclidean attribution difference (magnitude shift).
- **Rationale:** Provides complementary mathematical perspectives on how bias mitigation shifts feature attributions.
- **Alternatives Considered:** Proposing a novel unvalidated composite attribution metric. Rejected.
- **Review Trigger:** Literature consensus on feature importance stability metrics.

---

### DEC-012: Gemini / LLM Role in Research
- **Status:** `PROVISIONAL`
- **Decision:** Google Gemini 2.5 Flash API continues powering natural language explanations in the production product, but is excluded from the initial research scientific claims and experiment matrix.
- **Rationale:** LLM generation adds stochasticity, API cost, and external service dependency that would complicate baseline reproducibility. An LLM experiment will only be designed if a specific research question regarding automated governance reporting is formulated.
- **Alternatives Considered:** Benchmarking Gemini explanations against SHAP attributions. Deferred.

---

### DEC-013: Paper Visualizations
- **Status:** `PROVISIONAL`
- **Decision:** Omit radar charts. Prioritize:
  1. Fairness vs performance scatter/Pareto frontier plots.
  2. Before/after fairness delta bar/scatter plots.
  3. Before/after accuracy/F1 delta plots.
  4. Feature attribution similarity/shift distributions.
- **Rationale:** Radar charts can visually distort area and ordering. 2D scatter and paired delta charts provide clearer empirical comparisons.
- **Alternatives Considered:** Radar/spider charts. Rejected.
