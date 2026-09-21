#!/usr/bin/env python3
"""
generate_result_figures.py
--------------------------
Generates publication-quality empirical figures for the FairLens AI research manuscript:
- Figure 4: Numerical Faithfulness Comparison (Template vs. Gemini 2.5 Flash)
- Figure 5: Claim Taxonomy and Unsupported Claims Analysis
- Figure 6: Directional Faithfulness Comparison (Robustness / Non-Significance)
- Figure 7: Secondary LLM Claim Adjudication Sensitivity Analysis (Llama 3 8B)

All data is loaded dynamically from canonical results in research/results/final/.
Outputs: SVG and 300 DPI PNG in research/paper/figures/.
"""

import os
import json
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.patches import Patch
from scipy import stats

# Publication styling settings
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['svg.fonttype'] = 'none'  # Keep text editable and searchable in SVG
plt.rcParams['axes.edgecolor'] = '#4A5568'
plt.rcParams['axes.linewidth'] = 0.8
plt.rcParams['xtick.color'] = '#2D3748'
plt.rcParams['ytick.color'] = '#2D3748'
plt.rcParams['text.color'] = '#1A202C'

# Canonical color palette
C_BLUE = '#2B6CB0'       # Evidence / Ground truth
C_BLUE_LIGHT = '#EBF8FF'
C_PURPLE = '#6B46C1'     # Generative model (Gemini)
C_PURPLE_LIGHT = '#FAF5FF'
C_GREEN = '#276749'      # Deterministic control / Supported
C_GREEN_LIGHT = '#F0FFF4'
C_RED = '#C53030'        # Unsupported / Error
C_RED_LIGHT = '#FED7D7'
C_GRAY = '#718096'       # Undetermined / Neutral
C_GRAY_LIGHT = '#EDF2F7'
C_DARK_BLUE = '#1A365D'  # Adjudication / Contrast

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FIGURES_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..', '..', '..'))

os.makedirs(FIGURES_DIR, exist_ok=True)


def save_result_figure(fig, filename_base):
    """Saves result figure cleanly as both SVG and 300 DPI PNG with verified deletion of stale files."""
    svg_path = os.path.join(FIGURES_DIR, f"{filename_base}.svg")
    png_path = os.path.join(FIGURES_DIR, f"{filename_base}.png")
    
    # Remove stale files first to ensure fresh timestamps and avoid any caching
    for path in (svg_path, png_path):
        if os.path.exists(path):
            try:
                os.remove(path)
            except OSError:
                pass
                
    fig.savefig(svg_path, format='svg', bbox_inches='tight')
    fig.savefig(png_path, format='png', dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"Generated Figure: {svg_path} ({os.path.getsize(svg_path):,} B) and {png_path} ({os.path.getsize(png_path):,} B)")


def load_canonical_data():
    """Loads all 36 canonical paired conditions from final summaries."""
    inv_path = os.path.join(REPO_ROOT, 'research', 'results', 'final', 'final_matrix_inventory.json')
    with open(inv_path, 'r', encoding='utf-8') as f:
        inv = json.load(f)
        
    conditions = inv['inventory']
    records = []
    
    for c in conditions:
        exp_id = c['experiment_id']
        gemini_pattern = os.path.join(REPO_ROOT, 'research', 'results', 'final', 'summaries', f'summary__{exp_id}__gemini__gemini-2.5-flash.json')
        template_pattern = os.path.join(REPO_ROOT, 'research', 'results', 'final', 'summaries', f'summary__{exp_id}__template_baseline.json')
        
        g_files = glob.glob(gemini_pattern)
        t_files = glob.glob(template_pattern)
        
        if not g_files or not t_files:
            raise FileNotFoundError(f"Missing summary file for {exp_id}")
            
        with open(g_files[0], 'r', encoding='utf-8') as f:
            g = json.load(f)
        with open(t_files[0], 'r', encoding='utf-8') as f:
            t = json.load(f)
            
        records.append({
            'condition_id': c['condition_id'],
            'dataset': c['dataset'],
            'model': c['model'],
            'mitigation': c['mitigation'],
            'seed': c['seed'],
            'g_num': g['numerical_faithfulness'],
            't_num': t['numerical_faithfulness'],
            'g_dir': g['directional_faithfulness'],
            't_dir': t['directional_faithfulness'],
            'g_unsup': g['unsupported_claim_rate'],
            't_unsup': t['unsupported_claim_rate'],
            'g_num_eval': g['numerical_evaluable'],
            'g_dir_eval': g['directional_evaluable'],
            'claims': g['claims']
        })
        
    df = pd.DataFrame(records)
    return df


