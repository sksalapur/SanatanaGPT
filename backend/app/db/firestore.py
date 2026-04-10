from firebase_admin import firestore
from datetime import datetime, timezone

def get_db():
    return firestore.client()

def utc_now():
    return datetime.now(timezone.utc)
