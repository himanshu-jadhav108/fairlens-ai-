# Manuscript Figures: Reproducibility & Specification Guide

This directory contains the publication-quality figures, generation scripts, and visual assets for the FairLens AI research manuscript:

> **"Quantitative Faithfulness of LLM-Generated Natural-Language Explanations for Machine Learning Fairness Audits: An Empirical Study"**

---

## 1. Figure Inventory

| Figure | Filename | Purpose | Generation Tool | Source Data | Generation Script | Output Formats |
|---|---|---|---|---|---|---|
| **Fig 1** | `fig01_research_framework.svg` | End-to-end fairness auditing, SHA-256 evidence parity, explanation generation, and claim evaluation pipeline | Python Vector SVG | Architecture specification | `scripts/generate_diagram_figures.py` | SVG, PNG |
| **Fig 2** | `fig02_experimental_matrix.svg` | Full-factorial benchmark matrix ($3 \times 2 \times 2 \times 3 = 36$ conditions, 72 runs) and legacy retry quarantine ($N=43 \to N=36$) | Python Vector SVG | `final_matrix_inventory.json` | `scripts/generate_diagram_figures.py` | SVG, PNG |
| **Fig 3** | `fig03_claim_evaluation_framework.svg` | Claim boundary isolation, 5-type taxonomy, candidate state matching, and deterministic verification rules | Python Vector SVG | Evaluator architecture | `scripts/generate_diagram_figures.py` | SVG, PNG |
| **Fig 4** | `fig04_numerical_faithfulness.svg` | Primary numerical faithfulness comparison ($100.00\% \text{ vs. } 88.13\%$, $-11.87\text{ pp}, p=1.34\times 10^{-7}, d=-1.097$) and dataset breakdowns | Python / Matplotlib | `summaries/summary__*.json` | `scripts/generate_result_figures.py` | SVG, PNG |
| **Fig 5** | `fig05_unsupported_claims.svg` | Canonical claim taxonomy ($N=1,306$ claims) and comparison of condition-level mean ($8.51\%$) vs. pooled claim rate ($8.65\%$) | Python / Matplotlib | `summaries/summary__*.json` | `scripts/generate_result_figures.py` | SVG, PNG |
| **Fig 6** | `fig06_directional_faithfulness.svg` | Directional faithfulness comparison across $N=23$ evaluable pairs ($100.00\% \text{ vs. } 94.18\%$, $p=0.1979$ non-significant) | Python / Matplotlib | `summaries/summary__*.json` | `scripts/generate_result_figures.py` | SVG, PNG |
| **Fig 7** | `fig07_llama_adjudication.svg` | Secondary LLM sensitivity analysis (Llama 3 8B, $N=100$ sample, $77.0\%$ concordance) and confusion matrix with Kappa Paradox note | Python / Matplotlib | `adjudication/adjudication_records.json` | `scripts/generate_result_figures.py` | SVG, PNG |
| **Fig 8** | `fig08_evidence_claim_example.svg` | Side-by-side authentic examples: accepted rounding ($0.1895 \to 0.190$) vs. canonical failure ($0.2445 \to 0.2$, rel error $18.2\%$) | Python Vector SVG | Canonical audit evidence / claim `num_20` | `scripts/generate_diagram_figures.py` | SVG, PNG |

---

## 2. Global Styling & Color Palette

All figures follow a unified publication design system adhering to scientific visualization and accessibility best practices:
- **Background:** Crisp white (`#FFFFFF`) with thin, high-contrast borders (`#4A5568`).
- **Typography:** Sans-serif vector fonts (`DejaVu Sans`, `Arial`, `Helvetica`) with `svg.fonttype = 'none'` ensuring searchable, selectable text.
- **Colorblind-Safe Semantic Mapping:**
  - **Evidence / Ground Truth:** Navy Blue (`#2B6CB0`, `#EBF8FF`)
  - **Generative Model (Gemini 2.5 Flash):** Purple / Indigo (`#6B46C1`, `#FAF5FF`)
  - **Deterministic Reference Control / Evaluator:** Forest Green (`#22543D`, `#F0FFF4`)
  - **Supported / Faithful Claims:** Green (`#276749`, `#C6F6D5`)
  - **Unsupported / Error Claims:** Dark Red (`#C53030`, `#FFF5F5`)
  - **Undetermined / Conservative Boundary:** Neutral Slate Gray (`#4A5568`, `#EDF2F7`)
  - **Secondary Adjudication (Llama 3 8B):** Deep Navy (`#1A365D`, `#EBF8FF`)
- **Honest Axes:** No deceptive axis truncation; full distributions and error bars explicitly labeled.

---

## 3. How to Reproduce All Figures

To regenerate all 8 figures dynamically from the canonical results:

```bash
python research/paper/figures/scripts/run_all_figures.py
```

Or execute modular scripts individually:

```bash
# Structural diagrams (Figures 1, 2, 3, 8)
python research/paper/figures/scripts/generate_diagram_figures.py

# Empirical statistical figures (Figures 4, 5, 6, 7)
python research/paper/figures/scripts/generate_result_figures.py
```
