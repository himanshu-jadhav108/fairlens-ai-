> [!NOTE]
> **SUPERSEDED ARCHIVAL FRAGMENT:** This file is an early scaffold fragment retained for historical reference. The sole active, frozen, authoritative manuscript is [PAPER_DRAFT.md](./PAPER_DRAFT.md).

# 10. Discussion

## 10.1 Systematic Variation Across Experimental Conditions (RQ5)
- How explanation faithfulness varies across:
  - Benchmark datasets (varying sample size, feature dimensionality, baseline disparity magnitude).
  - Model families (linear vs. tree ensemble complexity).
  - Mitigation strategies (pre-processing vs. in-processing vs. post-processing).
  - Fairness metrics (distance-from-zero metrics vs. ratio metrics like Disparate Impact).
  - Prompt formulations (structured JSON-grounded vs. natural-language narrative prompts).

## 10.2 Implications for Algorithmic Accountability and AI Governance
- Risks of deploying conversational or generative AI interfaces as compliance tools in high-stakes auditing.
- The communicative trade-off: linguistic accessibility vs. quantitative fidelity.
- Why deterministic baseline explainers remain vital controls for mission-critical audit reporting.

## 10.3 Practical Recommendations for Practitioners
- Guideline 1: Enforce deterministic grounding checks before presenting LLM-generated audit reports to decision-makers.
- Guideline 2: Separate factual faithfulness evaluation from evidence coverage assessment.
- Guideline 3: Explicitly flag qualitative magnitude claims ("substantially fair") for human review.
- Guideline 4: Constrain prompts to prevent causal confabulation from observational disparity audits.
