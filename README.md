# AI Interview Preparation Coach

Production-ready AI-powered interview preparation platform with **RAG**, **Ollama (Mistral)**, **FastAPI**, and **Streamlit**.

## Features

- **Multi-domain interviews**: AI/ML, Web Development, Cybersecurity
- **RAG pipeline**: Domain-specific ChromaDB vector stores with SentenceTransformers embeddings
- **Adaptive questioning**: Dynamic questions, follow-ups, difficulty levels
- **Answer evaluation**: Technical correctness, clarity, confidence, depth
- **Weak area tracking**: SQLite persistence + learning roadmap
- **Analytics dashboard**: Plotly charts, trends, domain progress

## Architecture

```
Streamlit UI  →  FastAPI Backend  →  LangChain Chains  →  Ollama (Mistral/Phi3)
                      ↓
              ChromaDB (per domain) + SQLite (sessions/scores)
```

## Prerequisites

- Python 3.10+
- [Ollama](https://ollama.com/) with models: `mistral`, `phi3` (fallback)
- 8GB+ RAM recommended (embeddings + LLM)

## Quick Start

### 1. Ollama

```bash
ollama pull mistral
ollama pull phi3
ollama serve
```

### 2. Backend

```bash
cd AI_Interview_Preparation_Coach/backend
python -m venv venv
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate
pip install -r requirements.txt
copy .env .env   # already provided
```

### 3. Ingest RAG documents

```bash
# From backend/ with venv active
set PYTHONPATH=.
python -m app.rag.ingestion.ingest_ai_ml
python -m app.rag.ingestion.ingest_web_dev
python -m app.rag.ingestion.ingest_cybersecurity
```

Or via API after starting the server:

```bash
curl -X POST http://localhost:8000/api/v1/rag/ingest \
  -H "Content-Type: application/json" \
  -d "{\"domain\": \"ai_ml\", \"force_rebuild\": true}"
```

### 4. Run backend

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API docs: http://localhost:8000/docs

### 5. Run frontend

```bash
cd ../frontend
pip install -r requirements.txt
streamlit run streamlit_app.py
```

UI: http://localhost:8501

## Docker

```bash
docker compose up -d
# Pull models inside ollama container:
docker exec -it interview_coach_ollama ollama pull mistral
docker exec -it interview_coach_ollama ollama pull phi3
```

## Sample API Calls

**Health**
```bash
curl http://localhost:8000/api/v1/health
```

**Start interview**
```bash
curl -X POST http://localhost:8000/api/v1/interview/start \
  -H "Content-Type: application/json" \
  -d "{\"user_id\": \"user1\", \"domain\": \"ai_ml\", \"difficulty\": \"intermediate\", \"num_questions\": 5}"
```

**Submit answer**
```bash
curl -X POST http://localhost:8000/api/v1/interview/answer \
  -H "Content-Type: application/json" \
  -d "{\"session_id\": \"<SESSION_ID>\", \"answer\": \"Gradient descent minimizes loss by...\"}"
```

**Analytics**
```bash
curl http://localhost:8000/api/v1/evaluation/analytics/user1
```

## Adding Domain Documents

Place PDF or TXT files in:

- `backend/datasets/ai_ml/`
- `backend/datasets/web_dev/`
- `backend/datasets/cybersecurity/`

Re-run ingestion for that domain.

## Tests

```bash
cd backend
set PYTHONPATH=.
pytest app/tests/ -v
```

## Project Structure

See repository tree — clean separation of `frontend/`, `backend/app/rag/`, `chains/`, `prompts/`, `evaluation/`, `memory/`, and per-domain vector stores.

## License

MIT
