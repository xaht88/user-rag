# RAG Chat Application - Documentation Index

## Overview

**RAG Chat Application** — Full-stack web application for document-based Q&A using Retrieval-Augmented Generation (RAG) architecture.

**Purpose:** Enable users to upload documents and perform intelligent queries using LLMs with context-aware responses and source citations.

**Status:** Development Phase — In-memory session storage, mock LLM responses

---

## Quick Start

### Prerequisites

- **Backend:** Python 3.10+, pip
- **Frontend:** Node.js 18+, npm 9+
- **Testing:** Playwright (for E2E tests)

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

### Running Tests

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

## Documentation Structure

### 📚 Core Documentation

| Document | Location | Description |
|----------|----------|-------------|
| [System Architecture](./architecture/system-overview.md) | `docs/architecture/system-overview.md` | Complete architecture overview |
| [API Documentation](./api/README.md) | `docs/api/README.md` | Complete API reference |
| [Development Guide](./development/README.md) | `docs/development/README.md` | Development setup and workflow |
| [Deployment Guide](./deployment/README.md) | `docs/deployment/README.md` | Production deployment instructions |

### 🛠️ Agent Instructions

| Document | Location | Description |
|----------|----------|-------------|
| [Instructions Index](./instructions/README.md) | `docs/instructions/README.md` | Index of all agent guidelines |
| [TypeScript Conventions](./instructions/typescript.md) | `docs/instructions/typescript.md` | TypeScript patterns and best practices |
| [Python Conventions](./instructions/python.md) | `docs/instructions/python.md` | Python backend guidelines |
| [Code Style](./instructions/code-style.md) | `docs/instructions/code-style.md` | Code formatting and style rules |
| [Testing Guidelines](./instructions/testing.md) | `docs/instructions/testing.md` | Testing strategy (Vitest, Playwright, pytest) |
| [Git Workflow](./instructions/git-workflow.md) | `docs/instructions/git-workflow.md` | Git branching and commit conventions |
| [Architecture Patterns](./instructions/architecture.md) | `docs/instructions/architecture.md` | Design patterns and architecture decisions |
| [Security Guidelines](./instructions/security.md) | `docs/instructions/security.md` | Security best practices |
| [Development Workflow](./instructions/development-workflow.md) | `docs/instructions/development-workflow.md` | Development process and tools |
| [Documentation Standards](./instructions/documentation.md) | `docs/instructions/documentation.md` | Documentation conventions |

### 🏗️ Architecture Decision Records

| ADR | Title | Status |
|-----|-------|--------|
| [ADR-001](./decisions/ADR-001-client-server.md) | Client-Server Architecture Pattern | Accepted |
| [ADR-002](./decisions/ADR-002-session-management.md) | Session Management Strategy | Accepted |

### 📖 Technical Specifications

| Document | Location | Description |
|----------|----------|-------------|
| [Technical Specification](../technical_specification.md) | `../technical_specification.md` | Technical requirements |
| [Frontend Specification](../frontend_specification.md) | `../frontend_specification.md` | Frontend-specific requirements |
| [User Stories](../stories/user_stories.md) | `../stories/user_stories.md` | User stories and use cases |

---

## Project Structure

```
otus_dz2/
├── rag_app/
│   ├── backend/                    # FastAPI backend
│   │   ├── main.py                 # API entry point, REST endpoints
│   │   ├── rag_engine.py           # RAG core logic (embeddings, retrieval)
│   │   ├── requirements.txt        # Python dependencies
│   │   ├── .env                    # Environment variables
│   │   ├── uploads/                # Uploaded documents storage
│   │   ├── chroma_db/              # ChromaDB vector store
│   │   ├── static/                 # Static assets
│   │   ├── templates/              # HTML templates
│   │   └── tests/                  # Backend tests
│   │
│   └── frontend_next/              # Vite + React frontend
│       ├── app/                    # React pages
│       ├── components/             # React components
│       ├── features/               # Feature modules
│       ├── shared/                 # Shared types, API client
│       ├── smoke-test.spec.ts      # Playwright smoke tests
│       ├── playwright.config.ts    # Playwright configuration
│       ├── vite.config.ts          # Vite configuration
│       ├── package.json            # Node dependencies
│       └── tsconfig.json           # TypeScript config
│
├── docs/                           # Documentation
│   ├── index.md                    # This file
│   ├── api/                        # API documentation
│   ├── architecture/               # Architecture docs
│   ├── development/                # Development guide
│   ├── deployment/                 # Deployment guide
│   └── decisions/                  # Architecture Decision Records
│
├── stories/                        # User stories
│   ├── README.md
│   └── user_stories.md
├── technical_specification.md      # Technical requirements
├── frontend_specification.md       # Frontend specs
├── AGENTS.md                       # AI agent instructions
└── README.md                       # Project README
```

