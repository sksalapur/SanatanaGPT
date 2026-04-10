import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import Optional
from app.db.firestore import get_db
from app.middleware.auth import get_current_user
from app.core.config import settings
from firebase_admin import storage

router = APIRouter(prefix="/api/scriptures", tags=["scriptures"])

@router.get("/")
async def get_scriptures():
    """Public endpoint — no auth required. Lists all scriptures."""
    db = get_db()
    docs = db.collection("scriptures").order_by("addedAt", direction="DESCENDING").stream()
    
    scriptures = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        # Convert timestamps to ISO strings for JSON serialization
        if data.get("addedAt"):
            data["addedAt"] = data["addedAt"].isoformat() if hasattr(data["addedAt"], "isoformat") else str(data["addedAt"])
        scriptures.append(data)
        
    return {"scriptures": scriptures}

@router.delete("/{scriptureId}")
async def delete_scripture(scriptureId: str, user: dict = Depends(get_current_user)):
    """Admin-only endpoint to completely delete a scripture, its chunks, and its file."""
    admin_uid = settings.ADMIN_UID
    if not admin_uid or user.get("uid") != admin_uid:
        raise HTTPException(status_code=403, detail=f"Forbidden. Admin access required. Your UID: {user.get('uid')}")
        
    db = get_db()
    scripture_ref = db.collection("scriptures").document(scriptureId)
    doc = scripture_ref.get()
    
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Scripture not found")
        
    data = doc.to_dict()
    
    # 1. Delete chunks
    chunks = db.collection("scripture_chunks").where("scriptureId", "==", scriptureId).stream()
    batch = db.batch()
    count = 0
    for chunk in chunks:
        batch.delete(chunk.reference)
        count += 1
        if count % 490 == 0:
            batch.commit()
            batch = db.batch()
    if count % 490 != 0:
        batch.commit()
        
    # 2. Delete file from Storage
    storage_path = data.get("storagePath")
    if storage_path:
        try:
            bucket = storage.bucket()
            blob = bucket.blob(storage_path)
            if blob.exists():
                blob.delete()
        except Exception as e:
            print(f"Failed to delete storage file {storage_path}: {e}")
            
    # 3. Delete scripture document
    scripture_ref.delete()
    
    
    return {"status": "deleted", "chunksDeleted": count, "scriptureId": scriptureId}


class ScriptureUpdate(BaseModel):
    title: str
    language: str
    author: Optional[str] = ""
    description: Optional[str] = ""

@router.put("/{scriptureId}")
async def update_scripture(scriptureId: str, update_data: ScriptureUpdate, user: dict = Depends(get_current_user)):
    """Admin-only endpoint to update a scripture's metadata and propagate it to all chunks."""
    admin_uid = settings.ADMIN_UID
    if not admin_uid or user.get("uid") != admin_uid:
        raise HTTPException(status_code=403, detail="Forbidden. Admin access required.")
        
    db = get_db()
    scripture_ref = db.collection("scriptures").document(scriptureId)
    doc = scripture_ref.get()
    
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Scripture not found")
        
    # 1. Update main scripture document
    scripture_ref.update({
        "title": update_data.title,
        "language": update_data.language,
        "author": update_data.author,
        "description": update_data.description
    })
    
    # 2. Update all associated vector chunks so RAG cites the correct title
    chunks = db.collection("scripture_chunks").where("scriptureId", "==", scriptureId).stream()
    batch = db.batch()
    count = 0
    for chunk in chunks:
        # We update the nested metadata
        batch.update(chunk.reference, {
            "metadata.title": update_data.title,
            "metadata.language": update_data.language,
            "metadata.author": update_data.author
        })
        count += 1
        if count % 490 == 0:
            batch.commit()
            batch = db.batch()
            
    if count % 490 != 0:
        batch.commit()
        
    return {"status": "updated", "scriptureId": scriptureId, "chunksUpdated": count}


@router.get("/{scriptureId}/download")
@router.get("/{scriptureId}/download/{filename}")
async def get_scripture_download_url(scriptureId: str, filename: str = None):
    """Return a download URL or serve the file directly."""
    from fastapi.responses import FileResponse
    db = get_db()
    doc = db.collection("scriptures").document(scriptureId).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Scripture not found")
    
    data = doc.to_dict()
    title = data.get("title", "Scripture")
    storage_path = data.get("storagePath")
    local_path = data.get("localFilePath")

    import datetime
    from fastapi.responses import RedirectResponse, FileResponse, StreamingResponse
    
    # Option 1: Native Firebase Storage Direct Stream (bypasses URL signing IAM errors)
    if storage_path:
        try:
            bucket = storage.bucket()
            blob = bucket.blob(storage_path)
            if blob.exists():
                def iterfile():
                    # Stream in 1MB chunks natively using the blob reader
                    with blob.open('rb') as f:
                        while chunk := f.read(1024 * 1024):
                            yield chunk
                
                return StreamingResponse(
                    iterfile(),
                    media_type="application/pdf",
                    headers={"Content-Disposition": f'attachment; filename="{title}.pdf"'}
                )
        except Exception as e:
            print(f"Storage proxy failed, falling back to local: {e}")

    # Option 2: Serve direct from admin's local filesystem (dev fallback)
    if local_path and os.path.exists(local_path):
        filename = os.path.basename(local_path)
        return FileResponse(
            path=local_path,
            media_type="application/pdf",
            filename=f"{title}.pdf",
            headers={"Content-Disposition": f'attachment; filename="{title}.pdf"'}
        )

    # Option 3: Clear user-facing error
    raise HTTPException(
        status_code=404,
        detail=f"'{title}' PDF is not available for download. Please ensure Firebase Storage is enabled and the file has been uploaded."
    )

