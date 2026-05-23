from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from ..core.auth import get_current_user_id
from ..services.firebase_service import db
from google.cloud import firestore

router = APIRouter()

@router.get("/history")
async def get_history(user_id: str = Depends(get_current_user_id)):
    """
    Fetches the history of sessions/datasets for the authenticated user.
    """
    if not db:
        raise HTTPException(status_code=500, detail="Firebase is not configured.")
        
    try:
        sessions_ref = db.collection('sessions')
        query = sessions_ref.where('user_id', '==', user_id).order_by('created_at', direction=firestore.Query.DESCENDING).limit(50)
        docs = query.stream()
        
        history = []
        for doc in docs:
            data = doc.to_dict()
            history.append({
                "session_id": doc.id,
                "created_at": data.get("created_at"),
                "dataset": data.get("dataset", {}),
                "analysis_summary": data.get("analysis", {}).get("summary", {}),
                "fix_strategy": data.get("fix", {}).get("strategy", None),
            })
            
        return JSONResponse({"success": True, "history": history})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch history: {str(e)}")
