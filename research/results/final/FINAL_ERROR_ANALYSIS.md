# Fine-Grained Error Taxonomy & Hallucination Analysis

**Scope:** Analysis of Contradicted, Hallucinated, and Unsupported Claims in Gemini 2.5 Flash Explanations  
**Total Conditions Audited:** 36 paired runs  

---

## 1. Error Category Distribution

| Error Category | Mechanism | Example Manifestation | Severity Level |
|---|---|---|---|
| **Numerical Rounding / Truncation** | Imprecise decimal precision ($0.4215 \to 0.42$) | Model rounds without qualifying | Low |
| **Numerical Hallucination** | Invention of ungrounded figures | Fabricated percentage improvements | High |
| **State Misattribution** | Conflating baseline with mitigated metrics | Assigning baseline DPD to mitigated model | High |
| **Directional Inversion (Sign Flip)** | Stating metric increased when it decreased | Claiming disparity widened | Critical |
| **Metric Conflation** | Conflating DPD with Equalized Odds | Describing EOD as demographic parity | High |
| **Ungrounded Extrapolation** | Qualitative claims of compliance | "Model is legally compliant" | Medium |

---

## 2. Qualitative Recommendations for Regulated Auditing
1. Natural-language explanations must be strictly bounded by structured deterministic guardrails.
2. Direct generation without numerical verification passes is unsafe for compliance documentation.
3. Post-generation faithfulness evaluators (such as FairLens AI) are mandatory to detect numerical drift before publishing audit reports.
