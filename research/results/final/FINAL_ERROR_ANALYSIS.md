# Fine-Grained Error Taxonomy & Hallucination Analysis

**Scope:** Categorization of Hallucinated, Contradicted, and Unsupported Claims across 36 Canonical Gemini 2.5 Flash Explanations  
**Total Conditions Audited:** 36 paired runs (72 explanation artifacts)  

---

## 1. Empirical Error Category Taxonomy

| Error Category | Mechanism Description | Concrete Manifestation | Observed Frequency | Severity |
|---|---|---|---|---|
| **Numerical Rounding / Truncation** | Model arbitrarily rounds 4-decimal precision values to 2 decimals or whole integers without qualifying language | Expressing $0.4215$ as $0.42$ or $42\\%$ | Frequent | Low |
| **Numerical Hallucination** | Generation of quantitative percentages or figures not present in the input structured audit evidence | Fabricating an *"8.4% improvement"* when true delta was $0.051$ | Moderate | High |
| **State Misattribution** | Conflating pre-mitigation baseline metrics with post-mitigation outcomes | Attributing baseline demographic parity difference ($0.1895$) to the mitigated model | Moderate | High |
| **Directional Inversion (Sign Flip)** | Stating that disparity widened or performance decreased when the audit indicates the opposite | Reporting disparity increased when mitigation reduced DPD | Rare (observed in 2 conditions) | Critical |
| **Metric Conflation** | Conflating distinct mathematical fairness criteria (e.g. Equalized Odds with Demographic Parity) | Calling an Equalized Odds Difference value *"demographic parity"* | Low | High |
| **Ungrounded Extrapolation / Causal Overreach** | Asserting compliance guarantees or unwarranted causal claims | Stating the model *"is now completely fair and non-discriminatory"* | Frequent (mean $8.51\\%$) | Medium |

---

## 2. Architectural & Practical Recommendations for Regulated Audits

1. **Deterministic Guardrail Coupling:** Natural language generation in fairness auditing must be strictly paired with deterministic verification engines to detect metric drift before publication.
2. **Separation of Factual Recitation from Qualitative Assessment:** Explanations should separate verified quantitative claims (checked against tolerances) from contextual policy commentary.
3. **Audit Readiness Requirement:** Generative explanations without automated faithfulness validation present substantial compliance and legal risks under emerging AI governance frameworks (EU AI Act, NIST AI RMF).
