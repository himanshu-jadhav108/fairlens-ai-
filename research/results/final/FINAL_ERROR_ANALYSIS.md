# Fine-Grained Error Taxonomy & Hallucination Analysis

> **STATUS:** Synchronized Canonical Error Analysis Artifact  
> **Authoritative Manuscript Cross-Reference:** [`research/paper/PAPER_DRAFT.md`](../paper/PAPER_DRAFT.md) Section 9  
> **Scope:** Categorization of Hallucinated, Contradicted, and Unsupported Claims across 36 Canonical Gemini 2.5 Flash Explanations  
> **Total Conditions Audited:** 36 paired runs (72 explanation artifacts; $N=1,306$ claims evaluated)  

---

## 1. Empirical Error Category Taxonomy

| Error Category | Mechanism Description | Concrete Manifestation | Observed Frequency | Severity |
|---|---|---|---|---|
| **Numerical Rounding / Truncation** | Model arbitrarily rounds 4-decimal precision values beyond scientific tolerances ($\pm 0.015$ / $5\%$) | Truncating $0.2445 \to 0.2$ (18.2% relative error) | 109 unsupported claims ($9.69\%$) | Low to Medium |
| **Numerical Hallucination** | Generation of quantitative percentages or figures not present in the input structured audit evidence | Fabricating an *"8.4% improvement"* when true delta was $0.051$ | Moderate | High |
| **State Misattribution** | Conflating pre-mitigation baseline metrics with post-mitigation outcomes | Attributing baseline demographic parity difference ($0.1895$) to the mitigated model | Moderate | High |
| **Ratio-Transition Semantic Mismatch** | Model uses comparative terms (*"lower"*, *"higher"*) to describe static demographic selection ratios relative to ideal parity, which conflicts with longitudinal transition delta matching (not genuine trajectory inversions) | Matching *"lower positive prediction rate"* against positive mitigation delta $+0.2407$ | 4 claims across 4 conditions ($3.39\%$) | Medium |
| **Metric Conflation** | Conflating distinct mathematical fairness criteria (e.g. Equalized Odds with Demographic Parity) | Calling an Equalized Odds Difference value *"demographic parity"* | Low | High |
| **Ungrounded Extrapolation / Causal Overreach** | Asserting compliance guarantees or unwarranted causal claims lacking empirical proof in audit data | Stating the model *"is now completely fair and non-discriminatory"* | Condition mean $8.51\% \pm 8.72\%$ ($113/1,306 = 8.65\%$ pooled) | Medium |

---

## 2. Architectural & Practical Recommendations for Regulated Audits

1. **Deterministic Guardrail Coupling:** Natural language generation in fairness auditing must be strictly paired with deterministic verification engines to detect metric drift before publication.
2. **Separation of Factual Recitation from Qualitative Assessment:** Explanations should separate verified quantitative claims (checked against tolerances) from contextual policy commentary.
3. **Audit Readiness Requirement:** Generative explanations without automated faithfulness validation present substantial compliance and legal risks under emerging AI governance frameworks (EU AI Act, NIST AI RMF).
