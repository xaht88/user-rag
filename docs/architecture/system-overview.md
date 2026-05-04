# System Architecture Overview

Полное описание архитектуры RAG Chat Application.

## 📊 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────┐         ┌──────────────────┐             │
│  │   Next.js        │         │   Mobile         │             │
│  │   Frontend       │         │   Browser        │             │
│  │   (Port 3000)    │         │                  │             │
│  └────────┬─────────┘         └────────┬─────────┘             │
│           │                             │                        │
│           └─────────────┬───────────────┘                        │
│                         │                                        │
│                    HTTP/REST API                                  │
│                         │                                        │
└─────────────────────────┼────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API GATEWAY LAYER                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              FastAPI Backend (Port 8000)                  │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │              REST API Endpoints                     │  │  │
│  │  │  - /api/upload                                     │  │  │
│  │  │  - /api/sessions/{id}/documents                    │  │  │
│  │  │  - /api/sessions/{id}/query                        │  │  │
│  │  │  - /api/sessions/{id}/chat                         │  │  │
│  │  │  - /api/llm/providers                              │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  │                           │                                │  │
│  │  ┌────────────────────────┴────────────────────────────┐  │  │
│  │  │              RAG Engine                              │  │  │
│  │  │  - Document Processing                               │  │  │
│  │  │  - Embedding Generation                              │  │  │
│  │  │  - Vector Search                                     │  │  │
│  │  │  - Context Assembly                                  │  │  │
│  │  │  - LLM Integration                                   │  │  │
│  │  └────────────────────────┬────────────────────────────┘  │  │
│  └───────────────────────────┼────────────────────────────────┘  │
│                              │                                   │
└──────────────────────────────┼───────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATA LAYER                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────┐         ┌──────────────────┐             │
│  │   ChromaDB       │         │   File System    │             │
│  │   (Vector DB)    │         │   (Documents)    │             │
│  │                  │         │                  │             │
│  │  - Document      │         │  - PDF files     │             │
│  │    Embeddings    │         │  - DOCX files    │             │
│  │  - Metadata      │         │  - TXT files     │             │
│  │  - Indexes       │         │  - MD files      │             │
│  └──────────────────┘         └──────────────────┘             │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              In-Memory Session Store (Temporary)          │  │
│  │  - Session State                                         │  │
│  │  - Chat History                                          │  │
│  │  - LLM Configuration                                     │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    EXTERNAL SERVICES                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────┐         ┌──────────────────┐             │
│  │   OpenAI API     │         │    Ollama        │             │
│  │                  │         │    Local Server  │             │
│  │  - GPT-4         │         │                  │             │
│  │  - GPT-4o        │         │  - Llama2        │             │
│  │  - GPT-3.5       │         │  - Mistral       │             │
│  └──────────────────┘         └──────────────────┘             │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🏗️ Component Architecture

### 1. Frontend Layer (Next.js 14)

**Технологии:**
- Next.js 14 (App Router)
- React 18
- TypeScript
- Tailwind CSS
- Vitest (testing)

**Основные компоненты:**

```
frontend_next/
├── app/
│   ├── page.tsx              # Main chat interface
│   ├── layout.tsx            # Root layout
│   └── globals.css           # Global styles
│
├── components/
│   ├── chat-panel.tsx        # Chat interface component
│   ├── document-panel.tsx    # Document management
│   ├── llm-selector.tsx      # LLM configuration
│   └── ui/                   # Reusable UI components
│
├── shared/
│   ├── api/
│   │   └── client.ts         # API client
│   └── types.ts              # TypeScript types
│
└── features/
    └── rag/                  # RAG-specific features
```

**Responsibilities:**
- User interface rendering
- State management (React hooks)
- API communication
- Form validation
- Real-time updates

---

### 2. Backend Layer (FastAPI)

**Технологии:**
- FastAPI
- Python 3.10+
- Pydantic
- Uvicorn

**Основные модули:**

