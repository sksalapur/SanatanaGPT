import os
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import firebase_admin
from firebase_admin import credentials, auth
from app.core.config import settings

# Initialize Firebase Admin
if not firebase_admin._apps:
    try:
        # Local dev: use service account key file
        cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS)
        firebase_admin.initialize_app(cred, {
            "storageBucket": settings.FIREBASE_STORAGE_BUCKET
        })
    except Exception:
        try:
            # Cloud Run: use Application Default Credentials
            firebase_admin.initialize_app(options={
                "storageBucket": settings.FIREBASE_STORAGE_BUCKET
            })
            print("Firebase initialized with Application Default Credentials")
        except Exception as e:
            print(f"Warning: Failed to initialize Firebase Admin: {e}")

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token. Please sign in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
