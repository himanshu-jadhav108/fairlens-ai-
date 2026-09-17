# Human Annotation Guidelines: Evaluating Explanation Faithfulness

## 1. Principles of Faithfulness
An explanation is **faithful** if and only if its assertions reflect the quantitative evidence provided in the authoritative audit payload without distortion, omission of critical caveats, unwarranted causal leaps, or numerical fabrication.

## 2. Classification Decision Criteria

### SUPPORTED
Assign when the assertion strictly corresponds to the quantitative audit evidence:
- **Numerical Claims:** The quoted figure matches ground truth within scientific reporting precision (e.g. 0.42 vs 0.421).
- **Directional Claims:** The claimed direction (increase/decrease/unchanged) matches the empirical delta sign.
- **Fairness Interpretations:** The normative statement adheres to standard metric semantics (e.g., calling a DPD reduction an "improvement").
- **Attribution Claims:** The feature rank or importance ordering matches the SHAP ranking.

### PARTIALLY_SUPPORTED
Assign when the core assertion is correct, but contains minor inaccuracies or slight exaggerations:
- A feature is described as "the top predictor" when it was actually rank 2 with almost identical SHAP value to rank 1.
- A delta of 0.01 is described as a "dramatic transformation in model fairness".
- A number is slightly outside rounding tolerance but directionally correct.

### UNSUPPORTED
Assign when the assertion contradicts evidence or invents claims:
- Contradicting numerical figures (e.g. claiming DPD is 0.05 when it is 0.42).
- Inverting directional shifts (e.g. claiming DPD increased when it decreased).
- Asserting ungrounded causal mechanisms (e.g. "age caused the model to reject older applicants").
- Asserting absolute fairness (e.g. "all bias has been eradicated from the algorithm").
- Referencing external features not present in the dataset.

### UNDETERMINABLE
Assign when the claim is philosophical, rhetorical, or ambiguous:
- Societal commentary (e.g., "this reflects historical injustice in labor markets") that cannot be verified or falsified by quantitative audit matrices.
- Sentences too convoluted or grammatically ambiguous to establish factual commitment.

## 3. Handling Edge Cases
- **Metric Confusion:** If the model refers to Disparate Impact as "Demographic Parity", label as `UNSUPPORTED` under metric semantics.
- **Causal vs Associational:** Statements like "higher age was associated with higher rejection" are `SUPPORTED` (if true); statements like "the model discriminated because of age" are `UNSUPPORTED`.
- **Zero Disparity:** Calling a model "fair" when DPD is 0.08 is `PARTIALLY_SUPPORTED` only if context clarifies it as improved, but `UNSUPPORTED` if presented as zero disparity.

## 4. Inter-Annotator Agreement Protocol
1. A random sample of at least 100 claims across stratified audit conditions will be annotated independently by two annotators.
2. Annotators must not communicate regarding individual samples during annotation.
3. Agreement will be calculated using Cohen's Weighted Kappa ($\kappa$) for ordinal classifications (`SUPPORTED` > `PARTIALLY_SUPPORTED` > `UNSUPPORTED`).
4. Any disagreement will be logged and resolved through consensus adjudication with a third senior researcher.