```
backend/
├── main.py                   # API endpoints
├── rag_engine.py             # Core RAG logic
├── auth.py                   # Authentication (TODO)
├── database.py               # Database connection (TODO)
└── models.py                 # Database models (TODO)
```

**API Endpoints:**

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/upload` | Upload document |
| GET | `/api/sessions/{id}/documents` | List documents |
| POST | `/api/sessions/{id}/documents/{doc_id}/toggle` | Toggle selection |
| POST | `/api/sessions/{id}/documents/{doc_id}/delete` | Delete document |
| POST | `/api/sessions/{id}/llm/config` | Configure LLM |
| POST | `/api/sessions/{id}/query` | Send query |
| GET | `/api/sessions/{id}/chat` | Get chat history |
| GET | `/api/llm/providers` | List LLM providers |

---

### 3. RAG Engine

**Компоненты:**

```
rag_engine/
├── document_processor.py     # Document parsing & chunking
├── embedding_generator.py    # Vector embedding generation
├── vector_store.py           # ChromaDB integration
├── retriever.py              # Similarity search
├── context_builder.py        # Context assembly
└── llm_client.py             # LLM integration
```

**Workflow:**

```
1. Document Upload
   │
   ▼
2. Document Processing
   ├─ File validation
   ├─ Format detection
   ├─ Text extraction
   └─ Chunking
   │
   ▼
3. Embedding Generation
   ├─ Select embedding model
   ├─ Generate vectors
   └─ Store in ChromaDB
   │
   ▼
4. Query Processing
   ├─ User query received
   ├─ Generate query embedding
   ├─ Vector search
   └─ Retrieve relevant chunks
   │
   ▼
5. Context Assembly
   ├─ Format retrieved chunks
   ├─ Add metadata
   └─ Build prompt
   │
   ▼
6. LLM Generation
   ├─ Send to LLM (OpenAI/Ollama)
   ├─ Receive response
   └─ Format response with sources
```

---

## 📦 Data Flow

### Document Upload Flow

```
┌─────────┐     ┌─────────┐     ┌──────────┐     ┌──────────┐
│  User   │────▶│ Frontend│────▶│  Backend │────▶│  Storage │
└─────────┘     └─────────┘     └──────────┘     └──────────┘
                           │                │
                           │                ▼
                           │         ┌─────────────┐
                           │         │ ChromaDB    │
                           │         │ (Vectors)   │
                           │         └─────────────┘
                           │
                           ▼
                      ┌──────────┐
                      │ Response │
                      └──────────┘
```

### Query Flow

```
┌─────────┐     ┌─────────┐     ┌──────────┐     ┌──────────┐
│  User   │────▶│ Frontend│────▶│  Backend │────▶│  RAG     │
└─────────┘     └─────────┘     └──────────┘     └──────────┘
                                             │
                    ┌────────────────────────┼────────────────────┐
                    ▼                        ▼                    ▼
             ┌────────────┐         ┌─────────────┐      ┌────────────┐
             │ ChromaDB   │         │  Session    │      │  LLM       │
             │ (Search)   │         │  History    │      │  (Generate)│
             └────────────┘         └─────────────┘      └────────────┘
                    │                        │                    │
                    └────────────────────────┼────────────────────┘
                                             ▼
                                      ┌──────────┐
                                      │ Response │
                                      └──────────┘
```

---

## 🗄️ Data Models

### Session

```python
class Session:
    id: str                    # UUID
    created_at: datetime
    llm_config: LLMConfig
    documents: List[Document]
    chat_history: List[Message]
```

### Document

```python
class Document:
    id: str                    # UUID
    session_id: str
    filename: str
    filepath: str
    upload_date: datetime
    chunks_count: int
    pages_count: int
    status: str                # processing, ready, error
    selected: bool
```

### ChatMessage

```python
class ChatMessage:
    id: str                    # UUID
    session_id: str
    role: str                  # user, assistant
    content: str
    sources: List[Source]
    created_at: datetime
```

### Source

```python
class Source:
    filename: str
    page: int
    snippet: str
    chunk_id: str
