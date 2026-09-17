# 2. Background

## 2.1 Machine Learning Fairness Auditing
- Mathematical foundations of group fairness metrics on tabular classification models:
  - Demographic Parity Difference (DPD): Selection rate difference across demographic groups.
  - Equal Opportunity Difference (EODiff): True positive rate disparity between privileged and unprivileged groups.
  - Equalized Odds Difference (EOD): Maximum disparity across true positive and false positive rates.
  - Disparate Impact (DI): Ratio of unprivileged selection rate to privileged selection rate (ideal target = 1.0).
- Inherent metric trade-offs and incompatibility theorems (e.g., Kleinberg et al., Chouldechova).
- Distinction between observational empirical measurements (statistical associations in model outputs) and normative legal/ethical declarations.

## 2.2 Explainable AI and SHAP Feature Attribution
- Cooperative game-theoretic foundations of Shapley Additive Explanations (SHAP) (Lundberg & Lee, 2017).
- Local explanations vs. global feature importance rankings via mean absolute SHAP values:
  $$\phi_i(f) = \sum_{S \subseteq F \setminus \{i\}} \frac{|S|!(|F|-|S|-1)!}{|F|!} (f(S \cup \{i\}) - f(S))$$
- Distinction between associative feature attribution in model prediction and causal mechanisms in the data-generating process.
- Interaction between algorithmic bias mitigations (pre-, in-, post-processing) and feature importance distributions.

## 2.3 LLM-Generated Explanations for Technical Audits
- Growing use of foundation models (e.g., Google Gemini, GPT-4) as generative interfaces translating complex statistical audit tables into narrative summaries.
- The dual requirement of communicative fluency for non-technical stakeholders and rigorous factual fidelity to the underlying technical evidence.

## 2.4 Faithfulness in Natural Language Generation
- Operational definition of faithfulness: an explanation is faithful if and only if all empirical assertions made are fully supported by and consistent with the authoritative ground-truth evidence.
- Distinction between Faithfulness (precision of claims made) and Evidence Coverage (breadth/completeness of evidence reported).
- Vulnerabilities of generative models: numerical hallucination, cross-metric swapping, sign reversal, and unprompted causal confabulation.
