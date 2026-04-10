from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from app.middleware.auth import get_current_user
from app.db.firestore import get_db, utc_now

router = APIRouter(prefix="/api/users", tags=["users"])

class UserSync(BaseModel):
    email: Optional[str] = None
    displayName: Optional[str] = None
    photoURL: Optional[str] = None

@router.post("/sync")
async def sync_user(user_data: UserSync, user: dict = Depends(get_current_user)):
    db = get_db()
    uid = user.get("uid")
    if not uid:
        raise HTTPException(status_code=401, detail="Invalid token")

    doc_ref = db.collection("users").document(uid)
    doc = doc_ref.get()
    
    if not doc.exists:
        doc_ref.set({
            "email": user_data.email or user.get("email"),
            "displayName": user_data.displayName or user.get("name"),
            "photoURL": user_data.photoURL or user.get("picture"),
            "createdAt": utc_now()
        })
        return {"status": "created", "uid": uid}
    else:
        # Optional: update dynamic fields like photoURL if needed
        doc_ref.update({
            "displayName": user_data.displayName or user.get("name"),
            "photoURL": user_data.photoURL or user.get("picture")
        })
        return {"status": "updated", "uid": uid}