```

---

## 🔐 Security Architecture

### Current State (Development)

```
┌─────────────────────────────────────────┐
│          NO AUTHENTICATION               │
│          NO AUTHORIZATION                │
│          NO RATE LIMITING                │
└─────────────────────────────────────────┘
```

### Planned State (Production)

```
┌─────────────────────────────────────────┐
│         JWT Authentication               │
│         OAuth2 Support                   │
└─────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│         Role-Based Access Control        │
│         API Rate Limiting                │
└─────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│         Input Validation                 │
│         SQL Injection Prevention         │
│         XSS Protection                   │
└─────────────────────────────────────────┘
```

---

## 🔄 Deployment Architecture

### Development

```
┌──────────────┐     ┌──────────────┐
│   Frontend   │────▶│   Backend    │
│  (3000)      │     │   (8000)     │
└──────────────┘     └──────┬───────┘
                            │
                    ┌───────┴───────┐
                    │   ChromaDB    │
                    │   (Local)     │
                    └───────────────┘
```

### Production (Planned)

```
┌──────────────┐     ┌──────────────┐
│   Frontend   │────▶│   Backend    │
│  (CDN)       │     │  (K8s)       │
└──────────────┘     └──────┬───────┘
                            │
                    ┌───────┴────────┐
                    │                │
              ┌─────▼─────┐    ┌────▼────┐
              │ PostgreSQL│    │ChromaDB │
              │ (Sessions)│    │(Vectors)│
              └───────────┘    └─────────┘
```

---

## 📈 Scalability Considerations

### Current Limitations

1. **In-Memory Storage**
   - Sessions lost on restart
   - No horizontal scaling
   - Memory constraints

2. **Single Backend Instance**
   - No load balancing
   - Single point of failure

3. **Local ChromaDB**
   - Limited concurrent queries
   - No replication

### Scaling Strategies

#### Vertical Scaling

```
Increase resources:
- More RAM for embeddings
- More CPU for LLM processing
- Faster storage for documents
```

#### Horizontal Scaling

```
Load Balancer
    │
    ├─▶ Backend Instance 1
    ├─▶ Backend Instance 2
    ├─▶ Backend Instance 3
    └─▶ Backend Instance N
         │
         ├─▶ PostgreSQL Cluster
         ├─▶ ChromaDB Cluster
         └─▶ Redis Cache
```

#### Caching Strategy

```
┌─────────────────────────────────────┐
│         Response Cache (Redis)       │
│  - Query results                     │
│  - Embedding cache                   │
│  - Session data                      │
└─────────────────────────────────────┘
```

---

## 🧪 Testing Architecture

### Test Layers

```
┌─────────────────────────────────────┐
│         E2E Tests (Playwright)       │
│  - Full user workflows               │
│  - Integration testing               │
└─────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│      Integration Tests (pytest)      │
│  - API endpoints                     │
│  - Database operations               │
│  - External services                 │
└─────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│      Unit Tests (Vitest/pytest)      │
│  - Individual functions              │
│  - Components                        │
│  - Utilities                         │
└─────────────────────────────────────┘
```

---

## 📊 Monitoring & Observability

### Metrics to Track

1. **Performance**
   - API response times
   - Query latency
   - Embedding generation time
   - LLM response time

2. **Resource Usage**
   - CPU utilization
   - Memory consumption
   - Disk space (documents, vectors)
   - Network I/O

3. **Business Metrics**
   - Active sessions
   - Documents uploaded
   - Queries processed
   - User engagement

### Logging Strategy

```
┌─────────────────────────────────────┐
│         Structured Logging           │
│  - JSON format                       │
│  - Correlation IDs                   │
│  - Log levels (INFO, WARN, ERROR)   │
└─────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│       Log Aggregation                │
│  - Centralized log storage          │
│  - Log analysis tools               │
│  - Alerting                          │
└─────────────────────────────────────┘
```

---

## 🚀 Future Architecture Improvements

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
