# Inferential Statistical Analysis: Template Baseline vs. Gemini 2.5 Flash

**Study:** Quantitative Faithfulness of LLM-Generated Natural-Language Explanations for Machine Learning Fairness Audits  
**Test Design:** Paired Two-Tailed Hypothesis Testing ($N = 36$ canonical paired observations)  
**Evaluator Tolerances:** Absolute difference $\\le 0.015$ OR relative difference $\\le 5\%$  

---

## 1. Primary Statistical Comparisons

| Faithfulness Metric | $N$ Pairs | Mean Template | Mean Gemini | Mean Difference | Cohen's $d$ | Paired $t$-stat | $p$-value ($t$-test) | Wilcoxon $W$ | Wilcoxon $p$-value |
|---|---|---|---|---|---|---|---|---|---|
| **Numerical Faithfulness** | 36 | 100.00% ± 0.00% | 88.13% ± 10.82% | -11.87 pp | -1.097 | -6.581 | 1.34e-07 | 0.0 | 8.28e-06 |
| **Directional Faithfulness** | 23 | 100.00% ± 0.00% | 94.18% ± 21.02% | -5.82 pp | -0.277 | -1.328 | 0.1979 | 0.0 | 0.0679 |
| **Attribution Faithfulness** | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| **Unsupported Claim Rate** | 36 | 0.00% ± 0.00% | 8.51% ± 8.72% | +8.51 pp | 0.976 | 5.854 | 1.20e-06 | 0.0 | 8.28e-06 |

---

## 2. Hypothesis Testing Verdicts & Methodological Interpretation

### Hypothesis 1: Numerical Faithfulness Degradation
- **Observed Result:** Gemini-generated explanations achieved an average numerical faithfulness of $88.13\% \\pm 10.82\\%$, compared to $100.00\\% \\pm 0.00\\%$ for deterministic templates (mean degradation: $-11.87$ percentage points).
- **Statistical Evidence:** Paired $t$-test indicates a statistically significant difference ($t = -6.581, p = 1.34 \\times 10^{{-7}}$) with a large negative effect size (Cohen's $d = -1.097$). Non-parametric Wilcoxon signed-rank test corroborates this divergence ($W = 0.0, p = 8.28 \\times 10^{{-6}}$).
- **Interpretation:** The results provide empirical evidence of lower numerical faithfulness for Gemini 2.5 Flash explanations relative to deterministic templates. Foundation models frequently exhibit rounding drift, state conflation, or numerical invention when generating quantitative summaries of algorithmic fairness metrics.
- **Limitation:** Findings are established under prompt `combined_audit_v1` at temperature $0.2$; alternative prompting strategies or fine-tuning may yield different faithfulness profiles.

### Hypothesis 2: Generation of Unsupported Claims
- **Observed Result:** Gemini-generated explanations exhibited a mean unsupported claim rate of $8.51\\% \\pm 8.72\\%$, whereas templates produced $0.00\\% \\pm 0.00\\%$.
- **Statistical Evidence:** Paired $t$-test confirms that unsupported claim generation is significantly non-zero ($t = 5.854, p = 1.20 \\times 10^{{-6}}, d = 0.976$).
- **Interpretation:** Foundation models introduce ungrounded qualitative extrapolations, such as asserting causal mechanisms (*"the mitigation directly caused"*) or absolute legal compliance (*"ensures fair treatment"*), that are not mathematically evidenced by the underlying audit matrices.
- **Limitation:** Unsupported claim detection depends on explicit regularized boundary patterns; claims with subtle pragmatic overreach may fall outside automated heuristic bounds.

### Hypothesis 3: Directional vs. Numerical Faithfulness
- **Observed Result:** Gemini directional faithfulness averaged $94.18\\% \\pm 21.02\\%$ across 23 evaluable condition pairs (13 conditions generated 0 directional assertions and were correctly treated as N/A).
- **Statistical Evidence:** Paired difference between Gemini and template control is $-5.82$ percentage points ($t = -1.328, p = 0.1979$, Wilcoxon $W = 0.0, p = 0.0679$). This difference is **NOT statistically significant** at the standard significance threshold ($\\alpha = 0.05$).
- **Interpretation:** Foundation models retain qualitative directional trends (e.g., recognizing that disparity decreased or accuracy increased) substantially better than specific multi-decimal numerical values. However, researchers must not claim statistically significant directional degradation against templates.
- **Remediation Note:** The preliminary directional $p$-value ($p = 0.0396, N=29$) observed prior to audit remediation was contaminated by 7 legacy retry runs. On the clean canonical matrix ($N=23$), directional degradation is non-significant.
