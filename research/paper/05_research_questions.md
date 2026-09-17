# 5. Research Questions

This empirical study investigates the central research question:
> **How faithfully do LLM-generated natural-language explanations represent quantitative machine-learning fairness-audit evidence?**

The study is formally structured around five locked research questions:

### RQ1: Quantitative Accuracy
> *How accurately do LLM-generated explanations reproduce the quantitative results of machine-learning fairness audits?*  
> Evaluates numerical precision, tolerance-based matching, absolute error distributions, and cross-metric number associations between generated text and authoritative audit values.

### RQ2: Directional and Magnitude Faithfulness
> *How accurately do LLM-generated explanations represent the direction and magnitude of fairness changes following bias-mitigation interventions?*  
> Evaluates mathematical direction (increase/decrease/unchanged), domain semantic interpretation (improvement/degradation), and qualitative magnitude assertions against comparative audit deltas.

### RQ3: Attribution Faithfulness
> *How faithfully do LLM-generated explanations represent feature-importance information derived from SHAP-based explanations?*  
> Evaluates textual claims regarding the top-1 most influential predictor, top-$k$ feature set membership, and explicit rank ordering against authoritative ground-truth SHAP values.

### RQ4: Error Taxonomy and Distribution
> *What types of faithfulness errors occur most frequently in LLM-generated explanations of fairness audits?*  
> Characterizes the empirical distribution of errors across numerical association errors, directional reversals, ungrounded causal assertions, absolute fairness claims, overgeneralizations, and unsupported performance claims.

### RQ5: Systematic Variation Across Conditions
> *How does explanation faithfulness vary across datasets, predictive models, fairness metrics, mitigation methods, and LLM configurations?*  
> Investigates whether explanation fidelity is stable or exhibits systematic vulnerability across benchmark datasets, model architectures, mitigation strategies, and prompt formulations.