---

## API Endpoints

### Document Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/upload` | Upload document (PDF, DOCX, TXT, MD) |
| GET | `/api/sessions/{session_id}/documents` | List documents in session |
| POST | `/api/sessions/{session_id}/documents/{doc_id}/toggle` | Toggle document selection |
| POST | `/api/sessions/{session_id}/documents/{doc_id}/delete` | Delete document |

### LLM Configuration

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/sessions/{session_id}/llm/config` | Configure LLM for session |
| GET | `/api/llm/providers` | List available LLM providers |

### Query & Chat

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/sessions/{session_id}/query` | Send query to LLM |
| GET | `/api/sessions/{session_id}/chat` | Get chat history |

**Full API Documentation:** http://localhost:8000/docs

---

## Environment Variables

### Backend (.env)

```env
OPENAI_API_KEY=your_openai_api_key
OLLAMA_BASE_URL=http://localhost:11434
PORT=8000
DEBUG=true
```

### Frontend (.env.local)

```env
VITE_API_URL=http://localhost:8000
VITE_OPENAI_API_KEY=your_openai_api_key
VITE_OLLAMA_BASE_URL=http://localhost:11434
```

---

## Testing

### Frontend Testing

**Unit Tests (Vitest):**
```bash
npm run test          # Run all tests
npm run test:watch    # Watch mode
npm run test:coverage # With coverage report
```

**E2E Tests (Playwright):**
```bash
npx playwright test           # Run all tests
npx playwright test smoke-test.spec.ts  # Run smoke tests
npx playwright test --reporter=html     # Generate HTML report
npx playwright show-report  # Open HTML report
```

### Backend Testing

```bash
pytest tests/ -v
pytest tests/ --cov=. --cov-report=html  # With coverage
```

---

## Known Issues & Technical Debt

### Current Limitations

1. **In-Memory Session Storage**
   - Sessions lost on server restart
   - No horizontal scaling
   - **Solution:** Migrate to PostgreSQL + Redis

2. **Mock LLM Responses**
   - Real LLM integration pending
   - **Solution:** Implement real OpenAI/Ollama calls

3. **No Authentication**
   - No user authentication or authorization
   - **Solution:** Implement JWT authentication

4. **No Rate Limiting**
   - API can be abused
   - **Solution:** Implement rate limiting middleware

5. **Document Processing**
   - Asynchronous processing is simulated
   - **Solution:** Implement real async task queue (Celery)

---

## Future Roadmap

### Phase 1: Production Readiness

- [ ] Add PostgreSQL for session storage
- [ ] Implement JWT authentication
- [ ] Add Redis for caching
- [ ] Implement rate limiting
- [ ] Add comprehensive logging

### Phase 2: Scalability

- [ ] Containerize with Docker
- [ ] Kubernetes deployment
- [ ] Load balancing
- [ ] Database connection pooling
- [ ] Horizontal scaling

### Phase 3: Advanced Features

- [ ] Vector database clustering
- [ ] LLM model caching
- [ ] Async task queue (Celery)
- [ ] Real-time updates (WebSocket)
- [ ] Multi-tenancy support

---

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Vite Documentation](https://vitejs.dev/)
- [React Documentation](https://react.dev/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Ollama Documentation](https://github.com/ollama/ollama)
- [OpenAI API Documentation](https://platform.openai.com/docs/api-reference)

---

**Last Updated:** 2026-05-04  
**Version:** 1.0.0
