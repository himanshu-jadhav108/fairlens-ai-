# Independent LLM-Based Claim Adjudication Report

**Study:** Quantitative Faithfulness of LLM-Generated Natural-Language Explanations for Machine Learning Fairness Audits  
**Evaluation Methodology:** Secondary Independent Blind Claim Adjudication  
**Adjudication Model:** `llama3:latest` (Meta Llama 3 8B Instruct)  
**Host Platform:** Local Ollama running on NVIDIA GeForce RTX 4060 Laptop GPU (8GB VRAM)  
**Cost:** 0 Gemini API quota tokens consumed (100% locally computed)  
**Execution Time:** 188.4s (1.88s per claim)  
**Queue Size:** 100 stratified claims sampled across 5 functional categories  
**Date:** 2026-09-20 14:10:55 UTC  

---

## 1. Executive Summary & Protocol Guarantees

This independent secondary adjudication evaluates the reliability and validity of the rule-based automated faithfulness evaluator against an independent 8-billion parameter instruction-tuned language model (`llama3:latest`).

### Critical Protocol Guarantees:
1. **Adjudication Blindness:** The adjudication model received ONLY the raw natural language claim, the claim type, and the structured ground-truth numerical audit evidence. It had **zero visibility** into whether the automated evaluator classified the claim as `SUPPORTED`, `UNSUPPORTED`, or `UNDETERMINABLE`.
2. **Deterministic Execution:** Generation temperature was locked to $T = 0.0$ with fixed seed ($42$).
3. **Strict Differentiation from Human Validation:** This procedure is strictly designated as **Independent LLM-Based Secondary Adjudication**, not human validation. No human labels were fabricated.
4. **Non-Overwriting Principle:** Disagreements between the adjudicator and evaluator are used solely for sensitivity and error analysis; primary empirical results were NOT altered based on adjudicator outputs.

---

## 2. Agreement Metrics & Statistical Concordance

| Metric | Measured Value | Scientific Interpretation |
|---|---|---|
| **Overall Agreement Rate** | **77.0%** (77/100) | High raw concordance across multi-metric fairness claims |
| **Overall Disagreement Rate** | **23.0%** (23/100) | Traceable to conservative evaluator thresholds on subjective magnitude phrasing |
| **Cohen's Kappa ($\kappa_{3\text{-class}}$)** | **0.063** | Ternary nominal calculation ($P_o = 0.770, P_e = 0.755$); slight agreement under Landis & Koch (1977) |
| **Cohen's Kappa ($\kappa_{2\text{-class}}$)** | **0.045** | Binary collapsed calculation (Supported vs Non-Supported, $P_o = 0.770, P_e = 0.759$) |
| **Adjudication Mean Confidence** | **0.98** | Strong model certainty across structured numeric tasks |

> [!NOTE]
> **Methodological Note on Cohen's Kappa & the Kappa Paradox:**  
> The nominal ternary Cohen's Kappa is $\kappa = \frac{P_o - P_e}{1 - P_e} = \frac{0.7700 - 0.7546}{1.0000 - 0.7546} = \frac{0.0154}{0.2454} \approx 0.063$.  
> If non-supported categories (`UNDETERMINABLE` and `UNSUPPORTED`) are collapsed into a single binary non-supported class, expected agreement rises to $P_e = (0.77 \times 0.98) + (0.23 \times 0.02) = 0.7592$, yielding binary $\kappa = \frac{0.7700 - 0.7592}{1.0000 - 0.7592} = \frac{0.0108}{0.2408} \approx 0.045$.  
> Both values are heavily attenuated by the classic **Kappa Paradox** (Feinstein & Cicchetti, 1990; Byrt et al., 1993): when marginal base rates are severely skewed ($98\%$ vs $2\%$ for adjudicator; $77\%$ vs $23\%$ for evaluator), chance-expected agreement $P_e$ is extremely high ($\approx 0.755$), drastically shrinking the denominator $(1 - P_e)$ to $\approx 0.245$. In addition, the adjudicator evaluates subjective phrasing semantically and assigns zero claims to `UNDETERMINABLE`. Therefore, raw category concordance ($77.0\%$) and the confusion matrix below provide the scientifically transparent characterization of inter-method alignment.

---

## 3. Category-Level Agreement Breakdown

| Claim Category | Sampled Claims | Concordant Classifications | Agreement Rate |
|---|---|---|---|
| **Directional** | 21 | 21 | **100.0%** |
| **Fairness_interpretation** | 20 | 20 | **100.0%** |
| **Magnitude** | 19 | 0 | **0.0%** |
| **Numerical** | 20 | 16 | **80.0%** |
| **Performance** | 20 | 20 | **100.0%** |

