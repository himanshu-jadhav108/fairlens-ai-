"""
Generate Stratified Human Annotation Sample from Confirmatory Final Claims.
Extracts 100 stratified claims across datasets, models, and claim types
for inter-rater reliability protocol (Cohen's Kappa adjudication).
"""
import os
import glob
import json
import random
from pathlib import Path


def generate_final_human_sample(
    claims_dir: str = "research/results/final/claims",
    output_path: str = "research/results/final/human_annotation_sample.json",
    sample_size: int = 100,
    seed: int = 42
):
    claims_files = glob.glob(os.path.join(claims_dir, "*.json"))
    if not claims_files:
        print(f"[!] No claims files found in {claims_dir}")
        return

    all_claims = []
    for fp in sorted(claims_files):
        try:
            with open(fp, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            base_fname = os.path.basename(fp)
            inferred_source = "template_baseline" if "template_baseline" in base_fname else "gemini__gemini-2.5-flash"
            
            if isinstance(data, dict):
                exp_id = data.get("experiment_id")
                source = data.get("explanation_source") or inferred_source
                mode = data.get("execution_mode", "FINAL_EMPIRICAL_RUN")
                claims_list = data.get("extracted_claims", [])
            elif isinstance(data, list):
                claims_list = data
                exp_id = data[0].get("experiment_id") if data else None
                source = inferred_source
                mode = "FINAL_EMPIRICAL_RUN"
            else:
                continue

            for c in claims_list:
                all_claims.append({
                    "experiment_id": c.get("experiment_id") or exp_id,
                    "explanation_source": source,
                    "execution_mode": mode,
                    "source_file": base_fname,
                    "claim_id": c.get("claim_id"),
                    "claim_type": c.get("claim_type"),
                    "claim_text": c.get("claim_text"),
                    "extracted_values": c.get("extracted_values"),
                    "automated_classification": c.get("classification"),
                    "automated_rationale": c.get("rationale"),
                    "human_adjudication": {
                        "annotator_id": None,
                        "adjudicated_verdict": None,  # SUPPORTED, CONTRADICTED, UNSUPPORTED, UNDETERMINABLE
                        "is_factual": None,
                        "is_hallucination": None,
                        "status": "NOT_PERFORMED",
                        "notes": None
                    }
                })
        except Exception as e:
            print(f"[!] Failed to parse {fp}: {e}")

    # Stratified sampling across claim types
    random.seed(seed)
    by_type = {}
    for c in all_claims:
        ctype = c.get("claim_type", "unknown")
        by_type.setdefault(ctype, []).append(c)

    sampled = []
    target_per_type = sample_size // max(1, len(by_type))
    for ctype, items in by_type.items():
        k = min(len(items), target_per_type)
        sampled.extend(random.sample(items, k))

    # Fill remainder if needed
    remainder = sample_size - len(sampled)
    if remainder > 0:
        remaining_pool = [c for c in all_claims if c not in sampled]
        if remaining_pool:
            sampled.extend(random.sample(remaining_pool, min(remainder, len(remaining_pool))))

    # Assign queue IDs
    for idx, c in enumerate(sampled, 1):
        c["sample_queue_id"] = f"FINAL_CLAIM_{idx:03d}"

    out_data = {
        "status": "NOT_PERFORMED",
        "description": "Stratified human validation sample for inter-rater reliability protocol",
        "total_claims_in_universe": len(all_claims),
        "total_claims_sampled": len(sampled),
        "sampling_seed": seed,
        "strata_counts": {ctype: sum(1 for s in sampled if s["claim_type"] == ctype) for ctype in by_type},
        "claims": sampled
    }

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(out_data, f, indent=2)

    print(f"[+] Human annotation sample generated: {output_path} ({len(sampled)} claims)")


if __name__ == "__main__":
    generate_final_human_sample()
