# FairLens AI: Paper Evidence Package & Classification Matrix

**Study Title:** Quantitative Faithfulness of LLM-Generated Natural-Language Explanations for Machine Learning Fairness Audits: An Empirical Study  
**Document Purpose:** Clear, immutable demarcation of empirical vs. synthetic vs. validation evidence supporting research publications.

---

## 1. Evidence Tier Taxonomy

To ensure unimpeachable scientific integrity and prevent data contamination, all artifacts in this repository belong to exactly one of three strictly segregated tiers:

```
+-------------------------------------------------------------------------------+
|                             EVIDENCE TAXONOMY                                 |
+---------------------------+---------------------------+-----------------------+
| TIER 1: FINAL CONFIRMATORY| TIER 2: PILOT VALIDATION  | TIER 3: SOFTWARE      |
|         EMPIRICAL DATA    |         EMPIRICAL DATA    |         VALIDATION    |
| (FINAL_EMPIRICAL_RUN)     | (PILOT_VALIDATION_RUN)    | (SOFTWARE_VALIDATION) |
+---------------------------+---------------------------+-----------------------+
| - 135-condition matrix    | - 24-condition matrix     | - Unit/mock test runs |
| - Real Gemini API calls   | - Real Gemini API calls   | - MockLLMProvider runs|
| - Final paper tables/plots| - Pilot reports & stats   | - Adversarial tests   |
| - Pre-registered protocol | - Protocol validation     | - Regression suites   |
| - Staged / Not yet run    | - Completed (24/24)       | - 100% Passing        |
+---------------------------+---------------------------+-----------------------+
```

---

## 2. Directory Separation & Contamination Controls

| Evidence Class | Canonical Directory | `execution_mode` Field Value | Admitted to Paper Main Text? | Contamination Protections |
| :--- | :--- | :--- | :---: | :--- |
| **Tier 1: Final Empirical** | `research/results/final/` | `FINAL_EMPIRICAL_RUN` | Yes (Primary Evidence) | Aggregator rejects any file without `FINAL_EMPIRICAL_RUN`. |
| **Tier 2: Pilot Empirical** | `research/results/pilot/` | `PILOT_VALIDATION_RUN` | Yes (Pilot Evidence / Sec. 4) | Aggregator requires `PILOT_VALIDATION_RUN`; skips mock sources. |
| **Tier 3: Software Validation** | `research/results/smoke/` | `SOFTWARE_VALIDATION_ONLY` | No (Internal Verification Only) | Hardcoded exclusion in `aggregator.py` for `/smoke/` path. |

---

## 3. Inventory of Generated Artifacts by Tier

### Tier 2: Pilot Validation Run Artifacts (Completed)
- **Execution Summary:** [`pilot_execution_summary.json`](file:///d:/Projects/fairlens-ai/research/results/pilot/pilot_execution_summary.json) (24 completed, 0 failed)
- **Processed Tables:**
  - [`faithfulness_runs.csv`](file:///d:/Projects/fairlens-ai/research/results/pilot/processed/faithfulness_runs.csv) (50 evaluated explanation runs)
  - [`faithfulness_summary.csv`](file:///d:/Projects/fairlens-ai/research/results/pilot/processed/faithfulness_summary.csv)
- **Pilot Reports:**
  - [`PILOT_RESULTS_REPORT.md`](file:///d:/Projects/fairlens-ai/research/results/pilot/PILOT_RESULTS_REPORT.md)
  - [`PILOT_STATISTICAL_REPORT.md`](file:///d:/Projects/fairlens-ai/research/results/pilot/PILOT_STATISTICAL_REPORT.md)
  - [`PILOT_GO_NO_GO.md`](file:///d:/Projects/fairlens-ai/research/PILOT_GO_NO_GO.md)
- **Human Annotation Staging:**
  - [`ANNOTATION_QUEUE.json`](file:///d:/Projects/fairlens-ai/research/results/pilot/ANNOTATION_QUEUE.json) (742 queued claims; no fabricated labels)
  - [`ANNOTATION_README.md`](file:///d:/Projects/fairlens-ai/research/results/pilot/ANNOTATION_README.md)
- **Provenance Manifests:** 24 JSON files under `research/results/pilot/manifests/`
- **Faithfulness Summaries:** 50 JSON files under `research/results/pilot/summaries/`
- **Raw Evidence:** 24 JSON files under `research/results/pilot/raw/`

### Tier 3: Software Validation Artifacts (Passing)
- **Mock Smoke Directory:** `research/results/smoke/` (Contains only mock provider outputs)
- **Evaluator Validation:** [`EVALUATOR_VALIDATION.md`](file:///d:/Projects/fairlens-ai/research/EVALUATOR_VALIDATION.md)
- **Test Suite Results:** [`TEST_REPORT.md`](file:///d:/Projects/fairlens-ai/research/TEST_REPORT.md)

---

## 4. Citation and Attribution Guidelines

When referencing results in the manuscript:
1. **Pilot claims must be explicitly described as pilot empirical data** ($N = 24$), never confused with the 135-condition final matrix.
2. **Deterministic template comparisons** must cite the paired Wilcoxon test results ($p < 10^{-5}$ for numerical faithfulness, $p < 10^{-3}$ for directional faithfulness).
3. **Human agreement claims** must clarify that human annotation is pending Phase 4 protocol execution.
