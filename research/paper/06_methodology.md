> [!NOTE]
> **SUPERSEDED ARCHIVAL FRAGMENT:** This file is an early scaffold fragment retained for historical reference. The sole active, frozen, authoritative manuscript is [PAPER_DRAFT.md](./PAPER_DRAFT.md).

# 6. Methodology

## 6.1 Experimental Architecture
The end-to-end evaluation pipeline comprises eight sequential stages:
```text
Dataset → ML Model Training → Fairness Audit → Bias Mitigation → SHAP Attribution
        → Canonical Structured Evidence → Explanation Generation (LLM vs Template Baseline)
        → Deterministic Faithfulness Evaluation → Hierarchical Statistical Analysis
```

## 6.2 Canonical Structured Evidence
Ground-truth evidence is formalized as a validated schema (`AuditEvidence`) encapsulating:
- Dataset and model metadata, training split, random seed.
- Baseline and post-mitigation state evaluations (`AuditStateEvidence`):
  - Group fairness metrics: Demographic Parity Difference, Equal Opportunity Difference, Equalized Odds Difference, Disparate Impact.
  - Predictive performance metrics: Accuracy, F1 Score, Precision, Recall, ROC-AUC.
  - SHAP attribution evidence: Ranked features, mean $|SHAP|$ values, top-$k$ sets.
- Pairwise metric comparisons: Direction of change, absolute delta, relative delta, domain semantic interpretation, and rationale.
- Cryptographic SHA-256 evidence hash ensuring tamper-proof reproducibility.

## 6.3 Centralized Metric Semantics Registry
To prevent semantic divergence between evidence generation and evaluation:
- Centralized registry (`METRIC_REGISTRY`) codifying mathematical definitions, valid ranges, ideal targets (e.g. 0.0 for DPD, 1.0 for DI and Accuracy), and disparity directions.
- Explicit operational distinction:
  1. Mathematical direction: numerical delta ($after - before$).
  2. Fairness domain interpretation: movement toward or away from parity target.
  3. Performance domain interpretation: higher is better.

## 6.4 Explanation Generation
- **LLM Explanation:** Generated via standardized, versioned prompts (`research/llm/prompts/`) with fixed sampling parameters (e.g. temperature = 0.2, random seed = 42).
- **Template Control Baseline:** A deterministic rule-based explainer receiving the exact same structured evidence, guaranteeing 100% factual fidelity and establishing an empirical control.

## 6.5 Claim-Level Faithfulness Evaluation Framework
Evaluations are conducted against structured `ExtractedClaim` records with full end-to-end provenance:
- **Numerical Faithfulness:** Verifies numerical claims against ground truth with pre-defined tolerances ($\epsilon_{\text{abs}} = 0.015, \epsilon_{\text{rel}} = 0.05$). Strictly enforces clause-level metric-number association to catch cross-metric number swapping.
- **Directional Faithfulness:** Verifies mathematical direction and domain semantic interpretations against comparative evidence. Qualitative magnitude modifiers ("substantially", "slightly") are routed to `UNDETERMINABLE` for human annotation.
- **Attribution Faithfulness:** Verifies top-1, top-$k$, and explicit rank claims against ground-truth SHAP values.
- **Unsupported Claim Detection:** Flags ungrounded causal claims, absolute fairness declarations, overgeneralizations, certainty claims, and optimality assertions.

## 6.6 Decoupled Evidence Coverage
Following methodological standards, Evidence Coverage is evaluated as an orthogonal secondary metric measuring informational breadth (proportion of fairness metrics, performance metrics, and top-$k$ features communicated). Coverage does not dilute or penalize primary Faithfulness scores.
