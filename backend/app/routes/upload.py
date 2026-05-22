import io
import time
import pandas as pd
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from ..state import create_session_id, save_dataset
from ..services.firebase_service import save_analysis
from ..core.auth import get_optional_user_id

router = APIRouter()


@router.post("/upload")
async def upload_dataset(file: UploadFile = File(...), user_id: str | None = Depends(get_optional_user_id)):
    """
    Upload a CSV dataset. Stores it to disk, creates a session in Firestore,
    and returns session_id along with column names + preview.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")

    try:
        df = pd.read_csv(io.BytesIO(content))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse CSV. Please ensure it is a valid comma-separated file. Error: {str(e)}")

    if df.empty:
        raise HTTPException(status_code=400, detail="Uploaded CSV is empty.")

    # Create session
    session_id = create_session_id()
    
    # Save to local disk
    save_dataset(session_id, df)

    # Build column metadata
    col_info = []
    for col in df.columns:
        col_info.append({
            "name": col,
            "dtype": str(df[col].dtype),
            "unique_count": int(df[col].nunique()),
            "null_count": int(df[col].isnull().sum()),
        })

    # Preview: first 5 rows as list of dicts
    preview = df.head(5).fillna("").to_dict(orient="records")

    # Save initial metadata to Firestore
    save_analysis(session_id, {
        "user_id": user_id,
        "created_at": time.time(),
        "dataset": {
            "filename": file.filename,
            "rows": len(df),
            "columns": col_info
        }
    })

    return JSONResponse({
        "success": True,
        "session_id": session_id,
        "filename": file.filename,
        "rows": len(df),
        "columns": col_info,
        "preview": preview,
    })

@router.post("/demo")
async def load_demo_dataset(user_id: str | None = Depends(get_optional_user_id)):
    """
    Loads the sample_data.csv as a demo session to instantly showcase the platform.
    """
    import os
    sample_path = os.path.join(os.path.dirname(__file__), "..", "..", "sample_data.csv")
    if not os.path.exists(sample_path):
        raise HTTPException(status_code=404, detail="sample_data.csv not found on server.")
    
    df = pd.read_csv(sample_path)
    session_id = create_session_id()
    
    save_dataset(session_id, df)
    
    col_info = []
    for col in df.columns:
        col_info.append({
            "name": col,
            "dtype": str(df[col].dtype),
            "unique_count": int(df[col].nunique()),
            "null_count": int(df[col].isnull().sum()),
        })

    preview = df.head(5).fillna("").to_dict(orient="records")

    save_analysis(session_id, {
        "user_id": user_id,
        "created_at": time.time(),
        "dataset": {
            "filename": "sample_data.csv",
            "rows": len(df),
            "columns": col_info
        }
    })

    return JSONResponse({
        "success": True,
        "session_id": session_id,
        "filename": "sample_data.csv",
        "rows": len(df),
        "columns": col_info,
        "preview": preview,
    })
