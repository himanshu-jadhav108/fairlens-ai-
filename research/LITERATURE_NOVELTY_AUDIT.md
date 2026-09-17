# FairLens AI Research — Literature & Scientific Novelty Audit

**Branch:** `research/fairness-xai-study`  
**Date:** 2026-09-17  
**Locked Research Topic:**  
> **Quantitative Faithfulness of LLM-Generated Natural-Language Explanations for Machine Learning Fairness Audits: An Empirical Study**

---

## 1. Precise Scientific Positioning Against Key Literature

The study investigates the quantitative faithfulness of Large Language Model (LLM) natural-language summaries when communicating tabular algorithmic fairness audits. To prevent false claims of novelty, FairLens AI is explicitly situated within four converging bodies of academic literature:

### 1.1 Post-Hoc Explanation Faithfulness in ML (Lakkaraju et al., 2020; Ribeiro et al., 2016)
- **Prior Work:** Lakkaraju et al. ("Fool me once: Generating synthetic data for evaluating fidelity of post-hoc explanations") and LIME/SHAP literature define explanation fidelity as the extent to which a surrogate model accurately mimics the black-box predictor's decision boundary.
- **Divergence in FairLens AI:** Prior work evaluates whether a feature attribution vector reflects the classifier's internal scoring function. FairLens AI evaluates whether an *LLM translating tabular audit data into natural language* accurately preserves the underlying quantitative audit evidence (metrics, parity ratios, feature rankings).

### 1.2 Adversarial Fragility of Explainers (Slack et al., 2020)
- **Prior Work:** Slack et al. ("Fooling LIME and SHAP: Adversarial attacks on post hoc explanation methods") demonstrated that post-hoc explainers can be maliciously tricked into masking racial or gender bias through adversarial scaffolding.
- **Divergence in FairLens AI:** Slack et al. studied adversarial manipulation of the feature explainer itself. FairLens AI investigates unintentional hallucination, directional reversal, and numerical distortion introduced downstream by generative LLMs during human-facing report synthesis.

### 1.3 Faithfulness in NLP & Mechanistic Interpretability (Jacovi & Goldberg, 2020; Wiegreffe et al., 2021)
- **Prior Work:** Jacovi & Goldberg ("Towards Faithfully Interpretable NLP Systems: How Should We Define and Evaluate Faithfulness?") formalized that an explanation is faithful if and only if it reflects the true reasoning process of the model generating the prediction.
- **Divergence in FairLens AI:** FairLens AI adopts the grounded evidence verification formulation: the explanation's "ground truth" is not the internal attention weights of the LLM, but rather the authoritative, immutable `AuditEvidence` contract emitted by the statistical fairness auditing system.

### 1.4 LLM Faithfulness & Hallucination in Domain Reasoning (2023–2025)
- **Prior Work:** Benchmarks such as FaithDial, FactScore, and medical/financial NL summarization benchmarks evaluate entity and relation hallucinations in conversational or document-summarization contexts.
- **Divergence in FairLens AI:** Existing hallucination benchmarks focus on open-domain text or unstructured document retrieval. FairLens AI addresses structured mathematical and statistical domain grounding—specifically fairness metrics with complex sign conventions, non-linear parity ratios, and intersectional group statistics.

### 1.5 Algorithmic Fairness Auditing & Governance (Barocas et al., 2019; Raji et al., 2020)
- **Prior Work:** Auditing frameworks (e.g. AIF360, Fairlearn) compute quantitative fairness metrics and trade-off frontiers, but rely on technical dashboards or raw tables that non-technical stakeholders (compliance officers, legal teams, domain experts) struggle to interpret.
- **Divergence in FairLens AI:** While LLMs are increasingly deployed to translate technical audits into executive narratives, no prior study has quantitatively measured the rate at which LLMs invert fairness conclusions or fabricate statistical parity in safety-critical governance settings.

---

## 2. What FairLens AI Contributes That Is NOVEL

1. **First Quantitative Faithfulness Benchmark for ML Fairness Audits:**
   - Formalizes a claim-level extraction and verification protocol specifically tailored to fairness audit reports, evaluating numerical precision, directional veracity, and SHAP attribution fidelity against authoritative audit objects.
2. **Unsupported Claim & Deceptive Assertion Taxonomy:**
   - Identifies and quantifies specific failure modes unique to fairness communication: causal overreach (claiming correlation implies causation), false optimality ("bias is completely eliminated"), and false optimism (masking performance degradation).
3. **Decoupled Coverage vs. Faithfulness Evaluation:**
   - Establishes a rigorous separation between whether an explanation's claims are factual (faithfulness) versus whether the explanation summarizes all available audit metrics (coverage).
4. **End-to-End Cryptographic Traceability Harness:**
   - Pairs deterministic template baselines and LLM outputs under identical SHA-256 evidence digests, isolating linguistic generation variance from underlying audit variance.

---

## 3. What Is NOT Novel (Honest Boundary Declaration)

To maintain scientific integrity, the following aspects of this work are explicitly recognized as standard engineering or established methodology:
- **The underlying ML models and fairness metrics:** Logistic Regression, Random Forests, XGBoost, Demographic Parity, Equalized Odds, and Disparate Impact are established standard techniques from prior literature.
- **The mitigation algorithms:** Correlation Remover, Exponentiated Gradient, and Threshold Optimizer are implementations provided by Fairlearn (Agarwal et al., 2018; Hardt et al., 2016).
- **The SHAP explainers:** TreeSHAP and LinearSHAP are implementations from Lundberg & Lee (2017).
- **The LLM APIs:** Gemini and commercial LLMs are third-party services, not proprietary research contributions of this project.

---

## 4. Why This Is NOT a Generic XAI or LLM Benchmark Paper

- **Not a Generic XAI Study:** We do not evaluate or propose new post-hoc feature importance methods. Explainability is treated strictly as structured audit evidence feeding downstream natural language communication.
- **Not a Generic LLM Benchmark:** We do not test broad linguistic reasoning, general knowledge, or standard MMLU benchmarks. The evaluation is domain-specific to algorithmic fairness governance, where hallucinated metrics or inverted parity directions carry severe legal, compliance, and ethical risks.
- **Not an Abandoned Trade-Off Study:** We do not attempt to establish a novel theoretical Pareto frontier between accuracy, fairness, and explainability. The fairness interventions simply generate diverse empirical audit states to test the explanatory faithfulness of language models.
