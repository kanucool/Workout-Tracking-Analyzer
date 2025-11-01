import firebase_admin
from firebase_admin import auth
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Any

bearer_scheme = HTTPBearer()

async def get_user_from_credentials(
        credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)
        ) -> dict[str, Any]:
    if not credentials:
        raise HTTPException(status_code=401, detail="Missing credentials.")
    
    try:
        token = credentials.credentials
        return auth.verify_id_token(token)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid credentials.")