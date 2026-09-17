# FairLens AI Research — Results Directory Structure

This directory stores all machine-readable outputs, provenance manifests, processed statistical summaries, and candidate visualizations.

```
results/
├── smoke/        # Offline software verification outputs (tagged SOFTWARE_VALIDATION_ONLY; NEVER in paper)
├── pilot/        # Exploratory calibration runs prior to final pre-registration
├── manifests/    # JSON manifests with Git commit hashes, environment, and configuration metadata
├── raw/          # Unmodified JSON results and generated explanation outputs for empirical runs
├── claims/       # Atomic claim-level JSON records with full ground-truth traceability
├── summaries/    # Summary FaithfulnessReport JSON files
├── processed/    # Aggregated CSV summary tables (mean/std across seeds, delta comparisons)
└── figures/      # Candidate vector/raster visualizations generated from processed data
```

### Strict Output Tier Isolation (Section 20)
1. **Smoke Tests:** Executed via `--smoke-test` with synthetic data and mock providers. Outputs are written exclusively to `smoke/` with metadata `"execution_mode": "SOFTWARE_VALIDATION_ONLY"`. These results are strictly barred from research findings.
2. **Empirical Runs:** Full matrix executions written to `raw/`, `claims/`, `summaries/`, and `manifests/`.

### Traceability Guarantee
Every entry in `processed/` or `figures/` traces back to:
1. A raw result JSON file in `raw/`
2. A corresponding provenance manifest in `manifests/`
3. A unique `experiment_id` and SHA-256 `evidence_hash`
4. The exact `git_commit_hash` that generated the data

