# Research Paper Scaffold — Academic Guidelines & Constraints

> **CRITICAL SCIENTIFIC DIRECTIVE:**  
> This paper must **NOT** be written as a software engineering project report, hackathon summary, or product overview.  
> It must follow rigorous peer-reviewed academic standards (e.g., ACM FAccT, IEEE SaTML, NeurIPS, or ICML).

## Guidelines for Authoring

1. **No Fabricated Claims:**  
   Do NOT populate chapters with fabricated numbers, unverified statistical significance, or premature claims of novelty.
2. **Provisional Framing:**  
   The core research direction (*"Evaluating fairness–performance–explainability trade-offs in machine-learning bias mitigation"*) is PROVISIONAL. The final research question, formal hypotheses, and paper title will be established following the literature review.
3. **Traceability:**  
   Every table, figure, and quantitative claim in the Results section must directly link back to an experiment ID and machine-readable manifest under `research/results/manifests/`.
4. **Scaffold Structure:**  
   - `01_introduction.md`: Research context, provisional problem statement, and paper organization.
   - `02_related_work.md`: Structured survey of Algorithmic Fairness, Feature Attribution (SHAP), and Trade-Off Frontiers.
   - `03_research_gap.md`: Formal synthesis of open questions identified in literature.
   - `04_methodology.md`: Mathematical formulation of fairness constraints, model families, and attribution metrics.
   - `05_experimental_setup.md`: Dataset provenance, preprocessing protocols, seed strategies, and manifest tracking.
   - `06_results.md`: Empirical findings with standard deviations across seeds and Pareto trade-off analysis.
   - `07_discussion.md`: Scientific implications, trade-off dynamics, and practical governance insights.
   - `08_limitations.md`: Dataset constraints, tabular scope, and threat to validity.
   - `09_reproducibility.md`: Hardware, software, dependency versions, seed sequences, and execution commands.
   - `10_conclusion.md`: Summary of empirical takeaways and future directions.
   - `references.md`: BibTeX and markdown references.
