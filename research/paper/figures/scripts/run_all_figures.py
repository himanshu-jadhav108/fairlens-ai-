#!/usr/bin/env python3
"""
run_all_figures.py
------------------
Master execution and validation runner for all 8 FairLens AI manuscript figures.
Runs:
1. generate_diagram_figures.py (Figures 1, 2, 3, 8)
2. generate_result_figures.py  (Figures 4, 5, 6, 7)
Validates all outputs for completeness, file size, and canonical consistency.
"""

import os
import sys
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FIGURES_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))

EXPECTED_FIGURES = [
    ("fig01_research_framework.svg", "Figure 1: Overall Research Framework"),
    ("fig02_experimental_matrix.svg", "Figure 2: Full-Factorial Experimental Matrix"),
    ("fig03_claim_evaluation_framework.svg", "Figure 3: Claim-Level Evaluation Framework"),
    ("fig04_numerical_faithfulness.svg", "Figure 4: Numerical Faithfulness Comparison"),
    ("fig05_unsupported_claims.svg", "Figure 5: Unsupported Claims & Claim Taxonomy"),
    ("fig06_directional_faithfulness.svg", "Figure 6: Directional Faithfulness Robustness"),
    ("fig07_llama_adjudication.svg", "Figure 7: Secondary LLM Claim Adjudication Sensitivity Analysis"),
    ("fig08_evidence_claim_example.svg", "Figure 8: Authentic Evidence-to-Claim Verification Examples"),
]


def run_script(script_name):
    script_path = os.path.join(SCRIPT_DIR, script_name)
    print(f"\n--- Running {script_name} ---")
    result = subprocess.run([sys.executable, script_path], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"ERROR running {script_name}:")
        print(result.stderr)
        sys.exit(1)
    else:
        print(result.stdout)


