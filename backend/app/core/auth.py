from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import firebase_admin.auth
from typing import Optional

security = HTTPBearer(auto_error=False)

def get_optional_user_id(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[str]:
    """
    Validates Firebase Bearer token if present. Returns uid or None.
    """
    if credentials is None:
        return None
    token = credentials.credentials
    try:
        decoded_token = firebase_admin.auth.verify_id_token(token)
        return decoded_token.get('uid')
    except Exception as e:
        print(f"Auth error: {e}")
        return None

def get_current_user_id(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> str:
    """
    Forces valid authentication. Throws 401 if missing or invalid.
    """
    uid = get_optional_user_id(credentials)
    if not uid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return uid
