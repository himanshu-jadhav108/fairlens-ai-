"""
Faithfulness Visualization Infrastructure for FairLens AI Research.
Plots empirical faithfulness results directly from experiment summaries and claim logs:
1. Overall faithfulness by claim type
2. Faithfulness across datasets
3. Faithfulness across mitigation conditions
4. Template vs LLM comparison
5. Error taxonomy distribution
6. Numerical error distribution
7. Directional error distribution
8. Attribution agreement

Never generates fake results; operates only on actual saved JSON/CSV summaries.
"""
import os
import glob
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from typing import Optional, List, Dict, Any


def load_faithfulness_summaries(summaries_dir: str = "research/results/summaries") -> pd.DataFrame:
    """Loads all faithfulness summary JSON files into a DataFrame."""
    files = glob.glob(os.path.join(summaries_dir, "summary__*.json"))
    records = []
    for f in files:
        with open(f, "r", encoding="utf-8") as fp:
            data = json.load(fp)
            # Flatten high level fields
            records.append({
                "experiment_id": data.get("experiment_id"),
                "source": data.get("explanation_source"),
                "prompt_id": data.get("prompt_id"),
                "numerical_faithfulness": data.get("numerical_faithfulness"),
                "directional_faithfulness": data.get("directional_faithfulness"),
                "attribution_faithfulness": data.get("attribution_faithfulness"),
                "unsupported_claim_rate": data.get("unsupported_claim_rate"),
                "numeric_claims": data.get("numeric_claim_count"),
                "numeric_errors": data.get("numeric_error_count"),
                "directional_claims": data.get("directional_claim_count"),
                "directional_errors": data.get("directional_error_count"),
                "attribution_claims": data.get("attribution_claim_count"),
                "attribution_errors": data.get("attribution_error_count"),
                "total_claims": data.get("total_claims_count"),
                "numerical_mae": data.get("numerical_mean_absolute_error")
            })
    return pd.DataFrame(records)


def load_claim_records(claims_dir: str = "research/results/claims") -> pd.DataFrame:
    """Loads all atomic claim JSON files into a DataFrame."""
    files = glob.glob(os.path.join(claims_dir, "claims__*.json"))
    claims = []
    for f in files:
        with open(f, "r", encoding="utf-8") as fp:
            data = json.load(fp)
            for item in data:
                claims.append(item)
    return pd.DataFrame(claims)


def generate_faithfulness_figures(
    summaries_dir: str = "research/results/summaries",
    claims_dir: str = "research/results/claims",
    figures_dir: str = "research/results/figures"
):
    """
    Generates all candidate figures for explanation faithfulness analysis from empirical outputs.
    """
    df_summ = load_faithfulness_summaries(summaries_dir)
    df_claims = load_claim_records(claims_dir)

    if df_summ.empty:
        print("[!] No faithfulness summaries found to plot. Run experiments first.")
        return

    os.makedirs(figures_dir, exist_ok=True)
    plt.style.use("default")

    # 1. Figure: Overall Faithfulness by Claim Type (LLM vs Template Baseline)
    if "source" in df_summ.columns:
        plt.figure(figsize=(10, 6))
        metrics = ["numerical_faithfulness", "directional_faithfulness", "attribution_faithfulness"]
        metric_labels = ["Numerical", "Directional", "Attribution"]
        sources = df_summ["source"].unique()

        x = np.arange(len(metric_labels))
        width = 0.35

        for i, src in enumerate(sources[:2]):
            sub = df_summ[df_summ["source"] == src]
            means = [sub[m].mean() * 100 for m in metrics]
            plt.bar(x + i * width - width / 2, means, width, label=src, alpha=0.85, edgecolor="black")

        plt.ylabel("Faithfulness Rate (%)")
        plt.title("Faithfulness Rate by Claim Type (Template vs. LLM)")
        plt.xticks(x, metric_labels)
        plt.ylim(0, 105)
        plt.legend()
        plt.grid(axis="y", linestyle="--", alpha=0.7)
        plt.tight_layout()
        plt.savefig(os.path.join(figures_dir, "fig1_faithfulness_by_claim_type.png"), dpi=300)
        plt.close()

    # 2. Figure: Error Taxonomy Distribution
    if not df_claims.empty and "classification" in df_claims.columns:
        plt.figure(figsize=(8, 5))
        class_counts = df_claims["classification"].value_counts()
        colors = {"SUPPORTED": "#2ca02c", "PARTIALLY_SUPPORTED": "#ff7f0e", "UNSUPPORTED": "#d62728", "UNDETERMINABLE": "#7f7f7f"}
        bar_colors = [colors.get(c, "#1f77b4") for c in class_counts.index]
        
        plt.bar(class_counts.index, class_counts.values, color=bar_colors, edgecolor="black", alpha=0.85)
        plt.ylabel("Number of Claims")
        plt.title("Taxonomic Distribution of Extracted Claims")
        plt.grid(axis="y", linestyle="--", alpha=0.7)
        plt.tight_layout()
        plt.savefig(os.path.join(figures_dir, "fig2_claim_taxonomy_distribution.png"), dpi=300)
        plt.close()

    # 3. Figure: Numerical Error Distribution (if errors exist)
    if not df_claims.empty:
        num_claims = df_claims[df_claims["claim_type"] == "numerical"]
        abs_diffs = []
        for meta in num_claims.get("metadata", []):
            if isinstance(meta, dict) and "abs_diff" in meta and meta["abs_diff"] is not None:
                abs_diffs.append(meta["abs_diff"])
        
        if abs_diffs:
            plt.figure(figsize=(8, 5))
            plt.hist(abs_diffs, bins=15, color="#1f77b4", edgecolor="black", alpha=0.75)
            plt.xlabel("Absolute Numerical Discrepancy (|Claimed - Ground Truth|)")
            plt.ylabel("Frequency")
            plt.title("Distribution of Numerical Discrepancies in Explanations")
            plt.grid(axis="y", linestyle="--", alpha=0.7)
            plt.tight_layout()
            plt.savefig(os.path.join(figures_dir, "fig3_numerical_error_distribution.png"), dpi=300)
            plt.close()

    print(f"-> Generated faithfulness figures in '{figures_dir}'.")