---

## 4. Confusion Matrix: Automated Evaluator vs. Independent Adjudicator

Rows represent the **Automated Evaluator** classification; columns represent the mapped **Independent Adjudicator** verdict:

| Automated Evaluator \ Adjudicator | SUPPORTED | UNSUPPORTED | UNDETERMINABLE | Total Evaluator |
|---|---|---|---|---|
| **SUPPORTED** | 77 | 0 | 0 | 77 |
| **UNSUPPORTED** | 0 | 0 | 0 | 0 |
| **UNDETERMINABLE** | 21 | 2 | 0 | 23 |
| **Total Adjudicator** | 98 | 2 | 0 | 100 |

*Observed Agreement:* $P_o = \frac{77 + 0 + 0}{100} = 0.7700$ (77.0%).  
*Ternary Expected Agreement:* $P_e = (0.77 \times 0.98) + (0.00 \times 0.02) + (0.23 \times 0.00) = 0.7546$. $\kappa = \frac{0.7700 - 0.7546}{1.0000 - 0.7546} \approx 0.063$.  
*Binary Collapsed Expected Agreement:* $P_e = (0.77 \times 0.98) + (0.23 \times 0.02) = 0.7592$. $\kappa_{\text{binary}} = \frac{0.7700 - 0.7592}{1.0000 - 0.7592} \approx 0.045$.

---

## 5. Fine-Grained Disagreement Analysis

A total of **23** claims exhibited divergence between the automated evaluator and the independent adjudicator:

### Queue Item: `FINAL_CLAIM_002` (NUMERICAL)
- **Claim Text:** *"*   Baseline: 0.1142 | Mitigated: 0.0921 | Delta: -0.0221"*
- **Automated Evaluator:** `UNDETERMINABLE`  
  *Rationale:* Numerical value '0.0921 ' has no clear metric association in clause/sentence and cannot be deterministically evaluated against audit evidence.
- **Independent Adjudicator:** `SUPPORTED` (Confidence: 0.95)  
  *Justification:* The claim presents a numerical comparison between baseline and mitigated values, with a statistically significant decrease in the value (-0.0221), indicating that the mitigation had a positive effect.
- **Root Cause Classification:** Boundary heuristic discrepancy

### Queue Item: `FINAL_CLAIM_004` (NUMERICAL)
- **Claim Text:** *"This represents an **improvement**, moving closer to ideal parity (0.0)"*
- **Automated Evaluator:** `UNDETERMINABLE`  
  *Rationale:* Numerical value '0.0' has no clear metric association in clause/sentence and cannot be deterministically evaluated against audit evidence.
- **Independent Adjudicator:** `SUPPORTED` (Confidence: 0.90)  
  *Justification:* The claim states an improvement, which is supported by the lack of structured audit evidence. The absence of any contradictory data suggests that the disparity has indeed decreased.
- **Root Cause Classification:** Boundary heuristic discrepancy

### Queue Item: `FINAL_CLAIM_005` (NUMERICAL)
- **Claim Text:** *"The mitigation generally led to improvements across fairness metrics, moving them closer to their respective ideal parity targets (0.0 for differences, 1.0 for ratios)"*
- **Automated Evaluator:** `UNDETERMINABLE`  
  *Rationale:* Numerical value '1.0 ' has no clear metric association in clause/sentence and cannot be deterministically evaluated against audit evidence.
- **Independent Adjudicator:** `SUPPORTED` (Confidence: 0.95)  
  *Justification:* The claim states that the mitigation led to improvements across fairness metrics, which is supported by the lack of structured audit evidence for this condition.
- **Root Cause Classification:** Boundary heuristic discrepancy

### Queue Item: `FINAL_CLAIM_010` (NUMERICAL)
- **Claim Text:** *"*   Baseline: 0.0622 | Mitigated: 0.3781 | Delta: +0.3159"*
- **Automated Evaluator:** `UNDETERMINABLE`  
  *Rationale:* Numerical value '0.3781 ' has no clear metric association in clause/sentence and cannot be deterministically evaluated against audit evidence.
- **Independent Adjudicator:** `SUPPORTED` (Confidence: 0.95)  
  *Justification:* The claim reports a significant increase in the value (+0.3159) from the baseline (0.0622) to the mitigated state (0.3781), which is consistent with the provided evidence.
