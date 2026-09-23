# FairLens AI Publication Review Bundle Manifest

**Artifact Archive:** `publication_review_bundle.zip`  
**Creation Date:** September 23, 2026  
**Auditor:** Antigravity Publication Engineering & QA Agent  
**Certification:** **`SCIENTIFIC CONTENT PRESERVED: YES`**  
**Final Build Status:** **`READY TO FREEZE`**

---

## 1. Directory Structure

```text
publication_review_bundle/
├── arxiv/
│   ├── main.tex                       # Authoritative single-column LaTeX manuscript (11pt, margin=1in)
│   ├── references.bib                 # Verified 22-entry BibTeX bibliography
│   ├── main.pdf                       # 22-page preprint PDF compiled via pdflatex + bibtex
│   ├── README.md                      # Compilation and submission guide
│   └── figures/                       # Figures 1–8 in PNG and scalable SVG formats
│       ├── fig01_research_framework.[png|svg]
│       ├── fig02_experimental_matrix.[png|svg]
│       ├── fig03_claim_evaluation_framework.[png|svg]
│       ├── fig04_numerical_faithfulness.[png|svg]
│       ├── fig05_unsupported_claims.[png|svg]
│       ├── fig06_directional_faithfulness.[png|svg]
│       ├── fig07_llama_adjudication.[png|svg]
│       └── fig08_evidence_claim_example.[png|svg]
├── jssci/
│   ├── manuscript.docx                # Sanitized double-blind Word manuscript (official JSSCI template)
│   ├── manuscript.pdf                 # Complete 16-page journal PDF (exported via Word 16.0 COM)
│   ├── README.md                      # JSSCI compliance checklist and manifest
│   └── figures/                       # Figures 1–8 in PNG and scalable SVG formats
├── reports/
│   └── PUBLICATION_FINAL_QA_REPORT.md # Comprehensive final verification audit report
└── metadata/
    └── BUNDLE_MANIFEST.md             # This package manifest and verification summary
```

---

## 2. Package Checksums & Verification

- **Author Identification Policy:**
  - `arxiv/`: Sole author Himanshu Hemchandra Jadhav, Department of Artificial Intelligence and Data Science, Savitribai Phule Pune University, email `himanshujadhav40@gmail.com`, and public GitHub repository link visible.
  - `jssci/`: Fully anonymized for double-blind peer review. 0 occurrences of author name, email, institution, personal GitHub repository, or research branch. DOCX `docProps/core.xml` and `docProps/app.xml` sanitized (no creator, modifier, or company).
- **LaTeX Compilation:** Clean compilation via `pdflatex` $\to$ `bibtex` $\to$ `pdflatex` $\to$ `pdflatex` with 0 fatal errors, 0 undefined citations, 0 undefined references, 0 overfull boxes.
- **Word Conversion:** Rendered via Microsoft Word 16.0 COM automation.
- **Scientific Results:** 100% frozen data parity with `research/paper/PAPER_DRAFT.md`.
