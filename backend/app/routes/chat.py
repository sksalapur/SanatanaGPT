from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
from app.middleware.auth import get_current_user
from app.db.firestore import get_db, utc_now
from google import genai
import os
import asyncio
from google.cloud.firestore_v1.vector import Vector
from google.cloud.firestore_v1.base_vector_query import DistanceMeasure
from firebase_admin import firestore
from app.core.config import settings

if settings.GEMINI_API_KEY:
    os.environ["GEMINI_API_KEY"] = settings.GEMINI_API_KEY

router = APIRouter(prefix="/api", tags=["chat_and_conversations"])

class ChatMessage(BaseModel):
    content: str

class RenameConversationRequest(BaseModel):
    title: str

@router.get("/conversations")
async def get_conversations(user: dict = Depends(get_current_user)):
    db = get_db()
    uid = user.get("uid")
    docs = db.collection("users").document(uid).collection("conversations").order_by("updatedAt", direction=firestore.Query.DESCENDING).stream()
    
    convs = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        convs.append(data)
        
    return {"conversations": convs}

@router.post("/conversations")
async def create_conversation(user: dict = Depends(get_current_user)):
    db = get_db()
    uid = user.get("uid")
    conv_ref = db.collection("users").document(uid).collection("conversations").document()
    
    now = utc_now()
    conv_data = {
        "title": "New Conversation",
        "createdAt": now,
        "updatedAt": now,
        "uid": uid
    }
    conv_ref.set(conv_data)
    
    return {"convId": conv_ref.id, "title": "New Conversation"}

@router.patch("/conversations/{convId}/rename")
async def rename_conversation(convId: str, payload: RenameConversationRequest, user: dict = Depends(get_current_user)):
    new_title = payload.title.strip()
    if not new_title:
        raise HTTPException(status_code=400, detail="Title cannot be empty")
        
    db = get_db()
    uid = user.get("uid")
    conv_ref = db.collection("users").document(uid).collection("conversations").document(convId)
    
    doc = conv_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Conversation not found")
        
    conv_ref.update({
        "title": new_title,
        "updatedAt": utc_now()
    })
    
    return {"status": "success", "title": new_title}

@router.delete("/conversations/{convId}")
async def delete_conversation(convId: str, user: dict = Depends(get_current_user)):
    db = get_db()
    uid = user.get("uid")
    conv_ref = db.collection("users").document(uid).collection("conversations").document(convId)
    
    doc = conv_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Conversation not found")
        
    messages_ref = conv_ref.collection("messages").limit(100).stream()
    batch = db.batch()
    msg_count = 0
    for msg in messages_ref:
        batch.delete(msg.reference)
        msg_count += 1
    
    batch.delete(conv_ref)
    batch.commit()
    
    return {"status": "deleted", "deleted_messages": msg_count}

async def background_generate_title(uid: str, convId: str, db, first_message: str):
    """Generate a short, smart title using Groq, then save it to Firestore."""
    title = None
    
    if settings.GROQ_API_KEY:
        try:
            from groq import AsyncGroq
            groq_client = AsyncGroq(api_key=settings.GROQ_API_KEY)
            resp = await groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a chat title generator. Create a concise title of "
                            "3 to 4 words MAXIMUM for a conversation based on the user's question. "
                            "Respond with ONLY the title. No quotes, no punctuation, no explanation."
                        )
                    },
                    {"role": "user", "content": first_message}
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.5,
                max_tokens=20,
            )
            title = resp.choices[0].message.content.strip()
            print(f"[Title] Generated: '{title}'")
        except Exception as e:
            print(f"[Title] Groq failed, using fallback: {e}")
    
    # Fallback: clean word-truncation
    if not title:
        words = first_message.split()[:6]
        title = " ".join(words) + ("..." if len(first_message.split()) > 6 else "")
    
    conv_ref = db.collection("users").document(uid).collection("conversations").document(convId)
    conv_ref.update({"title": title, "updatedAt": utc_now()})


