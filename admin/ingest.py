#!/usr/bin/env python3
"""
SanatanaGPT Local Admin Ingestion CLI

Usage:
  python ingest.py --file "gita.pdf" --title "Bhagavad Gita" --language "Sanskrit"
  python ingest.py --file "gita.pdf" --title "Bhagavad Gita" --language "Sanskrit" --description "Commentary by Swami Mukundananda"
  python ingest.py --wipe
  python ingest.py --approve <request_id>
"""
import argparse
import os
import sys
import time
import asyncio
from pathlib import Path
from datetime import datetime, timezone

# Load .env from this directory or parent
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env")
load_dotenv(Path(__file__).parent.parent / "backend" / ".env")

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
if not GEMINI_API_KEY:
    print("ERROR: GEMINI_API_KEY not set. Add it to admin/.env or backend/.env")
    sys.exit(1)
os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY

# Firebase init — uses GOOGLE_APPLICATION_CREDENTIALS or local serviceAccountKey.json
import firebase_admin
from firebase_admin import credentials, firestore, storage

SERVICE_ACCOUNT_PATH = os.environ.get(
    "GOOGLE_APPLICATION_CREDENTIALS",
    str(Path(__file__).parent.parent / "backend" / "serviceAccountKey.json")
)
STORAGE_BUCKET = os.environ.get("FIREBASE_STORAGE_BUCKET", "sanatangpt-ee992.firebasestorage.app")

if not firebase_admin._apps:
    cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
    firebase_admin.initialize_app(cred, {"storageBucket": STORAGE_BUCKET})

db = firestore.client()

# Local embedding client
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-mpnet-base-v2')

# Text processing
import fitz  # pymupdf
from langchain_text_splitters import RecursiveCharacterTextSplitter
from google.cloud.firestore_v1.vector import Vector

# ─── Embedding Helper ─────────────────────────────────────────────
EMBED_MODEL = "all-mpnet-base-v2"
EMBED_DIMS = 768
EMBED_BATCH_SIZE = 50  # Huge batch size since it's local GPU/CPU hardware!

async def embed_batch(texts: list[str]) -> list[list[float]]:
    """Embed a batch of texts instantly using local hardware."""
    # sentence-transformers encode returns numpy arrays, we convert them to python lists
    embeddings = model.encode(texts)
    return [e.tolist() for e in embeddings]

# ─── File Reading ─────────────────────────────────────────────────
def read_file(filepath: str) -> str:
    """Extract text from PDF or TXT file."""
    path = Path(filepath)
    if not path.exists():
        print(f"ERROR: File not found: {filepath}")
        sys.exit(1)

    if path.suffix.lower() == ".pdf":
        doc = fitz.open(str(path))
        text = ""
        for page in doc:
            text += page.get_text()
        print(f"  📄 Extracted {len(text):,} characters from {len(doc)} PDF pages")
        return text
    else:
        text = path.read_text(encoding="utf-8", errors="ignore")
        print(f"  📄 Read {len(text):,} characters from text file")
        return text


# ─── Ingestion Pipeline ──────────────────────────────────────────
async def ingest(filepath: str, title: str, language: str, description: str = ""):
    """Full ingestion pipeline: read → chunk → embed → upload to Firestore."""
    start = time.time()

    print(f"\n{'='*60}")
    print(f"  INGESTING: {title}")
    print(f"  File: {filepath}")
    print(f"  Language: {language}")
    print(f"{'='*60}\n")

    # 1. Read file
    print("Step 1/6: Reading file...")
    text = read_file(filepath)

    # 2. Chunk
    print("Step 2/6: Chunking text...")
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    chunks = splitter.split_text(text)
    print(f"  ✂️  Split into {len(chunks)} chunks")

    # 3. Create scripture document
    print("Step 3/6: Creating scripture document in Firestore...")
    scripture_ref = db.collection("scriptures").document()
    scripture_id = scripture_ref.id
    storage_path = f"scriptures/{Path(filepath).name}"

    scripture_ref.set({
        "title": title,
        "language": language,
        "author": author,
        "description": description,
        "vectorized": False,
        "storagePath": storage_path,
        "localFilePath": str(Path(filepath).resolve()),  # absolute path for local serving
        "addedAt": datetime.now(timezone.utc),
        "chunkCount": len(chunks)
    })
    print(f"  📝 Scripture ID: {scripture_id}")

    # 4. Upload file to Firebase Storage
    print("Step 4/6: Uploading file to Firebase Storage...")
    try:
        bucket = storage.bucket()
        blob = bucket.blob(storage_path)
        blob.upload_from_filename(filepath)
        print(f"  ☁️  Uploaded to gs://{STORAGE_BUCKET}/{storage_path}")
    except Exception as e:
        print(f"  ⚠️  Storage upload failed (non-fatal): {e}")

    # 5. Embed and write chunks
    print(f"Step 5/6: Embedding and uploading {len(chunks)} chunks...")
    batch_obj = db.batch()
    op_count = 0
    total_written = 0

    for i in range(0, len(chunks), EMBED_BATCH_SIZE):
        chunk_batch = chunks[i:i + EMBED_BATCH_SIZE]
        embeddings = await embed_batch(chunk_batch)

        for j, embedding in enumerate(embeddings):
            if op_count >= 490:
                batch_obj.commit()
                batch_obj = db.batch()
                op_count = 0

            global_idx = i + j
            chunk_id = f"{scripture_id}_chunk_{global_idx}"
            chunk_ref = db.collection("scripture_chunks").document(chunk_id)

            batch_obj.set(chunk_ref, {
                "scriptureId": scripture_id,
                "text": chunk_batch[j],
                "embedding": Vector(embedding),
                "chunkIndex": global_idx,
                "metadata": {
                    "title": title,
                    "language": language,
                    "author": author
                }
            })
            op_count += 1
            total_written += 1

        pct = min(100, int((i + EMBED_BATCH_SIZE) / len(chunks) * 100))
        print(f"  📊 Progress: {pct}% ({total_written}/{len(chunks)} chunks)")

    if op_count > 0:
        batch_obj.commit()

    # 6. Mark vectorized
    print("Step 6/6: Marking scripture as vectorized...")
    scripture_ref.update({"vectorized": True})

    elapsed = time.time() - start
    print(f"\n{'='*60}")
    print(f"  ✅ SUCCESS: {total_written} chunks embedded and uploaded")
    print(f"  ⏱️  Time: {elapsed:.1f}s")
    print(f"  🆔 Scripture ID: {scripture_id}")
    print(f"{'='*60}\n")