def audit_terminology():
    print("\n--- Auditing Scientific Terminology in SVGs ---")
    forbidden_terms = [
        "sign flip",
        "sign flips",
        "sign reversal",
        "sign reversals",
        "genuine sign reversal",
        "genuine sign reversals",
        "Directional Degradation",
        "guarantees pure generation comparison",
    ]
    all_clean = True
    for svg_name, _ in EXPECTED_FIGURES:
        svg_path = os.path.join(FIGURES_DIR, svg_name)
        if not os.path.exists(svg_path):
            continue
        with open(svg_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        found_in_file = []
        for term in forbidden_terms:
            if term.lower() in content.lower():
                found_in_file.append(term)
        
        if found_in_file:
            print(f"FAIL [{svg_name}]: Found forbidden terminology: {found_in_file}")
            all_clean = False
        else:
            print(f"PASS [{svg_name}]: Clean of forbidden terminology.")
            
    if not all_clean:
        print("Terminology audit failed! Forbidden terms detected.")
        sys.exit(1)
    else:
        print("All SVGs passed the terminology audit!")


def audit_numerical_integrity():
    print("\n--- Auditing Numerical & Structural Integrity ---")
    
    # Figure 4 checks
    fig4_path = os.path.join(FIGURES_DIR, "fig04_numerical_faithfulness.svg")
    with open(fig4_path, 'r', encoding='utf-8') as f:
        fig4 = f.read()
    assert "88.13%" in fig4, "Fig 4 missing 88.13%"
    assert "100.0%" in fig4, "Fig 4 missing 100.0%"
    assert "-1.097" in fig4, "Fig 4 missing Cohen's d -1.097"
    print("PASS [fig04]: Verified 88.13%, 100.0%, and Cohen's d = -1.097")

    # Figure 6 checks
    fig6_path = os.path.join(FIGURES_DIR, "fig06_directional_faithfulness.svg")
    with open(fig6_path, 'r', encoding='utf-8') as f:
        fig6 = f.read()
    assert "94.18%" in fig6, "Fig 6 missing 94.18%"
    assert "0.1979" in fig6, "Fig 6 missing p=0.1979"
    assert "Difference Not Statistically Significant" in fig6, "Fig 6 title missing updated neutral phrasing"
    print("PASS [fig06]: Verified 94.18%, p=0.1979, and neutral non-significant title")

    # Figure 7 checks
    fig7_path = os.path.join(FIGURES_DIR, "fig07_llama_adjudication.svg")
    with open(fig7_path, 'r', encoding='utf-8') as f:
        fig7 = f.read()
    assert "NOT HUMAN VALIDATION" in fig7, "Fig 7 missing 'NOT HUMAN VALIDATION'"
    assert "Collapsed Sensitivity Confusion Matrix" in fig7, "Fig 7 missing collapsed matrix title"
    assert "Adjudicator UNDETERMINABLE = 0 cases; omitted from displayed" in fig7, "Fig 7 missing note"
    print("PASS [fig07]: Verified NOT HUMAN VALIDATION, collapsed matrix clarification, and note")

    # Figure 1 checks
    fig1_path = os.path.join(FIGURES_DIR, "fig01_research_framework.svg")
    with open(fig1_path, 'r', encoding='utf-8') as f:
        fig1 = f.read()
    assert "ratio-transition" in fig1 and "semantic mismatches" in fig1, "Fig 1 missing ratio-transition semantic mismatches"
    assert "SHA-256" in fig1, "Fig 1 missing SHA-256 parity note"
    print("PASS [fig01]: Verified ratio-transition semantic mismatch and SHA-256 parity text")

    # Figure 3 checks
    fig3_path = os.path.join(FIGURES_DIR, "fig03_claim_evaluation_framework.svg")
    with open(fig3_path, 'r', encoding='utf-8') as f:
        fig3 = f.read()
    assert "ratio-transition" in fig3 and "semantic mismatches" in fig3, "Fig 3 missing ratio-transition semantic mismatches"
    assert "METHODOLOGY DEMONSTRATION" in fig3 or "demonstration only" in fig3, "Fig 3 missing illustrative label"
    print("PASS [fig03]: Verified ratio-transition semantic mismatch and illustrative demonstration label")

    # Figure 8 checks
    fig8_path = os.path.join(FIGURES_DIR, "fig08_evidence_claim_example.svg")
    with open(fig8_path, 'r', encoding='utf-8') as f:
        fig8 = f.read()
    assert "German Credit — Random Forest" in fig8 and "Threshold Optimizer — Seed 123" in fig8, "Fig 8 missing polished label"
    assert "0.1895" in fig8 and "0.190" in fig8, "Fig 8 missing authentic rounding values"
    print("PASS [fig08]: Verified polished condition label and authentic rounding values")

    print("All numerical and structural integrity checks PASSED!")


def validate_figures():
    print("\n--- Validating Generated Figures ---")
    all_valid = True
    for svg_name, title in EXPECTED_FIGURES:
        svg_path = os.path.join(FIGURES_DIR, svg_name)
        png_path = os.path.join(FIGURES_DIR, svg_name.replace('.svg', '.png'))
        
        if not os.path.exists(svg_path):
            print(f"FAIL: Missing {svg_name}")
            all_valid = False
            continue
            
        svg_size = os.path.getsize(svg_path)
        if svg_size < 1000:
            print(f"FAIL: {svg_name} is unexpectedly small ({svg_size} bytes)")
            all_valid = False
            continue
            
        png_exists = os.path.exists(png_path)
        png_size = os.path.getsize(png_path) if png_exists else 0
        if not png_exists or png_size < 10000:
            print(f"FAIL: {png_path} missing or unexpectedly small ({png_size} bytes)")
            all_valid = False
            continue
        
        print(f"PASS: {svg_name} ({svg_size:,} bytes) | PNG ({png_size:,} bytes) - {title}")
        
    if all_valid:
        print("\nAll 8 publication-quality figures successfully generated and validated!")
    else:
        print("\nValidation failed for one or more figures.")
        sys.exit(1)


if __name__ == '__main__':
    run_script("generate_diagram_figures.py")
    run_script("generate_result_figures.py")
    validate_figures()
    audit_terminology()
    audit_numerical_integrity()
    run_script("audit_text_containment.py")

