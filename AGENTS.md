# Repository Overview

## Project Description

**RAG Chat Application** — Full-stack web application for document-based Q&A using Retrieval-Augmented Generation (RAG) architecture.

**Main Purpose:**
- Enable users to upload documents (PDF, DOCX, TXT, MD)
- Perform intelligent queries against uploaded documents using LLMs
- Provide context-aware responses with source citations

**Key Technologies:**
- **Backend:** Python, FastAPI, LangChain, ChromaDB, Ollama/OpenAI
- **Frontend:** Next.js 14, React 18, TypeScript, Tailwind CSS
- **Testing:** Vitest, @testing-library/react
- **Vector Database:** ChromaDB (for document embeddings)
- **LLM Providers:** OpenAI, Ollama (local)

## Architecture Overview

**High-Level Architecture:**
```
┌─────────────┐         ┌──────────────┐
│   Next.js   │◄───────►│   FastAPI    │
│  Frontend   │  HTTP   │    Backend   │
│  (3000)     │  API    │   (8000)     │
└─────────────┘         └──────────────┘
                               │
                    ┌──────────┴──────────┐
                    │                     │
              ┌─────▼─────┐       ┌──────▼─────┐
              │ ChromaDB  │       │   Ollama   │
              │ (Vectors) │       │   /OpenAI  │
              └───────────┘       └────────────┘
```

**Main Components:**
1. **FastAPI Backend:** REST API for document management, session handling, and LLM queries
2. **Next.js Frontend:** User interface for document upload, chat interface, LLM configuration
3. **ChromaDB:** Vector storage for document embeddings
4. **RAG Engine:** Core logic for document processing and retrieval

**Data Flow:**
1. User uploads document → Backend stores file, generates embeddings
2. User queries → Backend retrieves relevant chunks from ChromaDB
3. Context + query sent to LLM → Response with source citations returned

## Directory Structure

```
otus_dz2/
├── rag_app/
│   ├── backend/                    # FastAPI backend
│   │   ├── main.py                 # API entry point, REST endpoints
│   │   ├── rag_engine.py           # RAG core logic (embeddings, retrieval)
│   │   ├── requirements.txt        # Python dependencies
│   │   ├── uploads/                # Uploaded documents storage
│   │   ├── chroma_db/              # ChromaDB vector store
│   │   ├── static/                 # Static assets
│   │   ├── templates/              # HTML templates
│   │   └── tests/                  # Backend tests
│   │
│   └── frontend_next/              # Next.js frontend
│       ├── app/                    # Next.js App Router pages
│       ├── components/             # React components
│       ├── features/               # Feature modules
│       ├── shared/                 # Shared types, API client
│       ├── package.json            # Node dependencies
│       ├── tsconfig.json           # TypeScript config
│       ├── tailwind.config.ts      # Tailwind CSS config
│       ├── vitest.config.ts        # Vitest test config
│       └── scripts/                # Build/export scripts
│
├── stories/                        # User stories
│   └── user_stories.md
├── technical_specification.md      # Technical requirements
├── frontend_specification.md       # Frontend specs
└── AGENTS.md                       # This file
```

**Key Files:**
- `rag_app/backend/main.py` — API endpoints (upload, query, sessions)
- `rag_app/backend/rag_engine.py` — Document processing, embedding generation
- `rag_app/frontend_next/app/page.tsx` — Main chat interface
- `rag_app/frontend_next/shared/api/client.ts` — API client for frontend
- `rag_app/frontend_next/shared/types.ts` — TypeScript type definitions

## Development Workflow

### Setup

**Backend:**
```bash
cd rag_app/backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Frontend:**
```bash
cd rag_app/frontend_next
npm install
npm run dev
```

**Access Points:**
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`

### Build & Deployment

**Export Frontend for Backend Integration:**
```bash
cd rag_app/frontend_next
npm run export:backend
```
This exports static assets to `rag_app/backend/static/next` and template to `rag_app/backend/templates/next_index.html`.

### Testing

**Frontend Tests (Vitest):**
```bash
cd rag_app/frontend_next
npm run test
```

**Backend Tests:**
```bash
cd rag_app/backend
pytest tests/
```

**Test Coverage:**
- Frontend: `components/document-panel.test.tsx`, `components/chat-panel.test.tsx`, `components/llm-selector.test.tsx`

### Linting & Formatting

**Frontend:**
```bash
cd rag_app/frontend_next
npm run lint          # ESLint
```

**Backend:**
- Follow PEP 8 guidelines
- Use `black` for formatting (if configured)
- Use `flake8` or `pylint` for linting

### Key API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/upload` | Upload document |
| GET | `/api/sessions/{session_id}/documents` | List documents |
| POST | `/api/sessions/{session_id}/documents/{doc_id}/toggle` | Toggle document selection |
| POST | `/api/sessions/{session_id}/documents/{doc_id}/delete` | Delete document |
| POST | `/api/sessions/{session_id}/llm/config` | Configure LLM |
| POST | `/api/sessions/{session_id}/query` | Send query |
| GET | `/api/sessions/{session_id}/chat` | Get chat history |
| GET | `/api/llm/providers` | List LLM providers |

### Environment Variables

Required environment variables (set in `.env`):
- `OPENAI_API_KEY` — OpenAI API key (if using OpenAI)
- `OLLAMA_BASE_URL` — Ollama server URL (default: `http://localhost:11434`)

### Development Best Practices

1. **Session Management:** Sessions stored in-memory (use Redis/PostgreSQL for production)
2. **File Uploads:** Max 50MB per file, supported formats: PDF, DOCX, TXT, MD
3. **Error Handling:** HTTP exceptions with descriptive messages
4. **Type Safety:** TypeScript on frontend, Pydantic models on backend
5. **Testing:** Write tests for new features before implementation

### Known Issues & Notes

- Starlette 1.0.0 bug with Jinja2 templates — using direct HTML file reading
- In-memory session storage (not suitable for production)
- LLM responses currently mocked (real implementation pending)
- Document processing is asynchronous (simulated with delays)
