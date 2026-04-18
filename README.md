<h1 align="center">🕉️ SanatanaGPT</h1>

<p align="center">
  <strong>Have questions about life, dharma, or the universe? Search no more.</strong>
</p>

<p align="center">
  <em>An AI that doesn't just answer — it cites the exact Bhagavad Gita verse, the precise Upanishad passage, the specific Ramayana chapter.</em>
</p>

<p align="center">
  <a href="https://sanatangpt-ee992.web.app"><strong>🌐 Try it live → sanatangpt-ee992.web.app</strong></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Next.js-16-000000?logo=next.js&logoColor=white" />
  <img src="https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black" />
  <img src="https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/Google_Gemini-2.5_Flash-4285F4?logo=google&logoColor=white" />
  <img src="https://img.shields.io/badge/Firestore-Vector_Search-FFCA28?logo=firebase&logoColor=black" />
  <img src="https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white" />
  <img src="https://img.shields.io/badge/Status-Live_in_Production-brightgreen" />
</p>

---

## 💡 What Is This?

SanatanaGPT is a **full-stack Retrieval-Augmented Generation (RAG)** application that transforms how people learn from ancient Hindu scriptures. Instead of blindly generating answers like a generic chatbot, it:

1. **Embeds your question** into a 768-dimensional vector using `all-mpnet-base-v2`
2. **Searches vectorized scripture chunks** using Firestore's native `findNearest` cosine similarity
3. **Retrieves the most relevant passages** with a configurable distance threshold (0.85)
4. **Generates a grounded answer** using Groq LLaMA 3.3 70B (primary) or Google Gemini 2.5 Flash (fallback) — *always citing the source scripture*

