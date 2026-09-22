> [!NOTE]
> **SUPERSEDED ARCHIVAL FRAGMENT:** This file is an early scaffold fragment retained for historical reference. The sole active, frozen, authoritative manuscript is [PAPER_DRAFT.md](./PAPER_DRAFT.md).

# 8. Empirical Results

<!-- MANDATORY RESEARCH INTEGRITY DIRECTIVE:
Do NOT populate tables or narrative text with fabricated, simulated, or hallucinated numbers.
Every entry in this section must directly cross-reference an experiment_id and raw result artifact
from verified experimental runs in research/results/.
-->

## 8.1 Overall Faithfulness: LLM vs. Deterministic Template Baseline (RQ1)
- Quantitative comparison of primary faithfulness dimensions:
  - Numerical Faithfulness Rate
  - Directional Faithfulness Rate
  - Attribution Faithfulness Rate
  - Unsupported Claim Rate
  - Secondary: Evidence Coverage Rate
- *[Placeholder: Table 1 — Summary Faithfulness Metrics across Full Benchmark Suite]*
- *[Placeholder: Figure 1 — Distribution of Numerical Discrepancies and Directional Errors]*

## 8.2 Directional and Magnitude Faithfulness (RQ2)
- Evaluation of mathematical directional claims vs. domain semantic interpretations.
- Rate of sign inversions across fairness vs. predictive performance metrics.
- Analysis of qualitative magnitude claims (`UNDETERMINABLE` cases routed to human adjudication).
- *[Placeholder: Table 2 — Directional Error Rates and Semantic Inversions by Metric Type]*

## 8.3 Feature Attribution Faithfulness (RQ3)
- Top-1 feature attribution accuracy.
- Top-$k$ feature set overlap and rank preservation.
- Hallucinated or non-existent feature claims.
- *[Placeholder: Table 3 — SHAP Feature Attribution Faithfulness Across Predictive Models]*

## 8.4 Statistical Hypothesis Testing & Effect Sizes
- Paired comparison results between Template Explainer and LLM Explanations (Explanation-level paired $t$-tests and Wilcoxon signed-rank tests).
- 95% Bootstrap Confidence Intervals over explanation-level scores.
- *[Placeholder: Table 4 — Inferential Statistical Comparisons and Effect Sizes]*
