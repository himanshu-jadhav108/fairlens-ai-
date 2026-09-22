> [!NOTE]
> **SUPERSEDED ARCHIVAL FRAGMENT:** This file is an early scaffold fragment retained for historical reference. The sole active, frozen, authoritative manuscript is [PAPER_DRAFT.md](./PAPER_DRAFT.md).

# 1. Introduction

## 1.1 Context & Motivation
- Pervasiveness of automated decision systems in high-stakes socio-technical domains (lending, criminal justice, employment).
- Regulatory mandates (EU AI Act, US Algorithmic Accountability Act) requiring accessible auditing and transparency for non-technical stakeholders.
- Emergence of Large Language Models (LLMs) as generative interfaces to translate complex quantitative fairness metrics and explainability outputs into natural language.

## 1.2 The Research Problem: Explanation Unfaithfulness
- While LLMs synthesize complex evidence into fluent narratives, generative models are prone to factual drift, numerical fabrication, sign reversal, and unevidenced causal assertions.
- In algorithmic fairness auditing, an unfaithful explanation can lead to severe real-world harm: misrepresenting a discriminatory model as fair or inverting disparity conclusions.
- **Core Research Question:** *How faithfully do LLM-generated natural-language explanations represent quantitative machine-learning fairness-audit evidence?*

## 1.3 Scope of Empirical Investigation
- Tabular algorithmic fairness benchmarks (Adult Census, COMPAS, German Credit).
- Paired audit evaluations across predictive models (Logistic Regression, Random Forest, XGBoost) and bias mitigations (CorrelationRemover, ExponentiatedGradient, ThresholdOptimizer).
- Quantitative faithfulness evaluation across a multi-dimensional taxonomy: Numerical, Directional, Attribution, Fairness Interpretation, and Causal claims.
- Controlled comparison against a deterministic template baseline.

## 1.4 Paper Organization
- Section 2: Background (Fairness Auditing, SHAP, LLMs, Faithfulness).
- Section 3–5: Related Work, Research Gap, and Formal Research Questions.
- Section 6: Methodology and Experimental Architecture.
- Section 7–9: Experimental Setup, Empirical Results, and Error Analysis.
- Section 10–12: Discussion, Limitations, and Conclusion.
