# FairLens AI Research — Results Directory Structure

This directory stores all machine-readable outputs, provenance manifests, processed statistical summaries, and candidate visualizations.

```
results/
├── manifests/    # JSON manifests with Git commit hashes, environment, and configuration metadata
├── raw/          # Unmodified JSON results for each individual experiment run
├── processed/    # Aggregated CSV summary tables (mean/std across seeds, delta comparisons)
└── figures/      # Candidate vector/raster visualizations generated from processed data
```

### Traceability Guarantee
Every entry in `processed/` or `figures/` traces back to:
1. A raw result JSON file in `raw/`
2. A corresponding provenance manifest in `manifests/`
3. A unique `experiment_id`
4. The exact `git_commit_hash` that generated the data
