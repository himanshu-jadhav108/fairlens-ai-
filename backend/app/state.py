"""
Local session store for datasets.
Metadata and analysis results are stored in Firestore.
"""
import os
import uuid
import pandas as pd
from fastapi import HTTPException

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(DATA_DIR, exist_ok=True)

def create_session_id() -> str:
    return str(uuid.uuid4())

def save_dataset(session_id: str, df: pd.DataFrame):
    """Save dataset to local disk."""
    filepath = os.path.join(DATA_DIR, f"{session_id}.csv")
    df.to_csv(filepath, index=False)

def get_dataset(session_id: str) -> pd.DataFrame:
    """Load dataset from local disk."""
    filepath = os.path.join(DATA_DIR, f"{session_id}.csv")
    
    if os.path.exists(filepath):
        return pd.read_csv(filepath)
    else:
        raise HTTPException(status_code=400, detail="SESSION_EXPIRED: Dataset not found on local disk. Please re-upload.")

def save_fair_dataset(session_id: str, df: pd.DataFrame):
    """Save the fixed/fair dataset to local disk."""
    filepath = os.path.join(DATA_DIR, f"{session_id}_fair.csv")
    df.to_csv(filepath, index=False)

def get_fair_dataset(session_id: str) -> pd.DataFrame:
    """Load the fixed/fair dataset from local disk."""
    filepath = os.path.join(DATA_DIR, f"{session_id}_fair.csv")
    if os.path.exists(filepath):
        return pd.read_csv(filepath)
    raise HTTPException(status_code=404, detail="Fair dataset not found. Please run the mitigation pipeline first.")