async def generate_ai_response(input_text: str, context_str: str, history: str, has_context: bool) -> str:
    """Call LLM and return full text response. Uses Groq (primary) with Gemini (fallback)."""
    
    system_prompt = "You are SanatanaGPT, an AI assistant and scholarly guide on Hindu scriptures. Structure your answers beautifully using rich Markdown."
    
    if has_context:
        user_prompt = f"""Below is some scripture context that MAY OR MAY NOT be relevant.
<context>
{context_str}
</context>

Instructions:
1. If the <context> provides the answer or helpful information, use it and cite the text properly (e.g., *(Bhagavad Gita)*).
2. If the <context> DOES NOT contain the answer (for example, if the user asks about geography, general knowledge, or random facts), you MUST IGNORE the context entirely and use your general knowledge.
3. ABSOLUTE RULE: If you use your general knowledge, DO NOT apologize. DO NOT mention the scripture. DO NOT say "The provided context does not contain..." or anything similar. Pretend you never received the <context> at all. Just give the answer directly.

Conversation history:
{history}

User Question: {input_text}"""
    else:
        user_prompt = f"""The user asked a question for which no directly relevant scripture passages were found in the database.

Provide a thoughtful answer from your general knowledge. Be clear and honest. Structure your answer beautifully using rich Markdown.

Conversation history:
{history}

User: {input_text}"""

    # --- Provider 1: Groq (Primary) ---
    if settings.GROQ_API_KEY:
        try:
            from groq import AsyncGroq
            groq_client = AsyncGroq(api_key=settings.GROQ_API_KEY)
            
            for attempt in range(3):
                try:
                    chat_completion = await groq_client.chat.completions.create(
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        model="llama-3.3-70b-versatile",
                        temperature=0.7,
                        max_tokens=4096,
                    )
                    result = chat_completion.choices[0].message.content
                    print(f"[LLM] Groq llama-3.3-70b responded successfully")
                    return result or ""
                except Exception as e:
                    error_str = str(e)
                    if any(k in error_str for k in ["429", "rate_limit", "503", "overloaded"]):
                        wait_time = (2 ** attempt) + 1
                        print(f"[Groq] Attempt {attempt+1} rate limited, retrying in {wait_time}s...")
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        print(f"[Groq] Non-retryable error: {e}")
                        break  # Fall through to Gemini
        except Exception as e:
            print(f"[Groq] Provider failed: {e}")

    # --- Provider 2: Gemini (Fallback) ---
    print("[LLM] Falling back to Gemini...")
    full_prompt = f"{system_prompt}\n\n{user_prompt}"
    client = genai.Client()
    
    models_to_try = ["gemini-2.5-flash", "gemini-2.0-flash"]
    last_error = None
    
    for model_name in models_to_try:
        for attempt in range(3):
            try:
                response = await client.aio.models.generate_content(
                    model=model_name,
                    contents=full_prompt
                )
                print(f"[LLM] Gemini {model_name} responded successfully")
                return response.text or ""
            except Exception as e:
                last_error = e
                error_str = str(e)
                is_retryable = any(k in error_str for k in ["503", "UNAVAILABLE", "429", "RESOURCE_EXHAUSTED", "overloaded"])
                
                if is_retryable:
                    import re
                    delay_match = re.search(r'retryDelay.*?(\d+)', error_str)
                    wait_time = int(delay_match.group(1)) if delay_match else (2 ** attempt) + 1
                    wait_time = min(wait_time, 30)
                    print(f"[Gemini] {model_name} attempt {attempt+1} transient error, retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    raise
        print(f"[Gemini] All retries exhausted for {model_name}, trying next model...")
    
    raise last_error

@router.post("/chat/{convId}")
async def send_chat_message(convId: str, payload: ChatMessage, background_tasks: BackgroundTasks, user: dict = Depends(get_current_user)):
    db = get_db()
    uid = user.get("uid")
    conv_ref = db.collection("users").document(uid).collection("conversations").document(convId)
    
    if not conv_ref.get().exists:
        raise HTTPException(status_code=404, detail="Conversation not found")
        
    messages_ref = conv_ref.collection("messages")
    now = utc_now()
    
    # 1. Embed user message using local model
    query_vector = None
    try:
        from app.services.embedding import get_embedding_model
        embed_model = get_embedding_model()
        query_vector = [float(v) for v in embed_model.encode(payload.content)]
    except Exception as e:
        print(f"Embedding error: {e}")

    # 2. Vector Search Retrieval — track sources and confidence
    context_str = ""
    sources = []
    has_scripture_match = False
    MATCH_THRESHOLD = 0.85  # cosine distance 0=identical, 1=orthogonal. 0.85 allows broad conceptual relevance

    if query_vector:
        try:
            results = db.collection("scripture_chunks").find_nearest(
                vector_field="embedding",
                query_vector=Vector(query_vector),
                distance_measure=DistanceMeasure.COSINE,
                limit=5,
                distance_result_field="vector_distance"
            ).stream()
            
            for match in results:
                data = match.to_dict()
                md = data.get("metadata", {})
                ch_title = md.get("title", "Unknown Scripture")
                text_content = data.get("text", "")
                chunk_index = data.get("chunkIndex", 0)
                scripture_id = data.get("scriptureId", "")
                distance = data.get("vector_distance", 1.0)

                print(f"[RAG] Chunk distance={distance:.4f} title={ch_title}")

                if distance < MATCH_THRESHOLD:
                    has_scripture_match = True
                    context_str += f"\n[Source: {ch_title}]\n{text_content}\n"
                    sources.append({
                        "type": "scripture",
                        "title": ch_title,
                        "scriptureId": scripture_id,
                        "chunkIndex": chunk_index,
                        "snippet": text_content[:200] + "..." if len(text_content) > 200 else text_content,
                    })
        except Exception as e:
            print(f"[Vector Search Error]: {e}")
            context_str = ""
    
    # 3. Extract History
    history_str = ""
    past_msgs = messages_ref.order_by("timestamp", direction=firestore.Query.DESCENDING).limit(4).stream()
    past_list = []
    for msg in past_msgs:
        past_list.append(msg.to_dict())
    
    for msg in reversed(past_list):
        history_str += f"{msg['role'].capitalize()}: {msg['content']}\n"
        
    # 4. Save user message to Firestore
    user_msg_ref = messages_ref.document()
    user_msg_ref.set({
        "role": "user",
        "content": payload.content,
        "timestamp": now
    })
    
    conv_ref.update({"updatedAt": utc_now()})
    
    # 5. Generate AI response
    try:
        ai_text = await generate_ai_response(payload.content, context_str, history_str, has_scripture_match)
    except Exception as e:
        ai_text = f"[AI Error]: {str(e)}"
    
    # 6. Save assistant message with sources metadata
    assist_msg_ref = messages_ref.document()
    assist_msg_ref.set({
        "role": "assistant",
        "content": ai_text,
        "sources": sources,
        "has_scripture_match": has_scripture_match,
        "timestamp": utc_now()
    })
    
    # 7. Auto-title logic
    conv_doc = conv_ref.get().to_dict()
    if conv_doc.get("title") == "New Conversation":
        background_tasks.add_task(background_generate_title, uid, convId, db, payload.content)
        
    return {"content": ai_text, "sources": sources, "has_scripture_match": has_scripture_match}
