# Keval Multi-Agent AI Platform

Production-oriented starter implementation for a multimodal multi-agent AI SaaS:
- Customer Support Agent
- Document/PDF Agent
- Vision Agent
- Research Agent
- Intelligent Orchestrator
- Chat history
- PDF/DOCX/TXT/CSV/image upload
- Basic document extraction + retrieval
- Model-provider abstraction
- React + TypeScript + Vite frontend
- FastAPI backend

> **GPT Astra 6:** This project does not invent an Astra 6 API. Set `AI_BASE_URL`, `AI_MODEL`, and `AI_API_KEY` for the actual provider you use. If no provider is configured, the UI still runs and the backend returns a clear configuration message instead of pretending that live AI is available.

## 1. Requirements

- Python 3.11+
- Node.js 20+
- npm
- Optional: an OpenAI-compatible AI provider
- Optional: PostgreSQL for production

## 2. Backend

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

## 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open the Vite URL shown in the terminal.

## 4. Environment

Copy `backend/.env.example` to `backend/.env`.

Important variables:
- `AI_BASE_URL` - actual provider endpoint
- `AI_MODEL` - actual model name
- `AI_API_KEY` - secret key
- `CORS_ORIGINS` - frontend origin

Never put the AI key in frontend code.

## 5. Architecture

```text
Browser
  |
  v
React/TypeScript
  |
  v
FastAPI
  |
  +--> Orchestrator
  |      +--> Support Agent
  |      +--> Document Agent
  |      +--> Vision Agent
  |      +--> Research Agent
  |
  +--> File Processor --> local uploads
  |
  +--> AI Provider Adapter
  |
  +--> SQLite (development)
          |
          +--> PostgreSQL/pgvector (production upgrade)
```

## 6. API

- `GET /api/health`
- `POST /api/chat`
- `POST /api/upload`
- `GET /api/documents`
- `GET /api/documents/{id}`
- `DELETE /api/documents/{id}`
- `GET /api/conversations`
- `POST /api/conversations`
- `GET /api/conversations/{id}`
- `DELETE /api/conversations/{id}`
- `POST /api/agents/route`
- `GET /api/model-info`

## 7. Security

The backend validates file extension, MIME type and size, keeps secrets server-side, sanitizes filenames, and treats extracted document text as untrusted context. For public deployment, add real authentication, object storage, PostgreSQL/pgvector, rate limiting, antivirus scanning and background jobs.

## 8. Production upgrades

1. PostgreSQL + pgvector
2. Auth provider/session management
3. S3-compatible object storage
4. Redis/Celery or a managed queue for large documents
5. Streaming provider adapter
6. OCR for scanned PDFs
7. Automated evaluation suite
8. Observability and usage metering
9. Human support escalation workflow

## 9. Project author

**Keval Patel** — GTU Diploma IT Minor Project / AI SaaS prototype.
