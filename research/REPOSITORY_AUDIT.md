# FairLens AI — Comprehensive Repository & Research Audit

**Audit Date:** September 17, 2026  
**Audited Branch:** `main` (commit `af11ba2b9a52898a1a78f0d7542385225252900b`)  
**Target Research Branch:** `research/fairness-xai-study`  
**Repository:** [https://github.com/himanshu-jadhav108/fairlens-ai-](https://github.com/himanshu-jadhav108/fairlens-ai-)  
**Live Production Application:** [https://fairlens-ai-nine.vercel.app/](https://fairlens-ai-nine.vercel.app/)  

---

## 1. Executive Summary & Objective

This repository audit evaluates the existing FairLens AI codebase to prepare an isolated, mathematically defensible, and reproducible machine-learning research framework. FairLens AI is an enterprise-grade Responsible AI governance platform developed during a hackathon that detects, explains, and mitigates bias in machine learning models.

The primary objective of this audit is to:
1. Establish a clear boundary between the existing live production application and the research framework.
2. Identify reusable algorithmic components (`FairnessEngine`, Fairlearn mitigations, SHAP attributions).
3. Document existing technical debt, data leakage risks, and environment fragile points that could impede scientific reproducibility.
4. Establish an architectural design for `research/` that guarantees experimental validity without modifying or breaking the production software.

---

## 2. Existing Repository Architecture

The current repository is organized as a full-stack web application:

```
fairlens-ai/
├── backend/                  # FastAPI Python backend service
│   ├── app/
│   │   ├── api/              # API versioning & auth dependencies
│   │   ├── core/             # Configuration, security, JWT settings
│   │   ├── db/               # SQLAlchemy base models and SQLite/Postgres session
│   │   ├── ml/               # Core ML modules: fairness, mitigation, explainability
│   │   │   ├── fairness_engine.py
│   │   │   ├── mitigation_engine.py
│   │   │   └── explainability_engine.py
│   │   ├── routes/           # Endpoints: /upload, /analyze, /explain, /fix, /history
│   │   ├── services/         # Firebase Firestore & Google Gemini AI integration
│   │   ├── main.py           # FastAPI entrypoint, CORS middleware
│   │   ├── ml_pipeline.py    # Pipeline coordinator for user sessions
│   │   └── state.py          # Session-based CSV disk storage
│   ├── data/                 # User-uploaded session CSVs
│   ├── requirements.txt      # Production backend dependencies
│   ├── render.yaml           # Render deployment configuration (Python 3.10.12)
│   └── runtime.txt           # Pinned runtime: 3.10.12
├── frontend/                 # React 18 + Vite + TailwindCSS + Radix UI
│   ├── src/                  # Single Page Application
│   │   ├── components/       # UI components (upload, detect, explain, fix, report)
│   │   ├── context/          # Global application state (AppContext)
│   │   └── lib/              # API clients, PDF export utilities
│   ├── package.json          # Node dependencies (Vite, React, Vitest, Tailwind)
│   └── vercel.json           # Vercel static hosting routing configuration
├── datasets/                 # Synthetic sample datasets (hiring_bias.csv, loan_approval_bias.csv)
│   └── generate_datasets.py  # Script for generating synthetic benchmark data
├── ARCHITECTURE.md           # Production system design document
├── DEPLOYMENT_AUDIT.md       # Cloud deployment audit (Render + Vercel)
└── README.md                 # Primary project overview & screenshots
```

---

## 3. Detailed Component Audit

### 3.1 Frontend
- **Framework:** React 18.3.1 with Vite 5.4.19 and TypeScript 5.8.3.
- **Styling:** TailwindCSS 3.4.17, Radix UI primitives, Lucide icons.
- **State & Data:** Axios client connecting to backend API; Zustand / React Context for state.
- **Testing & Build:** Vitest suite (`npm run test`) and production build (`npm run build`) passing cleanly.
- **Deployment:** Vercel static site (`fairlens-ai-nine.vercel.app`).

### 3.2 Backend & API Routes
- **Framework:** FastAPI 0.111.0+ with Uvicorn ASGI server.
- **Endpoints:**
  - `POST /api/upload`: Receives CSV, stores file to `backend/data/{session_id}.csv`, registers schema.
  - `POST /api/analyze`: Encodes target/sensitive attributes, fits `LogisticRegression`, evaluates fairness via `FairnessEngine`.
  - `POST /api/explain`: Computes SHAP attributions using `LinearExplainer` on a 150-sample subset.
  - `POST /api/ai-explain`: Queries Google Gemini 2.5 Flash API for natural-language interpretation.
  - `POST /api/fix`: Evaluates 3 mitigation strategies (`CorrelationRemover`, `ExponentiatedGradient`, `ThresholdOptimizer`), saves `{session_id}_fair.csv`.
  - `GET /api/download-fixed/{session_id}`: Streams mitigated CSV with appended fair predictions.
  - `GET /api/history`: Retrieves user audit history from Firebase Firestore.

### 3.3 Core Machine Learning Stack
- **Dependencies:** `scikit-learn`, `fairlearn`, `shap`, `pandas`, `numpy`, `scipy`.
- **Model Training:** Hardcoded to `LogisticRegression(max_iter=1000, random_state=42)` with `StandardScaler`.
- **Fairness Engine:** Implements Demographic Parity Difference, Equalized Odds Difference, Equal Opportunity Difference, Disparate Impact Ratio, and per-group confusion matrices via Fairlearn's `MetricFrame`.
- **Mitigation Engine:** Evaluates:
  1. *Pre-processing:* `CorrelationRemover(sensitive_feature_ids=[...])`
  2. *In-processing:* `ExponentiatedGradient(estimator=LogisticRegression, constraints=DemographicParity(), max_iter=5)`
  3. *Post-processing:* `ThresholdOptimizer(estimator=LogisticRegression, constraints="demographic_parity", predict_method="predict_proba", prefit=True)`
- **Explainability Engine:** `shap.LinearExplainer` calculating global mean absolute SHAP, demographic subgroup importance, and local false-negative individual attributions.

---

## 4. Reusable Components for Research

| Component | Source File | Reusability Assessment | Adaptations Required for Research |
| :--- | :--- | :--- | :--- |
| **Fairness Metric Computations** | `backend/app/ml/fairness_engine.py` | Highly reusable mathematical formulations for DPD, EOD, EOppD, DI, FPR/FNR difference. | Add explicit handling for zero-division/empty subgroups; record reasons instead of returning fallback defaults; expose raw rates. |
| **Fairlearn Mitigation Algorithms** | `backend/app/ml/mitigation_engine.py` | Proven wrapping of Fairlearn reductions, pre-processors, and post-processors. | Decouple from LogisticRegression to support multiple model families (Random Forest, XGBoost); allow configurable iterations and constraints; eliminate test leakage in threshold fitting. |
| **SHAP Explainability Logics** | `backend/app/ml/explainability_engine.py` | Reusable concepts for global and subgroup-level attribution calculation. | Extend beyond `LinearExplainer` to support `TreeExplainer` and model-agnostic explainers; record complete SHAP provenance metadata (seed, background distribution, explainer type). |
| **Synthetic Dataset Generators** | `datasets/generate_datasets.py` | Useful for fast deterministic unit tests and smoke tests. | Encapsulate within test harness; ensure synthetic datasets are NEVER treated as empirical research evidence. |

---

## 5. Technical Debt & Reproducibility Risks

1. **Python Environment & C-Extension Mismatch:**
   - The production Render service runs Python 3.10.12.
   - The local environment has multiple Python versions. An existing virtual environment (`backend/venv`) created via Anaconda Python 3.14 failed to load compiled `.cp313` wheels for `scikit-learn`.
   - In contrast, Python 3.13 (`C:\Program Files\Python313\python.exe`) successfully executes modern versions of `scikit-learn 1.8.0`, `fairlearn 0.14.0`, `shap 0.50.0`, `xgboost 3.4.1`, `scipy 1.17.0`, and `pytest 9.1.1`.
   - *Mitigation:* Research code must specify strict dependency pins in `research/requirements-research.txt` and record execution environment metadata in all experiment manifests.

2. **Tracked Bytecode in Git History:**
   - A compiled bytecode file (`backend/app/ml/__pycache__/mitigation_engine.cpython-313.pyc`) was tracked in Git, causing spurious dirty states when Python executions update timestamps.
   - *Mitigation:* Discard changes on `main`, maintain clean workspace, and ensure `.gitignore` covers all research pycache and artifacts.

3. **Data Leakage in Post-Processing Mitigation:**
   - In the production MVP, `ThresholdOptimizer.fit` was passed `X_train` with `prefit=True` on a model fitted on the same `X_train`. For research validity, post-processing threshold selection requires a separate validation split to prevent overfitting the decision thresholds to training data.
   - *Mitigation:* Implement strict Train (model fitting) / Validation (threshold tuning, hyperparameter calibration) / Test (final evaluation only) discipline.

4. **Hardcoded In-Processing Iterations:**
   - `ExponentiatedGradient` in `mitigation_engine.py` has `max_iter=5` hardcoded for hackathon latency reasons. In research, optimization convergence requires configurable iterations and tolerance settings.

5. **Lack of Common Model Interface:**
   - The production app exclusively uses `LogisticRegression`. A rigorous study requires comparing linear baselines against non-linear ensembles (Random Forest, XGBoost).

---

## 6. Proposed Research Architecture (`research/`)

```
research/
├── README.md                 # Complete research guide & reproducibility instructions
├── REPOSITORY_AUDIT.md       # This comprehensive audit report
├── DECISIONS.md              # Research decision log (provisional vs locked)
├── requirements-research.txt # Pinned research dependencies
├── configs/                  # Configuration-driven experiment specifications
├── datasets/                 # Base abstractions, loaders for Adult, COMPAS, German Credit
├── preprocessing/            # Leak-free train-fitted preprocessing pipelines
├── models/                   # Common interface: Logistic Regression, Random Forest, XGBoost
├── mitigation/               # Common interface: Pre-, In-, and Post-processing strategies
├── fairness_metrics/         # Metric evaluators with explicit NaN/undefined handling
├── performance_metrics/      # Standard performance evaluation (Acc, Prec, Rec, F1, ROC-AUC)
├── explainability/           # Model-aware SHAP engine with complete provenance tracking
├── experiments/              # Single runner, batch runner, paired baseline/mitigation engine
├── analysis/                 # Aggregator and candidate visualization generators
├── statistics/               # Provisional inferential testing utilities
├── results/
│   ├── manifests/            # Machine-readable provenance manifests per experiment
│   ├── raw/                  # Detailed run results (JSON)
│   ├── processed/            # Aggregated summary tables (CSV)
│   └── figures/              # Candidate visualization figures (PNG)
├── notebooks/                # Reproducible analysis and inspection notebooks
├── scripts/                  # CLI tools for running experiments, aggregation, and figures
├── tests/                    # Fast, self-contained unit tests using synthetic benchmarks
└── paper/                    # Provisional paper structure scaffold (no fabricated text)
```

---

## 7. Files That MUST NOT Be Modified

To guarantee that the live production application remains 100% operational and undisturbed, the following directories and files are strictly locked:

- `backend/app/` (all API routes, controllers, services, database schemas, and production ML engines)
- `backend/render.yaml`, `backend/Procfile`, `backend/requirements.txt`, `backend/runtime.txt`
- `frontend/src/` (all React components, hooks, contexts, pages, styles)
- `frontend/package.json`, `frontend/vite.config.ts`, `frontend/vercel.json`
- `ARCHITECTURE.md`, `DEPLOYMENT_AUDIT.md`, `DEPLOYMENT_GUIDE.md`
- Root `README.md` (production documentation on `main`)

All research implementations must reside strictly within `research/` on the isolated branch `research/fairness-xai-study`.
