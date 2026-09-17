# FairLens AI Pilot Study: Human Annotation Guidelines & Protocol

> **CRITICAL EVIDENCE CLASSIFICATION NOTICE**
> 
> **Human annotation has NOT yet been performed for this pilot study.**
> All claims present in [`ANNOTATION_QUEUE.json`](file:///d:/Projects/fairlens-ai/research/results/pilot/ANNOTATION_QUEUE.json) reflect automated rule-based extractions generated during pilot validation runs (`PILOT_VALIDATION_RUN`).
> No human labels have been fabricated or synthetically imputed. The fields `annotator_id`, `annotator_judgment`, `is_factually_accurate`, `is_hallucination`, and `notes` remain strictly `null` until live human annotator recruitment commences.

---

## 1. Purpose of Human Annotation

The primary objective of the human annotation protocol is to calculate the **inter-annotator agreement** and determine the **ground-truth validation rate** for the automated NLI-style claim extraction and classification pipeline.

Specifically, it measures:
1. **Extraction Recall & Precision:** Did the regex and sentence segmentation extract complete, self-contained factual claims?
2. **Classification Accuracy:** Did the automated evaluator correctly classify claims as `SUPPORTED`, `REFUTED`, or `UNSUPPORTED` against the ground-truth Structured Audit Evidence?
3. **Hallucination Detection:** Does the human evaluator agree with the automated flag for ungrounded or contradictory assertions?

---

## 2. Queue Overview

- **Source Artifact:** [`ANNOTATION_QUEUE.json`](file:///d:/Projects/fairlens-ai/research/results/pilot/ANNOTATION_QUEUE.json)
- **Total Claims Queued:** 742 claims extracted across 24 experimental pilot conditions.
- **Breakdown by Claim Type:**
  - **Numerical Claims:** Values referencing performance (Accuracy, ROC AUC, Precision) and fairness metrics (Demographic Parity Difference, Equalized Odds).
  - **Directional Claims:** Comparative statements describing increases, decreases, or parity improvements across baseline vs. mitigated states.
  - **Attribution Claims:** Feature importance assertions referencing top SHAP features and their signed contributions.
  - **Unsupported Claims:** Extracted statements asserting external facts not present in the evidence artifact.

---

## 3. Annotation Schema & Labels

Each queue item contains the following fields to be populated by human reviewers:

```json
{
  "queue_id": "pilot_claim_0001",
  "experiment_id": "adult__logistic_regression__correlation_remover__seed42__ab326813",
  "claim_text": "* Demographic Parity Difference: 0.4222",
  "ground_truth_path": "baseline_state.fairness_metrics.demographic_parity_difference.value",
  "automated_classification": "SUPPORTED",
  "human_annotation": {
    "annotator_id": "ANON_USER_01",
    "annotator_judgment": "SUPPORTED",
    "is_factually_accurate": true,
    "is_hallucination": false,
    "notes": "Verified against baseline audit evidence.",
    "annotation_timestamp_utc": "2026-09-17T..."
  }
}
```

### Judgment Categories
1. `SUPPORTED`: The claim is directly substantiated by the corresponding value in the Structured Audit Evidence within tolerance (±0.005 for floats, exact sign for directions).
2. `REFUTED`: The claim makes a factual statement that directly contradicts the evidence (e.g. claims accuracy increased when it decreased).
3. `UNSUPPORTED`: The claim asserts a specific metric or comparison that does not exist anywhere in the evidence object.
4. `UNDETERMINABLE`: The statement is ambiguous, rhetorical, or subjective without a clearly testable factual assertion.

---

## 4. Evaluator Recruitment & Reliability Metrics

- **Annotators per Item:** 3 independent annotators per claim item.
- **Inter-Annotator Agreement Metrics:**
  - **Cohen's Kappa ($\kappa$):** For pairwise annotator concordance.
  - **Krippendorff's Alpha ($\alpha$):** For multi-annotator reliability across nominal and ordinal categories.
- **Acceptance Threshold:** $\alpha \ge 0.80$ required for final validation study release. Disagreements will be resolved by an adjudicating senior ML fairness researcher.

---

## 5. Execution Timeline

Human annotation is scheduled to take place during Phase 4 of the research roadmap, following the formal launch of the 135-condition confirmatory empirical study.
