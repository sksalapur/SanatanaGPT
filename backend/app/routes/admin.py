from fastapi import APIRouter, Depends, HTTPException
from app.middleware.auth import get_current_user
from app.core.config import settings
from app.db.firestore import get_db

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/scriptures")
async def list_scriptures(user: dict = Depends(get_current_user)):
    """List all scriptures (admin only)."""
    if user.get("uid") != settings.ADMIN_UID or not settings.ADMIN_UID:
        raise HTTPException(status_code=403, detail="Admin access required")

    db = get_db()
    docs = db.collection("scriptures").stream()
    scriptures = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        scriptures.append(data)

    return {"scriptures": scriptures}


@router.delete("/scriptures/{scripture_id}")
async def delete_scripture(scripture_id: str, user: dict = Depends(get_current_user)):
    """Delete a scripture and all its chunks (admin only)."""
    if user.get("uid") != settings.ADMIN_UID or not settings.ADMIN_UID:
        raise HTTPException(status_code=403, detail="Admin access required")

    db = get_db()
    scripture_ref = db.collection("scriptures").document(scripture_id)
    scripture_doc = scripture_ref.get()

    if not scripture_doc.exists:
        raise HTTPException(status_code=404, detail="Scripture not found")

    # Delete all chunks for this scripture
    chunks = db.collection("scripture_chunks").where(
        filter=("scriptureId", "==", scripture_id)
    ).stream()

    batch = db.batch()
    count = 0
    for chunk in chunks:
        batch.delete(chunk.reference)
        count += 1
        if count % 490 == 0:
            batch.commit()
            batch = db.batch()

    # Delete the scripture document itself
    batch.delete(scripture_ref)
    batch.commit()

    return {"status": "deleted", "deletedChunks": count}