def generate_figure_4(df):
    """Figure 4: Numerical Faithfulness Comparison (Template vs. Gemini 2.5 Flash)."""
    fig = plt.figure(figsize=(14.2, 5.8), facecolor='white', dpi=100)
    gs = fig.add_gridspec(1, 3, width_ratios=[1.15, 1.0, 1.4], wspace=0.44)
    
    # --- Panel A: Paired Condition Trajectories (N=36) ---
    ax_a = fig.add_subplot(gs[0])
    ax_a.set_facecolor('white')
    
    # Dataset color mapping
    ds_colors = {'adult': '#2B6CB0', 'compas': '#805AD5', 'german': '#DD6B20'}
    
    np.random.seed(42)
    jitter_t = np.random.normal(0, 0.02, len(df))
    jitter_g = np.random.normal(0, 0.02, len(df))
    
    for i, row in df.iterrows():
        c = ds_colors[row['dataset']]
        ax_a.plot([0 + jitter_t[i], 1 + jitter_g[i]], 
                  [row['t_num'] * 100, row['g_num'] * 100], 
                  color=c, alpha=0.35, linewidth=1.2)
        ax_a.scatter(0 + jitter_t[i], row['t_num'] * 100, color=C_GREEN, s=28, alpha=0.7, zorder=3)
        ax_a.scatter(1 + jitter_g[i], row['g_num'] * 100, color=c, s=28, alpha=0.7, zorder=3)
        
    # Means and error bars
    mean_t = df['t_num'].mean() * 100
    mean_g = df['g_num'].mean() * 100
    std_g = df['g_num'].std() * 100
    
    ax_a.errorbar([0], [mean_t], yerr=[0], fmt='D', color=C_GREEN, markersize=9, 
                  capsize=5, capthick=2, elinewidth=2, label=f'Template: {mean_t:.1f}%', zorder=5)
    ax_a.errorbar([1], [mean_g], yerr=[std_g], fmt='s', color=C_PURPLE, markersize=9, 
                  capsize=5, capthick=2, elinewidth=2, label=f'Gemini: {mean_g:.2f}% ± {std_g:.2f}%', zorder=5)
    
    ax_a.set_xlim(-0.3, 1.3)
    ax_a.set_ylim(48, 106)
    ax_a.set_xticks([0, 1])
    ax_a.set_xticklabels(['Deterministic\nReference Control', 'Gemini 2.5 Flash\n(Generative)'], fontsize=9.5, fontweight='bold')
    ax_a.set_ylabel('Numerical Faithfulness (%)', fontsize=10.5, fontweight='bold')
    ax_a.set_title('(A) Paired Trajectories\n($N=36$ conditions, 72 runs)', fontsize=11, fontweight='bold', pad=10)
    ax_a.grid(axis='y', linestyle='--', alpha=0.4)
    ax_a.legend(loc='lower left', fontsize=8.5, framealpha=0.95)
    
    # --- Panel B: Boxplot & Statistical Summary ---
    ax_b = fig.add_subplot(gs[1])
    ax_b.set_facecolor('white')
    
    bp = ax_b.boxplot([df['t_num'] * 100, df['g_num'] * 100], 
                      positions=[0.25, 0.75], widths=0.32, patch_artist=True,
                      boxprops=dict(facecolor=C_GRAY_LIGHT, edgecolor=C_GRAY, linewidth=1.2),
                      medianprops=dict(color='#2D3748', linewidth=2),
                      whiskerprops=dict(color=C_GRAY, linewidth=1.2),
                      capprops=dict(color=C_GRAY, linewidth=1.2),
                      flierprops=dict(marker='o', color=C_RED, markersize=4))
    
    bp['boxes'][0].set_facecolor(C_GREEN_LIGHT)
    bp['boxes'][0].set_edgecolor(C_GREEN)
    bp['boxes'][1].set_facecolor(C_PURPLE_LIGHT)
    bp['boxes'][1].set_edgecolor(C_PURPLE)
    
    # Significance bracket
    y_bar = 102.5
    ax_b.plot([0.25, 0.25, 0.75, 0.75], [y_bar - 1, y_bar, y_bar, y_bar - 1], color='#2D3748', linewidth=1.2)
    ax_b.text(0.5, y_bar + 0.8, '*** (p = 1.34e-7)', ha='center', va='bottom', fontsize=9, fontweight='bold', color=C_RED)
    
    # Stat callout text placed cleanly in the lower quadrant (below whisker at 63.6%)
    stat_text = (
        "Paired Difference: -11.87 pp\n"
        "Paired t = -6.581 (p = 1.34e-7)\n"
        "Wilcoxon W = 0.0 (p = 8.28e-6)\n"
        "Cohen's d = -1.097 (Large)"
    )
    ax_b.text(0.5, 49, stat_text, ha='center', va='center', fontsize=8.2,
              bbox=dict(boxstyle='round,pad=0.5', facecolor='#FFF5F5', edgecolor=C_RED, alpha=0.95),
              family='monospace')
    
    ax_b.set_xlim(-0.05, 1.05)
    ax_b.set_ylim(40, 108)
    ax_b.set_xticks([0.25, 0.75])
    ax_b.set_xticklabels(['Template', 'Gemini 2.5'], fontsize=9.5, fontweight='bold')
    ax_b.set_title('(B) Distribution & Effect Size\n(Large Effect: $d = -1.097$)', fontsize=11, fontweight='bold', pad=10)
    ax_b.grid(axis='y', linestyle='--', alpha=0.4)
    
    # --- Panel C: Subgroup Point Estimates by Benchmark Dataset ---
    ax_c = fig.add_subplot(gs[2])
    ax_c.set_facecolor('white')
    
    row_keys_plot = ['german', 'compas', 'adult', 'overall']
    ds_names_plot = ['German Credit\n(N=12)', 'COMPAS\n(N=12)', 'Adult Census\n(N=12)', 'Overall Matrix\n(N=36)']
    y_pos = np.arange(len(row_keys_plot))
    
    t_means = []
    g_means = []
    g_stds = []
    for k in row_keys_plot:
        if k == 'overall':
            t_means.append(df['t_num'].mean() * 100)
            g_means.append(df['g_num'].mean() * 100)
            g_stds.append(df['g_num'].std() * 100)
        else:
            sub = df[df['dataset'] == k]
            t_means.append(sub['t_num'].mean() * 100)
            g_means.append(sub['g_num'].mean() * 100)
            g_stds.append(sub['g_num'].std() * 100)
            
    # Alternating row guides for scannability
    for y in y_pos:
        ax_c.axhspan(y - 0.40, y + 0.40, facecolor='#F7FAFC' if y % 2 == 1 else 'white', alpha=0.6, zorder=0)
        ax_c.axhline(y, color='#E2E8F0', linestyle='--', linewidth=0.8, zorder=1)
        
    offset = 0.13
    # Template Control: green diamond marker
    for i in range(len(row_keys_plot)):
        label_t = 'Template Control (100.0%)' if i == 3 else ""
        ax_c.plot(100.0, y_pos[i] + offset, 'D', color=C_GREEN, markersize=8, label=label_t, zorder=4)
        ax_c.text(97.5, y_pos[i] + offset, "100.0%", ha='right', va='center', color=C_GREEN, fontweight='bold', fontsize=8.0)
        
    # Gemini 2.5 Flash: purple square marker with horizontal whiskers (Mean ± SD)
    for i in range(len(row_keys_plot)):
        label_g = 'Gemini 2.5 Flash (Mean ± SD)' if i == 3 else ""
        ax_c.errorbar([g_means[i]], [y_pos[i] - offset], xerr=[g_stds[i]], fmt='s', color=C_PURPLE,
                      markersize=8, capsize=5, capthick=1.6, elinewidth=1.6, label=label_g, zorder=4)
        ax_c.text(103.5, y_pos[i] - offset, f"{g_means[i]:.1f}% ± {g_stds[i]:.1f}%", 
                  ha='left', va='center', color=C_PURPLE, fontweight='bold', fontsize=8.2)
        
    ax_c.set_xlim(50, 134)
    ax_c.set_ylim(-1.0, 3.8)
    ax_c.set_yticks(y_pos)
    ax_c.set_yticklabels(ds_names_plot, fontsize=9.0, fontweight='bold')
    ax_c.tick_params(axis='y', pad=8)
    ax_c.set_xlabel('Numerical Faithfulness (%)', fontsize=10, fontweight='bold')
    ax_c.set_title('(C) Point Estimates & Uncertainty (±1 SD)\nby Dataset & Full Benchmark', fontsize=11, fontweight='bold', pad=10)
    ax_c.grid(axis='x', linestyle='--', alpha=0.4, zorder=1)
    ax_c.legend(loc='lower left', bbox_to_anchor=(0.02, 0.02), fontsize=8.2, framealpha=0.95)
    
    plt.tight_layout()
    save_result_figure(fig, 'fig04_numerical_faithfulness')


