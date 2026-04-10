# 🕉️ SanatanaGPT

**Try it here: [sanatangpt-ee992.web.app](https://sanatangpt-ee992.web.app)**

**Your Personal Guide to Hindu Wisdom** — powered by Gemini AI + Firestore Vector Search.

SanatanaGPT is a full-stack RAG (Retrieval-Augmented Generation) application that lets users ask questions about Hindu scriptures. It retrieves relevant passages from vectorized scripture chunks and uses Google Gemini to generate contextual answers.

## Architecture

```
┌─────────────────┐      ┌──────────────────────────┐
│   Next.js 16    │◄────►│   FastAPI + Uvicorn      │
│   React 19      │      │   Google Gemini 2.5      │
│   Firebase Auth │      │   Firestore Vector DB    │
│   Firestore SDK │      │   Firebase Admin SDK     │
└─────────────────┘      └──────────────────────────┘
     Frontend                    Backend
   (port 3000)                 (port 8000)
```

## Features

- 🔐 **Google Auth** — Firebase Authentication with Google Sign-In
- 💬 **AI Chat** — Conversational interface powered by Gemini 2.5 Flash
- 📚 **Scripture Library** — Public catalog of uploaded scriptures with search/filter
- 🔍 **RAG Pipeline** — Vector search over chunked scripture embeddings
- 📋 **Scripture Requests** — Users can request new scriptures; admin approves/rejects
- 🛡️ **Admin Panel** — Upload & vectorize scripture PDFs, manage requests
- 📱 **Mobile Responsive** — Sidebar converts to drawer on small screens

## Quick Start

### Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.10+
- A **Firebase project** with Authentication and Firestore enabled
- A **Gemini API key** from [Google AI Studio](https://aistudio.google.com/)

### 1. Backend Setup

```bash
cd backend
python -m venv venv
.\venv\Scripts\activate    # Windows
pip install -r requirements.txt
```

Create `backend/.env`:
```env
GEMINI_API_KEY="your-gemini-api-key"
FIREBASE_STORAGE_BUCKET="your-project.firebasestorage.app"
ADMIN_UID="your-firebase-admin-uid"
```

Place your Firebase service account key as `backend/serviceAccountKey.json`.

Start the backend:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Frontend Setup

```bash
cd frontend
npm install
```

Create `frontend/.env.local`:
```env
NEXT_PUBLIC_FIREBASE_API_KEY="your-firebase-api-key"
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN="your-project.firebaseapp.com"
NEXT_PUBLIC_FIREBASE_PROJECT_ID="your-project-id"
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET="your-project.firebasestorage.app"
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID="your-sender-id"
NEXT_PUBLIC_FIREBASE_APP_ID="your-app-id"
NEXT_PUBLIC_ADMIN_UID="your-firebase-admin-uid"
```

Start the frontend:
```bash
npm run dev
```

### 3. Open in Browser

Navigate to `http://localhost:3000`

## Environment Variable Checklist

### Backend (`backend/.env`)

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | ✅ | Google Gemini API key for AI generation and embeddings |
| `FIREBASE_STORAGE_BUCKET` | ✅ | Firebase Storage bucket URL (e.g. `project.firebasestorage.app`) |
| `ADMIN_UID` | ✅ | Firebase UID of the admin user |
| `FIREBASE_CREDENTIALS` | ⬜ | Path to service account JSON (default: `serviceAccountKey.json`) |

### Frontend (`frontend/.env.local`)

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXT_PUBLIC_FIREBASE_API_KEY` | ✅ | Firebase Web API key |
| `NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN` | ✅ | Firebase Auth domain |
| `NEXT_PUBLIC_FIREBASE_PROJECT_ID` | ✅ | Firebase project ID |
| `NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET` | ✅ | Firebase Storage bucket |
| `NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID` | ✅ | Firebase messaging sender ID |
| `NEXT_PUBLIC_FIREBASE_APP_ID` | ✅ | Firebase app ID |
| `NEXT_PUBLIC_ADMIN_UID` | ✅ | Must match `ADMIN_UID` in backend |

## Firestore Collections

| Collection | Purpose |
|------------|---------|
| `users/{uid}` | User profiles synced from Firebase Auth |
| `users/{uid}/conversations/{id}` | Chat conversations |
| `users/{uid}/conversations/{id}/messages/{id}` | Chat messages |
| `scriptures/{id}` | Uploaded scripture metadata |
| `scripture_chunks/{id}` | Vectorized scripture text chunks with embeddings |
| `scripture_requests/{id}` | User-submitted scripture requests |

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/health` | ❌ | Health check |
| GET | `/api/scriptures/` | ❌ | List all scriptures (public) |
| GET | `/api/scriptures/{id}/download` | ❌ | Download scripture PDF |
| PUT | `/api/scriptures/{id}` | 🛡️ | Update scripture metadata (admin) |
| DELETE | `/api/scriptures/{id}` | 🛡️ | Delete scripture + chunks (admin) |
| POST | `/api/users/sync` | ✅ | Sync Firebase user profile |
| GET | `/api/conversations` | ✅ | List user's conversations |
| POST | `/api/conversations` | ✅ | Create new conversation |
| DELETE | `/api/conversations/{id}` | ✅ | Delete conversation |
| POST | `/api/chat/{convId}` | ✅ | Send message, get AI response |
| POST | `/api/requests/` | ✅ | Submit scripture request |
| GET | `/api/requests/` | ✅ | List own requests |
| GET | `/api/requests/all` | 🛡️ | List all pending (admin) |
| PATCH | `/api/requests/{id}/approve` | 🛡️ | Approve request (admin) |
| PATCH | `/api/requests/{id}/reject` | 🛡️ | Reject request (admin) |
| POST | `/api/admin/scriptures` | 🛡️ | Upload & vectorize scripture (admin) |

## License

MIT