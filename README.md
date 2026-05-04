# RAG Chat Application

Full-stack web application for document-based Q&A using Retrieval-Augmented Generation (RAG) architecture.

## Overview

Enable users to upload documents and perform intelligent queries using LLMs with context-aware responses and source citations.

**Status:** Development Phase — In-memory session storage, mock LLM responses

---

## Quick Start

### Prerequisites

- **Backend:** Python 3.10+, pip
- **Frontend:** Node.js 18+, npm 9+

### Running the Application

```bash
# Terminal 1: Start Backend
cd rag_app/backend
python -m venv .venv
.venv\Scripts\activate  # Windows
# or source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Terminal 2: Start Frontend
cd rag_app/frontend_next
npm install
npm run dev  # Runs on http://localhost:5173
```

### Access Points

- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

---

## Technology Stack

| Layer | Technology |
|-------|------------|
| Frontend | Vite 8.0.10, React 18, TypeScript, Tailwind CSS |
| Backend | FastAPI, Python 3.10+, Pydantic, Uvicorn |
| Vector DB | ChromaDB |
| LLM | OpenAI API, Ollama |

---

## Testing

```bash
# Frontend Unit Tests
cd rag_app/frontend_next
npm run test

# Frontend E2E Tests (Playwright)
npx playwright test
npx playwright test --reporter=html

# Backend Tests
cd rag_app/backend
pytest tests/ -v
```

---

## Build for Backend Integration

```bash
cd rag_app/frontend_next
npm run export:backend
```

This exports static assets to `rag_app/backend/static/next` and template to `rag_app/backend/templates/next_index.html`.

---

## Documentation

- [System Architecture](docs/architecture/system-overview.md)
- [API Documentation](docs/api/README.md)
- [Development Guide](docs/development/README.md)
- [Deployment Guide](docs/deployment/README.md)
- [Architecture Decision Records](docs/decisions/README.md)
- [Agent Instructions](docs/instructions/README.md)

---

## Project Structure

```
otus_dz2/
├── rag_app/
│   ├── backend/                    # FastAPI backend
│   └── frontend_next/              # Vite + React frontend
├── docs/                           # Documentation
├── stories/                        # User stories
├── .agents/                        # Agent instructions
├── AGENTS.md                       # AI agent instructions
├── README.md                       # This file
└── technical_specification.md      # Technical requirements
```

---

## Known Issues & Technical Debt

1. **In-Memory Session Storage** — Sessions lost on restart
2. **Mock LLM Responses** — Real LLM integration pending
3. **No Authentication** — JWT authentication planned
4. **No Rate Limiting** — API can be abused

---

**Generated with [Continue](https://continue.dev)**

Co-Authored-By: Continue <noreply@continue.dev>