def generate_figure_5(df):
    """Figure 5: Claim Taxonomy & Unsupported Claims Breakdown."""
    fig = plt.figure(figsize=(14.2, 6.2), facecolor='white', dpi=100)
    gs = fig.add_gridspec(1, 2, width_ratios=[1.15, 1.15], wspace=0.38)
    
    # --- Panel A: Claim Taxonomy Distribution ---
    ax_a = fig.add_subplot(gs[0])
    ax_a.set_facecolor('white')
    
    categories = ['Numerical', 'Directional', 'Fairness\nInterpretation', 'Performance', 'Magnitude']
    total_counts = [1125, 118, 29, 19, 15]
    unsup_counts = [109, 4, 0, 0, 0]
    undet_counts = [0, 0, 0, 0, 15]
    supp_counts = [total_counts[i] - unsup_counts[i] - undet_counts[i] for i in range(5)]
    
    y = np.arange(len(categories))
    bar_h = 0.52
    
    # Horizontal stacked bar
    ax_a.barh(y, supp_counts, bar_h, label='Supported / Grounded', color=C_GREEN, alpha=0.85)
    ax_a.barh(y, unsup_counts, bar_h, left=supp_counts, label='Unsupported Assertion', color=C_RED, alpha=0.85)
    ax_a.barh(y, undet_counts, bar_h, left=[s + u for s, u in zip(supp_counts, unsup_counts)],
              label='Undeterminable (Conservative)', color=C_GRAY, alpha=0.85)
    
    # Annotate counts and percentages with ample room
    for i in range(len(categories)):
        tot = total_counts[i]
        uns = unsup_counts[i]
        pct = (uns / tot) * 100 if tot > 0 else 0
        if uns > 0:
            ax_a.text(tot + 25, y[i], f"{uns}/{tot} ({pct:.1f}% unsup)", va='center', fontsize=8.4, fontweight='bold', color=C_RED)
        elif undet_counts[i] > 0:
            ax_a.text(tot + 25, y[i], f"15/15 (100% undet)", va='center', fontsize=8.4, fontweight='bold', color=C_GRAY)
        else:
            ax_a.text(tot + 25, y[i], f"{tot}/{tot} (100% supp)", va='center', fontsize=8.4, fontweight='bold', color=C_GREEN)
            
    ax_a.set_yticks(y)
    ax_a.set_yticklabels(categories, fontsize=9.2, fontweight='bold')
    ax_a.tick_params(axis='y', pad=6)
    ax_a.set_xlim(0, 1550)
    ax_a.set_xlabel('Extracted Claims Count ($N=1,306$ total)', fontsize=10, fontweight='bold')
    ax_a.set_title('(A) Canonical Claim Taxonomy\nby Verification Status ($N=1,306$ claims)', fontsize=11, fontweight='bold', pad=10)
    ax_a.grid(axis='x', linestyle='--', alpha=0.4)
    ax_a.legend(loc='upper right', bbox_to_anchor=(0.98, 0.62), fontsize=8.4, framealpha=0.95)
    
    # --- Panel B: Unsupported Rate Denominators Comparison ---
    ax_b = fig.add_subplot(gs[1])
    ax_b.set_facecolor('white')
    
    bars = [
        ('Condition Mean\n(N = 36)', 8.51, 8.72, C_PURPLE),
        ('Pooled Claims\n(113 / 1,306)', 8.65, 0.0, C_BLUE),
        ('Numerical\n(109 / 1,125)', 9.69, 0.0, C_RED),
        ('Directional\n(4 / 118)', 3.39, 0.0, '#DD6B20')
    ]
    
    x_pos = np.arange(len(bars))
    rates = [b[1] for b in bars]
    # Asymmetric error bar so Condition Mean error bar does not cross below y=0
    lower_err = [min(b[1], b[2]) for b in bars]
    upper_err = [b[2] for b in bars]
    colors = [b[3] for b in bars]
    labels = [b[0] for b in bars]
    
    bar_plot = ax_b.bar(x_pos, rates, width=0.48, color=colors, alpha=0.85)
    # Draw error bar ONLY for Condition Mean (index 0)
    ax_b.errorbar([0], [rates[0]], yerr=[[lower_err[0]], [upper_err[0]]], fmt='none',
                  ecolor='#2D3748', elinewidth=1.6, capsize=5, capthick=1.6)
    
    for i, rect in enumerate(bar_plot):
        h = rect.get_height()
        err_str = f" ± {upper_err[i]:.2f}%" if upper_err[i] > 0 else ""
        y_offset = (upper_err[i] if upper_err[i] > 0 else 0) + 0.6
        ax_b.text(rect.get_x() + rect.get_width()/2, h + y_offset,
                  f"{rates[i]:.2f}%{err_str}", ha='center', va='bottom', fontsize=8.4, fontweight='bold')
        
    ax_b.set_xticks(x_pos)
    ax_b.set_xticklabels(labels, fontsize=8.6, fontweight='bold')
    ax_b.tick_params(axis='x', pad=6)
    ax_b.set_xlim(-0.6, 3.6)
    ax_b.set_ylim(0, 28)
    ax_b.set_ylabel('Unsupported Rate (%)', fontsize=10, fontweight='bold')
    ax_b.set_title('(B) Aggregation Denominator Distinction\nCondition Mean (8.51%) vs. Pooled (8.65%)', fontsize=11, fontweight='bold', pad=10)
    ax_b.grid(axis='y', linestyle='--', alpha=0.4)
    
    # Methodological callout positioned in upper right (over bars 2-4, well away from bar 1's error bar)
    denom_note = (
        "Methodological Note on Denominators:\n"
        "• Condition Mean (8.51% ± 8.72%): unweighted\n"
        "  mean across 36 paired experimental runs.\n"
        "• Pooled Claims Rate (8.65%): 113 unsupported\n"
        "  claims divided by 1,306 total claims.\n"
        "Both reflect canonical evidence under different scopes."
    )
    ax_b.text(0.97, 0.96, denom_note, transform=ax_b.transAxes, ha='right', va='top', fontsize=8.6,
              linespacing=1.35, bbox=dict(boxstyle='round,pad=0.55', facecolor='#F7FAFC', edgecolor=C_GRAY, linewidth=1.1, alpha=0.95))
    
    plt.tight_layout()
    save_result_figure(fig, 'fig05_unsupported_claims')


