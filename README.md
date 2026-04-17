# LexiDoc AI

**Intelligent Legal Document Analysis Platform**

FastAPI · LangGraph · OpenAI · Qdrant · Redis · PostgreSQL

---

## Overview

LexiDoc AI is a production-grade backend for intelligent legal document processing. It enables legal teams to upload, classify, embed, and conversationally query PDF legal documents using a Retrieval-Augmented Generation (RAG) pipeline powered by OpenAI and LangGraph.

Built with FastAPI, LexiDoc AI exposes a clean REST API secured with JWT authentication. Documents are classified automatically on upload, stored in a Qdrant vector database for semantic search, and chat sessions are persisted using Redis-backed LangGraph checkpointing.

---

## Key Features

- Automatic PDF classification into: **Court Order, Affidavit, Petition, Contract, Notice**
- Confidence-scored classification using structured LLM output
- Semantic vector search via Qdrant for context-aware question answering
- Conversational RAG pipeline built with LangGraph state machines
- Session memory with Redis-backed LangGraph checkpointing (24-hour TTL)
- JWT authentication with access and refresh token support
- Dashboard analytics: token usage, cost tracking, document type breakdown
- Metadata update API with real-time vector DB synchronization
- Full PostgreSQL persistence for users, documents, chat history, and costs

---

## Architecture

| Layer | Technology | Purpose |
|-------|-----------|---------|
| API Layer | FastAPI + Uvicorn | REST endpoints, request validation, JWT auth |
| LLM & RAG | LangChain + LangGraph + OpenAI | Document classification, RAG pipeline, conversational memory |
| Vector Store | Qdrant | Semantic embedding storage and similarity search |
| Session Store | Redis + LangGraph Checkpoint | Chat session persistence and graph state management |
| Relational DB | PostgreSQL + SQLAlchemy | Users, documents, metadata, chat logs, cost records |
| Embedding | OpenAI Embeddings | Text-to-vector conversion for RAG retrieval |

---

## Project Structure

```
LexiDoc_AI/
├── main.py                        # FastAPI app entry point
├── requirements.txt               # Python dependencies
└── app/
    ├── core/
    │   ├── config.py              # Environment configuration
    │   ├── rag_graph.py           # LangGraph RAG pipeline
    │   └── redis_checkpoint.py    # Redis checkpointer setup
    ├── db/
    │   ├── database.py            # SQLAlchemy engine & session
    │   ├── models.py              # ORM models
    │   └── deps.py                # DB dependency injection
    ├── routers/
    │   ├── user.py                # Auth endpoints
    │   ├── upload.py              # Document upload & metadata
    │   ├── chat.py                # Chat / RAG endpoint
    │   ├── dashboard.py           # Analytics endpoints
    │   ├── recent_responses.py    # Recent chat responses
    │   └── user_details.py        # User management
    ├── services/
    │   ├── vector_db.py           # Qdrant operations
    │   ├── redis_service.py       # Redis session management
    │   ├── document_service.py    # Document CRUD
    │   ├── recent_response_service.py
    │   └── user_details_service.py
    ├── schemas/                   # Pydantic request/response models
    ├── tasks/
    │   └── document_tasks.py      # PDF processing & classification
    └── utils/
        ├── auth.py                # JWT auth dependency
        ├── jwt.py                 # Token creation
        └── security.py            # Password hashing
```

---

## Setup & Installation

### Prerequisites

- Python 3.11+
- Docker (for Qdrant and Redis)
- PostgreSQL database
- OpenAI API key

### 1. Start Infrastructure

```bash
docker run -d -p 6333:6333 -p 6334:6334 --name qdrant qdrant/qdrant
docker run -d --name redis-stack -p 6379:6379 redis/redis-stack:latest
```

To restart existing containers:

```bash
docker start qdrant
docker start redis-stack
```

### 2. Configure Environment

Create a `.env` file in the project root:

```env
# Database
DB_USER=postgres
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=5432
DB_NAME=lexidoc

# Redis
REDIS_URI=redis://localhost:6379
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# OpenAI
OPENAI_API_KEY=sk-...
LLM_MODEL=gpt-4o
LLM_MODEL_NAME=gpt-4o
LLM_TEMPERATURE=0.0
EMBEDDING_MODEL=text-embedding-3-small

# Qdrant
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION=lexidoc

# JWT
SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Costs & Processing
INPUT_COST_PER_1K=0.005
OUTPUT_COST_PER_1K=0.015
COST_PER_1K_TOKENS=0.005
PREVIEW_PAGES=3
MAX_PAGE=20
BCRYPT_ROUNDS=12
```

### 3. Install Dependencies

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Run Database Migrations

```bash
pip install alembic
alembic init alembic
alembic revision --autogenerate -m "initial"
alembic upgrade head
```

### 5. Start the Server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API available at: `http://localhost:8000`  
Interactive docs: `http://localhost:8000/docs`

---

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/user-register` | Register a new user account |
| POST | `/user-login` | Login and receive JWT tokens |
| GET | `/me` | Get current authenticated user info |

### Documents

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/upload` | Upload one or more PDF files for classification |
| GET | `/doc-list` | List all documents for the authenticated user |
| GET | `/get-metadata/{file_id}` | Get metadata for a specific document |
| PUT | `/update-metadata/{file_id}` | Update document metadata and sync vector DB |

### Chat / RAG

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/chat/` | Submit a question about a document; returns AI answer and session ID |

**Request body:**
```json
{
  "input": "What is the ruling in this case?",
  "file_id": 1,
  "session_id": "optional-existing-session-id"
}
```

### Dashboard & Analytics

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/dashboard-card` | Summary stats: doc count, classified, errors, tokens, cost |
| GET | `/token-details` | Token usage per day for the last 7 days |
| GET | `/document-type-graph` | Document type distribution counts |
| POST | `/document-list` | Filtered and searchable document list |
| POST | `/list-sessions` | List all chat sessions for current user |
| GET | `/recent-responses` | Recent chat responses with token and cost info |
| GET | `/user-details` | All users with activity stats |

---

## RAG Pipeline

The chat endpoint is powered by a LangGraph state machine with two nodes:

**Retrieve** — Performs a filtered similarity search in Qdrant using the `document_id` metadata field, returning the top 5 most relevant text chunks for the user's question.

**Generation** — Formats retrieved context and chat history into a prompt and invokes the OpenAI LLM. The special `explain` query triggers a summary prompt that includes document metadata (type, source, confidence). All other queries use a QA prompt with full conversation history for context continuity.

State is persisted across turns using a Redis-backed LangGraph checkpointer keyed by `session_id`, enabling true multi-turn conversation memory.

---

## Document Classification

On upload, the first few pages (configurable via `PREVIEW_PAGES`) are extracted and sent to the LLM with structured output enabled. The LLM returns a `DocumentClassification` object:

- `document_type`: one of `Court Order`, `Affidavit`, `Petition`, `Contract`, `Notice`
- `confidence_score`: a float from `0.0` to `1.0`

Classification results are stored in PostgreSQL and embedded as metadata in every Qdrant vector point for the document, enabling type-filtered retrieval.

---

## Security

- All document and chat endpoints require a valid JWT Bearer token
- Passwords hashed with bcrypt (rounds configurable via `BCRYPT_ROUNDS`)
- Access tokens expire after `ACCESS_TOKEN_EXPIRE_MINUTES` minutes
- Refresh tokens expire after `REFRESH_TOKEN_EXPIRE_DAYS` days
- OAuth2PasswordBearer scheme used for token extraction

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Web Framework | FastAPI + Uvicorn |
| LLM Orchestration | LangChain + LangGraph |
| LLM Provider | OpenAI (gpt-4o) |
| Vector Database | Qdrant |
| Session Store | Redis + langgraph-checkpoint-redis |
| Relational Database | PostgreSQL + SQLAlchemy 2.0 |
| Authentication | python-jose (JWT) + passlib (bcrypt) |
| PDF Processing | pypdf |
| Tokenization | tiktoken |

---

## Contributing

1. Fork the repository and create a feature branch
2. Never commit `.env` or secrets
3. Follow the existing structure: routers → services → schemas
4. Open a pull request with a clear description of changes

---

*LexiDoc AI — Built with FastAPI & LangGraph*
