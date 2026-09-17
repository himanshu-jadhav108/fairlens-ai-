"""
Candidate Visualization Generator for FairLens AI Research.
NOTE: Figures generated here are CANDIDATE VISUALIZATIONS for exploratory and pilot analysis.
They are NOT described as final publication-ready figures.
Radar charts are explicitly excluded in accordance with Methodological Correction 7.
"""
import os
import matplotlib
matplotlib.use("Agg")  # Non-interactive headless backend
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


def generate_candidate_figures(
    processed_dir: str = "research/results/processed",
    figures_dir: str = "research/results/figures"
):
    """
    Generates candidate scientific plots from aggregated results:
    1. Fairness vs. Performance Scatter / Pareto Analysis
    2. Baseline vs. Mitigation Fairness Change (DPD Delta)
    3. Baseline vs. Mitigation Performance Change (Accuracy Delta)
    4. Explanation Similarity / Attribution Shift Distribution
    """
    runs_file = os.path.join(processed_dir, "individual_runs.csv")
    if not os.path.exists(runs_file):
        print(f"[!] Cannot generate figures: '{runs_file}' not found. Run aggregator first.")
        return

    df = pd.read_csv(runs_file)
    if df.empty:
        print("[!] Dataset of runs is empty.")
        return

    os.makedirs(figures_dir, exist_ok=True)
    plt.style.use("default")

    # Figure 1: Fairness vs Performance Scatter / Pareto Analysis
    plt.figure(figsize=(8, 6))
    if "mitigated_dpd" in df.columns and "mitigated_accuracy" in df.columns:
        valid_mask = df["mitigated_dpd"].notna() & df["mitigated_accuracy"].notna()
        sub_df = df[valid_mask]
        
        scatter = plt.scatter(
            sub_df["mitigated_dpd"],
            sub_df["mitigated_accuracy"],
            c=pd.factorize(sub_df["mitigation"])[0],
            cmap="viridis",
            s=80,
            alpha=0.8,
            edgecolors="k"
        )
        # Also plot baselines if present
        if "baseline_dpd" in sub_df.columns and "baseline_accuracy" in sub_df.columns:
            plt.scatter(
                sub_df["baseline_dpd"],
                sub_df["baseline_accuracy"],
                marker="x",
                color="red",
                s=70,
                label="Baseline Models"
            )
            
        plt.xlabel("Demographic Parity Difference (Lower is Fairer)", fontsize=11)
        plt.ylabel("Test Accuracy (Higher is Better)", fontsize=11)
        plt.title("Candidate Plot 1: Fairness-Performance Trade-Off", fontsize=12, fontweight="bold")
        plt.grid(True, linestyle="--", alpha=0.5)
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(figures_dir, "candidate_01_pareto_tradeoff.png"), dpi=200)
        plt.close()

    # Figure 2: Fairness Change (Delta DPD)
    if "delta_dpd" in df.columns and df["delta_dpd"].notna().any():
        plt.figure(figsize=(8, 5))
        sub_df = df.dropna(subset=["delta_dpd"])
        mitigations = sub_df["mitigation"].unique()
        deltas_by_mit = [sub_df[sub_df["mitigation"] == m]["delta_dpd"].values for m in mitigations]
        
        plt.axhline(0, color="gray", linestyle="--", linewidth=1)
        plt.boxplot(deltas_by_mit, tick_labels=mitigations)
        plt.ylabel("Change in DPD (Negative = Fairness Improved)", fontsize=11)
        plt.title("Candidate Plot 2: Fairness Improvement across Mitigations", fontsize=12, fontweight="bold")
        plt.grid(True, linestyle="--", alpha=0.4)
        plt.tight_layout()
        plt.savefig(os.path.join(figures_dir, "candidate_02_fairness_deltas.png"), dpi=200)
        plt.close()

    # Figure 3: Performance Change (Delta Accuracy)
    if "delta_accuracy" in df.columns and df["delta_accuracy"].notna().any():
        plt.figure(figsize=(8, 5))
        sub_df = df.dropna(subset=["delta_accuracy"])
        mitigations = sub_df["mitigation"].unique()
        deltas_by_mit = [sub_df[sub_df["mitigation"] == m]["delta_accuracy"].values for m in mitigations]
        
        plt.axhline(0, color="gray", linestyle="--", linewidth=1)
        plt.boxplot(deltas_by_mit, tick_labels=mitigations)
        plt.ylabel("Change in Accuracy (Percentage Points)", fontsize=11)
        plt.title("Candidate Plot 3: Performance Impact of Bias Mitigation", fontsize=12, fontweight="bold")
        plt.grid(True, linestyle="--", alpha=0.4)
        plt.tight_layout()
        plt.savefig(os.path.join(figures_dir, "candidate_03_performance_deltas.png"), dpi=200)
        plt.close()

    # Figure 4: Attribution Similarity / Shift Distribution
    if "cosine_similarity" in df.columns and df["cosine_similarity"].notna().any():
        plt.figure(figsize=(8, 5))
        sub_df = df.dropna(subset=["cosine_similarity"])
        mitigations = sub_df["mitigation"].unique()
        sims_by_mit = [sub_df[sub_df["mitigation"] == m]["cosine_similarity"].values for m in mitigations]
        
        plt.boxplot(sims_by_mit, tick_labels=mitigations)
        plt.ylabel("SHAP Attribution Cosine Similarity (1.0 = Identical)", fontsize=11)
        plt.ylim(-0.1, 1.1)
        plt.title("Candidate Plot 4: Feature Attribution Stability", fontsize=12, fontweight="bold")
        plt.grid(True, linestyle="--", alpha=0.4)
        plt.tight_layout()
        plt.savefig(os.path.join(figures_dir, "candidate_04_attribution_stability.png"), dpi=200)
        plt.close()

    print(f"[*] Candidate visualization figures generated under '{figures_dir}'.")