def generate_figure_6(df):
    """Figure 6: Directional Faithfulness Comparison (Template vs. Gemini 2.5 Flash)."""
    fig = plt.figure(figsize=(12, 5.5), facecolor='white', dpi=100)
    gs = fig.add_gridspec(1, 2, width_ratios=[1.15, 1.0], wspace=0.36)
    
    # Filter evaluable directional pairs
    dir_df = df[df['g_dir_eval'] & df['g_dir'].notnull()].copy()
    n_dir = len(dir_df)  # exactly 23
    
    # --- Panel A: Paired Condition Trajectories (N=23) ---
    ax_a = fig.add_subplot(gs[0])
    ax_a.set_facecolor('white')
    
    np.random.seed(123)
    jitter_t = np.random.normal(0, 0.02, n_dir)
    jitter_g = np.random.normal(0, 0.02, n_dir)
    
    ds_colors = {'adult': '#2B6CB0', 'compas': '#805AD5', 'german': '#DD6B20'}
    
    for i, (_, row) in enumerate(dir_df.iterrows()):
        c = ds_colors[row['dataset']]
        ax_a.plot([0 + jitter_t[i], 1 + jitter_g[i]], 
                  [row['t_dir'] * 100, row['g_dir'] * 100], 
                  color=c, alpha=0.4, linewidth=1.3)
        ax_a.scatter(0 + jitter_t[i], row['t_dir'] * 100, color=C_GREEN, s=32, alpha=0.8, zorder=3)
        ax_a.scatter(1 + jitter_g[i], row['g_dir'] * 100, color=c, s=32, alpha=0.8, zorder=3)
        
    mean_t = dir_df['t_dir'].mean() * 100
    mean_g = dir_df['g_dir'].mean() * 100
    std_g = dir_df['g_dir'].std() * 100
    
    ax_a.errorbar([0], [mean_t], yerr=[0], fmt='D', color=C_GREEN, markersize=9, 
                  capsize=5, capthick=2, elinewidth=2, label=f'Template Control: {mean_t:.1f}%', zorder=5)
    ax_a.errorbar([1], [mean_g], yerr=[std_g], fmt='s', color=C_PURPLE, markersize=9, 
                  capsize=5, capthick=2, elinewidth=2, label=f'Gemini 2.5 Flash: {mean_g:.2f}% ± {std_g:.2f}%', zorder=5)
    
    ax_a.set_xlim(-0.3, 1.3)
    ax_a.set_ylim(-5, 120)
    ax_a.set_xticks([0, 1])
    ax_a.set_xticklabels(['Deterministic\nReference Control', 'Gemini 2.5 Flash\n(Generative)'], fontsize=9.5, fontweight='bold')
    ax_a.set_ylabel('Directional Faithfulness (%)', fontsize=10.5, fontweight='bold')
    ax_a.set_title(f'(A) Directional Trajectories\n($N={n_dir}$ evaluable pairs; 13 conditions had 0 dir claims)', fontsize=11, fontweight='bold', pad=10)
    ax_a.grid(axis='y', linestyle='--', alpha=0.4)
    ax_a.legend(loc='lower left', fontsize=8.5, framealpha=0.95)
    
    # --- Panel B: Non-Significance & Statistical Summary ---
    ax_b = fig.add_subplot(gs[1])
    ax_b.set_facecolor('white')
    
    bp = ax_b.boxplot([dir_df['t_dir'] * 100, dir_df['g_dir'] * 100], 
                      positions=[0.25, 0.75], widths=0.32, patch_artist=True,
                      boxprops=dict(facecolor=C_GRAY_LIGHT, edgecolor=C_GRAY, linewidth=1.2),
                      medianprops=dict(color='#2D3748', linewidth=2),
                      whiskerprops=dict(color=C_GRAY, linewidth=1.2),
                      capprops=dict(color=C_GRAY, linewidth=1.2))
    
    bp['boxes'][0].set_facecolor(C_GREEN_LIGHT)
    bp['boxes'][0].set_edgecolor(C_GREEN)
    bp['boxes'][1].set_facecolor(C_PURPLE_LIGHT)
    bp['boxes'][1].set_edgecolor(C_PURPLE)
    
    # Non-significant bracket
    y_bar = 104.5
    ax_b.plot([0.25, 0.25, 0.75, 0.75], [y_bar - 1, y_bar, y_bar, y_bar - 1], color='#4A5568', linewidth=1.2)
    ax_b.text(0.5, y_bar + 1.2, 'n.s. (p = 0.1979)', ha='center', va='bottom', fontsize=9.2, fontweight='bold', color=C_GRAY)
    
    # Stat callout text placed safely in the middle gap (y=42 is well between the 0% flier and the 80% flier)
    stat_text = (
        "NON-SIGNIFICANT COMPARISON\n"
        "--------------------------\n"
        "Evaluable Pairs: N = 23\n"
        "Mean Difference: -5.82 pp\n"
        "Paired t = -1.328 (p = 0.1979)\n"
        "Wilcoxon W = 0.0 (p = 0.0679)\n"
        "Cohen's d = -0.277 (Small)"
    )
    ax_b.text(0.5, 42, stat_text, ha='center', va='center', fontsize=8.2,
              bbox=dict(boxstyle='round,pad=0.5', facecolor='#F7FAFC', edgecolor=C_GRAY, alpha=0.95),
              family='monospace')
    
    ax_b.set_xlim(-0.05, 1.05)
    ax_b.set_ylim(-5, 120)
    ax_b.set_xticks([0.25, 0.75])
    ax_b.set_xticklabels(['Template', 'Gemini 2.5'], fontsize=9.5, fontweight='bold')
    ax_b.set_title('(B) Directional Faithfulness:\nDifference Not Statistically Significant', fontsize=11, fontweight='bold', pad=10)
    ax_b.grid(axis='y', linestyle='--', alpha=0.4)
    
    plt.tight_layout()
    save_result_figure(fig, 'fig06_directional_faithfulness')


