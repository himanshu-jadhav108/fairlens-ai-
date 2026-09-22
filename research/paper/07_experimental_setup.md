> [!NOTE]
> **SUPERSEDED ARCHIVAL FRAGMENT:** This file is an early scaffold fragment retained for historical reference. The sole active, frozen, authoritative manuscript is [PAPER_DRAFT.md](./PAPER_DRAFT.md).

# 7. Experimental Setup

## 7.1 Benchmark Datasets
Three widely adopted algorithmic fairness benchmarks:
1. **Adult Census Income:** 48,842 samples; binary prediction of income $\ge \$50\text{K}$; protected attribute: Sex (binary).
2. **COMPAS Recidivism:** 7,214 samples; binary prediction of two-year recidivism; protected attribute: Race (African-American vs. Caucasian).
3. **German Credit:** 1,000 samples; binary credit risk assessment; protected attribute: Age / Sex.

## 7.2 Predictive Classifiers
1. **Logistic Regression:** Linear decision boundary; deterministic baseline.
2. **Random Forest:** Ensemble of decision trees capturing non-linear interactions.
3. **XGBoost:** Gradient boosted tree ensembles representing state-of-the-art tabular performance.

## 7.3 Bias Mitigation Algorithms
1. **CorrelationRemover (Pre-processing):** Linear projection removing correlation between sensitive attributes and features.
2. **ExponentiatedGradient (In-processing):** Reductions approach optimizing empirical risk subject to fairness constraints.
3. **ThresholdOptimizer (Post-processing):** Group-specific threshold adjustment achieving equalized odds or demographic parity.

## 7.4 Explainability Engine
- SHAP (Shapley Additive Explanations) with exact linear or tree explainer implementations.
- Ranked features, mean absolute SHAP values, and top-$k$ subsets ($k=5$).

## 7.5 LLM Configurations & Prompts
- Model: Google Gemini API (experimental configuration, strictly not the research contribution) alongside deterministic mock provider for verification.
- Temperature: 0.2 (deterministic sampling control).
- Versioned Prompts: `combined_audit_v1`, `fairness_audit_v1`, `fairness_comparison_v1`, `shap_explanation_v1`.
- Raw outputs, token usage, timestamps, and model identifiers logged with SHA-256 evidence hashes.

## 7.6 Statistical Hierarchy & Sampling Unit
- Experimental Unit: Explanation run (paired by experiment ID and structured evidence).
- Hierarchical structure: Claims (nested) within Explanations within Runs across Seeds.
- Statistical testing: Paired differences and bootstrap confidence intervals over explanations; random seeds capture initialization split sensitivity, not independent scientific observations.
