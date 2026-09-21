#!/usr/bin/env python3
"""
generate_diagram_figures.py
---------------------------
Generates publication-quality structural diagrams and visual examples for the
FairLens AI research manuscript:
- Figure 1: Overall Research Framework & Evaluation Pipeline
- Figure 2: Full-Factorial Experimental Matrix (N=36 canonical conditions)
- Figure 3: Claim-Level Evaluation Framework & Decision Logic
- Figure 8: Authentic Evidence-to-Claim Verification Examples (Rounding vs. Truncation Error)

Outputs both vector SVGs and high-resolution 300 DPI PNGs in research/paper/figures/
using native Matplotlib drawing routines with explicit top-anchored typography
and generous coordinate spacing for 100% collision-free, publication-grade rendering.
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch

# Styling constants
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['svg.fonttype'] = 'none'

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FIGURES_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
os.makedirs(FIGURES_DIR, exist_ok=True)

# Color tokens
C_BLUE = '#2B6CB0'       # Evidence / Ground truth
C_BLUE_LIGHT = '#EBF8FF'
C_BLUE_BORDER = '#3182CE'
C_PURPLE = '#6B46C1'     # Generative model (Gemini)
C_PURPLE_LIGHT = '#FAF5FF'
C_PURPLE_BORDER = '#805AD5'
C_GREEN = '#276749'      # Reference control / Supported
C_GREEN_LIGHT = '#F0FFF4'
C_GREEN_BORDER = '#38A169'
C_RED = '#C53030'        # Unsupported / Error
C_RED_LIGHT = '#FFF5F5'
C_RED_BORDER = '#E53E3E'
C_GRAY = '#4A5568'       # Neutral / Undetermined
C_GRAY_LIGHT = '#F7FAFC'
C_GRAY_BORDER = '#CBD5E0'
C_DARK = '#1A202C'       # Headings / text


def save_figure(fig, filename_base):
    """Saves figure cleanly as both SVG and 300 DPI PNG."""
    svg_path = os.path.join(FIGURES_DIR, f"{filename_base}.svg")
    png_path = os.path.join(FIGURES_DIR, f"{filename_base}.png")
    fig.savefig(svg_path, format='svg', bbox_inches='tight')
    fig.savefig(png_path, format='png', dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"Generated Figure: {svg_path} and {png_path}")


def draw_box(ax, x, y, w, h, bg_color, border_color, border_width=1.2, radius=8, zorder=1):
    """Draws a rounded rectangular box."""
    box = FancyBboxPatch((x, y), w, h,
                         boxstyle=f"round,pad=0,rounding_size={radius}",
                         facecolor=bg_color, edgecolor=border_color,
                         linewidth=border_width, zorder=zorder)
    ax.add_patch(box)
    return box


def draw_arrow(ax, p1, p2, color='#718096', lw=1.6):
    """Draws a connecting arrow between two coordinate pairs."""
    arrow = patches.FancyArrowPatch(p1, p2,
                                   arrowstyle='->,head_width=5,head_length=6',
                                   color=color, linewidth=lw, zorder=3)
    ax.add_patch(arrow)
    return arrow


# ==============================================================================
# FIGURE 1: Overall Research Framework & Evaluation Pipeline
# ==============================================================================
def generate_figure_1():
    """Generates Figure 1: Research Framework."""
    W, H = 1360, 640
    fig, ax = plt.subplots(figsize=(17.0, 8.0), dpi=100, facecolor='white')
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.axis('off')

    col_w = 300
    top_y = 600
    card_h = 560
    y_base = top_y - card_h  # 40

    # ------------------ STAGE 1: ALGORITHMIC AUDITING ------------------
    x1 = 35
    draw_box(ax, x1, y_base, col_w, card_h, C_BLUE_LIGHT, C_BLUE_BORDER, 1.5, 10)
    # Header bar
    draw_box(ax, x1, top_y - 40, col_w, 40, C_BLUE, C_BLUE, 0, 8)
    ax.text(x1 + col_w/2, top_y - 20, "1. ALGORITHMIC AUDITING", ha='center', va='center',
            color='white', fontweight='bold', fontsize=11.5)

    # Box 1.1: Benchmark Data
    b1_h = 95
    b1_y = top_y - 40 - 15 - b1_h  # 450
    draw_box(ax, x1 + 12, b1_y, col_w - 24, b1_h, 'white', C_BLUE_BORDER, 1.0, 6)
    ax.text(x1 + col_w/2, b1_y + b1_h - 12, "Benchmark Data ($N=57,056$)", ha='center', va='top',
            color=C_BLUE, fontweight='bold', fontsize=10.2)
    ax.text(x1 + 22, b1_y + b1_h - 32,
            "• Adult Census Income: 48,842 instances\n"
            "• COMPAS Recidivism: 7,214 instances\n"
            "• German Credit: 1,000 instances",
            ha='left', va='top', color=C_DARK, fontsize=8.6, linespacing=1.35)

    # Box 1.2: Model Matrix
    b2_h = 115
    b2_y = b1_y - 14 - b2_h  # 321
    draw_box(ax, x1 + 12, b2_y, col_w - 24, b2_h, 'white', C_BLUE_BORDER, 1.0, 6)
    ax.text(x1 + col_w/2, b2_y + b2_h - 12, "Model & Mitigation Matrix", ha='center', va='top',
            color=C_BLUE, fontweight='bold', fontsize=10.2)
    ax.text(x1 + 22, b2_y + b2_h - 32,
            "• Logistic Regression & Random Forest\n"
            "• Correlation Remover & Threshold Opt.\n"
            "• Seeds: 42, 123, 456 (3 splits)\n"
            "• 36 full-factorial audit conditions",
            ha='left', va='top', color=C_DARK, fontsize=8.6, linespacing=1.35)

    # Box 1.3: Audit Evidence
    b3_h = 115
    b3_y = b2_y - 14 - b3_h  # 192
    draw_box(ax, x1 + 12, b3_y, col_w - 24, b3_h, 'white', C_BLUE_BORDER, 1.0, 6)
    ax.text(x1 + col_w/2, b3_y + b3_h - 12, "Structured Audit Evidence", ha='center', va='top',
            color=C_BLUE, fontweight='bold', fontsize=10.2)
    ax.text(x1 + 22, b3_y + b3_h - 32,
            "• Fairness: DPD, EOD, Disparate Impact\n"
            "• Performance: Accuracy, Selection Rate\n"
            "• Attribution: Top-5 SHAP values\n"
            "• Metric states: Baseline ($S_0$), Mitigated ($S_1$), $\\Delta$",
            ha='left', va='top', color=C_DARK, fontsize=8.6, linespacing=1.35)

    # Box 1.4: Evidence Hash Parity
    b4_h = 110
    b4_y = b3_y - 14 - b4_h  # 68
    draw_box(ax, x1 + 12, b4_y, col_w - 24, b4_h, 'white', C_BLUE_BORDER, 1.0, 6)
    ax.text(x1 + col_w/2, b4_y + b4_h - 12, "Evidence Hash Verification", ha='center', va='top',
            color=C_BLUE, fontweight='bold', fontsize=10.2)
    ax.text(x1 + 22, b4_y + b4_h - 32,
            "• SHA-256 payload parity verified\n"
            "• SHA-256 evidence parity verifies\n"
            "  identical inputs for controlled comparison",
            ha='left', va='top', color=C_DARK, fontsize=8.4, linespacing=1.3)
    draw_box(ax, x1 + 20, b4_y + 10, col_w - 40, 24, C_GREEN_LIGHT, C_GREEN_BORDER, 0.8, 4)
    ax.text(x1 + col_w/2, b4_y + 22, "SHA-256(Input) == SHA-256(Exp)", ha='center', va='center',
            color=C_GREEN, fontweight='bold', fontsize=8.0, family='monospace')

    # Arrow 1 -> 2
    draw_arrow(ax, (x1 + col_w, top_y - 280), (x1 + col_w + 35, top_y - 280), lw=2.0)

    # ------------------ STAGE 2: DUAL EXPLANATIONS ------------------
    x2 = x1 + col_w + 35  # 370
    draw_box(ax, x2, y_base, col_w, card_h, C_PURPLE_LIGHT, C_PURPLE_BORDER, 1.5, 10)
    draw_box(ax, x2, top_y - 40, col_w, 40, C_PURPLE, C_PURPLE, 0, 8)
    ax.text(x2 + col_w/2, top_y - 20, "2. DUAL EXPLANATIONS", ha='center', va='center',
            color='white', fontweight='bold', fontsize=11.5)

    # Branch A: Template Explainer (Control)
    ba_h = 215
    ba_y = top_y - 40 - 15 - ba_h  # 330
    draw_box(ax, x2 + 12, ba_y, col_w - 24, ba_h, C_GREEN_LIGHT, C_GREEN_BORDER, 1.2, 8)
    ax.text(x2 + col_w/2, ba_y + ba_h - 14, "Deterministic Reference Control", ha='center', va='top',
            color=C_GREEN, fontweight='bold', fontsize=10.5)
    ax.text(x2 + col_w/2, ba_y + ba_h - 32, "TemplateExplainer (Rule-Based)", ha='center', va='top',
            color='#2D3748', fontstyle='italic', fontsize=8.6)
    ax.text(x2 + 22, ba_y + ba_h - 56,
            "• Standardized factual templates\n"
            "• Direct evidence extraction logic\n"
            "• Zero stochastic sampling or drift\n"
            "• Evidence-grounded baseline anchor",
            ha='left', va='top', color=C_DARK, fontsize=8.6, linespacing=1.35)
    # Badge inside control
    draw_box(ax, x2 + 24, ba_y + 14, col_w - 48, 32, 'white', C_GREEN_BORDER, 1.0, 5)
    ax.text(x2 + col_w/2, ba_y + 30, "Faithfulness: 100.00% ± 0.00%", ha='center', va='center',
            color=C_GREEN, fontweight='bold', fontsize=9.2)

    # Branch B: Generative LLM
    bb_h = 250
    bb_y = ba_y - 15 - bb_h  # 65
    draw_box(ax, x2 + 12, bb_y, col_w - 24, bb_h, 'white', C_PURPLE_BORDER, 1.2, 8)
    ax.text(x2 + col_w/2, bb_y + bb_h - 14, "Generative Language Model", ha='center', va='top',
            color=C_PURPLE, fontweight='bold', fontsize=10.5)
    ax.text(x2 + col_w/2, bb_y + bb_h - 32, "Gemini 2.5 Flash (API)", ha='center', va='top',
            color='#2D3748', fontstyle='italic', fontsize=8.6)
    ax.text(x2 + 22, bb_y + bb_h - 54,
            "• Prompt template: combined_audit_v1\n"
            "• T = 0.2, Top_p = 0.95, Max_tokens = 1500\n"
            "• Multi-metric synthesis narrative",
            ha='left', va='top', color=C_DARK, fontsize=8.6, linespacing=1.35)
    # Observed stats subcard
    draw_box(ax, x2 + 18, bb_y + 12, col_w - 36, 96, C_PURPLE_LIGHT, C_PURPLE_BORDER, 1.0, 5)
    ax.text(x2 + col_w/2, bb_y + 94, "Empirical Performance (N=36):", ha='center', va='top',
            color=C_PURPLE, fontweight='bold', fontsize=8.8)
    ax.text(x2 + 26, bb_y + 76,
            "• Numerical: 88.13% ± 10.82%\n"
            "• Directional: 94.18% ± 21.02%\n"
            "• Unsupported: 8.51% ± 8.72%\n"
            "• Total parsed claims: 1,306",
            ha='left', va='top', color=C_DARK, fontsize=8.2, linespacing=1.3)

    # Arrow 2 -> 3
    draw_arrow(ax, (x2 + col_w, top_y - 280), (x2 + col_w + 35, top_y - 280), lw=2.0)

    # ------------------ STAGE 3: CLAIM-LEVEL EVALUATION ------------------
    x3 = x2 + col_w + 35  # 705
    draw_box(ax, x3, y_base, col_w, card_h, C_GREEN_LIGHT, C_GREEN_BORDER, 1.5, 10)
    draw_box(ax, x3, top_y - 40, col_w, 40, C_GREEN, C_GREEN, 0, 8)
    ax.text(x3 + col_w/2, top_y - 20, "3. CLAIM-LEVEL EVALUATION", ha='center', va='center',
            color='white', fontweight='bold', fontsize=11.5)

    # Box 3.1: Clause Segmentation
    b31_h = 82
    b31_y = top_y - 40 - 14 - b31_h  # 464
    draw_box(ax, x3 + 12, b31_y, col_w - 24, b31_h, 'white', C_GREEN_BORDER, 1.0, 6)
    ax.text(x3 + col_w/2, b31_y + b31_h - 12, "Boundary Isolation & Extraction", ha='center', va='top',
            color=C_GREEN, fontweight='bold', fontsize=10.2)
    ax.text(x3 + 22, b31_y + b31_h - 30,
            "• Deterministic regex clause segmentation\n"
            "• Splits compound narrative sentences\n"
            "• Preserves atomic assertion context",
            ha='left', va='top', color=C_DARK, fontsize=8.6, linespacing=1.35)

    # Box 3.2: 5 Dimensions of Decision Engine
    b32_h = 396
    b32_y = b31_y - 14 - b32_h  # 54
    draw_box(ax, x3 + 12, b32_y, col_w - 24, b32_h, 'white', C_GREEN_BORDER, 1.0, 6)
    ax.text(x3 + col_w/2, b32_y + b32_h - 12, "Deterministic Decision Engine", ha='center', va='top',
            color=C_GREEN, fontweight='bold', fontsize=10.5)

    # Dim 1: Numerical
    d_h = 62
    d1_y = b32_y + b32_h - 32 - d_h  # 356
    draw_box(ax, x3 + 18, d1_y, col_w - 36, d_h, '#F7FAFC', C_BLUE_BORDER, 0.8, 4)
    ax.text(x3 + 24, d1_y + d_h - 8, "1. Numerical Verification", ha='left', va='top', color=C_BLUE, fontweight='bold', fontsize=8.8)
    ax.text(x3 + 24, d1_y + d_h - 24, "|v_claim - v_truth| ≤ 0.015 or rel ≤ 5%", ha='left', va='top', color=C_DARK, fontsize=7.8, family='monospace')
    ax.text(x3 + 24, d1_y + d_h - 41, "109/1,125 unsupported (9.69%)", ha='left', va='top', color=C_RED, fontweight='bold', fontsize=8.0)

    # Dim 2: Directional
    d2_h = 76
    d2_y = d1_y - 8 - d2_h  # 272
    draw_box(ax, x3 + 18, d2_y, col_w - 36, d2_h, '#F7FAFC', C_PURPLE_BORDER, 0.8, 4)
    ax.text(x3 + 24, d2_y + d2_h - 8, "2. Directional Consistency", ha='left', va='top', color=C_PURPLE, fontweight='bold', fontsize=8.8)
    ax.text(x3 + 24, d2_y + d2_h - 24, "sign(asserted_dir) == sign(S₁ - S₀)", ha='left', va='top', color=C_DARK, fontsize=7.8, family='monospace')
    ax.text(x3 + 24, d2_y + d2_h - 41, "4/118 unsupported ratio-transition", ha='left', va='top', color=C_RED, fontweight='bold', fontsize=8.0)
    ax.text(x3 + 24, d2_y + d2_h - 57, "semantic mismatches (3.39%)", ha='left', va='top', color=C_RED, fontweight='bold', fontsize=8.0)

    # Dim 3: Fairness & Perf
    d3_h = 58
    d3_y = d2_y - 8 - d3_h  # 206
    draw_box(ax, x3 + 18, d3_y, col_w - 36, d3_h, '#F7FAFC', C_GREEN_BORDER, 0.8, 4)
    ax.text(x3 + 24, d3_y + d3_h - 7, "3. Fairness & Performance", ha='left', va='top', color=C_GREEN, fontweight='bold', fontsize=8.6)
    ax.text(x3 + 24, d3_y + d3_h - 22, "Disparity narrative & accuracy assertions", ha='left', va='top', color=C_DARK, fontsize=7.8)
    ax.text(x3 + 24, d3_y + d3_h - 39, "48/48 supported (100.0%)", ha='left', va='top', color=C_GREEN, fontweight='bold', fontsize=7.8)

    # Dim 4: Magnitude
    d4_h = 58
    d4_y = d3_y - 8 - d4_h  # 140
    draw_box(ax, x3 + 18, d4_y, col_w - 36, d4_h, '#F7FAFC', C_GRAY_BORDER, 0.8, 4)
    ax.text(x3 + 24, d4_y + d4_h - 7, "4. Subjective Magnitude", ha='left', va='top', color=C_GRAY, fontweight='bold', fontsize=8.6)
    ax.text(x3 + 24, d4_y + d4_h - 22, "Unanchored modifiers ('substantially')", ha='left', va='top', color=C_DARK, fontsize=7.8)
    ax.text(x3 + 24, d4_y + d4_h - 39, "15/15 routed to UNDETERMINABLE", ha='left', va='top', color=C_GRAY, fontweight='bold', fontsize=7.8)

    # Dim 5: Unsupported
    d5_h = 58
    d5_y = d4_y - 8 - d5_h  # 74
    draw_box(ax, x3 + 18, d5_y, col_w - 36, d5_h, C_RED_LIGHT, C_RED_BORDER, 0.8, 4)
    ax.text(x3 + 24, d5_y + d5_h - 7, "5. Unsupported Claims Rate", ha='left', va='top', color=C_RED, fontweight='bold', fontsize=8.6)
    ax.text(x3 + 24, d5_y + d5_h - 22, "Condition Mean: 8.51% ± 8.72%", ha='left', va='top', color=C_DARK, fontsize=7.8)
    ax.text(x3 + 24, d5_y + d5_h - 39, "Pooled: 113/1,306 unsupported (8.65%)", ha='left', va='top', color=C_RED, fontweight='bold', fontsize=7.8)

    # Arrow 3 -> 4
    draw_arrow(ax, (x3 + col_w, top_y - 280), (x3 + col_w + 35, top_y - 280), lw=2.0)

    # ------------------ STAGE 4: BENCHMARK GOVERNANCE ------------------
    x4 = x3 + col_w + 35  # 1040
    draw_box(ax, x4, y_base, col_w, card_h, '#F7FAFC', C_GRAY_BORDER, 1.5, 10)
    draw_box(ax, x4, top_y - 40, col_w, 40, C_DARK, C_DARK, 0, 8)
    ax.text(x4 + col_w/2, top_y - 20, "4. BENCHMARK GOVERNANCE", ha='center', va='center',
            color='white', fontweight='bold', fontsize=11.5)

    # Box 4.1: Empirical Findings
    b41_h = 230
    b41_y = top_y - 40 - 15 - b41_h  # 315
    draw_box(ax, x4 + 12, b41_y, col_w - 24, b41_h, 'white', C_GRAY_BORDER, 1.0, 6)
    ax.text(x4 + col_w/2, b41_y + b41_h - 12, "Primary Empirical Findings", ha='center', va='top',
            color=C_DARK, fontweight='bold', fontsize=10.5)

    # Clean non-overlapping layout for the 3 RQs
    # RQ1
    ax.text(x4 + 20, b41_y + b41_h - 34, "RQ1 (Numerical Faithfulness):", ha='left', va='top', color=C_DARK, fontweight='bold', fontsize=8.6)
    ax.text(x4 + 20, b41_y + b41_h - 50, "• -11.87 pp degradation (p = 1.34e-7)\n• Cohen's d = -1.097 (Large effect)",
            ha='left', va='top', color=C_RED, fontsize=8.0, linespacing=1.25)
    # RQ2
    ax.text(x4 + 20, b41_y + b41_h - 96, "RQ2 (Directional Faithfulness):", ha='left', va='top', color=C_DARK, fontweight='bold', fontsize=8.6)
    ax.text(x4 + 20, b41_y + b41_h - 112, "• 94.18% vs. 100% control (N=23 pairs)\n• Diff: -5.82 pp (p = 0.1979, n.s.)",
            ha='left', va='top', color=C_GREEN, fontsize=8.0, linespacing=1.25)
    # RQ3
    ax.text(x4 + 20, b41_y + b41_h - 158, "RQ3 (Unsupported Claims):", ha='left', va='top', color=C_DARK, fontweight='bold', fontsize=8.6)
    ax.text(x4 + 20, b41_y + b41_h - 174, "• 8.51% condition mean (p = 1.20e-6)\n• 8.65% pooled claim-level rate",
            ha='left', va='top', color=C_RED, fontsize=8.0, linespacing=1.25)

    # Box 4.2: Secondary Adjudication
    b42_h = 240
    b42_y = b41_y - 14 - b42_h  # 61
    draw_box(ax, x4 + 12, b42_y, col_w - 24, b42_h, C_BLUE_LIGHT, C_BLUE_BORDER, 1.0, 6)
    ax.text(x4 + col_w/2, b42_y + b42_h - 12, "Secondary LLM Sensitivity Study", ha='center', va='top',
            color=C_BLUE, fontweight='bold', fontsize=10.2)
    ax.text(x4 + col_w/2, b42_y + b42_h - 30, "Llama 3 8B Adjudicator (N=100)", ha='center', va='top',
            color='#2D3748', fontstyle='italic', fontsize=8.6)
    ax.text(x4 + 20, b42_y + b42_h - 52,
            "• 77.0% overall raw concordance\n"
            "• 100% on Dir, Fair, & Perf claims\n"
            "• 80% numerical claim agreement\n"
            "• 0% magnitude agreement (undet)\n"
            "• Ternary κ = 0.063 | Binary κ = 0.045\n"
            "• Kappa Paradox: Pe = 75.5%",
            ha='left', va='top', color=C_DARK, fontsize=8.2, linespacing=1.35)

    # Methodological boundary badge
    draw_box(ax, x4 + 18, b42_y + 12, col_w - 36, 52, 'white', C_BLUE_BORDER, 1.2, 5)
    ax.text(x4 + col_w/2, b42_y + 54, "Methodological Scoping:", ha='center', va='top',
            color=C_DARK, fontweight='bold', fontsize=8.4)
    ax.text(x4 + col_w/2, b42_y + 38, "Sensitivity Analysis Only", ha='center', va='top',
            color='#4A5568', fontsize=8.0)
    ax.text(x4 + col_w/2, b42_y + 24, "Explicitly NOT Human Validation", ha='center', va='top',
            color=C_RED, fontweight='bold', fontsize=8.2)

    save_figure(fig, 'fig01_research_framework')


# ==============================================================================
# FIGURE 2: Full-Factorial Experimental Matrix
# ==============================================================================
def generate_figure_2():
    """Generates Figure 2: Full-Factorial Experimental Matrix."""
    W, H = 1260, 620
    fig, ax = plt.subplots(figsize=(16.2, 7.8), dpi=100, facecolor='white')
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.axis('off')

    # Main factors y range
    y_card = 135
    h_card = 455
    top_y = y_card + h_card  # 590

    # Factor 1: Datasets
    x1, w1 = 25, 235
    draw_box(ax, x1, y_card, w1, h_card, C_BLUE_LIGHT, C_BLUE_BORDER, 1.5, 10)
    draw_box(ax, x1, top_y - 38, w1, 38, C_BLUE, C_BLUE, 0, 8)
    ax.text(x1 + w1/2, top_y - 19, "FACTOR 1: DATASETS (3)", ha='center', va='center',
            color='white', fontweight='bold', fontsize=10.5)

    # 3 Dataset cards
    d_cards = [
        ("Adult Census Income", "• N = 48,842 instances\n• Sensitive: Sex (binary)\n• Target: Income > $50K", 442),
        ("COMPAS Recidivism", "• N = 7,214 instances\n• Sensitive: Race (binary)\n• Target: 2-yr Recidivism", 336),
        ("German Credit", "• N = 1,000 instances\n• Sensitive: Age (binary)\n• Target: Credit Risk", 230)
    ]
    for title, desc, yc in d_cards:
        draw_box(ax, x1 + 12, yc, w1 - 24, 94, 'white', C_BLUE_BORDER, 1.0, 6, zorder=2)
        ax.text(x1 + 20, yc + 94 - 12, title, ha='left', va='top', color=C_BLUE, fontweight='bold', fontsize=9.6, zorder=3)
        ax.text(x1 + 20, yc + 94 - 32, desc, ha='left', va='top', color=C_DARK, fontsize=8.5, linespacing=1.35, zorder=3)

    # Balanced 2-line population badge with generous margins
    draw_box(ax, x1 + 14, 160, w1 - 28, 50, 'white', C_BLUE_BORDER, 1.2, 6, zorder=2)
    ax.text(x1 + w1/2, 160 + 34, "Total Benchmark Instances", ha='center', va='center',
            color=C_BLUE, fontweight='bold', fontsize=8.6, zorder=3)
    ax.text(x1 + w1/2, 160 + 15, "N = 57,056 Audited Records", ha='center', va='center',
            color=C_DARK, fontweight='bold', fontsize=9.2, zorder=3)

    # Multiply 1
    ax.text(x1 + w1 + 16, y_card + h_card/2, "×", ha='center', va='center',
            fontsize=26, fontweight='bold', color=C_DARK)

    # Factor 2: Models
    x2, w2 = x1 + w1 + 32, 215
    draw_box(ax, x2, y_card, w2, h_card, C_PURPLE_LIGHT, C_PURPLE_BORDER, 1.5, 10)
    draw_box(ax, x2, top_y - 38, w2, 38, C_PURPLE, C_PURPLE, 0, 8)
    ax.text(x2 + w2/2, top_y - 19, "FACTOR 2: MODELS (2)", ha='center', va='center',
            color='white', fontweight='bold', fontsize=10.5)

    m_cards = [
        ("Logistic Regression", "• Linear decision boundary\n• L2 regularized (C=1.0)\n• Solver: liblinear\n• 18 canonical conditions", top_y - 38 - 20 - 165, 165),
        ("Random Forest", "• Non-linear tree ensemble\n• 100 decision trees\n• Max tree depth: 10\n• 18 canonical conditions", top_y - 38 - 20 - 165 - 25 - 165, 165)
    ]
    for title, desc, yc, hc in m_cards:
        draw_box(ax, x2 + 12, yc, w2 - 24, hc, 'white', C_PURPLE_BORDER, 1.0, 6)
        ax.text(x2 + 20, yc + hc - 14, title, ha='left', va='top', color=C_PURPLE, fontweight='bold', fontsize=9.8)
        ax.text(x2 + 20, yc + hc - 36, desc, ha='left', va='top', color=C_DARK, fontsize=8.6, linespacing=1.4)

    # Multiply 2
    ax.text(x2 + w2 + 16, y_card + h_card/2, "×", ha='center', va='center',
            fontsize=26, fontweight='bold', color=C_DARK)

    # Factor 3: Mitigations
    x3, w3 = x2 + w2 + 32, 225
    draw_box(ax, x3, y_card, w3, h_card, C_GREEN_LIGHT, C_GREEN_BORDER, 1.5, 10)
    draw_box(ax, x3, top_y - 38, w3, 38, C_GREEN, C_GREEN, 0, 8)
    ax.text(x3 + w3/2, top_y - 19, "FACTOR 3: MITIGATION (2)", ha='center', va='center',
            color='white', fontweight='bold', fontsize=10.2)

    mit_cards = [
        ("Correlation Remover", "• Pre-processing mitigation\n• Linear projection decorr.\n• Removes sensitive link\n• 18 canonical conditions", top_y - 38 - 20 - 165, 165),
        ("Threshold Optimizer", "• Post-processing mitigation\n• Group-specific thresholds\n• Equalizes selection rates\n• 18 canonical conditions", top_y - 38 - 20 - 165 - 25 - 165, 165)
    ]
    for title, desc, yc, hc in mit_cards:
        draw_box(ax, x3 + 12, yc, w3 - 24, hc, 'white', C_GREEN_BORDER, 1.0, 6)
        ax.text(x3 + 20, yc + hc - 14, title, ha='left', va='top', color=C_GREEN, fontweight='bold', fontsize=9.8)
        ax.text(x3 + 20, yc + hc - 36, desc, ha='left', va='top', color=C_DARK, fontsize=8.6, linespacing=1.4)

    # Multiply 3
    ax.text(x3 + w3 + 16, y_card + h_card/2, "×", ha='center', va='center',
            fontsize=26, fontweight='bold', color=C_DARK)

    # Factor 4: Seeds (evenly spaced to align gracefully with bottom cards)
    x4, w4 = x3 + w3 + 32, 145
    draw_box(ax, x4, y_card, w4, h_card, '#EDF2F7', C_GRAY_BORDER, 1.5, 10)
    draw_box(ax, x4, top_y - 38, w4, 38, C_GRAY, C_GRAY, 0, 8)
    ax.text(x4 + w4/2, top_y - 19, "SEEDS (3)", ha='center', va='center',
            color='white', fontweight='bold', fontsize=10.5)

    s_cards = [
        ("Seed 42", "Split / Train 1", 427),
        ("Seed 123", "Split / Train 2", 302),
        ("Seed 456", "Split / Train 3", 177)
    ]
    for title, desc, yc in s_cards:
        draw_box(ax, x4 + 12, yc, w4 - 24, 95, 'white', C_GRAY_BORDER, 1.0, 6)
        ax.text(x4 + w4/2, yc + 95 - 20, title, ha='center', va='top', color=C_DARK, fontweight='bold', fontsize=10.0)
        ax.text(x4 + w4/2, yc + 95 - 50, desc, ha='center', va='top', color='#4A5568', fontsize=8.8)

    # Equals
    ax.text(x4 + w4 + 18, y_card + h_card/2, "=", ha='center', va='center',
            fontsize=30, fontweight='bold', color=C_DARK)

    # Output: Canonical Matrix
    x5, w5 = x4 + w4 + 36, 215
    draw_box(ax, x5, y_card, w5, h_card, C_RED_LIGHT, C_RED_BORDER, 1.5, 10)
    draw_box(ax, x5, top_y - 38, w5, 38, C_RED, C_RED, 0, 8)
    ax.text(x5 + w5/2, top_y - 19, "CANONICAL MATRIX", ha='center', va='center',
            color='white', fontweight='bold', fontsize=10.5)

    # Stats card 1
    draw_box(ax, x5 + 12, top_y - 38 - 18 - 175, w5 - 24, 175, 'white', C_RED_BORDER, 1.0, 6)
    ax.text(x5 + w5/2, top_y - 75, "36", ha='center', va='center', color=C_RED, fontweight='bold', fontsize=34)
    ax.text(x5 + w5/2, top_y - 105, "Canonical Conditions", ha='center', va='center', color=C_DARK, fontweight='bold', fontsize=9.8)
    ax.plot([x5 + 24, x5 + w5 - 24], [top_y - 120, top_y - 120], color='#E2E8F0', lw=1)
    ax.text(x5 + w5/2, top_y - 142, "72 Paired Runs", ha='center', va='center', color=C_PURPLE, fontweight='bold', fontsize=12.5)
    ax.text(x5 + w5/2, top_y - 168, "36 Gemini + 36 Control\nSHA-256 Parity Verified", ha='center', va='center',
            color='#4A5568', fontsize=8.4, linespacing=1.2)

    # Subgroups card 2
    draw_box(ax, x5 + 12, y_card + 10, w5 - 24, 170, 'white', C_GRAY_BORDER, 1.0, 6)
    ax.text(x5 + w5/2, y_card + 170 - 12, "Subgroup Stratification", ha='center', va='top', color=C_DARK, fontweight='bold', fontsize=9.5)
    ax.text(x5 + 20, y_card + 170 - 36,
            "• Adult Census: 12 conditions\n"
            "• COMPAS: 12 conditions\n"
            "• German Credit: 12 conditions\n"
            "• LogReg / RF: 18 each\n"
            "• Directional Eval: 23 pairs",
            ha='left', va='top', color=C_DARK, fontsize=8.4, linespacing=1.35)

    # ------------------ BOTTOM REMEDIATION CARD ------------------
    draw_box(ax, x1, 15, W - 50, 100, '#FFFBF0', '#DD6B20', 1.5, 8)
    ax.text(x1 + 22, 15 + 100 - 14,
            "Methodological Integrity: Quarantine of Legacy Retry Artifacts ($N=43 \\to N=36$)",
            ha='left', va='top', color='#C05621', fontweight='bold', fontsize=10.5)
    ax.text(x1 + 22, 15 + 100 - 38,
            "• Prior uncalibrated runs contained 7 duplicate retries ($N=43$), which inflated sample size and artificially distorted directional significance ($p = 0.0396$).\n"
            "• Remediation quarantined all 7 retry artifacts into research/results/legacy_retries/, restoring strict 100% full-factorial balance ($N=36$ conditions).\n"
            "• On the true canonical matrix ($N=23$ evaluable pairs), directional difference is non-significant ($p = 0.1979$), preventing false scientific claims.",
            ha='left', va='top', color=C_DARK, fontsize=8.6, linespacing=1.4)

    save_figure(fig, 'fig02_experimental_matrix')


# ==============================================================================
# FIGURE 3: Claim-Level Evaluation Framework
# ==============================================================================
def generate_figure_3():
    """Generates Figure 3: Claim-Level Evaluation Framework."""
    W, H = 1360, 680
    fig, ax = plt.subplots(figsize=(17.0, 8.5), dpi=100, facecolor='white')
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.axis('off')

    col_w = 300
    top_y = 640
    card_h = 600
    y_base = top_y - card_h  # 40

    # ------------------ STEP 1: Input Narrative ------------------
    x1 = 35
    draw_box(ax, x1, y_base, col_w, card_h, C_PURPLE_LIGHT, C_PURPLE_BORDER, 1.5, 10)
    draw_box(ax, x1, top_y - 40, col_w, 40, C_PURPLE, C_PURPLE, 0, 8)
    ax.text(x1 + col_w/2, top_y - 20, "1. EXPLANATION INPUT", ha='center', va='center',
            color='white', fontweight='bold', fontsize=11.5)

    # Narrative excerpt
    box_n_h = 245
    box_n_y = 350
    draw_box(ax, x1 + 12, box_n_y, col_w - 24, box_n_h, 'white', C_PURPLE_BORDER, 1.0, 6)
    ax.text(x1 + col_w/2, box_n_y + box_n_h - 14, "Audit Narrative Text", ha='center', va='top',
            color=C_PURPLE, fontweight='bold', fontsize=10.5)

    # Dedicated prominent banner for illustrative demonstration with ample clearance
    draw_box(ax, x1 + 22, 524, col_w - 44, 24, '#FFFBF0', '#DD6B20', 1.0, 5)
    ax.text(x1 + col_w/2, 536, "METHODOLOGY DEMONSTRATION", ha='center', va='center',
            color='#C05621', fontweight='bold', fontsize=8.0)

    # Quote box inside with generous margins and explicit synthetic attribution
    draw_box(ax, x1 + 16, 360, col_w - 32, 150, C_PURPLE_LIGHT, '#D6BCFA', 0.8, 6)
    sample_text = (
        '"Baseline demographic\n'
        'parity difference was\n'
        '0.1895, but mitigation\n'
        'decreased disparity to\n'
        '0.0412, improving fairness\n'
        'substantially with 82.4%\n'
        'accuracy."'
    )
    ax.text(x1 + col_w/2, 496, sample_text, ha='center', va='top',
            color=C_DARK, fontstyle='italic', fontsize=8.4, linespacing=1.25)
    ax.text(x1 + col_w/2, 372, "Illustrative excerpt — not canonical data", ha='center', va='bottom',
            color='#744210', fontsize=7.6, fontweight='bold')

    # Segmentation details
    box_s_h = 285
    box_s_y = 50
    draw_box(ax, x1 + 12, box_s_y, col_w - 24, box_s_h, 'white', C_PURPLE_BORDER, 1.0, 6)
    ax.text(x1 + col_w/2, box_s_y + box_s_h - 14, "Boundary Segmentation", ha='center', va='top',
            color=C_PURPLE, fontweight='bold', fontsize=10.5)
    ax.text(x1 + 20, box_s_y + box_s_h - 36,
            "• Deterministic regex clause delimiter\n"
            "• Isolates independent assertions\n"
            "• Prevents cross-metric bleed\n"
            "• Preserves atomic assertion context",
            ha='left', va='top', color=C_DARK, fontsize=8.6, linespacing=1.35)

    ax.plot([x1 + 20, x1 + col_w - 20], [box_s_y + 140, box_s_y + 140], color='#E2E8F0', lw=1)
    ax.text(x1 + 20, box_s_y + 126,
            "Evaluated Corpus Statistics:\n"
            "• 36 Control Explanations\n"
            "• 36 Gemini 2.5 Explanations\n"
            "• 72 Total Full Documents\n"
            "• 1,306 Extracted Atomic Claims",
            ha='left', va='top', color=C_DARK, fontweight='bold', fontsize=8.4, linespacing=1.35)

    draw_arrow(ax, (x1 + col_w, top_y - 295), (x1 + col_w + 35, top_y - 295), lw=2.0)

    # ------------------ STEP 2: Taxonomy Classification ------------------
    x2 = x1 + col_w + 35  # 370
    draw_box(ax, x2, y_base, col_w, card_h, C_BLUE_LIGHT, C_BLUE_BORDER, 1.5, 10)
    draw_box(ax, x2, top_y - 40, col_w, 40, C_BLUE, C_BLUE, 0, 8)
    ax.text(x2 + col_w/2, top_y - 20, "2. CLAIM TAXONOMY", ha='center', va='center',
            color='white', fontweight='bold', fontsize=11.5)

    t_items = [
        ("1. Numerical Claims (1,125)", "Extracts numbers, percentages, ratios.\n109 unsupported (9.69% error rate)", C_BLUE, top_y - 40 - 15 - 90, 90),
        ("2. Directional Claims (118)", "Verbs: 'decreased', 'narrowed', 'widened'.\n4 unsupported ratio-transition\nsemantic mismatches (3.39%)", C_PURPLE, top_y - 40 - 15 - 90 - 12 - 98, 98),
        ("3. Fairness Interp. (29)", "Disparity narrative vs 4/5ths standard.\n29 supported (100.0% agreement)", C_GREEN, top_y - 40 - 15 - 90 - 12 - 98 - 12 - 86, 86),
        ("4. Performance Claims (19)", "Accuracy, utility, selection assertions.\n19 supported (100.0% agreement)", C_DARK, top_y - 40 - 15 - 90 - 12 - 98 - 12 - 86 - 12 - 86, 86),
        ("5. Subjective Magnitude (15)", "Unanchored adverbs ('substantially').\n15/15 UNDETERMINABLE (100%)", C_GRAY, top_y - 40 - 15 - 90 - 12 - 98 - 12 - 86 - 12 - 86 - 12 - 86, 86)
    ]
    for title, desc, col, yc, hc in t_items:
        draw_box(ax, x2 + 12, yc, col_w - 24, hc, 'white', col, 1.0, 6)
        ax.text(x2 + 20, yc + hc - 12, title, ha='left', va='top', color=col, fontweight='bold', fontsize=9.6)
        ax.text(x2 + 20, yc + hc - 34, desc, ha='left', va='top', color=C_DARK, fontsize=8.4, linespacing=1.3)

    draw_arrow(ax, (x2 + col_w, top_y - 295), (x2 + col_w + 35, top_y - 295), lw=2.0)

    # ------------------ STEP 3: State-Aware Matching ------------------
    x3 = x2 + col_w + 35  # 705
    draw_box(ax, x3, y_base, col_w, card_h, C_GREEN_LIGHT, C_GREEN_BORDER, 1.5, 10)
    draw_box(ax, x3, top_y - 40, col_w, 40, C_GREEN, C_GREEN, 0, 8)
    ax.text(x3 + col_w/2, top_y - 20, "3. EVIDENCE MATCHING", ha='center', va='center',
            color='white', fontweight='bold', fontsize=11.5)

    # State Resolution
    s_h = 145
    s_y = top_y - 40 - 15 - s_h  # 440
    draw_box(ax, x3 + 12, s_y, col_w - 24, s_h, 'white', C_GREEN_BORDER, 1.0, 6)
    ax.text(x3 + col_w/2, s_y + s_h - 14, "Audit State Resolution", ha='center', va='top',
            color=C_GREEN, fontweight='bold', fontsize=10.5)
    ax.text(x3 + 20, s_y + s_h - 36,
            "• Baseline State ($S_0$): unmitigated run\n"
            "• Mitigated State ($S_1$): post-mitigation run\n"
            "• Absolute Delta: $|S_1 - S_0|$\n"
            "• Signed Delta: $(S_1 - S_0)$",
            ha='left', va='top', color=C_DARK, fontsize=8.8, linespacing=1.35)

    # Evidence Filtering
    e_h = 175
    e_y = s_y - 12 - e_h  # 253
    draw_box(ax, x3 + 12, e_y, col_w - 24, e_h, 'white', C_GREEN_BORDER, 1.0, 6)
    ax.text(x3 + col_w/2, e_y + e_h - 14, "Candidate Evidence Filtering", ha='center', va='top',
            color=C_GREEN, fontweight='bold', fontsize=10.5)
    ax.text(x3 + 20, e_y + e_h - 36,
            "• Disparities: DPD, EOD, Disparate Impact\n"
            "• Performance: Accuracy, Selection Rate\n"
            "• Attributions: Top-5 SHAP values\n"
            "• Group pairs: Privileged vs Unprivileged",
            ha='left', va='top', color=C_DARK, fontsize=8.8, linespacing=1.35)
    ax.text(x3 + col_w/2, e_y + 14, "Maps textual terms to canonical JSON keys", ha='center', va='bottom',
            color='#4A5568', fontstyle='italic', fontsize=8.4)

    # Unsupported Pattern Filter
    u_h = 160
    u_y = e_y - 12 - u_h  # 81
    draw_box(ax, x3 + 12, u_y, col_w - 24, u_h, C_RED_LIGHT, C_RED_BORDER, 1.0, 6)
    ax.text(x3 + col_w/2, u_y + u_h - 14, "Unsupported Pattern Filter", ha='center', va='top',
            color=C_RED, fontweight='bold', fontsize=10.5)
    ax.text(x3 + 20, u_y + u_h - 36,
            "• Causal assertions: 'caused by', 'led to'\n"
            "• Compliance: 'completely fair', 'legal'\n"
            "• Unanchored delta extrapolations",
            ha='left', va='top', color=C_DARK, fontsize=8.8, linespacing=1.35)
    draw_box(ax, x3 + 20, u_y + 14, col_w - 40, 28, 'white', C_RED_BORDER, 1.0, 4)
    ax.text(x3 + col_w/2, u_y + 28, "Flags 113 Unsupported Assertions", ha='center', va='center',
            color=C_RED, fontweight='bold', fontsize=8.8)

    draw_arrow(ax, (x3 + col_w, top_y - 295), (x3 + col_w + 35, top_y - 295), lw=2.0)

    # ------------------ STEP 4: Verification Rules & Verdicts ------------------
    x4 = x3 + col_w + 35  # 1040
    draw_box(ax, x4, y_base, col_w, card_h, '#F7FAFC', C_GRAY_BORDER, 1.5, 10)
    draw_box(ax, x4, top_y - 40, col_w, 40, C_DARK, C_DARK, 0, 8)
    ax.text(x4 + col_w/2, top_y - 20, "4. DETERMINISTIC RULES", ha='center', va='center',
            color='white', fontweight='bold', fontsize=11.5)

    # Rule 1: Numerical
    r1_h = 120
    r1_y = top_y - 40 - 15 - r1_h  # 465
    draw_box(ax, x4 + 12, r1_y, col_w - 24, r1_h, 'white', C_BLUE_BORDER, 1.0, 6)
    ax.text(x4 + 20, r1_y + r1_h - 14, "Numerical Rule:", ha='left', va='top', color=C_BLUE, fontweight='bold', fontsize=9.6)
    ax.text(x4 + 20, r1_y + r1_h - 34, "|v_claim - v_truth| ≤ 0.015\nOR |v_claim - v_truth|/|v_truth| ≤ 5%",
            ha='left', va='top', color=C_DARK, fontsize=8.2, family='monospace', linespacing=1.25)
    ax.text(x4 + 20, r1_y + r1_h - 72,
            "• Accepts rounding (e.g. 0.1895 → 0.190)\n"
            "• Flags excessive drift (e.g. 0.2445 → 0.2)",
            ha='left', va='top', color='#4A5568', fontsize=8.0, linespacing=1.22)

    # Rule 2: Directional
    r2_h = 120
    r2_y = r1_y - 12 - r2_h  # 333
    draw_box(ax, x4 + 12, r2_y, col_w - 24, r2_h, 'white', C_PURPLE_BORDER, 1.0, 6)
    ax.text(x4 + 20, r2_y + r2_h - 14, "Directional Rule:", ha='left', va='top', color=C_PURPLE, fontweight='bold', fontsize=9.6)
    ax.text(x4 + 20, r2_y + r2_h - 34, "sign(asserted_dir) == sign(S₁ - S₀)",
            ha='left', va='top', color=C_DARK, fontsize=8.2, family='monospace')
    ax.text(x4 + 20, r2_y + r2_h - 54,
            "• Verifies widening vs narrowing disparity\n"
            "• 4 ratio-transition semantic mismatches\n"
            "  identified in canonical dataset\n"
            "• 94.18% faithfulness (p = 0.1979 n.s.)",
            ha='left', va='top', color='#4A5568', fontsize=7.8, linespacing=1.24)

    # Rule 3: Magnitude & Undetermined
    r3_h = 95
    r3_y = r2_y - 12 - r3_h  # 226
    draw_box(ax, x4 + 12, r3_y, col_w - 24, r3_h, 'white', C_GRAY_BORDER, 1.0, 6)
    ax.text(x4 + 20, r3_y + r3_h - 14, "Magnitude & Scoping Rule:", ha='left', va='top', color=C_GRAY, fontweight='bold', fontsize=9.6)
    ax.text(x4 + 20, r3_y + r3_h - 34, "Unanchored modifiers → UNDET.",
            ha='left', va='top', color=C_GRAY, fontsize=8.2, family='monospace')
    ax.text(x4 + 20, r3_y + r3_h - 54,
            "• Refuses subjective guesswork\n"
            "• Prioritizes precision over recall",
            ha='left', va='top', color='#4A5568', fontsize=8.0, linespacing=1.22)

    # Verdicts Card
    v_h = 145
    v_y = r3_y - 14 - v_h  # 67
    draw_box(ax, x4 + 12, v_y, col_w - 24, v_h, 'white', C_DARK, 1.2, 6)
    ax.text(x4 + col_w/2, v_y + v_h - 14, "Atomic Output Verdicts", ha='center', va='top',
            color=C_DARK, fontweight='bold', fontsize=10.2)

    # 3 Badges
    draw_box(ax, x4 + 18, v_y + 88, 95, 26, C_GREEN_LIGHT, C_GREEN_BORDER, 0.8, 4)
    ax.text(x4 + 65, v_y + 101, "SUPPORTED", ha='center', va='center', color=C_GREEN, fontweight='bold', fontsize=8.0)
    ax.text(x4 + 124, v_y + 101, "Grounded in truth", ha='left', va='center', color=C_DARK, fontsize=8.4)

    draw_box(ax, x4 + 18, v_y + 52, 105, 26, C_RED_LIGHT, C_RED_BORDER, 0.8, 4)
    ax.text(x4 + 70, v_y + 65, "UNSUPPORTED", ha='center', va='center', color=C_RED, fontweight='bold', fontsize=8.0)
    ax.text(x4 + 134, v_y + 65, "Deviates from truth", ha='left', va='center', color=C_DARK, fontsize=8.4)

    draw_box(ax, x4 + 18, v_y + 16, 120, 26, '#EDF2F7', C_GRAY_BORDER, 0.8, 4)
    ax.text(x4 + 78, v_y + 29, "UNDETERMINABLE", ha='center', va='center', color=C_GRAY, fontweight='bold', fontsize=7.8)
    ax.text(x4 + 148, v_y + 29, "Unverified adverb", ha='left', va='center', color=C_DARK, fontsize=8.4)

    save_figure(fig, 'fig03_claim_evaluation_framework')


# ==============================================================================
# FIGURE 8: Authentic Evidence-to-Claim Verification Examples
# ==============================================================================
def generate_figure_8():
    """Generates Figure 8: Evidence-to-Claim Verification Examples."""
    W, H = 1260, 640
    fig, ax = plt.subplots(figsize=(16.2, 8.2), dpi=100, facecolor='white')
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.axis('off')

    panel_w = 585
    top_y = 600
    panel_h = 560
    y_base = top_y - panel_h  # 40

    # ================== PANEL A: ROUNDING EXAMPLE (SUPPORTED) ==================
    xa = 25
    draw_box(ax, xa, y_base, panel_w, panel_h, C_GREEN_LIGHT, C_GREEN_BORDER, 1.5, 10)
    draw_box(ax, xa, top_y - 40, panel_w, 40, C_GREEN, C_GREEN, 0, 8)
    ax.text(xa + panel_w/2, top_y - 20, "(A) ACCEPTED ROUNDING EXAMPLE (SUPPORTED)",
            ha='center', va='center', color='white', fontweight='bold', fontsize=11.5)

    # Card A1: Ground Truth
    a1_h = 95
    a1_y = top_y - 40 - 15 - a1_h  # 450
    draw_box(ax, xa + 18, a1_y, panel_w - 36, a1_h, 'white', C_BLUE_BORDER, 1.2, 6)
    ax.text(xa + 30, a1_y + a1_h - 14, "Canonical Audit Ground Truth Evidence", ha='left', va='top',
            color=C_BLUE, fontweight='bold', fontsize=10.5)
    ax.text(xa + 30, a1_y + a1_h - 36,
            "• Metric: Demographic Parity Difference (DPD)\n"
            "• State: Baseline Disparity (unmitigated model)",
            ha='left', va='top', color=C_DARK, fontsize=8.8, linespacing=1.35)
    draw_box(ax, xa + panel_w - 185, a1_y + 16, 165, 62, C_BLUE_LIGHT, C_BLUE_BORDER, 1.0, 5)
    ax.text(xa + panel_w - 102, a1_y + 53, "Canonical Truth", ha='center', va='center', color=C_BLUE, fontsize=8.2, fontweight='bold')
    ax.text(xa + panel_w - 102, a1_y + 31, "v_truth = 0.1895", ha='center', va='center',
            color=C_BLUE, fontweight='bold', fontsize=9.8, family='monospace')

    draw_arrow(ax, (xa + panel_w/2, a1_y), (xa + panel_w/2, a1_y - 22), color='#718096', lw=1.8)

    # Card A2: Generated Text
    a2_h = 95
    a2_y = a1_y - 22 - a2_h  # 333
    draw_box(ax, xa + 18, a2_y, panel_w - 36, a2_h, 'white', C_PURPLE_BORDER, 1.2, 6)
    ax.text(xa + 30, a2_y + a2_h - 14, "Generative LLM Narrative Assertion", ha='left', va='top',
            color=C_PURPLE, fontweight='bold', fontsize=10.5)
    ax.text(xa + 30, a2_y + a2_h - 38,
            '"Baseline demographic parity difference was 0.190..."\n(Atomic assertion parsed as claim num_02)',
            ha='left', va='top', color=C_DARK, fontstyle='italic', fontsize=8.5, linespacing=1.3)
    draw_box(ax, xa + panel_w - 185, a2_y + 16, 165, 62, C_PURPLE_LIGHT, C_PURPLE_BORDER, 1.0, 5)
    ax.text(xa + panel_w - 102, a2_y + 53, "Extracted Value", ha='center', va='center', color=C_PURPLE, fontsize=8.2, fontweight='bold')
    ax.text(xa + panel_w - 102, a2_y + 31, "v_claim = 0.190", ha='center', va='center',
            color=C_PURPLE, fontweight='bold', fontsize=9.8, family='monospace')

    draw_arrow(ax, (xa + panel_w/2, a2_y), (xa + panel_w/2, a2_y - 22), color='#718096', lw=1.8)

    # Card A3: Tolerance Verification
    a3_h = 145
    a3_y = a2_y - 22 - a3_h  # 166
    draw_box(ax, xa + 18, a3_y, panel_w - 36, a3_h, 'white', C_GREEN_BORDER, 1.2, 6)
    ax.text(xa + 30, a3_y + a3_h - 14, "Deterministic Tolerance Verification", ha='left', va='top',
            color=C_GREEN, fontweight='bold', fontsize=10.5)
    ax.text(xa + 30, a3_y + a3_h - 36, "Absolute Error: |0.190 - 0.1895| = 0.0005", ha='left', va='top', color=C_DARK, fontsize=9.2, family='monospace')
    ax.text(xa + 30, a3_y + a3_h - 58, "✔ 0.0005 ≤ 0.015 (Absolute Tolerance Window Satisfied)", ha='left', va='top', color=C_GREEN, fontweight='bold', fontsize=9.0)
    ax.text(xa + 30, a3_y + a3_h - 84, "Relative Error: 0.0005 / 0.1895 = 0.26%", ha='left', va='top', color=C_DARK, fontsize=9.2, family='monospace')
    ax.text(xa + 30, a3_y + a3_h - 106, "✔ 0.26% ≤ 5.0% (Relative Error Threshold Satisfied)", ha='left', va='top', color=C_GREEN, fontweight='bold', fontsize=9.0)

    draw_arrow(ax, (xa + panel_w/2, a3_y), (xa + panel_w/2, a3_y - 20), color='#718096', lw=1.8)

    # Card A4: Verdict
    a4_h = 58
    a4_y = 54
    draw_box(ax, xa + 18, a4_y, panel_w - 36, a4_h, C_GREEN, C_GREEN, 0, 6)
    ax.text(xa + panel_w/2, a4_y + 36, "CLASSIFICATION: SUPPORTED", ha='center', va='center',
            color='white', fontweight='bold', fontsize=12.0)
    ax.text(xa + panel_w/2, a4_y + 16, "Standard scientific rounding accepted under pre-defined tolerances.",
            ha='center', va='center', color='white', fontsize=8.8)

    # ================== PANEL B: FAILURE EXAMPLE (UNSUPPORTED) ==================
    xb = xa + panel_w + 40  # 650
    draw_box(ax, xb, y_base, panel_w, panel_h, C_RED_LIGHT, C_RED_BORDER, 1.5, 10)
    draw_box(ax, xb, top_y - 40, panel_w, 40, C_RED, C_RED, 0, 8)
    ax.text(xb + panel_w/2, top_y - 20, "(B) CANONICAL FAILURE EXAMPLE (UNSUPPORTED)",
            ha='center', va='center', color='white', fontweight='bold', fontsize=11.5)

    # Card B1: Ground Truth
    b1_h = 98
    b1_y = top_y - 40 - 15 - b1_h  # 447
    draw_box(ax, xb + 18, b1_y, panel_w - 36, b1_h, 'white', C_BLUE_BORDER, 1.2, 6)
    ax.text(xb + 28, b1_y + b1_h - 14, "Canonical Audit Ground Truth Evidence", ha='left', va='top',
            color=C_BLUE, fontweight='bold', fontsize=10.5)
    ax.text(xb + 28, b1_y + b1_h - 36,
            "• Condition: German Credit — Random Forest —\n"
            "  Threshold Optimizer — Seed 123\n"
            "• Metric: Baseline Equal Opportunity Difference",
            ha='left', va='top', color=C_DARK, fontsize=8.4, linespacing=1.28)
    draw_box(ax, xb + panel_w - 180, b1_y + 16, 160, 64, C_BLUE_LIGHT, C_BLUE_BORDER, 1.0, 5)
    ax.text(xb + panel_w - 100, b1_y + 53, "Canonical Truth", ha='center', va='center', color=C_BLUE, fontsize=8.2, fontweight='bold')
    ax.text(xb + panel_w - 100, b1_y + 31, "v_truth = 0.2445", ha='center', va='center',
            color=C_BLUE, fontweight='bold', fontsize=9.8, family='monospace')

    draw_arrow(ax, (xb + panel_w/2, b1_y), (xb + panel_w/2, b1_y - 22), color='#718096', lw=1.8)

    # Card B2: Generated Text
    b2_h = 95
    b2_y = b1_y - 22 - b2_h  # 333
    draw_box(ax, xb + 18, b2_y, panel_w - 36, b2_h, 'white', C_PURPLE_BORDER, 1.2, 6)
    ax.text(xb + 30, b2_y + b2_h - 14, "Generative LLM Narrative Assertion", ha='left', va='top',
            color=C_PURPLE, fontweight='bold', fontsize=10.5)
    ax.text(xb + 30, b2_y + b2_h - 38,
            '"Equal Opportunity Difference: Decreased from 0.2..."\n(Atomic assertion parsed as claim num_20)',
            ha='left', va='top', color=C_DARK, fontstyle='italic', fontsize=8.5, linespacing=1.3)
    draw_box(ax, xb + panel_w - 185, b2_y + 16, 165, 62, C_PURPLE_LIGHT, C_PURPLE_BORDER, 1.0, 5)
    ax.text(xb + panel_w - 102, b2_y + 53, "Extracted Value", ha='center', va='center', color=C_PURPLE, fontsize=8.2, fontweight='bold')
    ax.text(xb + panel_w - 102, b2_y + 31, "v_claim = 0.2", ha='center', va='center',
            color=C_PURPLE, fontweight='bold', fontsize=9.8, family='monospace')

    draw_arrow(ax, (xb + panel_w/2, b2_y), (xb + panel_w/2, b2_y - 22), color='#718096', lw=1.8)

    # Card B3: Tolerance Verification
    b3_h = 145
    b3_y = b2_y - 22 - b3_h  # 166
    draw_box(ax, xb + 18, b3_y, panel_w - 36, b3_h, 'white', C_RED_BORDER, 1.2, 6)
    ax.text(xb + 30, b3_y + b3_h - 14, "Deterministic Tolerance Verification", ha='left', va='top',
            color=C_RED, fontweight='bold', fontsize=10.5)
    ax.text(xb + 30, b3_y + b3_h - 36, "Absolute Error: |0.2 - 0.2445| = 0.0445", ha='left', va='top', color=C_DARK, fontsize=9.2, family='monospace')
    ax.text(xb + 30, b3_y + b3_h - 58, "✘ 0.0445 > 0.015 (Exceeds Absolute Tolerance Window)", ha='left', va='top', color=C_RED, fontweight='bold', fontsize=9.0)
    ax.text(xb + 30, b3_y + b3_h - 84, "Relative Error: 0.0445 / 0.2445 = 18.20%", ha='left', va='top', color=C_DARK, fontsize=9.2, family='monospace')
    ax.text(xb + 30, b3_y + b3_h - 106, "✘ 18.20% > 5.0% (Exceeds Relative Error Threshold)", ha='left', va='top', color=C_RED, fontweight='bold', fontsize=9.0)

    draw_arrow(ax, (xb + panel_w/2, b3_y), (xb + panel_w/2, b3_y - 20), color='#718096', lw=1.8)

    # Card B4: Verdict
    b4_h = 58
    b4_y = 54
    draw_box(ax, xb + 18, b4_y, panel_w - 36, b4_h, C_RED, C_RED, 0, 6)
    ax.text(xb + panel_w/2, b4_y + 36, "CLASSIFICATION: UNSUPPORTED", ha='center', va='center',
            color='white', fontweight='bold', fontsize=12.0)
    ax.text(xb + panel_w/2, b4_y + 16, "Excessive truncation distorts metric fidelity beyond scientific bounds.",
            ha='center', va='center', color='white', fontsize=8.8)

    save_figure(fig, 'fig08_evidence_claim_example')


if __name__ == '__main__':
    print("Generating Figure 1 (Research Framework)...")
    generate_figure_1()

    print("Generating Figure 2 (Experimental Matrix)...")
    generate_figure_2()

    print("Generating Figure 3 (Claim-Level Evaluation Framework)...")
    generate_figure_3()

    print("Generating Figure 8 (Evidence-to-Claim Verification Examples)...")
    generate_figure_8()

    print("Structural diagrams generation complete.")
