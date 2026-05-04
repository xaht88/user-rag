# AGENTS.md — Instructions for AI Agents

## Project Overview

**RAG Chat Application** — Full-stack web application for document-based Q&A using Retrieval-Augmented Generation (RAG) architecture.

**Purpose:** Enable users to upload documents and perform intelligent queries using LLMs with context-aware responses and source citations.

**Status:** Development Phase — In-memory session storage, mock LLM responses

---

## Quick Reference

### Access Points

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:5173 | Vite + React application |
| Backend API | http://localhost:8000 | FastAPI REST API |
| API Docs | http://localhost:8000/docs | Swagger UI |
| ReDoc | http://localhost:8000/redoc | Alternative API docs |

### Technology Stack

| Layer | Technology | Version |
|-------|------------|---------|
| Frontend | Vite | 8.0.10 |
| Frontend | React | 18 |
| Frontend | TypeScript | Latest |
| Frontend | Tailwind CSS | Latest |
| Frontend | Vitest | Latest (testing) |
| Backend | FastAPI | Latest |
| Backend | Python | 3.10+ |
| Backend | Pydantic | Latest |
| Backend | Uvicorn | Latest |
| Vector DB | ChromaDB | Latest |
| LLM | OpenAI | API |
| LLM | Ollama | Local |

---

## Development Workflow

### Setup

**Backend:**
```bash
cd rag_app/backend
python -m venv .venv
.venv\Scripts\activate  # Windows
# or source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Frontend:**
```bash
cd rag_app/frontend_next
npm install
npm run dev  # Runs on http://localhost:5173
```

### Testing

**Frontend:**
```bash
cd rag_app/frontend_next
npm run test          # Run tests
npm run test:watch    # Watch mode
npm run test:coverage # With coverage
```

**Backend:**
```bash
cd rag_app/backend
pytest tests/ -v
pytest tests/ --cov=. --cov-report=html  # With coverage
```

### Linting & Formatting

**Frontend:**
```bash
cd rag_app/frontend_next
npm run lint          # ESLint
```

**Backend:**
```bash
pip install black flake8 isort
black rag_app/backend/
flake8 rag_app/backend/
isort rag_app/backend/
```

### Build for Production

**Export Frontend for Backend Integration:**
```bash
cd rag_app/frontend_next
npm run export:backend
```

This exports static assets to `rag_app/backend/static/next` and template to `rag_app/backend/templates/next_index.html`.

**Note:** The frontend is currently developed with Vite + React (not Next.js). The export script may need adjustment based on actual build configuration.

---

## Project Structure

```
otus_dz2/
├── rag_app/
│   ├── backend/                    # FastAPI backend
│   │   ├── main.py                 # API entry point, REST endpoints
│   │   ├── rag_engine.py           # RAG core logic (embeddings, retrieval)
│   │   ├── rag/                    # RAG services (deprecated)
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
│       ├── package.json            # Node dependencies
│       ├── tsconfig.json           # TypeScript config
│       ├── tailwind.config.ts      # Tailwind CSS config
│       ├── vitest.config.ts        # Vitest test config
│       ├── vite.config.ts          # Vite configuration
│       ├── .env.local              # Frontend environment
│       └── scripts/                # Build/export scripts
│
├── docs/                           # Documentation
│   ├── index.md                    # Documentation index
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
└── AGENTS.md                       # This file
```

---

## Key Files

### Backend

| File | Description |
|------|-------------|
| `rag_app/backend/main.py` | API endpoints (upload, query, sessions) |
| `rag_app/backend/rag_engine.py` | Document processing, embedding generation |
| `rag_app/backend/requirements.txt` | Python dependencies |
| `rag_app/backend/.env` | Environment variables |

### Frontend

| File | Description |
|------|-------------|
| `rag_app/frontend_next/app/page.tsx` | Main chat interface |
| `rag_app/frontend_next/shared/api/client.ts` | API client for frontend |
| `rag_app/frontend_next/shared/types.ts` | TypeScript type definitions |
| `rag_app/frontend_next/components/` | React components |
| `rag_app/frontend_next/vite.config.ts` | Vite configuration |

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/upload` | Upload document (PDF, DOCX, TXT, MD) |
| GET | `/api/sessions/{session_id}/documents` | List documents in session |
| POST | `/api/sessions/{session_id}/documents/{doc_id}/toggle` | Toggle document selection |
| POST | `/api/sessions/{session_id}/documents/{doc_id}/delete` | Delete document |
| POST | `/api/sessions/{session_id}/llm/config` | Configure LLM for session |
| POST | `/api/sessions/{session_id}/query` | Send query to LLM |
| GET | `/api/sessions/{session_id}/chat` | Get chat history |
| GET | `/api/llm/providers` | List available LLM providers |

