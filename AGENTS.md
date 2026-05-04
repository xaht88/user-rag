# RAG Chat Application

Full-stack web application for document-based Q&A using Retrieval-Augmented Generation (RAG) architecture.

## Quick Reference

### Access Points

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:5173 | Vite + React application |
| Backend API | http://localhost:8000 | FastAPI REST API |
| API Docs | http://localhost:8000/docs | Swagger UI |

### Technology Stack

| Layer | Technology |
|-------|------------|
| Frontend | Vite 8.0.10, React 18, TypeScript, Tailwind CSS |
| Backend | FastAPI, Python 3.10+, Pydantic, Uvicorn |
| Vector DB | ChromaDB |
| LLM | OpenAI API, Ollama |

### Commands

**Backend:**
```bash
cd rag_app/backend
uvicorn main:app --reload --port 8000
```

**Frontend:**
```bash
cd rag_app/frontend_next
npm run dev
```

**Testing:**
```bash
# Frontend
npm run test          # Unit tests
npx playwright test   # E2E tests

# Backend
pytest rag_app/backend/tests/ -v
```

---

## Detailed Instructions

For specific guidelines, see:

### Code & Style
- [TypeScript Conventions](docs/instructions/typescript.md)
- [Python Conventions](docs/instructions/python.md)
- [Code Style](docs/instructions/code-style.md)

### Testing
- [Testing Guidelines](docs/instructions/testing.md)

### Architecture
- [Architecture Patterns](docs/instructions/architecture.md)
- [Security Guidelines](docs/instructions/security.md)

### Workflow
- [Git Workflow](docs/instructions/git-workflow.md)
- [Development Workflow](docs/instructions/development-workflow.md)

### Documentation
- [Documentation Standards](docs/instructions/documentation.md)

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
├── AGENTS.md                       # This file
├── README.md                       # Project README
└── technical_specification.md      # Technical requirements
```

---

## Known Issues & Technical Debt

1. **In-Memory Session Storage** — Sessions lost on restart
2. **Mock LLM Responses** — Real LLM integration pending
3. **No Authentication** — JWT authentication planned
4. **No Rate Limiting** — API can be abused

---

## Documentation Index

- [System Architecture](docs/architecture/system-overview.md)
- [API Documentation](docs/api/README.md)
- [Development Guide](docs/development/README.md)
- [Deployment Guide](docs/deployment/README.md)
- [Architecture Decision Records](docs/decisions/README.md)

---

**Generated with [Continue](https://continue.dev)**

Co-Authored-By: Continue <noreply@continue.dev>
