from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from ..state import get_dataset
from ..services.firebase_service import save_analysis
from ..ml_pipeline import run_full_analysis

router = APIRouter()


class AnalyzeRequest(BaseModel):
    session_id: str
    target_col: str
    sensitive_col: str


@router.post("/analyze")
def analyze_bias(req: AnalyzeRequest):
    """
    Train a logistic regression model and compute fairness metrics.
    """
    try:
        df = get_dataset(req.session_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"SESSION_EXPIRED: {str(e)}")

    if df is None:
        raise HTTPException(status_code=400, detail="SESSION_EXPIRED: No dataset uploaded. Please upload a CSV first.")

    if req.target_col not in df.columns:
        raise HTTPException(status_code=400, detail=f"Target column '{req.target_col}' not found.")

    if req.sensitive_col not in df.columns:
        raise HTTPException(status_code=400, detail=f"Sensitive column '{req.sensitive_col}' not found.")

    if req.target_col == req.sensitive_col:
        raise HTTPException(status_code=400, detail="Target and sensitive columns must be different.")

    try:
        result = run_full_analysis(df, req.target_col, req.sensitive_col)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

    # We do NOT save the model/weights to Firestore due to size limits.
    # If the user reruns analysis or uses the fix engine, it trains on the fly (fast enough for LR MVP).
    # Save metrics to Firestore.
    analysis_data = {
        "analysis": {
            "target_col": req.target_col,
            "sensitive_col": req.sensitive_col,
            "metrics": result["metrics"],
            "model_info": {
                "type": "Logistic Regression",
                "features_used": len(result["feature_names"]),
                "test_samples": len(result["y_test"]),
            }
        }
    }
    
    save_analysis(req.session_id, analysis_data)

    ret = analysis_data["analysis"]
    ret["success"] = True
    return JSONResponse(ret)

