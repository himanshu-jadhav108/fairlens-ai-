# Pilot Empirical Evidence

> [!IMPORTANT]
> **PILOT EMPIRICAL EVIDENCE — Not final confirmatory evidence.**

Execution Mode: `PILOT_VALIDATION_RUN`

This directory contains artifacts from the **empirical pilot study** using the real Gemini API.

The pilot matrix is:
- 2 Datasets × 2 Models × 2 Mitigations × 3 Seeds = **24 conditions**

## Purpose

The pilot serves to:
1. Validate the end-to-end pipeline with real LLM API calls
2. Expose evaluator bugs before the confirmatory experiment
3. Validate provenance completeness
4. Validate paired template/LLM evaluation
5. Validate data leakage controls
6. Provide preliminary descriptive statistics

## What pilot results are NOT

Pilot results must NOT be treated as:
- Final confirmatory empirical evidence
- Final statistical conclusions
- Evidence for definitive claims in the paper
- Ground truth for hypotheses H1/H2/H3

Pilot results become final evidence ONLY if they are explicitly re-analyzed as part of the Final Empirical Study with a documented justification.

## Contents

| Subdirectory | Contents |
|:---|:---|
| `raw/` | Real Gemini explanation JSONs (PILOT_VALIDATION_RUN) |
| `summaries/` | Pilot faithfulness evaluation summaries |
| `claims/` | Pilot claim decompositions |
| `manifests/` | Pilot experiment manifests |
| `processed/` | Aggregated pilot statistics |
| `figures/` | Pilot visualization outputs |

## Key documents

- `pilot_execution_summary.json` — Machine-readable execution summary
- `PILOT_RESULTS_REPORT.md` — Human-readable pilot results
- `PILOT_STATISTICAL_REPORT.md` — Provisional statistical analysis
- `ANNOTATION_QUEUE.json` — Claims requiring human adjudication
- `pilot_failures.json` — Failed conditions (if any)
