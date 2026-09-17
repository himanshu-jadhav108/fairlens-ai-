# FairLens AI Research — Final Research Audit

**Branch:** `research/fairness-xai-study`  
**Audit Commit:** `43c5592`  
**Audit Date:** 2026-09-17  
**Auditor:** Automated Research Infrastructure Audit  
**Status:** `RESEARCH INFRASTRUCTURE COMPLETE — EMPIRICAL PILOT COMPLETE (24/24) — READY FOR FINAL EXPERIMENT`

---

## Locked Research Topic

> **Quantitative Faithfulness of LLM-Generated Natural-Language Explanations for Machine Learning Fairness Audits: An Empirical Study**

This topic is PERMANENTLY LOCKED and must not be changed, renamed, broadened, or replaced.

---

## 1. Production Isolation

**Result: CLEAN — 0 production files modified**

The research branch modifies ONLY files under `research/`. All 158 changed files in `git diff main...research/fairness-xai-study` are within the `research/` directory.

Verified via: `git diff main...research/fairness-xai-study --name-only`

- `backend/`: Untouched ✅
- `frontend/`: Untouched ✅
- Root configuration files: Untouched ✅
- Deployment manifests: Untouched ✅

---

## 2. Evidence Classification System

The repository implements three strictly separated evidence classes:

### A. SOFTWARE_VALIDATION_ONLY
- Unit tests, adversarial tests, mock-provider runs, smoke tests, synthetic benchmark validation
- Stored in: `research/results/smoke/`
- Tagged with: `execution_mode: SOFTWARE_VALIDATION_ONLY`
- **NOT research findings. NOT admissible to empirical aggregation.**

### B. PILOT_EMPIRICAL_EVIDENCE  (execution_mode: PILOT_VALIDATION_RUN)
- Real Gemini API outputs from 24-condition pilot study
- Stored in: `research/results/pilot/`
- Tagged with: `execution_mode: PILOT_VALIDATION_RUN`
- **Methodological validation ONLY — not confirmatory final evidence**

### C. FINAL_EMPIRICAL_EVIDENCE  (execution_mode: FINAL_EMPIRICAL_RUN)
- Results from the 135-condition confirmatory experiment (NOT YET EXECUTED)
- Stored in: `research/results/final/`
- Tagged with: `execution_mode: FINAL_EMPIRICAL_RUN`
- **The ONLY evidence class suitable for definitive paper claims**

---

## 3. Data Leakage Audit

**Result: NO LEAKAGE DETECTED**

| Check | Status | Evidence |
|:---|:---:|:---|
| Preprocessor fit only on X_train | ✅ | `ResearchPreprocessor.fit()` called with X_train, `.transform()` for val/test |
| Threshold calibration uses val split | ✅ | `mitigation.fit(X_val, y_val, s_val)` in `runner.py` L117-124 |
| SHAP background distribution is X_train | ✅ | `SHAPEngine(X_train=X_train_proc)` in `runner.py` L153-165 |
| Test split used only for final evaluation | ✅ | `y_pred_mit = mitigation.predict(X_test_proc)` in `runner.py` L127 |
| No cross-partition references | ✅ | Split isolation maintained throughout pipeline |

---

## 4. Provenance Completeness Audit

**Result: COMPLETE**

Every experiment record captures:

| Field | Captured | Location |
|:---|:---:|:---|
| experiment_id | ✅ | ExperimentConfig, manifest, raw result |
| git_commit_hash | ✅ | manifest, ExplanationRecord |
| timestamp_utc | ✅ | manifest, FaithfulnessReport |
| dataset name + version + source_url | ✅ | DatasetMetadata in manifest |
| is_synthetic_benchmark | ✅ | manifest, raw result |
| model family + parameters | ✅ | manifest |
| mitigation strategy_type + parameters | ✅ | manifest |
| random_seed | ✅ | ExperimentConfig, manifest |
| train/val/test split ratios | ✅ | manifest |
| split_id (SHA-256 of data) | ✅ | DatasetSplit |
| preprocessor configuration | ✅ | manifest |
| environment versions (sklearn, fairlearn, etc.) | ✅ | manifest |
| LLM provider + model + sdk_version | ✅ | ExplanationRecord |
| generation_parameters (temp, max_tokens, top_p, seed) | ✅ | ExplanationRecord |
| input_evidence_hash (SHA-256) | ✅ | ExplanationRecord |
| prompt_id + prompt_version | ✅ | ExplanationRecord |
| execution_mode | ✅ | FaithfulnessReport, run_experiment() output |
| finish_reason | ✅ | LLMResponse metadata |
| latency_seconds | ✅ | LLMResponse metadata |

---

## 5. Faithfulness Evaluator Audit

**Result: IMPLEMENTED — ADVERSARIAL VALIDATED**

