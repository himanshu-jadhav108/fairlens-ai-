"""
Acquire real benchmark datasets for FairLens AI confirmatory experiments:
- Adult Census Income (UCI 1996 release via Fairlearn)
- ProPublica COMPAS Recidivism (Official ProPublica release)
- Statlog German Credit (OpenML credit-g, ID 31)
"""
import os
import sys
import pandas as pd

def setup_datasets():
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
    os.makedirs(data_dir, exist_ok=True)
    
    # 1. Adult Dataset
    adult_path = os.path.join(data_dir, "adult.csv")
    if not os.path.exists(adult_path):
        print("[*] Fetching real Adult Census Income dataset via Fairlearn...")
        import fairlearn.datasets as flds
        adult_data = flds.fetch_adult(as_frame=True)
        df_adult = adult_data.frame
        # Standardize target column name to 'income'
        if "class" in df_adult.columns and "income" not in df_adult.columns:
            df_adult = df_adult.rename(columns={"class": "income"})
        df_adult.to_csv(adult_path, index=False)
        print(f"[+] Saved Adult dataset to {adult_path} (shape: {df_adult.shape})")
    else:
        print(f"[+] Adult dataset already present at {adult_path}")

    # 2. COMPAS Dataset
    compas_path = os.path.join(data_dir, "compas.csv")
    if not os.path.exists(compas_path):
        print("[*] Fetching real COMPAS dataset from ProPublica official repository...")
        compas_url = "https://raw.githubusercontent.com/propublica/compas-analysis/master/compas-scores-two-years.csv"
        df_compas = pd.read_csv(compas_url)
        df_compas.to_csv(compas_path, index=False)
        print(f"[+] Saved COMPAS dataset to {compas_path} (shape: {df_compas.shape})")
    else:
        print(f"[+] COMPAS dataset already present at {compas_path}")

    # 3. German Credit Dataset
    german_path = os.path.join(data_dir, "german.csv")
    if not os.path.exists(german_path):
        print("[*] Fetching real German Credit dataset via OpenML (credit-g)...")
        from sklearn.datasets import fetch_openml
        german_data = fetch_openml("credit-g", version=1, as_frame=True)
        df_german = german_data.frame
        # Standardize target column name to 'credit_risk'
        if "class" in df_german.columns and "credit_risk" not in df_german.columns:
            df_german = df_german.rename(columns={"class": "credit_risk"})
        df_german.to_csv(german_path, index=False)
        print(f"[+] Saved German Credit dataset to {german_path} (shape: {df_german.shape})")
    else:
        print(f"[+] German Credit dataset already present at {german_path}")

if __name__ == "__main__":
    setup_datasets()
