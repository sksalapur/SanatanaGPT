import os
import json
import firebase_admin
from firebase_admin import credentials
from app.core.config import settings

def init_firebase():
    """Initialize Firebase Admin SDK with support for Secrets."""
    if firebase_admin._apps:
        return

    json_env = os.environ.get("FIREBASE_SERVICE_ACCOUNT_JSON")
    storage_bucket = settings.FIREBASE_STORAGE_BUCKET or "sanatangpt-ee992.firebasestorage.app"
    
    if json_env:
        try:
            print(f"[Firebase] Attempting to init with JSON secret (len: {len(json_env)})")
            # Clear any potential wrapping quotes if they were pasted accidentally
            json_str = json_env.strip()
            if json_str.startswith('"') and json_str.endswith('"'):
                json_str = json_str[1:-1].replace('\\"', '"')
            
            cred_dict = json.loads(json_str)
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred, {
                "storageBucket": storage_bucket
            })
            print("[Firebase] Initialized successfully using JSON secret.")
            return
        except Exception as e:
            print(f"[Firebase] Error parsing JSON secret: {e}")
    
    # Fallback 1: Local File
    try:
        if settings.FIREBASE_CREDENTIALS and os.path.exists(settings.FIREBASE_CREDENTIALS):
            cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS)
            firebase_admin.initialize_app(cred, {
                "storageBucket": storage_bucket
            })
            print("[Firebase] Initialized using local service account file.")
            return
    except Exception as e:
        print(f"[Firebase] Local file init failed: {e}")

    # Fallback 2: Application Default Credentials (ADC)
    try:
        firebase_admin.initialize_app(options={
            "storageBucket": storage_bucket
        })
        print("[Firebase] Initialized using Application Default Credentials.")
    except Exception as e:
        print(f"[Firebase] ADC init failed: {e}")
