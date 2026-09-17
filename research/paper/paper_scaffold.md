# Quantitative Faithfulness of LLM-Generated Natural-Language Explanations for Machine Learning Fairness Audits: An Empirical Study

**Author(s):** FairLens AI Research Initiative  
**Status:** In Progress / Research Pipeline Active  
**Repository Branch:** `research/fairness-xai-study`  

---

## Abstract
Machine learning fairness audits increasingly rely on large language models (LLMs) to synthesize complex quantitative disparity metrics and feature attributions into natural-language reports for non-technical stakeholders. However, natural-language generation is susceptible to numerical hallucination, directional inversion, ungrounded causal assertions, and subjective distortion. In this work, we present a rigorous empirical study evaluating the quantitative faithfulness of LLM-generated explanations for machine learning fairness audits. Using structured, authoritative audit evidence generated across tabular datasets, predictive models, bias mitigation strategies, and SHAP explainability engines, we evaluate LLM explanations against a formal claim taxonomy (Numerical, Directional, Attribution, Fairness Interpretation, and Causal). We compare LLM explanations against a deterministic rule-based template baseline to isolate the fidelity costs and communicative benefits of natural-language generation. Our findings provide the first systematic benchmark quantifying how faithfully LLMs report quantitative fairness evidence and establish methodological guidelines for deploying generative AI in algorithmic auditing.

---

## 1. Introduction
- The growing deployment of high-stakes automated decision-making systems and regulatory requirements for algorithmic accountability.
- The dual necessity of quantitative auditing (demographic parity, equalized odds, SHAP attributions) and accessible communication.
- The emerging paradigm of utilizing LLMs as interactive report generators and auditors.
- The fundamental challenge of **explanation unfaithfulness**: numerical hallucinations, directional errors, and unwarranted causal inferences.
- Statement of Core Scientific Question: *How faithfully do LLM-generated natural-language explanations represent quantitative machine-learning fairness-audit evidence?*
- Summary of contributions:
  1. An open, reproducible benchmark pipeline transforming empirical ML fairness audits into canonical structured evidence.
  2. A fine-grained claim taxonomy and deterministic evaluation suite for measuring numerical, directional, attributional, and causal faithfulness.
  3. A deterministic template baseline establishing an empirical upper bound on faithful communication.
  4. Systematic empirical analysis across multiple datasets, models, and mitigation conditions.

---

## 2. Background
### 2.1 Machine Learning Fairness Auditing
- Mathematical foundations of group fairness metrics: Demographic Parity Difference (DPD), Equal Opportunity Difference (EODiff), Equalized Odds Difference (EOD), and Disparate Impact (DI).
- Inherent metric trade-offs and incompatibility theorems (Kleinberg et al., Chouldechova).
- Distinction between empirical measurements (statistical disparities) and normative claims (fairness declarations).

### 2.2 Explainable AI and SHAP
- Shapley additive explanations (SHAP) for local and global feature attribution.
- Distinction between associative feature importance in model decision boundaries and real-world causal mechanisms.
- Interaction between bias mitigation techniques and feature importance shifts.

### 2.3 LLM-Generated Explanations
- The role of foundation models (e.g., Google Gemini) as narrative synthesizers of structured data.
- Prompting strategies for scientific and technical report generation.
- The risk of sycophancy, over-generalization, and hallucination in high-stakes domain summaries.

### 2.4 Explanation Faithfulness
- Defining faithfulness in natural language explanations: strict fidelity to underlying evidentiary facts.
- Distinguishing faithfulness (alignment with internal audit evidence) from plausibility (convincingness to a human reader).

---

## 3. Related Work
- Algorithmic fairness benchmarks and auditing toolkits (AIF360, Fairlearn).
- Explainable AI evaluation and attribution faithfulness (Samek et al., Guidotti et al.).
- Natural language generation evaluation (hallucination detection, fact-checking, NLI).
- LLMs for code, data science, and automated reporting.
- Critical gap: Lack of empirical benchmarks evaluating LLM narrative accuracy against multi-dimensional quantitative fairness audits.

---

## 4. Research Gap
While prior work has investigated LLM hallucinations in open-domain question answering and general summarization, no existing study has systematically and quantitatively measured whether LLMs faithfully preserve the exact numerical, directional, and attributional integrity of algorithmic fairness audits. Because fairness auditing directly impacts legal compliance and human rights, unfaithful explanations carry severe ethical and legal ramifications.

---

## 5. Research Questions
- **RQ1 (Numerical Faithfulness):** To what degree do LLM-generated explanations faithfully report quantitative fairness and performance figures within acceptable scientific tolerances?
- **RQ2 (Directional Faithfulness):** How accurately do LLMs represent the direction and semantic implication of metric shifts following bias mitigation?
- **RQ3 (Attribution Faithfulness):** Do LLMs preserve top-ranked SHAP feature attributions and relative importance orderings without introducing ungrounded features?
- **RQ4 (Unsupported Assertions):** How frequently do LLMs introduce unevidenced causal claims or unqualified fairness declarations?
- **RQ5 (LLM vs. Deterministic Baseline):** Does LLM text generation offer measurable clarity advantages that outweigh its observed fidelity errors compared to deterministic template reporting?

