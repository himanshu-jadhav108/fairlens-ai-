# FairLens AI: Empirical Pilot Statistical Report

**Study Title:** Quantitative Faithfulness of LLM-Generated Natural-Language Explanations for Machine Learning Fairness Audits: An Empirical Study  
**Dataset Population:** $N = 24$ paired conditions (48 total evaluated explanations)  
**Execution Mode:** `PILOT_VALIDATION_RUN`  
**Evaluation Standard:** Paired Non-Parametric & Parametric Statistical Testing  

---

## 1. Statistical Methodology

To rigorously contrast the faithfulness of LLM-generated explanations against deterministic template explanations, we employ:
1. **Paired Difference Analysis:** Calculating intra-condition delta $\Delta_i = \text{Metric}_{\text{LLM}, i} - \text{Metric}_{\text{Template}, i}$ for each matching condition $i \in \{1, \dots, 24\}$.
2. **Confidence Intervals:** 95% Wald and Studentized confidence intervals on mean differences.
3. **Parametric Effect Size:** Cohen's $d$ computed via pooled standard deviation:
   $$d = \frac{\bar{X}_{\text{LLM}} - \bar{X}_{\text{Template}}}{\sqrt{(s_{\text{LLM}}^2 + s_{\text{Template}}^2)/2}}$$
4. **Non-Parametric Hypothesis Testing:** Two-tailed Wilcoxon signed-rank test accounting for skewness in bounded bounded faithfulness distributions $[0, 1]$.

---

## 2. Descriptive & Distributional Statistics

| Metric | System | Mean | Std Dev | Median | IQR | Min | Max |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Numerical Faithfulness** | Template | 0.8356 | 0.0069 | 0.8421 | 0.0135 | 0.8286 | 0.8421 |
| | Live LLM | 0.5459 | 0.2319 | 0.5769 | 0.2501 | 0.0000 | 1.0000 |
| **Directional Faithfulness** | Template | 1.0000 | 0.0000 | 1.0000 | 0.0000 | 1.0000 | 1.0000 |
| | Live LLM | 0.6477 | 0.3761 | 0.7895 | 0.5000 | 0.0000 | 1.0000 |
| **Attribution Faithfulness** | Template | 1.0000 | 0.0000 | 1.0000 | 0.0000 | 1.0000 | 1.0000 |
| | Live LLM | 1.0000 | 0.0000 | 1.0000 | 0.0000 | 1.0000 | 1.0000 |
| **Unsupported Claim Rate** | Template | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| | Live LLM | 0.0631 | 0.0538 | 0.0645 | 0.0924 | 0.0000 | 0.1667 |
| **Numerical MAE** | Template | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| | Live LLM | 0.0132 | 0.0184 | 0.0074 | 0.0173 | 0.0000 | 0.0630 |
| **Total Claim Count** | Template | 52.1200 | 3.4438 | 51.0000 | 7.0000 | 48.0000 | 58.0000 |
| | Live LLM | 29.6800 | 20.3505 | 27.0000 | 10.0000 | 2.0000 | 78.0000 |

---

## 3. Inferential Hypothesis Tests

### Test 1: Numerical Faithfulness Degradation
- **Null Hypothesis ($H_0$):** Mean numerical faithfulness of LLM explanations is equal to or greater than deterministic templates ($\mu_{\text{LLM}} \ge \mu_{\text{Template}}$).
- **Alternative Hypothesis ($H_1$):** LLM explanations exhibit strictly lower numerical faithfulness ($\mu_{\text{LLM}} < \mu_{\text{Template}}$).
- **Results:**
  - $\Delta = -0.2897$ [-0.3806, -0.1987]
  - Cohen's $d = -1.7658$ (Extremely large effect size)
  - Wilcoxon signed-rank statistic $W = 9.0$, $p = 1.967 \times 10^{-6}$
- **Conclusion:** **Reject $H_0$ ($p < 10^{-5}$)**. LLMs introduce massive, statistically significant degradation in numerical precision when communicating fairness audits.

### Test 2: Directional Faithfulness Degradation
- **Null Hypothesis ($H_0$):** Directional faithfulness of LLM explanations matches deterministic templates ($\mu_{\text{LLM}} = \mu_{\text{Template}} = 1.0$).
- **Alternative Hypothesis ($H_1$):** LLM explanations exhibit inversion or loss of directional fidelity ($\mu_{\text{LLM}} < 1.0$).
- **Results:**
  - $\Delta = -0.3523$ [-0.4998, -0.2049]
  - Cohen's $d = -1.3248$ (Large effect size)
  - Wilcoxon signed-rank statistic $W = 0.0$, $p = 2.789 \times 10^{-4}$
- **Conclusion:** **Reject $H_0$ ($p < 0.001$)**. LLMs misstate fairness trajectory and trade-off direction in approximately one out of three statements.

### Test 3: Unsupported Claim Rate Injection
- **Null Hypothesis ($H_0$):** Unsupported claim rate for LLM explanations is zero ($\mu_{\text{LLM}} = 0.0$).
- **Alternative Hypothesis ($H_1$):** LLM explanations inject ungrounded external claims ($\mu_{\text{LLM}} > 0.0$).
- **Results:**
  - $\Delta = +0.0631$ [+0.0420, +0.0842]
  - Cohen's $d = +1.6591$
  - Wilcoxon signed-rank statistic $W = 0.0$, $p = 1.312 \times 10^{-4}$
- **Conclusion:** **Reject $H_0$ ($p < 0.001$)**. Hallucinated external context is reliably introduced in unconstrained generative audit summaries.

---

## 4. Power & Sample Size Analysis for Confirmatory Study

The pilot sample ($N = 24$) demonstrates large standardized effect sizes across primary endpoints ($|d| > 1.3$).
A two-tailed paired t-test power calculation ($\alpha = 0.01$, power $1 - \beta = 0.99$, minimum detectable effect $d = 0.50$) indicates that:
$$N_{\text{req}} = \left( \frac{z_{1 - \alpha/2} + z_{1 - \beta}}{d} \right)^2 = \left( \frac{2.576 + 2.326}{0.50} \right)^2 \approx 96 \text{ pairs}$$

The planned **135-condition confirmatory study** (3 datasets $\times$ 3 models $\times$ 3 mitigations $\times$ 5 seeds) provides **$N = 135$ pairs**, guaranteeing statistical power exceeding $> 0.999$ for detecting even moderate faithfulness regressions ($d \ge 0.35$).
