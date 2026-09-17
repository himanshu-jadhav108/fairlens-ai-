# FairLens AI Research — Faithfulness Evaluator Technical Validation

**Branch:** `research/fairness-xai-study`  
**Date:** 2026-09-17  
**Status:** `VERIFIED & VALIDATED VIA 11 UNIT & ADVERSARIAL TESTS`

---

## 1. Overview of Evaluator Architecture

The FairLens Faithfulness Evaluator (`research/faithfulness/`) performs quantitative verification of natural-language ML fairness audit explanations against structured `AuditEvidence` objects. It is designed to replace qualitative human assessment with deterministic, reproducible, claim-level ground-truth verification.

The architecture comprises four orthogonal evaluation components orchestrated by `FaithfulnessEvaluator` (`evaluator.py`):
1. **Numerical Faithfulness Evaluator (`numerical.py`)**
2. **Directional Faithfulness Evaluator (`directional.py`)**
3. **Attribution Faithfulness Evaluator (`attribution.py`)**
4. **Unsupported Claims Detector (`unsupported_claims.py`)**
5. **Evidence Coverage Evaluator (`coverage.py` — decoupled from faithfulness)**

---

## 2. Numerical Extraction and Matching Methodology

### 2.1 Pattern Parsing & Token Normalization
- **Regular Expressions:** Captures signed and unsigned floating-point values, scientific notation, integers, and percentage notation (`[+-]?\d+(?:\.\d+)?%?`).
- **Percentage Normalization:** Percentage claims (e.g. `12.5%`) are dual-checked against decimal ratios (`0.125`) and percentage scales (`12.5`) to prevent false-negative penalization for standard mathematical conventions.
- **Decimal Isolation:** Sentence tokenization (`split_into_sentences`) uses negative lookahead (`\.(?!\d)`) ensuring numbers like `0.0420` are not cleaved across sentence boundaries.
- **Non-Metric Filtering:** Uses `NON_METRIC_COUNT_UNITS` filtering (e.g. "500 samples", "10 trees", "20 iterations", "5 folds") so that sample counts and architectural hyperparameters are not erroneously parsed as fairness or performance metrics.
- **Clause Splitting:** Employs `CLAUSE_DELIMITER_PATTERN` (`and`, `while`, `whereas`, `but`, `however`) to correctly map distinct metrics to their respective numbers within compound sentences.

### 2.2 Dual-Tolerance Matching Logic
A claimed numerical value $\hat{v}$ for metric $m$ is matched against ground-truth value $v^* \in \{\text{baseline}, \text{mitigated}, \Delta_{\text{abs}}, \Delta_{\text{rel}}\}$:
$$\text{Match}(\hat{v}, v^*) \iff |\hat{v} - v^*| \le \epsilon_{\text{abs}} \quad \lor \quad \left| \frac{\hat{v} - v^*}{v^*} \right| \le \epsilon_{\text{rel}}$$
- **Default Parameters:** $\epsilon_{\text{abs}} = 0.015$, $\epsilon_{\text{rel}} = 0.05$ (5%).
- **Rationale:** Accommodates natural rounding (e.g., 0.0423 reported as 0.04 or 4.2%) while rejecting hallucinated numbers or values transposed across different metrics.

### 2.3 Cross-Metric Swapping Detection
When a number appears in a clause referencing metric $A$, the evaluator verifies whether the number matches metric $B$ instead. If an explanation claims "Equal Opportunity Difference was 0.82" when 0.82 was actually the Demographic Parity Ratio, the claim is strictly labeled `UNSUPPORTED` due to metric transposition.

---

## 3. Directional Matching Logic

### 3.1 Lexical Direction Mapping
Directional claims are extracted using regex pattern matching over validated linguistic lexicons:
- **Increase:** `increased`, `rose`, `higher`, `amplified`, `widened`, `greater`, `elevated`
- **Decrease:** `decreased`, `dropped`, `fell`, `narrowed`, `reduced`, `lower`, `lesser`, `shrunk`
- **Unchanged:** `remained unchanged`, `stable`, `constant`, `no change`, `maintained`