# ─── Wipe Command ────────────────────────────────────────────────
def wipe():
    """Delete ALL scripture_chunks and reset vectorized=false on all scriptures."""
    print("\n⚠️  WIPE MODE: This will delete ALL scripture chunks from Firestore.")
    print("Executing wipe programmatically...")

    print("Deleting all scripture_chunks...")
    chunks = db.collection("scripture_chunks").stream()
    batch = db.batch()
    count = 0
    for doc in chunks:
        batch.delete(doc.reference)
        count += 1
        if count % 490 == 0:
            batch.commit()
            batch = db.batch()
            print(f"  Deleted {count} chunks so far...")

    if count % 490 != 0:
        batch.commit()

    print(f"  🗑️  Deleted {count} chunk documents.")

    print("Resetting vectorized=false on all scriptures...")
    scriptures = db.collection("scriptures").stream()
    for s in scriptures:
        s.reference.update({"vectorized": False, "chunkCount": 0})
    print("  ✅ All scriptures reset.\n")


# ─── Approve Command ────────────────────────────────────────────
async def approve_request(request_id: str):
    """Approve a user's scripture request and run ingestion."""
    print(f"\nFetching request: {request_id}...")
    req_ref = db.collection("scripture_requests").document(request_id)
    req_doc = req_ref.get()

    if not req_doc.exists:
        print(f"ERROR: Request '{request_id}' not found in Firestore.")
        sys.exit(1)

    data = req_doc.to_dict()
    title = data.get("title", "Unknown")
    language = data.get("language", "")
    description = data.get("description", "")
    requested_by = data.get("requestedByEmail", data.get("requestedBy", "Unknown"))
    ref_url = data.get("referenceUrl", "")
    status = data.get("status", "unknown")

    if status != "pending":
        print(f"WARNING: Request status is '{status}', not 'pending'.")

    print(f"\n  Title:        {title}")
    print(f"  Language:     {language}")
    print(f"  Description:  {description}")
    print(f"  Requested by: {requested_by}")
    if ref_url:
        print(f"  Reference:    {ref_url}")

    confirm = input(f"\nApprove request for '{title}' by {requested_by}? [y/n]: ")
    if confirm.strip().lower() != "y":
        print("Aborted.")
        return

    filepath = input("Enter local file path to the PDF/TXT: ").strip().strip('"')
    if not Path(filepath).exists():
        print(f"ERROR: File not found: {filepath}")
        sys.exit(1)

    # Run standard ingestion
    await ingest(filepath, title, language or "English", description, author="")

    # Update request status
    req_ref.update({
        "status": "approved",
        "approvedAt": datetime.now(timezone.utc)
    })
    print(f"✅ Request '{request_id}' marked as approved in Firestore.\n")


# ─── CLI ──────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="SanatanaGPT Admin Ingestion CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python ingest.py --file "gita.pdf" --title "Bhagavad Gita" --language "Sanskrit"
  python ingest.py --wipe
  python ingest.py --approve abc123
        """
    )

    parser.add_argument("--file", type=str, help="Path to PDF or TXT file to ingest")
    parser.add_argument("--title", type=str, help="Scripture title")
    parser.add_argument("--language", type=str, default="English", help="Language (default: English)")
    parser.add_argument("--author", type=str, default="", help="Optional Author")
    parser.add_argument("--description", type=str, default="", help="Optional description")
    parser.add_argument("--wipe", action="store_true", help="Wipe all chunks and reset scriptures")
    parser.add_argument("--approve", type=str, metavar="REQUEST_ID", help="Approve a pending scripture request")

    args = parser.parse_args()

    if args.wipe:
        wipe()
    elif args.approve:
        asyncio.run(approve_request(args.approve))
    elif args.file:
        if not args.title:
            print("ERROR: --title is required when using --file")
            sys.exit(1)
        asyncio.run(ingest(args.file, args.title, args.language, args.description, args.author))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
