from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.middleware.auth import get_current_user
from app.db.firestore import get_db, utc_now
from app.core.config import settings

router = APIRouter(prefix="/api/requests", tags=["requests"])

class ScriptureRequest(BaseModel):
    title: str
    language: Optional[str] = ""
    description: Optional[str] = ""
    referenceUrl: Optional[str] = ""

@router.post("/")
async def create_request(payload: ScriptureRequest, user: dict = Depends(get_current_user)):
    """Authenticated users can submit scripture requests."""
    db = get_db()
    uid = user.get("uid")
    
    req_ref = db.collection("scripture_requests").document()
    req_ref.set({
        "title": payload.title,
        "language": payload.language,
        "description": payload.description,
        "referenceUrl": payload.referenceUrl,
        "status": "pending",
        "requestedBy": uid,
        "requestedByEmail": user.get("email", ""),
        "createdAt": utc_now()
    })
    
    return {"status": "created", "requestId": req_ref.id}

@router.get("/")
async def list_my_requests(user: dict = Depends(get_current_user)):
    """List the current user's own scripture requests."""
    db = get_db()
    uid = user.get("uid")
    
    docs = db.collection("scripture_requests").where("requestedBy", "==", uid).stream()
    
    reqs = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        if data.get("createdAt"):
            data["createdAt"] = data["createdAt"].isoformat() if hasattr(data["createdAt"], "isoformat") else str(data["createdAt"])
        reqs.append(data)
        
    return {"requests": reqs}

@router.get("/all")
async def list_all_pending(user: dict = Depends(get_current_user)):
    """Admin only — list all pending scripture requests."""
    if user.get("uid") != settings.ADMIN_UID or not settings.ADMIN_UID:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    db = get_db()
    docs = db.collection("scripture_requests").where("status", "==", "pending").stream()
    
    reqs = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        if data.get("createdAt"):
            data["createdAt"] = data["createdAt"].isoformat() if hasattr(data["createdAt"], "isoformat") else str(data["createdAt"])
        reqs.append(data)
        
    return {"requests": reqs}

@router.patch("/{requestId}/approve")
async def approve_request(requestId: str, user: dict = Depends(get_current_user)):
    """Admin only — approve a scripture request."""
    if user.get("uid") != settings.ADMIN_UID or not settings.ADMIN_UID:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    db = get_db()
    req_ref = db.collection("scripture_requests").document(requestId)
    doc = req_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Request not found")
    
    req_ref.update({"status": "approved", "reviewedAt": utc_now()})
    return {"status": "approved", "requestId": requestId}

@router.patch("/{requestId}/reject")
async def reject_request(requestId: str, user: dict = Depends(get_current_user)):
    """Admin only — reject a scripture request."""
    if user.get("uid") != settings.ADMIN_UID or not settings.ADMIN_UID:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    db = get_db()
    req_ref = db.collection("scripture_requests").document(requestId)
    doc = req_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Request not found")
    
    req_ref.update({"status": "rejected", "reviewedAt": utc_now()})
    return {"status": "rejected", "requestId": requestId}
