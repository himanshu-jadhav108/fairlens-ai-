# 4. Methodology

<!-- PROVISIONAL SCAFFOLD ONLY: Mathematical definitions and formulations. -->

## 4.1 Problem Formulation & Notation
- Input features $X \in \mathcal{X}$, binary label $Y \in \{0, 1\}$, protected attribute $S \in \mathcal{S}$.
- Classifier $f: \mathcal{X} \to \{0, 1\}$ or scoring function $g: \mathcal{X} \to [0, 1]$.

## 4.2 Fairness Criteria
- **Demographic Parity Difference (DPD):**  
  $$\Delta_{\text{DP}} = \max_{s_1, s_2} |P(\hat{Y}=1 \mid S=s_1) - P(\hat{Y}=1 \mid S=s_2)|$$
- **Equalized Odds Difference (EOD):**  
  $$\Delta_{\text{EO}} = \max \left( |\text{FPR}_{s_1} - \text{FPR}_{s_2}|, |\text{TPR}_{s_1} - \text{TPR}_{s_2}| \right)$$
- **Disparate Impact (DI):**  
  $$\text{DI} = \frac{\min_s P(\hat{Y}=1 \mid S=s)}{\max_s P(\hat{Y}=1 \mid S=s)}$$

## 4.3 Mitigation Interventions
- Pre-processing: Fairlearn `CorrelationRemover`.
- In-processing: Fairlearn `ExponentiatedGradient` reductions.
- Post-processing: Fairlearn `ThresholdOptimizer`.

## 4.4 Attribution Metrics & Distance Measures (Provisional)
- Shapley values: $\phi_i(x) = \sum_{S \subseteq F \setminus \{i\}} \frac{|S|!(|F|-|S|-1)!}{|F|!} (f_x(S \cup \{i\}) - f_x(S))$
- Cosine similarity: $S_C(\phi_{\text{base}}, \phi_{\text{mit}})$
- Spearman rank correlation: $\rho_s(\text{rank}(\phi_{\text{base}}), \text{rank}(\phi_{\text{mit}}))$
- Attribution shift: $L_1$ and $L_2$ Euclidean norms.
