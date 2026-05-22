from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from ..state import get_dataset
from ..services.firebase_service import get_analysis, save_analysis
from ..ml_pipeline import apply_advanced_mitigation

router = APIRouter()

class FixRequest(BaseModel):
    session_id: str

@router.post("/fix")
def fix_bias(req: FixRequest):
    """
    Apply advanced bias mitigation (evaluates multiple strategies) and return updated metrics.
    """
    session_data = get_analysis(req.session_id)
    if not session_data or "analysis" not in session_data:
        raise HTTPException(status_code=400, detail="SESSION_EXPIRED: No analysis found. Please run /analyze first.")

    target_col = session_data["analysis"]["target_col"]
    sensitive_col = session_data["analysis"]["sensitive_col"]
    original_metrics = session_data["analysis"]["metrics"]

    try:
        df = get_dataset(req.session_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"SESSION_EXPIRED: {str(e)}")

    try:
        result = apply_advanced_mitigation(df, target_col, sensitive_col)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Mitigation failed: {str(e)}")

    fixed_metrics = result["metrics"]
    y_pred_full = result["y_pred_full"]
    
    # Append the new predictions to the original dataset
    df_fair = df.copy()
    df_fair["FairLens_Prediction"] = y_pred_full
    
    from ..state import save_fair_dataset
    save_fair_dataset(req.session_id, df_fair)
    
    save_analysis(req.session_id, {"fix_result": result})

    # Compute improvements
    def improvement(before, after):
        if before == 0:
            return 0.0
        return round((before - after) / before * 100, 2)

    comparison = {
        "demographic_parity_difference": {
            "before": original_metrics["demographic_parity_difference"],
            "after": fixed_metrics["demographic_parity_difference"],
            "improvement_pct": improvement(
                original_metrics["demographic_parity_difference"],
                fixed_metrics["demographic_parity_difference"]
            ),
        },
        "equalized_odds_difference": {
            "before": original_metrics["equalized_odds_difference"],
            "after": fixed_metrics["equalized_odds_difference"],
            "improvement_pct": improvement(
                original_metrics["equalized_odds_difference"],
                fixed_metrics["equalized_odds_difference"]
            ),
        },
        "disparate_impact_ratio": {
            "before": original_metrics.get("disparate_impact_ratio", 1.0),
            "after": fixed_metrics.get("disparate_impact_ratio", 1.0),
            "improvement_pct": improvement(
                abs(1.0 - original_metrics.get("disparate_impact_ratio", 1.0)),
                abs(1.0 - fixed_metrics.get("disparate_impact_ratio", 1.0))
            ),
        },
        "fairness_score": {
            "before": original_metrics.get("fairness_score", 0),
            "after": fixed_metrics.get("fairness_score", 0),
            "change": round(fixed_metrics.get("fairness_score", 0) - original_metrics.get("fairness_score", 0), 1),
        },
        "accuracy": {
            "before": original_metrics["accuracy"],
            "after": fixed_metrics["accuracy"],
            "change_pct": round(
                (fixed_metrics["accuracy"] - original_metrics["accuracy"]) / original_metrics["accuracy"] * 100, 2
            ),
        },
    }

    return JSONResponse({
        "success": True,
        "strategy": result["strategy"],
        "original_metrics": original_metrics,
        "fixed_metrics": fixed_metrics,
        "comparison": comparison,
    })

from fastapi.responses import FileResponse
from ..state import get_fair_dataset, DATA_DIR
import os

@router.get("/download-fixed/{session_id}")
def download_fixed(session_id: str):
    """Download the mitigated dataset with fair predictions appended."""
    try:
        # Just check if it exists via get_fair_dataset (which raises 404 if not)
        get_fair_dataset(session_id)
        filepath = os.path.join(DATA_DIR, f"{session_id}_fair.csv")
        return FileResponse(filepath, media_type="text/csv", filename="fairlens_mitigated_dataset.csv")
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Dataset not found: {str(e)}")