**Full API Documentation:** http://localhost:8000/docs or [docs/api/openapi.yaml](./docs/api/openapi.yaml)

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

### Architecture Decision Records

See [docs/decisions/](./docs/decisions/) for detailed ADRs:

- **ADR-001:** Client-Server Architecture Pattern
- **ADR-002:** Session Management Strategy

---

## Documentation Index

| Document | Location | Description |
|----------|----------|-------------|
| Project Overview | [docs/index.md](./docs/index.md) | Main documentation index |
| API Documentation | [docs/api/README.md](./docs/api/README.md) | Complete API reference |
| System Architecture | [docs/architecture/system-overview.md](./docs/architecture/system-overview.md) | Full architecture overview |
| Development Guide | [docs/development/README.md](./docs/development/README.md) | Development setup and workflow |
| Deployment Guide | [docs/deployment/README.md](./docs/deployment/README.md) | Production deployment instructions |
| Technical Specification | [technical_specification.md](./technical_specification.md) | Technical requirements |
| Frontend Specification | [frontend_specification.md](./frontend_specification.md) | Frontend-specific requirements |
| User Stories | [stories/user_stories.md](./stories/user_stories.md) | User stories and use cases |

---

## Best Practices for Agents

### Code Style

**Python (Backend):**
- Follow PEP 8 guidelines
- Use `black` for formatting
- Use `flake8` for linting
- Use `isort` for import sorting
- Document all functions and classes with docstrings

**TypeScript (Frontend):**
- Follow TypeScript best practices
- Use ESLint for code quality
- Use Tailwind CSS for styling
- Write tests for all components

### Testing

- Write tests before implementing new features (TDD)
- Maintain high test coverage (>80%)
- Test both happy paths and error cases
- Use mocking for external services

### Documentation

- Document the **why**, not the **what**
- Keep API documentation up to date
- Update ADRs when making architectural decisions
- Write clear commit messages

### Git Workflow

- Use descriptive commit messages
- Create feature branches from `main`
- Open pull requests for all changes
- Get approval before merging

---

## Common Tasks

### Adding a New API Endpoint

1. Create route handler in `rag_app/backend/main.py`
2. Add Pydantic models for request/response validation
3. Update OpenAPI documentation
4. Add tests in `rag_app/backend/tests/`
5. Document in [docs/api/README.md](./docs/api/README.md)

### Adding a New Component

1. Create component in `rag_app/frontend_next/components/`
2. Add TypeScript types in `rag_app/frontend_next/shared/types.ts`
3. Write tests in `*.test.tsx`
4. Update component documentation

### Running Specific Tests

**Backend:**
```bash
pytest tests/test_file.py::test_function_name -v
```

**Frontend:**
```bash
npm run test -- components/component-name.test.tsx
```

---

## Security Considerations

### Current State

⚠️ **No authentication or authorization implemented**

### Planned Security Features

1. **Authentication**
   - JWT-based authentication
   - OAuth2 support for third-party auth
   - Session management with Redis

2. **Authorization**
   - Role-based access control (RBAC)
   - API rate limiting
   - Input validation and sanitization

3. **Data Protection**
   - Encrypt sensitive data at rest
   - Use HTTPS everywhere
   - Secure database connections

---

## Performance Considerations

### Optimization Strategies

1. **Caching**
   - Redis for session caching
   - Response caching for repeated queries
   - Embedding cache

2. **Database Optimization**
   - Index frequently queried columns
   - Connection pooling
   - Query optimization

3. **Frontend Optimization**
   - Code splitting
   - Lazy loading
   - Image optimization
   - Static generation where possible

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
- [Next.js Documentation](https://nextjs.org/docs)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Ollama Documentation](https://github.com/ollama/ollama)
- [OpenAI API Documentation](https://platform.openai.com/docs/api-reference)

---

**Generated with [Continue](https://continue.dev)**

Co-Authored-By: Continue <noreply@continue.dev>
