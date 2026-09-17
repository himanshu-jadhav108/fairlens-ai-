# 3. Research Gap & Hypotheses

## 3.1 The Research Gap
While substantial research has focused on:
1. Detecting hallucinations in general NLP summarization and question answering.
2. Developing mathematical group fairness metrics and mitigation algorithms.
3. Feature attribution methods (e.g., SHAP, Integrated Gradients) for model transparency.

There is a critical **empirical research gap**:
> No prior study has quantitatively evaluated how faithfully generative LLMs translate multi-dimensional algorithmic fairness audit evidence (disparity metrics, performance metrics, and feature importance distributions) into natural-language explanations.

Because natural language explanations in auditing are used by compliance officers, regulators, and affected communities, unfaithful claims—such as subtly altering numbers, reversing the direction of an intervention, or asserting unsupported causal blame—carry acute ethical and societal risks.

## 3.2 Research Hypotheses
- **H1 (Numerical Decay):** LLM explanations exhibit significantly higher numerical error rates on fractional fairness metrics (e.g., DPD < 0.1) than on standard percentage accuracy metrics.
- **H2 (Directional Sensitivity):** LLMs confuse the mathematical direction of change ("decreased") with the normative implication ("improved") when explaining metrics where lower values represent fairness improvements.
- **H3 (Attribution Substitution):** When explaining model behavior, LLMs exhibit a prior bias towards intuitively plausible features, occasionally promoting them above empirically higher-ranked SHAP features.
- **H4 (Causal Leakage):** LLMs introduce unprompted causal language (attributing disparity to explicit demographic discrimination) despite prompts instructing observational reporting.
- **H5 (Template Dominance in Fidelity):** A deterministic rule-based template achieves near-perfect faithfulness, highlighting the exact fidelity cost of generative natural language fluidity.
