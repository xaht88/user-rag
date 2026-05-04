# ADR-001: Client-Server Architecture Pattern

## Status

Accepted

## Date

2024-01-15

## Context

We need to design the overall architecture for the RAG Chat Application. The application needs to:

- Support multiple users uploading and querying documents
- Process documents and generate embeddings
- Provide real-time chat interface
- Scale to handle concurrent users
- Support multiple LLM providers (OpenAI, Ollama)

## Decision

We will use a **Client-Server architecture** with the following components:

1. **Frontend:** Next.js 14 (React, TypeScript, Tailwind CSS)
2. **Backend:** FastAPI (Python, REST API)
3. **Vector Database:** ChromaDB (embedded mode for development, cluster for production)
4. **LLM Integration:** Abstracted layer supporting multiple providers

### Architecture Diagram

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

## Alternatives Considered

### 1. Monolithic Architecture (All-in-One)

**Description:** Single application handling both frontend and backend.

**Pros:**
- Simpler deployment
- No CORS issues
- Easier for small projects

**Cons:**
- Limited scalability
- Frontend and backend tightly coupled
- Cannot scale independently
- Harder to maintain codebase as it grows

**Rejected:** Our application needs independent scaling of frontend and backend, plus we want to support multiple frontend clients in the future.

### 2. Serverless Architecture

**Description:** Use serverless functions for backend (AWS Lambda, Vercel Functions).

**Pros:**
- Automatic scaling
- Pay-per-use pricing
- No server management

**Cons:**
- Cold start latency (bad for real-time chat)
- Limited execution time (document processing can be slow)
- Vendor lock-in
- Higher cost for consistent traffic

**Rejected:** Document processing and real-time chat require longer execution times and consistent performance.

### 3. GraphQL API

**Description:** Use GraphQL instead of REST for API communication.

**Pros:**
- Flexible data fetching
- Single endpoint
- Strong typing with GraphQL Schema

**Cons:**
- More complex setup
- Overkill for our use case
- Caching is more complex
- Learning curve for team

**Rejected:** Our API is relatively simple with well-defined endpoints. REST is simpler and sufficient.

### 4. PostgreSQL for Vector Storage

**Description:** Use PostgreSQL with pgvector extension instead of ChromaDB.

**Pros:**
- Single database for everything
- Mature ecosystem
- Better transaction support

**Cons:**
- Vector search performance not as good as dedicated vector DB
- More complex setup
- Less specialized for RAG use case

**Rejected:** ChromaDB is purpose-built for RAG, easier to set up, and has better performance for vector operations.

## Consequences

### Positive

1. **Scalability:** Frontend and backend can scale independently
2. **Technology Flexibility:** Can swap out components without affecting others
3. **Team Collaboration:** Frontend and backend teams can work independently
4. **Future-Proof:** Easy to add new frontend clients (mobile, etc.)
5. **Development Experience:** Hot reload, separate dev servers

### Negative

1. **CORS Configuration:** Need to handle cross-origin requests
2. **Deployment Complexity:** Multiple services to deploy and manage
3. **Network Latency:** Additional hop between frontend and backend
4. **State Management:** Sessions need to be stored externally (Redis/PostgreSQL) for production

### Technical Debt

- In-memory session storage (needs to be replaced with Redis/PostgreSQL for production)
- No authentication currently (needs JWT implementation)
- Mock LLM responses (needs real implementation)

## References

- [System Architecture Overview](../architecture/system-overview.md)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [ChromaDB Documentation](https://docs.trychroma.com/)
