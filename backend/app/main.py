from pathlib import Path
import uuid
import json
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.models.schemas import ChatRequest, ChatResponse, RouteRequest, UploadResponse
from app.services.provider import AIProvider, AIProviderError
from app.services.documents import SUPPORTED, safe_name, extract_text, chunk_text, new_id
from app.agents.orchestrator import Orchestrator

app = FastAPI(title=settings.app_name, version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[x.strip() for x in settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path(settings.upload_dir)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
DOCS: dict[str, dict] = {}
CONVERSATIONS: dict[str, list[dict]] = {}

provider = AIProvider()
orchestrator = Orchestrator(provider)

@app.get("/api/health")
def health():
    return {"status": "ok", "ai_configured": bool(settings.ai_base_url and settings.ai_model and settings.ai_api_key)}

@app.get("/api/model-info")
def model_info():
    return {"provider_configured": bool(settings.ai_base_url and settings.ai_api_key), "model": settings.ai_model or None}

@app.post("/api/agents/route")
def route(req: RouteRequest):
    return {"agent": orchestrator.route(req.message)}

@app.post("/api/upload", response_model=UploadResponse)
async def upload(file: UploadFile = File(...)):
    name = safe_name(file.filename or "upload")
    suffix = Path(name).suffix.lower()
    if suffix not in SUPPORTED:
        raise HTTPException(400, "Unsupported file type.")
    data = await file.read()
    if len(data) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(413, f"File exceeds {settings.max_upload_mb} MB limit.")
    doc_id = new_id()
    path = UPLOAD_DIR / f"{doc_id}{suffix}"
    path.write_bytes(data)
    text, pages = extract_text(path)
    DOCS[doc_id] = {
        "id": doc_id, "filename": name, "content_type": file.content_type or SUPPORTED[suffix],
        "size": len(data), "path": str(path), "text": text,
        "chunks": chunk_text(text) if text else [],
        "pages": pages,
    }
    return UploadResponse(id=doc_id, filename=name, content_type=file.content_type or SUPPORTED[suffix], size=len(data), pages=pages)

@app.get("/api/documents")
def documents():
    return [{k: v[k] for k in ("id", "filename", "content_type", "size", "pages")} for v in DOCS.values()]

@app.get("/api/documents/{doc_id}")
def document(doc_id: str):
    if doc_id not in DOCS:
        raise HTTPException(404, "Document not found.")
    d = DOCS[doc_id]
    return {k: d[k] for k in ("id", "filename", "content_type", "size", "pages", "chunks")}

@app.delete("/api/documents/{doc_id}")
def delete_document(doc_id: str):
    d = DOCS.pop(doc_id, None)
    if not d:
        raise HTTPException(404, "Document not found.")
    try:
        Path(d["path"]).unlink(missing_ok=True)
    except OSError:
        pass
    return {"deleted": True}

@app.post("/api/conversations")
def create_conversation():
    cid = uuid.uuid4().hex
    CONVERSATIONS[cid] = []
    return {"id": cid}

@app.get("/api/conversations")
def conversations():
    return [{"id": k, "messages": len(v)} for k, v in CONVERSATIONS.items()]

@app.get("/api/conversations/{cid}")
def conversation(cid: str):
    if cid not in CONVERSATIONS:
        raise HTTPException(404, "Conversation not found.")
    return {"id": cid, "messages": CONVERSATIONS[cid]}

@app.delete("/api/conversations/{cid}")
def delete_conversation(cid: str):
    CONVERSATIONS.pop(cid, None)
    return {"deleted": True}

@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    cid = req.conversation_id or uuid.uuid4().hex
    CONVERSATIONS.setdefault(cid, [])
    has_docs = bool(req.document_ids)
    agent = orchestrator.route(req.message, bool(req.image_data_url), has_docs)

    contexts = []
    citations = []
    for doc_id in req.document_ids:
        d = DOCS.get(doc_id)
        if not d:
            continue
        # Simple lexical retrieval for the starter. Replace with pgvector embeddings in production.
        terms = [x.lower() for x in req.message.split() if len(x) > 3]
        chunks = d["chunks"]
        ranked = sorted(chunks, key=lambda c: sum(t in c.lower() for t in terms), reverse=True)[:5]
        for chunk in ranked:
            contexts.append(f"[{d['filename']}] {chunk}")
        citations.append({"document_id": d["id"], "filename": d["filename"], "pages": d["pages"]})

    CONVERSATIONS[cid].append({"role": "user", "content": req.message})
    try:
        answer = await orchestrator.answer(req.message, "\n\n".join(contexts), req.image_data_url, agent)
    except AIProviderError as e:
        answer = str(e) + "\n\nThe application architecture is ready; configure a compatible AI provider to enable live responses."
    except Exception:
        answer = "The AI request could not be completed. Please retry."
    CONVERSATIONS[cid].append({"role": "assistant", "content": answer, "agent": agent})
    return ChatResponse(answer=answer, agent=agent, citations=citations, conversation_id=cid)
