from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import chat, scriptures, requests, users, admin
from app.core.config import settings
import firebase_admin
from firebase_admin import credentials
import os
import json

from app.core.firebase import init_firebase

# Initialize Firebase before routing starts
init_firebase()

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

@app.get("/")
def read_root():
    return {"message": "SanatanaGPT API is running. Access /docs for Swagger UI."}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
