# Final Empirical Evidence

> [!CAUTION]
> **FINAL EMPIRICAL EVIDENCE — This directory must only contain results from the authorized confirmatory experiment.**

Execution Mode: `FINAL_EMPIRICAL_RUN`

## Status: NOT YET POPULATED

This directory will be populated ONLY after:
1. The pilot study has passed all Go/No-Go gates (see `research/PILOT_GO_NO_GO.md`)
2. The researcher has explicitly authorized the final experiment run
3. The final experiment protocol has been reviewed and locked (see `research/FINAL_EXPERIMENT_PROTOCOL.md`)
4. The 135-condition confirmatory experiment has been executed

## Intended matrix (pending researcher authorization)

- 3 Datasets × 3 Models × 3 Mitigations × 5 Seeds = **135 conditions**

## Evidence classification

Final results in this directory are the ONLY results that should be used for:
- Definitive quantitative claims in the paper
- Final statistical inference
- Conclusions on H1, H2, H3
- Absolute faithfulness measurements cited in the abstract

## Contents (after population)

| Subdirectory | Contents |
|:---|:---|
| `raw/` | Final Gemini explanation JSONs (FINAL_EMPIRICAL_RUN) |
| `summaries/` | Final faithfulness evaluation summaries |
| `claims/` | Final claim decompositions |
| `manifests/` | Final experiment manifests |
| `processed/` | Final aggregated statistics |
| `figures/` | Final paper figures |

Do NOT mix pilot results from `research/results/pilot/` into this directory.