### Evaluator Components
| Component | Status |
|:---|:---:|
| NumericalFaithfulnessEvaluator | ✅ Implemented, adversarially tested |
| DirectionalFaithfulnessEvaluator | ✅ Implemented, adversarially tested |
| AttributionFaithfulnessEvaluator | ✅ Implemented, adversarially tested |
| UnsupportedClaimsDetector | ✅ Implemented, adversarially tested |
| EvidenceCoverageEvaluator (secondary) | ✅ Implemented, kept separate from primary faithfulness |

### Evaluation Protocol
- Primary judge: Deterministic rule-based extraction and comparison against structured AuditEvidence
- LLM-as-judge: NOT used as primary evaluator (excluded by DEC-003)
- Human annotation: Protocol prepared, queue populated per pilot run
- Tolerances: ±0.015 absolute, ±5% relative (pre-registered, not adjusted post-hoc)

### Coverage vs. Faithfulness Separation
- Coverage evaluator is separate (`EvidenceCoverageEvaluator`)
- Coverage is classified as a SECONDARY metric
- Primary faithfulness score does NOT include coverage
- This separation is enforced in all reporting and aggregation

---

## 6. Aggregation Contamination Guards

**Result: HARDENED — 6 regression tests passing**

The `aggregate_faithfulness_summaries()` and `aggregate_raw_results()` functions enforce:

1. **Path isolation**: Files under `/smoke/` are always excluded
2. **Mock source detection**: `explanation_source` starting with `mock` is rejected
3. **Missing execution_mode**: Conservatively excluded, never admitted as empirical
4. **Mode enforcement**: `required_execution_mode` parameter enforces PILOT vs FINAL separation
5. **Deduplication**: Experiment IDs deduplicated before aggregation
6. **SOFTWARE_VALIDATION_ONLY**: Always excluded from empirical aggregation

---

## 7. Template Baseline Pairing Audit

**Result: CORRECT**

For every experimental condition:
- Both `TemplateExplainer` and `GeminiProvider` receive IDENTICAL `AuditEvidence` objects
- Both receive the same `evidence_hash`
- Both are evaluated by the same `FaithfulnessEvaluator` with identical tolerances
- Results are stored with matching `experiment_id` for paired analysis

---

## 8. Research Hypotheses (Non-Predictive)

Pre-registered testable hypotheses:

**H1:** LLM-generated explanations exhibit measurable numerical discrepancies relative to the underlying quantitative fairness-audit evidence.

**H2:** LLM-generated explanations exhibit measurable directional or normative interpretation errors when describing changes in fairness or performance metrics.

**H3:** LLM-generated feature-importance statements exhibit measurable disagreement with SHAP-derived attribution evidence.

**NOTE:** These hypotheses do NOT predict the direction or magnitude of any effect. They do not imply LLMs perform poorly. Hypotheses are frozen and must not be modified based on pilot results.

---

## 9. Statistical Analysis Audit

**Result: PROVISIONAL — Appropriate for pilot descriptive statistics**

- Unit of analysis: Explanation/run-level (NOT claim-level)
- Claims are nested within explanations — claim-level counts are descriptive only
- Paired statistical tests: Wilcoxon signed-rank test (primary), paired t-test (secondary)
- Bootstrap CIs: 95% bootstrap confidence intervals at explanation level
- Multiple comparison correction: Bonferroni or Benjamini-Hochberg (to be finalized before final experiment)
- All test statistics carry `PROVISIONAL` disclaimer until pre-registration is complete

---

## 10. Open Decisions (Provisional)

| ID | Decision | Status |
|:---|:---|:---:|
| DEC-010 | Final Gemini model version | PROVISIONAL |
| DEC-011 | Prompt variants for ablation | PROVISIONAL |
| DEC-012 | Full experiment matrix scale | PROVISIONAL |
| DEC-013 | Statistical analysis details | PROVISIONAL |
| DEC-014 | Human annotation sample size | PROVISIONAL |

---

## 11. Stale References Cleaned

| File | Stale Reference | Resolution |
|:---|:---|:---|
| `experiments/experiment_config.py` | "Fairness-Performance-Explainability evaluation" | Fixed to correct topic |
| `scripts/run_experiment.py` | "fairness-performance-XAI experiment" | Fixed to correct topic |
| `IMPLEMENTATION_REPORT.md` | Stale provisional working title | Fixed to locked topic |

---

## 12. Current Research Status

```
RESEARCH INFRASTRUCTURE: COMPLETE
SOFTWARE VALIDATION: COMPLETE
MOCK CONTAMINATION: CLEANED
PILOT EXPERIMENT: COMPLETE (24/24 CONDITIONS EXECUTED VIA GEMINI)
PILOT STATISTICAL ANALYSIS: COMPLETE
ANNOTATION QUEUE: GENERATED (742 CLAIMS)
FINAL EXPERIMENT PROTOCOL: LOCKED (135 CONDITIONS)
FINAL EXPERIMENT EXECUTION: NOT AUTHORIZED (STAGED FOR PHASE 4)
PAPER EVIDENCE PACKAGE: COMPILED
```

**Next Step:** Lock branch and await authorized launch of 135-condition confirmatory study (`FINAL_EMPIRICAL_RUN`).
