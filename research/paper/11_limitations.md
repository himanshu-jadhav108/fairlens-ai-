# 11. Limitations & Threats to Validity

## 11.1 Construct Validity
- Deterministic extraction relies on surface-level and syntactic regex patterns; while regularized and audited, edge cases in complex syntax may evade pattern matching.
- Separation between deterministic automated evaluation and human annotation for subjective magnitude and sociotechnical claims.
- Decoupled operational definition of Faithfulness vs. Evidence Coverage.

## 11.2 Internal Validity
- Random seeds represent stochastic variance across algorithmic splits and initializations, not independent sampling units.
- Dependence on specific prompting strategies and temperature regimes.

## 11.3 External Validity
- Tabular algorithmic fairness benchmarks (Adult, COMPAS, German Credit) represent standard academic audit datasets but do not capture complex unstructured multi-modal auditing domains.
- Focus on specific predictive model architectures and tabular bias mitigations.

## 11.4 LLM Provider Scope
- The empirical investigation utilizes Google Gemini configurations alongside deterministic baselines. Findings may vary across other closed or open-weight foundation model families.
- Gemini is treated strictly as an experimental provider/configuration, not as a research contribution or claim of universality.
