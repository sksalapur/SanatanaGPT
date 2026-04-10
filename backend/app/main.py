from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import chat, scriptures, requests, users, admin
from app.core.config import settings
import firebase_admin
from firebase_admin import credentials

# Initialize Firebase before routing starts
try:
    if not firebase_admin._apps:
        # Tries to use serviceAccountKey.json locally, or falls back to App Default Credentials in Cloud Run
        try:
            cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS)
            firebase_admin.initialize_app(cred, {'storageBucket': "sanatangpt-ee992.firebasestorage.app"})
        except Exception:
            # Fallback for Cloud Run when serviceAccountKey is ignored by docker
            firebase_admin.initialize_app(options={'storageBucket': "sanatangpt-ee992.firebasestorage.app"})
except Exception as e:
    print(f"Firebase Init Error: {e}")

app = FastAPI(
    title="SanatanaGPT API",
    description="Backend API for the SanatanaGPT Revamp",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://sanatangpt-ee992.web.app",
        "https://sanatangpt-ee992.firebaseapp.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)

app.include_router(users.router)
app.include_router(chat.router)
app.include_router(scriptures.router)
app.include_router(requests.router)
app.include_router(admin.router)

@app.get("/health")
def health_check():
    return {"status": "healthy"}
