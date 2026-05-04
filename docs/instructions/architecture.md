# Architecture Guidelines

## Overview

Client-server architecture with RAG (Retrieval-Augmented Generation) pattern.

## System Architecture

```
┌─────────────────┐         ┌──────────────────┐         ┌──────────────┐
│   Frontend      │         │    Backend       │         │   Vector DB  │
│   (Vite + React)│◄───────►│   (FastAPI)      │◄───────►│  (ChromaDB)  │
│                 │  HTTP   │                  │  RPC    │              │
│ - Chat UI       │         │ - REST API       │         │ - Embeddings │
│ - Document UI   │         │ - RAG Engine     │         │ - Indexing   │
│ - State Mgmt    │         │ - Session Mgmt   │         └──────────────┘
└─────────────────┘         └──────────────────┘                │
                                                                 │
                                                                 ▼
                                                        ┌──────────────┐
                                                        │    LLM       │
                                                        │ (OpenAI/Ollama)│
                                                        └──────────────┘
```

## Key Components

### 1. Frontend

**Technology Stack:**
- Vite 8.0.10
- React 18
- TypeScript
- Tailwind CSS
- Vitest (testing)

**Architecture:**
- Component-based architecture
- Custom hooks for state management
- API client abstraction layer
- Feature-based folder structure

### 2. Backend

**Technology Stack:**
- FastAPI
- Python 3.10+
- Pydantic
- Uvicorn

**Architecture:**
- RESTful API design
- Dependency injection
- Service layer pattern
- In-memory session storage (temporary)

### 3. RAG Engine

**Components:**
- Document processor (PDF, DOCX, TXT, MD)
- Text chunker with overlap
- Embedding generator
- Vector store indexer
- Similarity search

## Design Patterns

### 1. Repository Pattern

```python
# ✅ Good: Repository pattern for data access
class DocumentRepository:
    def __init__(self, db_session):
        self.session = db_session
    
    def find_by_id(self, doc_id: str) -> Optional[Document]:
        return self.session.query(Document).filter(
            Document.id == doc_id
        ).first()
    
    def find_all_by_session(self, session_id: str) -> List[Document]:
        return self.session.query(Document).filter(
            Document.session_id == session_id
        ).all()
```

### 2. Service Layer

```python
# ✅ Good: Service layer for business logic
class DocumentService:
    def __init__(self, repository: DocumentRepository):
        self.repository = repository
    
    async def upload_document(self, file: UploadFile, session_id: str) -> Document:
        # Validate file
        self._validate_file(file)
        
        # Save to storage
        file_path = await self._save_file(file)
        
        # Create document record
        doc = Document(
            filename=file.filename,
            session_id=session_id,
            file_path=file_path
        )
        
        # Add to repository
        return self.repository.add(doc)
```

### 3. Factory Pattern

```typescript
// ✅ Good: Factory pattern for LLM providers
class LLMFactory {
  static create(provider: LLMProvider): LLMClient {
    switch (provider) {
      case 'openai':
        return new OpenAIClient();
      case 'ollama':
        return new OllamaClient();
      default:
        throw new Error(`Unknown provider: ${provider}`);
    }
  }
}
```

## Data Flow

### Document Upload Flow

```
1. User selects file
   ↓
2. Frontend validates file type/size
   ↓
3. POST /api/upload
   ↓
4. Backend saves file to uploads/
   ↓
5. Backend creates document record
   ↓
6. Backend triggers embedding generation (async)
   ↓
7. Frontend receives success response
   ↓
8. Embedding process completes
   ↓
9. Vector store updated
```

### Query Flow

```
1. User enters query
   ↓
2. Frontend POST /api/sessions/{id}/query
   ↓
3. Backend retrieves session documents
   ↓
4. Backend searches vector store for similar chunks
   ↓
5. Backend retrieves top-k chunks
   ↓
6. Backend constructs prompt with context
   ↓
7. Backend calls LLM
   ↓
8. LLM returns response
   ↓
9. Backend stores chat history
   ↓
10. Frontend displays response with citations
```

## Security Considerations

### Current State

⚠️ **No authentication implemented**

### Recommended Implementation

1. **JWT Authentication**
   - Access token (short-lived)
   - Refresh token (long-lived, secure storage)
   - Token validation middleware

2. **Input Validation**
   - Pydantic models for all inputs
   - File type validation
   - Size limits

3. **Rate Limiting**
   - Per-user rate limiting
   - Per-endpoint rate limiting
   - Redis-based storage

4. **CORS Configuration**
   - Whitelist allowed origins
   - Secure headers

## Performance Optimization

### Caching Strategy

```python
# ✅ Good: Response caching
from functools import lru_cache

@lru_cache(maxsize=100)
def get_embedding(text: str) -> Embedding:
    """Cache embeddings to avoid redundant API calls."""
    return llm_client.embed(text)
```

### Database Optimization

```python
# ✅ Good: Connection pooling
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600
)
```

## Future Architecture Improvements

### Phase 1: Production Readiness

- [ ] Migrate to PostgreSQL for sessions
- [ ] Add Redis for caching
- [ ] Implement JWT authentication
- [ ] Add rate limiting

### Phase 2: Scalability

- [ ] Containerize with Docker
- [ ] Kubernetes deployment
- [ ] Load balancing
- [ ] Horizontal scaling

### Phase 3: Advanced Features

- [ ] Async task queue (Celery)
- [ ] Real-time updates (WebSocket)
- [ ] Multi-tenancy support
- [ ] Vector database clustering

---

**Generated with [Continue](https://continue.dev)**

Co-Authored-By: Continue <noreply@continue.dev>