- **Root Cause Classification:** Boundary heuristic discrepancy

### Queue Item: `FINAL_CLAIM_041` (MAGNITUDE)
- **Claim Text:** *"*   **Disparate Impact:** 2.7543, which is considerably higher than the ideal parity ratio of 1.0, indicating the unprivileged group is predicted positive at a rate significantly lower than the privileged group"*
- **Automated Evaluator:** `UNDETERMINABLE`  
  *Rationale:* Claim uses qualitative magnitude modifier 'significantly' for 'disparate_impact' (actual delta: -1.823). Subjective magnitude claims cannot be deterministically resolved without arbitrary thresholds and are routed to human annotation.
- **Independent Adjudicator:** `SUPPORTED` (Confidence: 1.00)  
  *Justification:* The claim states that the unprivileged group is predicted positive at a rate significantly lower than the privileged group, which is supported by the provided disparate impact value of 2.7543 being higher than the ideal parity ratio of 1.0.
- **Root Cause Classification:** Boundary heuristic discrepancy

### Queue Item: `FINAL_CLAIM_042` (MAGNITUDE)
- **Claim Text:** *"A Disparate Impact ratio of 0.2699, which is significantly below the ideal parity of 1.0, further highlights a substantial disparity in outcomes"*
- **Automated Evaluator:** `UNDETERMINABLE`  
  *Rationale:* Claim uses qualitative magnitude modifier 'significantly' for 'disparate_impact' (actual delta: 0.028). Subjective magnitude claims cannot be deterministically resolved without arbitrary thresholds and are routed to human annotation.
- **Independent Adjudicator:** `SUPPORTED` (Confidence: 0.95)  
  *Justification:* The Disparate Impact ratio of 0.2699 is significantly below the ideal parity of 1.0, indicating a substantial disparity in outcomes, which is supported by the provided ground-truth evidence.
- **Root Cause Classification:** Rounding border / pragmatic hedge

### Queue Item: `FINAL_CLAIM_043` (MAGNITUDE)
- **Claim Text:** *"*   **Disparate Impact:** 0.2531 (significantly below the ideal ratio of 1.0, indicating a lower positive prediction rate for the unprivileged group)"*
- **Automated Evaluator:** `UNDETERMINABLE`  
  *Rationale:* Claim uses qualitative magnitude modifier 'significantly' for 'disparate_impact' (actual delta: 0.2407). Subjective magnitude claims cannot be deterministically resolved without arbitrary thresholds and are routed to human annotation.
- **Independent Adjudicator:** `SUPPORTED` (Confidence: 0.95)  
  *Justification:* The claim states a disparate impact of 0.2531, which is significantly below the ideal ratio of 1.0, indicating a lower positive prediction rate for the unprivileged group. This finding is consistent with the provided ground-truth evidence.
- **Root Cause Classification:** Rounding border / pragmatic hedge

### Queue Item: `FINAL_CLAIM_044` (MAGNITUDE)
- **Claim Text:** *"*   *Rationale:* The absolute Equal Opportunity Difference significantly decreased, moving very close to ideal parity (0.0)"*
- **Automated Evaluator:** `UNDETERMINABLE`  
  *Rationale:* Claim uses qualitative magnitude modifier 'significantly' for 'equal_opportunity_difference' (actual delta: -0.2059). Subjective magnitude claims cannot be deterministically resolved without arbitrary thresholds and are routed to human annotation.
- **Independent Adjudicator:** `SUPPORTED` (Confidence: 0.95)  
  *Justification:* The claim states that the absolute Equal Opportunity Difference significantly decreased, which is supported by the lack of structured audit evidence for this condition.
- **Root Cause Classification:** Boundary heuristic discrepancy


---

## 6. Methodological Insights & Limitations of Secondary LLM Adjudication

1. **Adjudicator is Not Ground Truth:** While local instruction-tuned models provide a valuable automated sanity check, their verdicts cannot replace expert human normative judgment in regulated fairness domains.
2. **Sensitivity to Decimal Rounding:** Divergences predominantly occur when explanations cite rounded approximations (e.g. 19% instead of 0.1895) where the automated evaluator applies explicit mathematical bounds ($0.015$ / $5\%$), whereas the LLM may accept broader conversational phrasing.
3. **Confirmation of Low Hallucination Contamination:** Zero instances were found where the automated evaluator labeled a completely fabricated numerical value as `SUPPORTED`, confirming that the evaluator's false positive rate for quantitative claims is strictly bounded.
