import firebase_admin
from firebase_admin import credentials, firestore
from typing import Dict, Any, Optional
import json

from ..core.config import settings

db = None

if not firebase_admin._apps:
    try:
        if settings.FIREBASE_CREDENTIALS_JSON:
            cert = credentials.Certificate(settings.firebase_credentials_dict)
            firebase_admin.initialize_app(cert)
            db = firestore.client()
        else:
            print("Warning: FIREBASE_CREDENTIALS_JSON not provided. Firebase features will be disabled.")
    except Exception as e:
        print(f"Warning: Failed to initialize Firebase Admin. Firebase features will be disabled. Error: {e}")

def get_analysis(session_id: str) -> Optional[Dict[str, Any]]:
    """Get the session document from Firestore."""
    if not db:
        return None
    doc_ref = db.collection('sessions').document(session_id)
    doc = doc_ref.get()
    return doc.to_dict() if doc.exists else None

def save_analysis(session_id: str, data: Dict[str, Any]):
    """Merge data into the session document in Firestore."""
    if not db:
        return
    # Convert numpy/pandas data types to built-in Python types for Firestore compatibility
    safe_data = json.loads(json.dumps(data, default=lambda x: str(x)))
    db.collection('sessions').document(session_id).set(safe_data, merge=True)