> **"What does the Gita say about overcoming fear?"**
>
> SanatanaGPT doesn't hallucinate an answer. It finds the exact verses from the Bhagavad Gita stored in your Firestore vector database, feeds them as context to the LLM, and produces an answer that *cites Chapter 2, Verse 14* — because the data is really there.

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                         USER                                     │
│                          │                                       │
│                          ▼                                       │
│  ┌────────────────────────────────────────┐                      │
│  │   Next.js 16 Frontend                  │                      │
│  │   React 19 + Firebase Auth             │                      │
│  │   Chat UI · Scripture Library · Admin  │                      │
│  │   Deployed: Firebase Hosting           │                      │
│  └──────────────┬─────────────────────────┘                      │
│                 │ Authenticated API calls                        │
│                 ▼                                                │
│  ┌────────────────────────────────────────┐                      │
│  │   FastAPI Backend (Uvicorn)            │                      │
│  │                                        │                      │
│  │   1. Embed query → 768-dim vector      │                      │
│  │      (all-mpnet-base-v2, local)        │                      │
│  │                                        │                      │
│  │   2. findNearest() on Firestore        │                      │
│  │      → top 5 scripture chunks          │                      │
│  │      → cosine distance < 0.85          │                      │
│  │                                        │                      │
│  │   3. Generate answer with context      │                      │
│  │      → Groq LLaMA 3.3 70B (primary)    │                      │
│  │      → Gemini 2.5 Flash (fallback)     │                      │
│  │      → Auto-retry with backoff         │                      │
│  │                                        │                      │
│  │   4. Auto-generate chat title          │                      │
│  │      → Groq background task            │                      │
│  │                                        │                      │
│  │   Deployed: Hugging Face Spaces        │                      │
│  │   (Docker container)                   │                      │
│  └──────────────┬─────────────────────────┘                      │
│                 │                                                │
│                 ▼                                                │
│  ┌────────────────────────────────────────┐                      │
│  │   Firestore Vector Database            │                      │
│  │                                        │                      │
│  │   scripture_chunks collection          │                      │
│  │   ├── text: "Arjuna said: O Krishna…"  │                      │
│  │   ├── embedding: Vector([768 floats])  │                      │
│  │   ├── metadata.title: "Bhagavad Gita"  │                      │
│  │   └── chunkIndex: 42                   │                      │
│  └────────────────────────────────────────┘                      │
└──────────────────────────────────────────────────────────────────┘
```

### Why Firestore Vector Search instead of Pinecone/Weaviate?

Most RAG tutorials reach for purpose-built vector databases. SanatanaGPT deliberately uses **Firestore's native `findNearest`** vector search because:
- **Zero infrastructure** — no separate vector DB to provision, scale, or pay for
- **Single source of truth** — scripture metadata, chunks, embeddings, user data, and chat history all live in the same Firestore project
- **Firebase-native auth** — Firestore security rules protect all data; no cross-service token management
- **Production-ready at scale** — Firestore handles indexing, replication, and caching automatically

---

## ✨ Features

### 💬 AI Chat with Source Citations
- Conversational interface with full Markdown rendering
- Every answer includes source citations (e.g., *(Bhagavad Gita)*)
- If the question isn't about scriptures, the AI answers from general knowledge — **without apologizing or mentioning irrelevant context**
- Conversation history maintained in Firestore with 4-message context window

### 🧠 Smart Chat Naming
- New conversations auto-generate 3-4 word titles using **Groq LLaMA 3.3 70B** as a background task
- Fallback: clean word-truncation if Groq is unavailable

### 📚 Scripture Library
- Public catalog of all uploaded scriptures with search and filter
- Scripture request system — users can request new additions; admin approves/rejects
- Download original PDFs directly from Firebase Storage

### 🛡️ Admin Panel
- Upload PDF/TXT scriptures → auto-chunk with `RecursiveCharacterTextSplitter` (800 chars, 100 overlap) → embed with `all-mpnet-base-v2` → batch-write to Firestore with `Vector()` type
- Manage scripture metadata, delete scriptures with cascading chunk cleanup
- CLI ingestion tool (`admin/ingest.py`) for bulk local processing

### 🔄 Dual-LLM Failover
- **Primary**: Groq LLaMA 3.3 70B — fast, free-tier friendly, 3 retries with exponential backoff
- **Fallback**: Google Gemini 2.5 Flash → Gemini 2.0 Flash cascade — 3 retries each

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Frontend** | Next.js 16, React 19, TailwindCSS | SSR, responsive chat UI, sidebar navigation |
| **Auth** | Firebase Auth (Google Sign-In) | Zero-friction user onboarding + admin role gating |
| **Backend** | FastAPI + Uvicorn | Async Python API for RAG pipeline |
| **Embeddings** | `all-mpnet-base-v2` (768-dim, local) | Query + document embedding without API costs |
| **Vector DB** | Firestore `findNearest()` | Native cosine similarity search, zero infra overhead |
| **Primary LLM** | Groq LLaMA 3.3 70B Versatile | Fast inference, 4096 token responses |
| **Fallback LLM** | Google Gemini 2.5 Flash / 2.0 Flash | Redundancy when Groq is rate-limited |
| **Text Splitting** | LangChain `RecursiveCharacterTextSplitter` | Semantic chunking for optimal retrieval |
| **Containerization** | Docker + Docker Compose | Reproducible backend deployments |
| **Frontend Hosting** | Firebase Hosting | CDN-backed, auto-SSL |
| **Backend Hosting** | Hugging Face Spaces (Docker) | Free-tier GPU/CPU, persistent deployment |

---

## 📐 Project Structure

```
SanatanaGPT/
├── frontend/                    # Next.js 16 + React 19
│   ├── app/
│   │   ├── page.tsx             # Landing → redirect to chat
│   │   ├── chat/[id]/page.tsx   # Chat interface with RAG
│   │   ├── login/page.tsx       # Google Sign-In
│   │   ├── scriptures/page.tsx  # Public scripture library
│   │   └── admin/page.tsx       # Admin panel (gated)
│   ├── components/              # ChatLayout, Sidebar, ProtectedRoute
│   ├── contexts/                # AuthContext (Firebase)
│   └── firebase.ts              # Firebase client init
│
├── backend/                     # FastAPI + Uvicorn
│   ├── app/
│   │   ├── routes/
│   │   │   ├── chat.py          # RAG pipeline: embed → search → generate
│   │   │   ├── scriptures.py    # Public scripture CRUD
│   │   │   ├── admin.py         # Admin operations (gated by UID)
│   │   │   ├── requests.py      # Scripture request system
│   │   │   └── users.py         # User profile sync
│   │   ├── services/
│   │   │   └── embedding.py     # Thread-safe SentenceTransformer singleton
│   │   ├── middleware/
│   │   │   └── auth.py          # Firebase ID token verification
│   │   ├── core/
│   │   │   ├── config.py        # Pydantic settings (env vars)
│   │   │   └── firebase.py      # Firebase Admin SDK init
│   │   └── db/
│   │       └── firestore.py     # Firestore client + helpers
│   ├── Dockerfile               # Production container
│   └── requirements.txt
│
├── admin/
│   └── ingest.py                # CLI: PDF → chunk → embed → Firestore
│
├── docker-compose.yml           # Full-stack local orchestration
├── firebase.json                # Hosting + Firestore config
└── firestore.rules              # Security rules
```

---

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ · Python 3.10+ · Firebase project · Gemini API key

### Backend
```bash
cd backend
python -m venv venv && .\venv\Scripts\activate
pip install -r requirements.txt
# Create backend/.env with GEMINI_API_KEY, FIREBASE_STORAGE_BUCKET, ADMIN_UID
uvicorn app.main:app --port 8000 --reload
```

### Frontend
```bash
cd frontend && npm install
# Create frontend/.env.local with Firebase config
npm run dev
```

### Ingest a Scripture
```bash
cd admin
python ingest.py --file "gita.pdf" --title "Bhagavad Gita" --language "Sanskrit"
```

---

## 🔗 API Endpoints

| Method | Path | Auth | Description |
|--------|------|:----:|-------------|
| `GET` | `/health` | ❌ | Health check |
| `GET` | `/api/scriptures/` | ❌ | List all scriptures |
| `POST` | `/api/chat/{convId}` | ✅ | Send message → RAG → AI response with citations |
| `GET` | `/api/conversations` | ✅ | List user's conversations |
| `POST` | `/api/conversations` | ✅ | Create new conversation |
| `POST` | `/api/requests/` | ✅ | Submit scripture request |
| `POST` | `/api/admin/scriptures` | 🛡️ | Upload + vectorize scripture (admin) |
| `DELETE` | `/api/admin/scriptures/{id}` | 🛡️ | Delete scripture + chunks (admin) |

---

<p align="center">
  <strong>Ancient wisdom, modern intelligence.</strong><br/>
  <em>Ask anything. Get answers grounded in 5,000 years of scripture.</em>
</p>

<p align="center">
  Made with ❤️ by <a href="https://github.com/sksalapur">Shashank Salapur</a>
</p>
