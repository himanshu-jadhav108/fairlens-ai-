> [!NOTE]
> **SUPERSEDED ARCHIVAL FRAGMENT:** This file is an early scaffold fragment retained for historical reference. The sole active, frozen, authoritative manuscript is [PAPER_DRAFT.md](./PAPER_DRAFT.md).

# 9. Error Analysis

<!-- MANDATORY DIRECTIVE: To be populated strictly from extracted claims artifacts in research/results/claims/ -->

## 9.1 Empirical Distribution of Faithfulness Errors (RQ4)
Analysis of failure modes categorized according to the formal error taxonomy:
- **Numerical Association Errors:** Number correctly extracted from evidence but erroneously attached to a different metric (e.g. associating accuracy score with demographic parity difference).
- **Rounding and Tolerance Discrepancies:** Values differing from ground truth beyond allowable bounds.
- **Directional Reversals:** Claiming disparity or performance increased when evidence confirms a decrease.
- **Domain Semantic Inversions:** Confusing mathematical direction with fairness interpretation (e.g. reporting a decrease in disparate impact as an improvement when it actually moves further from 1.0).
- **Attribution Inversions:** Reporting a lower-ranked or hallucinated feature as the most important predictor.
- **Ungrounded Causal Assertions:** Asserting that sensitive demographic attributes "caused" model predictions or disparities.
- **Absolute Fairness Declarations:** Claiming that a mitigated model is "completely unbiased" or "entirely fair".
- **Overgeneralization:** Asserting that the model is "fair for everyone" based on evaluations over limited demographic subgroups.

## 9.2 Qualitative Case Studies of High-Stakes Failure Modes
- *[Placeholder: Concrete examples of extracted claims contrasting generated text against structured ground truth]*
- Qualitative evaluation of failure triggers (e.g., prompt complexity, long evidence tables, ambiguous feature names).
