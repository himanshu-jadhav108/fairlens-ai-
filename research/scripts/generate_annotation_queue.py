"""
Generate Human Annotation Queue from Pilot Summaries.
Builds a structured queue of claims sampled across all 24 pilot conditions
ready for human evaluation during the confirmatory phase.
"""
import os
import glob
import json
import random

def generate_annotation_queue():
    summaries_dir = "research/results/pilot/summaries"
    files = glob.glob(os.path.join(summaries_dir, "*gemini*.json"))
    
    queue_items = []
    
    for fp in sorted(files):
        with open(fp, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        exp_id = data.get("experiment_id")
        source = data.get("explanation_source")
        claims = data.get("claims", [])
        
        for c in claims:
            queue_items.append({
                "queue_id": f"pilot_claim_{len(queue_items) + 1:04d}",
                "experiment_id": exp_id,
                "explanation_source": source,
                "claim_id": c.get("claim_id"),
                "claim_type": c.get("claim_type"),
                "claim_text": c.get("claim_text"),
                "extracted_values": c.get("extracted_values"),
                "ground_truth_path": c.get("referenced_evidence"),
                "automated_classification": c.get("classification"),
                "automated_rationale": c.get("rationale"),
                "human_annotation": {
                    "annotator_id": None,
                    "annotator_judgment": None,  # SUPPORTED, REFUTED, UNSUPPORTED, UNDETERMINABLE
                    "is_factually_accurate": None,  # true/false
                    "is_hallucination": None,  # true/false
                    "notes": None,
                    "annotation_timestamp_utc": None
                }
            })
            
    out_path = "research/results/pilot/ANNOTATION_QUEUE.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({
            "generated_utc": "2026-09-17T10:45:00Z",
            "study_phase": "PILOT_STAGE",
            "status": "QUEUED_PENDING_HUMAN_ANNOTATION",
            "human_annotation_performed": False,
            "total_claims_queued": len(queue_items),
            "claim_type_counts": {
                "numerical": sum(1 for q in queue_items if q["claim_type"] == "numerical"),
                "directional": sum(1 for q in queue_items if q["claim_type"] == "directional"),
                "attribution": sum(1 for q in queue_items if q["claim_type"] == "attribution"),
                "unsupported": sum(1 for q in queue_items if q["claim_type"] == "unsupported"),
            },
            "claims": queue_items
        }, f, indent=2)
        
    print(f"[+] Generated {out_path} with {len(queue_items)} queued claims.")

if __name__ == "__main__":
    generate_annotation_queue()