### 3.2 Semantic Truth Alignment
Ground truth direction is defined in `AuditEvidence.metric_comparisons[m].direction`:
- `Direction.INCREASE` ($v_{\text{mit}} - v_{\text{base}} > \tau$)
- `Direction.DECREASE` ($v_{\text{mit}} - v_{\text{base}} < -\tau$)
- `Direction.UNCHANGED` ($|v_{\text{mit}} - v_{\text{base}}| \le \tau$, where $\tau = 0.005$)

Directional claims are classified as:
- `SUPPORTED`: Claimed direction matches ground-truth change direction.
- `UNSUPPORTED`: Claimed direction directly opposes ground-truth change (e.g. claiming disparity widened when it decreased).
- `UNDETERMINABLE`: Ambiguous or unquantifiable qualitative change assertions.

---

## 4. Feature Attribution Verification (SHAP)

### 4.1 Ground Truth Top-K Ranking
SHAP feature attributions are computed across global test samples and ordered by mean absolute Shapley values ($|\phi_j|$). The ground truth top-$K$ feature list ($K=5$) is recorded in `AuditEvidence.feature_attributions`.

### 4.2 Ranking Verification
- When an explanation claims a feature $f$ is the "primary driver" or "top feature", the evaluator checks if $\text{rank}(f) \le 2$.
- When an explanation claims feature $f_1$ has greater impact than $f_2$, the evaluator verifies $|\phi_{f_1}| > |\phi_{f_2}|$.
- Attributed features not present in top-$K$ or ranked incorrectly are flagged as `UNSUPPORTED`.

---

## 5. Unsupported Claim Taxonomy

The framework detects four distinct classes of ungrounded or deceptive statements:

1. **Causal Overreach (`ClaimType.CAUSAL`):**
   - Assertions claiming that a feature or mitigation *causes* an outcome without causal DAG identification or randomized experimental conditions (e.g., "Age caused the model to deny loans").
2. **Hallucinated Metric Claims (`ClaimType.OTHER` / `UNSUPPORTED`):**
   - References to metrics that do not exist in the metric registry or were not computed in the audit evidence (e.g., referencing "Theil Index" or "predictive equality" when uncalculated).
3. **Overgeneralization & False Optimality (`ClaimType.FAIRNESS_INTERPRETATION`):**
   - Absolute claims of perfect fairness or optimality (e.g., "the model is completely fair", "bias has been eliminated", "optimal tradeoff achieved").
4. **Unsupported Performance Claims on Degraded Models (`ClaimType.PERFORMANCE`):**
   - Claiming that accuracy or F1 "improved" or "remained intact" when empirical performance degraded beyond the tolerance threshold.

---

## 6. Decoupling Evidence Coverage from Faithfulness

A fundamental principle of FairLens AI is the mathematical decoupling of **Faithfulness** from **Evidence Coverage**:
- **Faithfulness Rate:** $\frac{\text{Count}(\text{SUPPORTED})}{\text{Count}(\text{SUPPORTED}) + \text{Count}(\text{UNSUPPORTED})}$. Measures the accuracy of claims *that were made*.
- **Evidence Coverage:** $\frac{\text{Metrics Discussed}}{\text{Total Audit Metrics in Evidence}}$. Measures the breadth of the audit evidence addressed.

*Why decoupling matters:* An explanation that accurately discusses only Demographic Parity Difference has 100% faithfulness and ~25% coverage. Conflating coverage with faithfulness would improperly label concise, factually perfect explanations as unfaithful.

---

## 7. Unit and Adversarial Test Coverage

The evaluator's robustness is verified by the following tests in `research/tests/test_faithfulness.py`:
- `test_numerical_exact_match_and_tolerance`: Validates boundary matching at $\epsilon_{\text{abs}}$ and $\epsilon_{\text{rel}}$.
- `test_cross_metric_number_swapping`: Confirms that transposing numbers across metrics produces `UNSUPPORTED`.
- `test_qualitative_magnitude_undeterminable`: Confirms ungrounded adjectives produce `UNDETERMINABLE` rather than false passes.
- `test_overgeneralization_certainty_and_optimality`: Confirms flags on "completely unbiased" assertions.
- `test_unsupported_performance_claim_on_degraded_model`: Catches false optimism on performance loss.
- `test_evidence_coverage_decoupled`: Verifies that partial coverage does not deflate numerical faithfulness scores.
- `test_weighted_cohen_kappa`: Validates inter-annotator calibration metric calculation.
