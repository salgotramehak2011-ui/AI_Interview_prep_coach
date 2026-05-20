# Backend — AI Interview Preparation Coach

FastAPI application with RAG, LangChain chains, Ollama LLM, SQLite, and Loguru logging.

## Run

```bash
cd backend
python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
set PYTHONPATH=.
uvicorn app.main:app --reload --port 8000
```

## Ingestion

```bash
set PYTHONPATH=.
python -m app.rag.ingestion.ingest_ai_ml
python -m app.rag.ingestion.ingest_web_dev
python -m app.rag.ingestion.ingest_cybersecurity
```

## Environment

Copy `.env` and adjust `OLLAMA_BASE_URL`, models, and chunk settings.

## API Routes

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/health` | Health check |
| POST | `/api/v1/interview/start` | Start session |
| POST | `/api/v1/interview/answer` | Submit answer |
| GET | `/api/v1/interview/session/{id}` | Get session |
| POST | `/api/v1/rag/ingest` | Ingest documents |
| POST | `/api/v1/rag/retrieve` | Retrieve context |
| GET | `/api/v1/evaluation/analytics/{user_id}` | User analytics |
