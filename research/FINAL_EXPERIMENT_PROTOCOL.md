# FairLens AI: Confirmatory Experiment Protocol (Phase 3)

**Study Title:** Quantitative Faithfulness of LLM-Generated Natural-Language Explanations for Machine Learning Fairness Audits: An Empirical Study  
**Document Status:** **LOCKED PROTOCOL (READY FOR EXECUTION)**  
**Target Execution Mode:** `FINAL_EMPIRICAL_RUN`  
**Planned Sample Size:** $N = 135$ conditions $\times$ 2 explanation sources = 270 full evaluation pipelines  

---

## 1. Locked Research Question & Scope

The research topic and core inquiry are permanently fixed:
> **How quantitatively faithful are LLM-generated natural-language explanations of machine learning fairness audits when evaluated against deterministic, ground-truth structured audit evidence?**

This confirmatory study scales the validated empirical methodology established during the 24-condition pilot across a comprehensive, multi-domain benchmark matrix.

---

## 2. Experimental Design & Factorial Matrix

The confirmatory study evaluates a fully balanced $3 \times 3 \times 3 \times 5$ factorial design:

### 2.1 Factors & Levels
1. **Datasets ($D = 3$):**
   - `adult`: Adult Census Income (Income prediction, sensitive attribute: `sex`)
   - `compas`: ProPublica COMPAS Recidivism (Recidivism risk, sensitive attribute: `race`)
   - `german`: German Credit Risk (Creditworthiness, sensitive attribute: `age`)
2. **ML Classifiers ($M = 3$):**
   - `logistic_regression`: Generalized linear model (L2 penalty, liblinear solver)
   - `random_forest`: Non-linear tree ensemble (100 estimators, max depth 10)
   - `xgboost`: Gradient boosted decision trees (100 estimators, learning rate 0.1)
3. **Fairness Mitigation Strategies ($F = 3$):**
   - `reweighing`: Pre-processing sample weight calibration
   - `correlation_remover`: Pre-processing sensitive correlation projection
   - `threshold_optimizer`: Post-processing group-specific decision threshold tuning
4. **Random Initialization Seeds ($S = 5$):**
   - `42`, `123`, `456`, `789`, `1011`

$$\text{Total Matrix Conditions} = 3 \times 3 \times 3 \times 5 = 135 \text{ conditions}$$

---

## 3. Explanatory Systems & Conditions

For each of the 135 conditions, two explanations will be generated and evaluated:
1. **Target Experimental System:** Live Large Language Model (Google Gemini API via `GeminiProvider`, standardized prompt `combined_audit_v1`, temperature $T = 0.2$, seed fixed).
2. **Control Baseline System:** Grounded deterministic template explanation (`template_baseline`), inserting ground truth metrics directly without generative paraphrasing.

---

## 4. Evaluation Endpoints & Primary Metrics

All explanations are evaluated against the canonical `StructuredAuditEvidence` artifact via deterministic, rule-based NLI claim extraction and verification:

1. **Numerical Faithfulness ($F_{\text{num}} \in [0, 1]$):**
   $$\text{Ratio of numerical claims matching ground-truth audit metrics within absolute tolerance } \epsilon = 0.005.$$
2. **Directional Faithfulness ($F_{\text{dir}} \in [0, 1]$):**
   $$\text{Ratio of qualitative trend claims correctly matching observed performance and parity deltas.}$$
3. **Attribution Faithfulness ($F_{\text{attr}} \in [0, 1]$):**
   $$\text{Concordance of top-5 reported SHAP features and sign contributions with computed attributions.}$$
4. **Unsupported Claim Rate ($U \in [0, 1]$):**
   $$\text{Proportion of extracted factual claims that cannot be traced to any field in the evidence JSON.}$$
5. **Numerical Mean Absolute Error (MAE):**
   $$\text{Mean absolute deviation of reported numerical values from ground-truth targets.}$$

---

## 5. Provenance, Isolation, and Replicability

- **Execution Mode Tag:** All confirmatory experiment artifacts must strictly record `"execution_mode": "FINAL_EMPIRICAL_RUN"`.
- **Output Directory:** Canonical outputs must be isolated under `research/results/final/` (`raw/`, `summaries/`, `manifests/`, `processed/`).
- **Evidence Hashing:** Every run must compute and record the SHA-256 hash of its input `StructuredAuditEvidence`.
- **Git Commit Anchoring:** Every manifest records the HEAD git commit hash and exact package versions.

---

## 6. Execution Command (Pre-Staged)

The execution script is pre-staged and validated for execution:
```bash
python research/scripts/run_llm_experiment.py \
    --config research/configs/final_protocol_config.yaml \
    --provider gemini \
    --execution-mode FINAL_EMPIRICAL_RUN \
    --output-dir research/results/final
```

> **EXECUTION STATUS:** STAGED AND FROZEN.
> In accordance with project research boundaries, execution of the 135-condition confirmatory study will be initiated in Phase 4 under designated batch compute resources.