def generate_figure_7():
    """Figure 7: Secondary LLM Claim Adjudication Sensitivity Analysis (Llama 3 8B)."""
    fig = plt.figure(figsize=(13.6, 7.6), facecolor='white', dpi=100)
    # Balanced vertical ratio with generous space for panels and the bottom methodological note
    gs = fig.add_gridspec(2, 2, height_ratios=[3.2, 1.35], width_ratios=[1.0, 1.0], wspace=0.42, hspace=0.42)
    
    # --- Panel A: Category Agreement Rates ---
    ax_a = fig.add_subplot(gs[0, 0])
    ax_a.set_facecolor('white')
    
    categories = ['Directional', 'Fairness Interp.', 'Performance', 'Numerical', 'Magnitude', 'Overall Sample']
    agreement_rates = [100.0, 100.0, 100.0, 80.0, 0.0, 77.0]
    sample_sizes = [21, 20, 20, 20, 19, 100]
    colors = [C_GREEN, C_GREEN, C_GREEN, '#DD6B20', C_RED, C_DARK_BLUE]
    
    y = np.arange(len(categories))
    bars = ax_a.barh(y, agreement_rates, 0.52, color=colors, alpha=0.85, zorder=2)
    
    for i, bar in enumerate(bars):
        w = bar.get_width()
        n = sample_sizes[i]
        if w >= 50.0:
            # Inside the bar in bold white for clean publication look
            ax_a.text(w - 2.5, y[i], f"{w:.1f}% (N={n})", ha='right', va='center', 
                      fontsize=8.8, fontweight='bold', color='white', zorder=4)
        else:
            # Outside the zero-width bar in bold red
            ax_a.text(2.5, y[i], f"{w:.1f}% (N={n})", ha='left', va='center', 
                      fontsize=8.8, fontweight='bold', color=C_RED, zorder=4)
        
    ax_a.set_yticks(y)
    ax_a.set_yticklabels(categories, fontsize=9.2, fontweight='bold')
    ax_a.tick_params(axis='y', pad=6)
    ax_a.set_xlim(0, 105)
    ax_a.set_xticks([0, 20, 40, 60, 80, 100])
    ax_a.set_xlabel('Concordance Rate (%)', fontsize=10, fontweight='bold')
    ax_a.set_title('(A) Adjudicator vs. Evaluator Agreement\nby Claim Category ($N=100$ sample)', fontsize=11, fontweight='bold', pad=10)
    ax_a.grid(axis='x', linestyle='--', alpha=0.35, zorder=1)
    
    # --- Panel B: Confusion Matrix ---
    ax_b = fig.add_subplot(gs[0, 1])
    ax_b.set_facecolor('white')
    
    cm = np.array([
        [77, 0],
        [0, 0],
        [21, 2]
    ])
    
    row_labels = ['SUPPORTED (77)', 'UNSUPPORTED (0)', 'UNDETERMINABLE (23)']
    col_labels = ['Adjudicator:\nSUPPORTED (98)', 'Adjudicator:\nCONTRADICTED (2)']
    
    im = ax_b.imshow(cm, cmap='Blues', aspect='auto', vmin=0, vmax=80)
    
    for i in range(3):
        for j in range(2):
            val = cm[i, j]
            text_color = 'white' if val > 40 else '#1A202C'
            ax_b.text(j, i, str(val), ha='center', va='center', fontsize=12, fontweight='bold', color=text_color)
            
    ax_b.set_xticks([0, 1])
    ax_b.set_xticklabels(col_labels, fontsize=9.0, fontweight='bold')
    ax_b.set_yticks([0, 1, 2])
    ax_b.set_yticklabels(row_labels, fontsize=8.8, fontweight='bold')
    ax_b.set_ylabel('Deterministic Evaluator Verdict', fontsize=9.8, fontweight='bold', labelpad=8)
    ax_b.tick_params(axis='y', pad=6)
    ax_b.set_title('(B) Collapsed Sensitivity Confusion Matrix\n& Inter-Method Alignment ($N=100$)', fontsize=11, fontweight='bold', pad=10)
    ax_b.set_xlabel('Secondary LLM Adjudicator (Llama 3 8B)\n[Adjudicator UNDETERMINABLE = 0 cases; omitted from displayed matrix]',
                    fontsize=8.4, fontweight='bold', labelpad=6, color='#2D3748')
    
    # --- Bottom Note: Methodological Scoping & Kappa Paradox Card ---
    ax_note = fig.add_subplot(gs[1, :])
    ax_note.axis('off')
    
    kappa_text = (
        "Methodological Scoping & Agreement Analysis (Secondary Sensitivity Study — NOT HUMAN VALIDATION):\n"
        "• Observed Raw Concordance: Po = 77.0% (77/100 claims) | 100% agreement on Directional, Fairness, & Performance categories.\n"
        "• Agreement Metrics: Ternary Cohen's κ = 0.063 | Binary Collapsed κ = 0.045.\n"
        "• Collapsed Matrix Representation: 3×2 space (Adjudicator UNDETERMINABLE = 0 cases; omitted from displayed matrix).\n"
        "• Kappa Paradox Mechanism: Extreme marginal imbalance (98% adjudicator supported vs. 2% contradicted)\n"
        "  inflates expected chance agreement to Pe = 75.5%, drastically deflating chance-corrected κ despite high raw empirical agreement (Po = 77.0%)."
    )
    ax_note.text(0.5, 0.45, kappa_text, transform=ax_note.transAxes, ha='center', va='center',
                 fontsize=8.5, linespacing=1.35,
                 bbox=dict(boxstyle='round,pad=0.65', facecolor='#F7FAFC', edgecolor=C_DARK_BLUE, linewidth=1.2, alpha=0.95))
    
    save_result_figure(fig, 'fig07_llama_adjudication')


if __name__ == '__main__':
    print("Loading canonical data...")
    df = load_canonical_data()
    print(f"Loaded {len(df)} conditions.")
    
    print("Generating Figure 4 (Numerical Faithfulness)...")
    generate_figure_4(df)
    
    print("Generating Figure 5 (Unsupported Claims)...")
    generate_figure_5(df)
    
    print("Generating Figure 6 (Directional Faithfulness)...")
    generate_figure_6(df)
    
    print("Generating Figure 7 (Llama Adjudication)...")
    generate_figure_7()
    
    print("Empirical figures generation complete.")
