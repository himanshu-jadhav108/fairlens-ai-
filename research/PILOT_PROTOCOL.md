# FairLens AI Research — Empirical Pilot & Protocol Specification

**Branch:** `research/fairness-xai-study`  
**Locked Research Topic:**  
> **Quantitative Faithfulness of LLM-Generated Natural-Language Explanations for Machine Learning Fairness Audits: An Empirical Study**

---

## 1. Protocol Freezing (Phase 1) 🔒

To maintain scientific integrity, all experimental dimensions and evaluation policies are explicitly documented before launching empirical runs.

### 1.1 Datasets
* **Adult Census Income (`adult`):** Tabular benchmark; protected attribute = `sex` (Privileged: `Male`, Unprivileged: `Female`); binary classification on high income (`>50K`).
* **COMPAS Recidivism (`compas`):** Tabular criminal justice benchmark; protected attribute = `race` (Privileged: `Caucasian`, Unprivileged: `African-American`); binary recidivism risk classification.
* **South German Credit (`german`):** Tabular financial benchmark; protected attribute = `age` (Privileged: `>25`, Unprivileged: `<=25`); binary credit risk classification.

### 1.2 Model Architectures
* **Logistic Regression (`logistic_regression`):** Linear baseline with calibrated probabilities.
* **Random Forest (`random_forest`):** Non-linear ensemble model.
* **XGBoost (`xgboost`):** Gradient-boosted decision tree estimator.

### 1.3 Fairness Mitigations
* **CorrelationRemover (`correlation_remover`):** Preprocessing mitigation removing linear dependencies on protected attributes.
* **ExponentiatedGradient (`exponentiated_gradient`):** In-processing reduction optimizing accuracy under demographic parity constraints.
* **ThresholdOptimizer (`threshold_optimizer`):** Post-processing group-specific decision threshold calibration.

### 1.4 Random Seeds
* **Empirical Study Matrix:** Exactly 5 seeds: `[42, 123, 456, 789, 2026]`.
* **Pilot Validation Matrix:** Exactly 3 seeds: `[42, 123, 456]`.
* *Note: Seeds capture initialization and partition sensitivity across splits; they are not pooled as independent scientific observations.*

### 1.5 LLM Configuration
* **Provider:** `GeminiProvider` (via Google Generative AI API) with deterministic parameters.
* **Model Identifier:** `gemini-2.5-flash` (provisional default; configurable).
* **Generation Parameters:** `temperature = 0.2`, `max_output_tokens = 1500`, `top_p = 0.95`.
* **Prompt Versions:** `combined_audit_v1` (primary), `fairness_audit_v1`, `fairness_comparison_v1`, `shap_explanation_v1`.

### 1.6 Evaluation Metrics
* **Primary Metric 1 — Numerical Faithfulness:** Fraction of extracted numerical claims that match structured audit evidence within tolerance ($\epsilon_{abs} \le 0.015$ or $\epsilon_{rel} \le 0.05$).
* **Primary Metric 2 — Directional Faithfulness:** Fraction of mathematical directional claims (`increase`, `decrease`, `unchanged`) that match ground-truth deltas.
* **Primary Metric 3 — Attribution Faithfulness:** Fraction of feature importance rank and top-predictor statements supported by SHAP evidence.
* **Primary Metric 4 — Unsupported Claim Rate:** Rate of unevidenced causal assertions, absolute fairness declarations, overgeneralizations, and unwarranted performance claims.
* **Secondary Metric — Evidence Coverage:** Informational completeness across fairness, performance, and SHAP evidence. Decoupled from faithfulness.

### 1.7 Statistical Plan
* **Sampling Unit:** Explanation / Paired Run (Level 2). Claims within an explanation are nested and treated as non-independent.
* **Paired Comparison:** Paired differences between deterministic `TemplateExplainer` and LLM explanations evaluated on identical canonical evidence.
* **Inferential Tests:** Paired Student's t-test, Wilcoxon signed-rank test, Cohen's d effect size. Sample size guard requires $N \ge 3$.
* **Confidence Intervals:** 95% non-parametric bootstrap ($B=1000$ resamples) over explanation-level scores.
* **Multiple Testing Correction:** Bonferroni and Benjamini-Hochberg FDR adjustments.

