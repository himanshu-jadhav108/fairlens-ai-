# Human Annotation Protocol: Schema

## 1. Objective
To independently validate the faithfulness of LLM-generated explanations for ML fairness audits where semantic nuance, implicit causal claims, or complex domain interpretations cannot be fully evaluated with rule-based regex or deterministic numerical parsing.

## 2. Unit of Annotation
The fundamental unit of annotation is an **atomic claim** extracted from a generated explanation.

## 3. Claim Record Schema

Each annotation record conforms to the following JSON structure:

```json
{
  "annotation_id": "ann_0001",
  "experiment_id": "adult__lr__correlation_remover__seed42",
  "claim_id": "dir_interp_1",
  "claim_text": "The model exhibited a substantial improvement in fairness after mitigation.",
  "claim_type": "FAIRNESS_INTERPRETATION",
  "ground_truth_context": {
    "metric": "demographic_parity_difference",
    "before": 0.421,
    "after": 0.082,
    "absolute_change": -0.339,
    "direction": "decrease",
    "domain_interpretation": "improvement"
  },
  "annotator_id": "annotator_A",
  "label": "SUPPORTED",
  "confidence": 5,
  "rationale": "DPD decreased by 0.339 towards zero, which mathematically confirms substantial fairness improvement.",
  "flags": {
    "contains_implicit_causality": false,
    "hallucinates_domain_facts": false,
    "exaggerates_magnitude": false
  }
}
```

## 4. Annotation Fields

| Field Name | Type | Allowed Values | Description |
| :--- | :--- | :--- | :--- |
| `claim_type` | String | `NUMERICAL`, `DIRECTIONAL`, `ATTRIBUTION`, `PERFORMANCE`, `FAIRNESS_INTERPRETATION`, `CAUSAL`, `OTHER` | Category of the atomic claim |
| `label` | String | `SUPPORTED`, `PARTIALLY_SUPPORTED`, `UNSUPPORTED`, `UNDETERMINABLE` | Faithful classification against evidence |
| `confidence` | Integer | `1` (low) to `5` (high) | Annotator certainty score |
| `contains_implicit_causality`| Boolean | `true`, `false` | True if text implies causality without empirical proof |
| `hallucinates_domain_facts` | Boolean | `true`, `false` | True if text invents external unprovided attributes |
| `exaggerates_magnitude` | Boolean | `true`, `false` | True if qualitative adverbs exaggerate minor delta |
