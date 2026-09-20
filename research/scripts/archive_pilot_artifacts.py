"""
Archive Gemini Lite artifacts and duplicate pilot runs from active pilot directories.
Preserves historical audit trail while isolating final confirmatory datasets.
"""
import os
import shutil
import json

def archive_artifacts():
    pilot_dir = "research/results/pilot"
    archive_dir = os.path.join(pilot_dir, "archive")
    lite_archive = os.path.join(archive_dir, "lite_model_runs")
    dup_archive = os.path.join(archive_dir, "duplicate_runs")
    
    os.makedirs(lite_archive, exist_ok=True)
    os.makedirs(dup_archive, exist_ok=True)
    
    # Target exp_ids for Lite
    lite_exp_ids = [
        "compas__logistic_regression__threshold_optimizer__seed123__76fa7964",
        "compas__logistic_regression__threshold_optimizer__seed456__9b4afa7a",
        "compas__random_forest__threshold_optimizer__seed123__35ea1003",
        "compas__random_forest__threshold_optimizer__seed42__6febbe1b",
        "compas__random_forest__threshold_optimizer__seed456__936e3c3a"
    ]
    
    # Target exp_id for duplicate
    dup_exp_id = "compas__logistic_regression__correlation_remover__seed456__e61a33c9"
    
    # 1. Archive Lite runs
    for sub in ["summaries", "raw", "manifests"]:
        sub_dir = os.path.join(pilot_dir, sub)
        if not os.path.exists(sub_dir):
            continue
        dest_sub = os.path.join(lite_archive, sub)
        os.makedirs(dest_sub, exist_ok=True)
        for fname in os.listdir(sub_dir):
            if any(exp_id in fname for exp_id in lite_exp_ids):
                src = os.path.join(sub_dir, fname)
                dst = os.path.join(dest_sub, fname)
                # Annotate JSON with exclusion tag before moving
                try:
                    with open(src, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    data["EXCLUDED_FROM_FINAL_CONFIRMATORY_ANALYSIS"] = True
                    data["exclusion_reason"] = "Generated using a different Gemini model version (Gemini Flash Lite)."
                    with open(dst, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=2)
                    os.remove(src)
                    print(f"[+] Archived Lite artifact: {fname} -> {dst}")
                except Exception as e:
                    shutil.move(src, dst)
                    print(f"[+] Moved Lite artifact: {fname} -> {dst}")

    # 2. Archive Duplicate run
    for sub in ["summaries", "raw", "manifests"]:
        sub_dir = os.path.join(pilot_dir, sub)
        if not os.path.exists(sub_dir):
            continue
        dest_sub = os.path.join(dup_archive, sub)
        os.makedirs(dest_sub, exist_ok=True)
        for fname in os.listdir(sub_dir):
            if dup_exp_id in fname:
                src = os.path.join(sub_dir, fname)
                dst = os.path.join(dest_sub, fname)
                try:
                    with open(src, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    data["DUPLICATE_EXCLUDED_FROM_FINAL_ANALYSIS"] = True
                    data["exclusion_reason"] = "Duplicate condition run in exploratory pilot."
                    with open(dst, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=2)
                    os.remove(src)
                    print(f"[+] Archived Duplicate artifact: {fname} -> {dst}")
                except Exception as e:
                    shutil.move(src, dst)
                    print(f"[+] Moved Duplicate artifact: {fname} -> {dst}")

    # 3. Create Archive README
    readme_path = os.path.join(archive_dir, "ARCHIVE_README.md")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write("""# Pilot Artifacts Archive

This directory contains historical exploratory pilot artifacts segregated from active experimental analysis:

## 1. `lite_model_runs/`
- **Exclusion Classification:** `EXCLUDED_FROM_FINAL_CONFIRMATORY_ANALYSIS`
- **Reason:** Generated using `gemini-flash-lite-latest` rather than the locked primary model `gemini-2.5-flash`.
- **Count:** 5 experimental runs (and matching template records).

## 2. `duplicate_runs/`
- **Exclusion Classification:** `DUPLICATE_EXCLUDED_FROM_FINAL_ANALYSIS`
- **Reason:** Duplicate execution of condition `compas__logistic_regression__correlation_remover__seed456` (`e61a33c9`).
- **Count:** 1 experimental run (and matching template record).

All raw files are preserved intact for complete provenance tracking.
""")
    print(f"[+] Created {readme_path}")

if __name__ == "__main__":
    archive_artifacts()