### 1.8 Human Annotation Protocol
* **Adjudication Scope:** Claims classified as `UNDETERMINABLE` (e.g. qualitative magnitude claims like "decreased moderately", orphan numbers, sociotechnical assertions).
* **Inter-Annotator Agreement:** Quadratic weighted Cohen's Kappa ($\kappa_w$) across independent annotators on a sampled subset of explanation pairs.

### 1.9 Research Hypotheses
* **$H_1$ (Numerical Precision):** LLM-generated explanations exhibit statistically significant numerical discrepancy rates compared to deterministic template controls when reporting audit metrics.
* **$H_2$ (Directional & Normative Conflation):** LLMs conflate mathematical movement with normative domain interpretations (e.g., asserting "improvement" when metric values worsen disparity).
* **$H_3$ (Feature Attribution Disagreement):** Natural-language feature importance claims frequently depart from authoritative SHAP rankings despite receiving structured SHAP tables in context.

---

## 2. Small Empirical Pilot Design (Phase 2) 🧪

The pilot is a **method-validation experiment** to stress-test the pipeline on real Gemini explanations before launching the full matrix.

* **Configuration:** [`research/configs/pilot_config.yaml`](file:///d:/Projects/fairlens-ai/research/configs/pilot_config.yaml)
* **Runner:** [`research/scripts/run_pilot_experiment.py`](file:///d:/Projects/fairlens-ai/research/scripts/run_pilot_experiment.py)
* **Dimensions:** 2 Datasets (`adult`, `compas`) × 2 Models (`logistic_regression`, `random_forest`) × 2 Mitigations (`correlation_remover`, `threshold_optimizer`) × 3 Seeds (`42`, `123`, `456`) = **24 conditions**.
* **Output Location:** [`research/results/pilot/`](file:///d:/Projects/fairlens-ai/research/results/pilot)
* **Execution Mode:** `"PILOT_VALIDATION_RUN"`

```text
Canonical Audit Evidence
          │
    ┌─────┴─────┐
    ▼           ▼
Template     Gemini
Baseline   Explanation
    │           │
    └─────┬─────┘
          ▼
Faithfulness Evaluator
          ▼
Claim-Level Verification
          ▼
Explanation-Level Aggregation
```

---

## 3. Failure Inspection Protocol Checklist (Phase 3) 🔍

After the pilot execution completes, the researcher manually reviews actual outputs using this checklist:

1. **Numerical Claim Extraction:**
   * Did the parser extract every numerical claim in the explanation?
   * Was each number bound to the correct metric within its local clause?
   * Were percentage-to-decimal conversions executed accurately?
2. **Directional Semantics:**
   * Did the parser distinguish mathematical direction (`decrease`) from fairness interpretation (`improvement`)?
3. **SHAP Feature Claims:**
   * Were top-1 and top-k feature mentions accurately mapped?
   * Did the parser avoid false substring matches?
4. **Unsupported Claims:**
   * Were causal statements ("caused the fairness improvement") caught?
   * Were absolute fairness declarations ("completely unbiased") flagged?
5. **Evaluator Blind Spots:**
   * Did Gemini use phrasing that the evaluator could not resolve?
   * Are claims classified as `UNDETERMINABLE` appropriate for human annotation?
6. **Provenance Integrity:**
   * Are raw explanation outputs, prompt versions, Git commits, and evidence hashes properly stored in [`research/results/pilot/`](file:///d:/Projects/fairlens-ai/research/results/pilot)?

---

## 4. Transition to Full Empirical Study (Phases 4 & 5) 🚀

* If failure inspection uncovers evaluator weaknesses $\rightarrow$ fix $\rightarrow$ re-run pilot.
* Once the pilot passes cleanly $\rightarrow$ freeze the protocol and pre-register hypotheses.
* Execute the full empirical study matrix:
  **3 Datasets × 3 Models × 3 Mitigations × 5 Seeds = 135 experimental conditions.**
