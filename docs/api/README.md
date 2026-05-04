# API Documentation

## Overview

Complete REST API documentation for the RAG Chat Application.

## OpenAPI Specification

The API is fully documented using OpenAPI 3.0.3 specification.

### View API Documentation

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI YAML:** [openapi.yaml](./openapi.yaml)

## Endpoints

### Documents

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/upload` | Upload document (PDF, DOCX, TXT, MD) |
| GET | `/api/sessions/{session_id}/documents` | List documents in session |
| POST | `/api/sessions/{session_id}/documents/{doc_id}/toggle` | Toggle document selection |
| POST | `/api/sessions/{session_id}/documents/{doc_id}/delete` | Delete document |

### Sessions

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/sessions/{session_id}/llm/config` | Configure LLM for session |

### Chat

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/sessions/{session_id}/query` | Send query to LLM |
| GET | `/api/sessions/{session_id}/chat` | Get chat history |

### LLM

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/llm/providers` | List available LLM providers |

## Request/Response Formats

### Upload Document

**Request:**
```http
POST /api/upload
Content-Type: multipart/form-data

file: <binary>
```

**Response:**
```json
{
  "session_id": "uuid",
  "document_id": "uuid",
  "message": "Document uploaded successfully"
}
```

### Send Query

**Request:**
```http
POST /api/sessions/{session_id}/query
Content-Type: application/json

{
  "query": "What is the main topic?",
  "document_ids": ["uuid1", "uuid2"]
}
```

**Response:**
```json
{
  "message": "Generated response",
  "sources": [
    {
      "filename": "document.pdf",
      "page": 1,
      "snippet": "Relevant text excerpt..."
    }
  ],
  "history": [
    {
      "role": "user",
      "content": "What is the main topic?"
    },
    {
      "role": "assistant",
      "content": "Generated response",
      "sources": [...]
    }
  ]
}
```

## Data Models

### DocumentInfo

```json
{
  "id": "uuid",
  "filename": "document.pdf",
  "upload_date": "2024-01-15T10:30:00Z",
  "chunks_count": 10,
  "pages_count": 5,
  "status": "ready",
  "selected": true
}
```

### LLMConfig

```json
{
  "provider": "openai",
  "model": "gpt-4",
  "api_key": "sk-..."
}
```

### ChatMessage

```json
{
  "role": "user",
  "content": "Question text",
  "sources": []
}
```

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error description"
}
```

### Status Codes

- `200` — Success
- `400` — Bad Request (validation error)
- `404` — Not Found
- `500` — Internal Server Error

## Authentication

⚠️ **Current State:** No authentication implemented.

**Planned:** JWT-based authentication with OAuth2 support.

## Rate Limiting

⚠️ **Current State:** No rate limiting implemented.

**Planned:** Rate limiting per IP/session.

---

**See also:**
- [System Architecture](../architecture/README.md)
- [Development Guide](../development/README.md)