---

## 6. Methodology
### 6.1 Experimental Framework
- End-to-end reproducible architecture:
  `Dataset -> ML Model -> Fairness Audit -> Mitigation -> SHAP Engine -> Structured Evidence -> LLM Generator -> Faithfulness Evaluator -> Results`.

### 6.2 Datasets
- Standard benchmark tabular datasets: Adult Census Income, COMPAS Recidivism, and German Credit.
- Strict leak-free train/validation/test partitioning (stratified by target).

### 6.3 Predictive Models
- Standard classifier families: Logistic Regression, Random Forest, and Gradient Boosted Trees (XGBoost).
- Hyperparameters, random seeds, and training provenance explicitly tracked.

### 6.4 Fairness Auditing
- Comprehensive evaluation of DPD, EODiff, EOD, Disparate Impact, and subgroup-level confusion matrices.
- Explicit tracking of undefined/NaN metrics.

### 6.5 Bias Mitigation
- Representative algorithmic paradigms: Pre-processing (CorrelationRemover), In-processing (ExponentiatedGradient), and Post-processing (ThresholdOptimizer).

### 6.6 SHAP Evidence
- TreeExplainer and LinearExplainer with background distribution sampling.
- Mean absolute SHAP values, feature importance rankings, and subgroup attributions.

### 6.7 Structured Audit Evidence
- Canonical, machine-readable `AuditEvidence` schema strictly separating:
  - *Observed Values* (empirical measurements).
  - *Derived Values* (deltas, percentage changes, ratios).
  - *Domain Interpretations* (fairness implications).
- Cryptographic SHA-256 evidence hashing for provenance verification.

### 6.8 LLM Explanation Generation
- Modular `LLMProvider` abstraction supporting Google Gemini and extensible local models.
- Versioned, structured prompts (`combined_audit_v1`, `fairness_audit_v1`, `fairness_comparison_v1`, `shap_explanation_v1`).
- Strict provenance tracking: model version, temperature (0.2), tokens, seed, and timestamps.

### 6.9 Template Baseline
- Deterministic rule-based explainer generating text directly from structured evidence without an LLM.
- Serves as the experimental control baseline.

### 6.10 Faithfulness Evaluation
- Deterministic extraction and verification against authoritative evidence:
  - Numerical matching with configurable tolerances ($\pm 0.015$ absolute, $\pm 5\%$ relative).
  - Directional matching (mathematical delta vs. semantic interpretation).
  - Attribution matching (top-1 identity, top-$k$ overlap, rank ordering).

### 6.11 Claim Taxonomy
- Formal classification of atomic claims:
  - Types: `NUMERICAL`, `DIRECTIONAL`, `ATTRIBUTION`, `PERFORMANCE`, `FAIRNESS_INTERPRETATION`, `CAUSAL`, `OTHER`.
  - Labels: `SUPPORTED`, `PARTIALLY_SUPPORTED`, `UNSUPPORTED`, `UNDETERMINABLE`.

### 6.12 Statistical Analysis
- Hierarchical nesting: Claims $\subset$ Explanations $\subset$ Experiments.
- Paired statistical tests (Wilcoxon signed-rank test, paired t-test) and bootstrap confidence intervals at the explanation level.
- Rejection of naive claim-level i.i.d. assumptions.

---

## 7. Experimental Setup
- System environment, library versions, and compute infrastructure.
- Prompt parameters: temperature $T = 0.2$, top-$p = 0.95$, seed = 42.
- Pre-registered evaluation thresholds and tolerances.

---

## 8. Results
*(Placeholders for empirical experiment results; no fabricated data)*
- **Table 1:** Overall Faithfulness Rates by Provider and Prompt Version.
- **Table 2:** Numerical Faithfulness and Mean Absolute Error across Metrics.
- **Table 3:** Directional Faithfulness for Baseline-to-Mitigation Shifts.
- **Table 4:** Attribution Overlap (Top-1 and Top-5) with Authoritative SHAP.
- **Table 5:** Comparative Analysis: Template Baseline vs. LLM.

---

## 9. Error Analysis
- Categorization of observed failure modes:
  1. *Subtle Hallucinations:* Metric values slightly shifted due to rounding or tokenization artifacts.
  2. *Sign Reversals:* Inverting disparity shifts or mistaking degradation for improvement.
  3. *Attribution Substitution:* Promoting intuitive features over empirically dominant SHAP features.
  4. *Causal Leaps:* Inferring societal or operational intent from statistical correlations.

---

## 10. Discussion
- Communicative trade-offs: Fluid natural language vs. strict numerical precision.
- Implications for regulatory reporting and algorithmic auditing standards.
- Recommendations for practitioners deploying LLM-assisted audit tools.

---

## 11. Limitations
- Scope focused on tabular classification benchmarks.
- Proprietary API dependencies (Google Gemini API updates over time).
- Deterministic parser limitations requiring human annotation for complex semantic claims.

---

## 12. Conclusion
- Summary of empirical findings on explanation faithfulness.
- Closing synthesis on the necessity of deterministic verification layers in generative AI auditing workflows.
