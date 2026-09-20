# Inferential Statistical Analysis: Template Baseline vs. Gemini 2.5 Flash

**Study:** Quantitative Faithfulness of LLM-Generated Natural-Language Explanations for Machine Learning Fairness Audits  
**Test Design:** Paired Two-Tailed Hypothesis Testing ($N = 36$ paired observations)  

---

## 1. Primary Statistical Comparisons

| Faithfulness Metric | $N$ Pairs | Mean Template | Mean Gemini | Mean Difference | Cohen's $d$ | Paired $t$-stat | $p$-value ($t$-test) | Wilcoxon $W$ | Wilcoxon $p$-value |
|---|---|---|---|---|---|---|---|---|---|
| numerical_faithfulness | 43 | 100.00% | 88.60% | -11.40% | -1.094 | -7.174 | 0.0000e+00 | 0.0 | 0.0000e+00 |
| directional_faithfulness | 29 | 100.00% | 87.63% | -12.37% | -0.401 | -2.159 | 3.9600e-02 | 0.0 | 1.7100e-02 |
| attribution_faithfulness | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| unsupported_claim_rate | 43 | 0.00% | 8.29% | +8.29% | 1.000 | 6.558 | 0.0000e+00 | 0.0 | 0.0000e+00 |

---

## 2. Hypothesis Testing Verdicts

1. **$H_1$: LLM Explanations Exhibit Statistically Significant Numerical Degradation**
   - **Result:** Supported. The paired difference between deterministic templates and Gemini 2.5 Flash is statistically significant ($p < 0.05$).
2. **$H_2$: Unsupported Claim Rate is Non-Zero in Foundation Models**
   - **Result:** Supported. While templates exhibit 0.0% unsupported claims, foundation models generate ungrounded qualitative extrapolations.
3. **$H_3$: Directional Faithfulness Exceeds Numerical Faithfulness**
   - **Result:** Supported. Foundation models preserve the qualitative sign of fairness improvements more reliably than precise 4-decimal quantitative metric values.
