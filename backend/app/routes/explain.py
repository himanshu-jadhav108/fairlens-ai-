from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from ..state import get_dataset
from ..services.firebase_service import get_analysis, save_analysis
from ..services.gemini_service import generate_bias_explanation
from ..ml_pipeline import run_full_analysis
import pandas as pd

router = APIRouter()

class ExplainRequest(BaseModel):
    session_id: str

from ..ml.explainability_engine import ExplainabilityEngine

@router.post("/explain")
def explain_model(req: ExplainRequest):
    """
    Compute Global, Demographic, and Local SHAP explainability.
    To remain stateless, we retrain the light model on the fly.
    """
    session_data = get_analysis(req.session_id)
    if not session_data or "analysis" not in session_data:
        raise HTTPException(status_code=400, detail="SESSION_EXPIRED: No analysis found. Please run /analyze first.")

    target_col = session_data["analysis"]["target_col"]
    sensitive_col = session_data["analysis"]["sensitive_col"]

    try:
        df = get_dataset(req.session_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"SESSION_EXPIRED: {str(e)}")

    try:
        result = run_full_analysis(df, target_col, sensitive_col)
        model = result["model"]
        scaler = result["scaler"]
        X_train = result["X_train"]
        feature_names = result["feature_names"]
        X_test_scaled = pd.DataFrame(result["X_test_scaled"], columns=feature_names)
        y_test = result["y_test"]
        s_test = result["s_test"]

        X_train_scaled = pd.DataFrame(scaler.transform(X_train), columns=feature_names)
        
        # Initialize Engine
        engine = ExplainabilityEngine(
            model=model,
            X_train_scaled=X_train_scaled,
            X_test_scaled=X_test_scaled,
            feature_names=feature_names,
            sensitive_test=s_test.values,
            y_test=y_test.values
        )

        global_shap = engine.compute_global_shap()
        demographic_shap = engine.compute_demographic_shap()
        local_shap = engine.compute_local_shap()

        shap_result = {
            "method": "SHAP (LinearExplainer)",
            "global_importance": global_shap,
            "demographic_analysis": demographic_shap,
            "local_explanation": local_shap
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SHAP computation failed: {str(e)}")

    save_analysis(req.session_id, {"shap_values": shap_result})

    ret = shap_result.copy()
    ret["success"] = True
    return JSONResponse(ret)


@router.post("/ai-explain")
def ai_explain(req: ExplainRequest):
    """
    Generate a human-readable explanation using Vertex AI Gemini.
    """
    session_data = get_analysis(req.session_id)
    if not session_data or "analysis" not in session_data:
        raise HTTPException(status_code=400, detail="SESSION_EXPIRED: No metrics found. Please run /analyze first.")

    metrics = session_data["analysis"]["metrics"]
    shap_values = session_data.get("shap_values", {})

    try:
        explanation_data = generate_bias_explanation(metrics, shap_values)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini API failure: {str(e)}")

    save_analysis(req.session_id, {"ai_explanation": explanation_data})

    ret = explanation_data.copy()
    ret["success"] = True
    return JSONResponse(ret)
