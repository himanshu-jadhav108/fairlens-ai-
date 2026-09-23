# Final Publication QA

## ARXIV

- **Source:** `main.tex`
- **Bibliography:** `references.bib`
- **Build method:** `pdflatex -interaction=nonstopmode -halt-on-error main.tex` $\to$ `bibtex main` $\to$ `pdflatex` $\to$ `pdflatex` (MiKTeX 25.12 engine)
- **Build completed:** YES
- **PDF generated from source:** YES
- **Page count:** 22
- **Figures:** 8 (Figures 1–8 present, centered, captioned)
- **References:** 22 (References [1]–[9] rendered on page 21; References [10]–[22] on page 22)
- **Unresolved citations:** 0 (All 45 in-text citations resolved to bracketed numbers; 0 `[?]` markers)
- **Unresolved references:** 0 (0 undefined reference warnings)
- **Fatal LaTeX errors:** 0
- **Overfull boxes:** 0 (0 overfull `\hbox`, 0 overfull `\vbox`)
- **Underfull boxes:** 2 (harmless loose lines in paragraph at line 132)
- **Author Identity:** Himanshu Hemchandra Jadhav, Department of Artificial Intelligence and Data Science, Savitribai Phule Pune University, `himanshujadhav40@gmail.com`, and GitHub repository link visible.

## JSSCI

- **manuscript.docx verified:** YES (Generated directly from official `JSSCI_Manuscript_Template-OTH.docx`)
- **manuscript.pdf verified:** YES (Rendered via Microsoft Word 16.0 COM automation)
- **Page count:** 16 (Main manuscript body Sections 1–6 concludes on page 14; Backmatter statements & References [1]–[22] occupy pages 15–16)
- **Figures:** 8 (Figures 1–8 embedded with captions)
- **Tables:** 4 (Tables 1–4 embedded with captions)
- **References:** 22 (IEEE bracketed format `[1]`–`[22]`, sequentially cited)
- **Double-blind anonymization:** PASS (0 author names, 0 email addresses, 0 institutional affiliations, 0 personal GitHub usernames, 0 repository/branch URLs in manuscript body; generic truthful review statement in Data Availability)
- **DOCX identity metadata:** PASS (`docProps/core.xml` creator, modifier, description, keywords emptied; `docProps/app.xml` company emptied; exported PDF metadata free of author/company info)
- **License wording:** PASS (Official CC BY 4.0 policy preserved: *"Copyright: © the Author(s). Published by JSSCI. This is an open-access article distributed under the terms of the Creative Commons Attribution 4.0 International License (CC BY 4.0)."*; template review history placeholder retained)

## SCIENTIFIC PARITY

All frozen scientific values from `research/paper/PAPER_DRAFT.md` remain 100% unchanged across both preprint and journal packages:
- **Canonical Conditions:** 36
- **Paired Explanation Runs:** 72
- **Total Claims Extracted:** 1,306
- **Total Benchmark Instances:** 57,056 (Adult: 48,842; COMPAS: 7,214; German Credit: 1,000)
- **Numerical Faithfulness:** Gemini 2.5 Flash = $88.13\% \pm 10.82\%$; TemplateExplainer = $100.00\% \pm 0.00\%$
- **Degradation Difference:** $-11.87$ percentage points
- **Cohen's d:** $-1.097$ (large effect)
- **Paired t-statistic:** $t = -6.581, p = 1.34 \times 10^{-7}$
- **Wilcoxon signed-rank:** $W = 0.0, p = 8.28 \times 10^{-6}$
- **Unsupported Claims:** Pooled = $113/1,306 = 8.65\%$; Condition-level unweighted mean = $8.51\% \pm 8.72\%$ ($t = 5.854, p = 1.20 \times 10^{-6}$)
- **Directional Faithfulness:** Gemini 2.5 Flash = $94.18\% \pm 21.02\%$ across $N = 23$ evaluable pairs ($t = -1.328, p = 0.1979$; Wilcoxon $W = 0.0, p = 0.0679$)
- **Secondary Adjudication:** Llama 3 8B (`llama3:latest`), $N = 100$ claims, $77.0\%$ concordance, $98/100$ supported, expected agreement $P_e = 0.7546$, Cohen's $\kappa = 0.063$; formal human validation NOT PERFORMED (explicitly declared)
- **Terminology:** Zero occurrences of "sign flip"; ratio-transition semantic mismatches preserved.

## FINAL BLOCKERS

None.

## FINAL STATUS

READY TO FREEZE
