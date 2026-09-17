# FairLens AI Research — Production Isolation Audit

**Branch:** `research/fairness-xai-study`  
**Base Branch:** `main`  
**Date:** 2026-09-17  
**Status:** `STRICT ISOLATION VERIFIED — 0 PRODUCTION FILES TOUCHED`

---

## 1. Executive Summary

This audit rigorously verifies that all research engineering, experimental pipelines, LLM interfaces, and evaluation harnesses developed for the study *"Quantitative Faithfulness of LLM-Generated Natural-Language Explanations for Machine Learning Fairness Audits: An Empirical Study"* reside strictly within the `/research` directory. The production FairLens AI application (`backend/` and `frontend/`), its root deployment configurations, and public-facing assets remain 100% untouched and unaffected.

---

## 2. Verification of Git Diff Against Main

A structural diff check against `main` demonstrates complete encapsulation:

```bash
git diff main...research/fairness-xai-study --name-only
```

**Results:**
- Total changed files: All localized under `research/`.
- `backend/`: **0 files modified / 0 files deleted / 0 files added**
- `frontend/`: **0 files modified / 0 files deleted / 0 files added**
- Root configuration files (`runtime.txt`, `ARCHITECTURE.md`, `DEPLOYMENT_*.md`): **0 files modified**

---

## 3. Dependency Isolation Audit

### 3.1 Separate Requirements Specification
- **Production Dependencies:** Managed independently in `backend/requirements.txt`.
- **Research Dependencies:** Managed strictly in `research/requirements-research.txt`.
- **No Cross-Contamination:** No scientific or experimental packages (e.g. `shap`, `fairlearn`, `pytest`, `scipy`) were injected into the production application bundle, preventing dependency bloat or runtime conflicts in production hosting.

---

## 4. Execution Sandbox & Data Directory Isolation

1. **Working Directory Containment:** All research scripts (`run_experiment.py`, `run_pilot_experiment.py`, `run_llm_experiment.py`, `aggregator.py`) write artifacts exclusively to `research/results/` (or subdirectories `pilot/`, `final/`, `smoke/`).
2. **No Shared State:** The research subsystem does not share or manipulate production database instances, cached sessions, or frontend local storage.
3. **Reproducibility Guarantee:** Any developer or reviewer can clone the repository, install `research/requirements-research.txt`, and execute research scripts without initializing or running the FairLens web application.
