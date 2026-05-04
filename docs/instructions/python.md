# Python Backend Conventions

## Overview

Python backend follows PEP 8 guidelines with strict type hints and modern async patterns.

## Core Rules

### Code Style

- **Follow PEP 8** — use `black` for formatting
- **Use `flake8`** for linting
- **Use `isort`** for import sorting
- **4-space indentation**, max line length 88 characters
- **Use type hints** for all function signatures

### Project Structure

```python
rag_app/backend/
├── main.py                 # FastAPI app entry point
├── rag_engine.py           # RAG core logic
├── models.py               # Pydantic models
├── schemas.py              # API schemas
├── services/               # Business logic
│   ├── document_service.py
│   └── query_service.py
├── utils/                  # Utility functions
│   └── embedding_utils.py
└── tests/                  # Tests
```

### FastAPI Patterns

```python
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List

app = FastAPI(title="RAG Chat API")

# ✅ Good: Pydantic model with validation
class DocumentUpload(BaseModel):
    filename: str = Field(..., min_length=1, max_length=255)
    content_type: str
    session_id: str

# ✅ Good: Dependency injection
def get_session(session_id: str):
    session = session_store.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

# ✅ Good: Async endpoint with proper typing
@app.post("/api/upload")
async def upload_document(
    doc: DocumentUpload,
    session = Depends(get_session)
) -> dict:
    """Upload a document to the session."""
    # Implementation
    return {"status": "uploaded", "doc_id": doc_id}
```

### Error Handling

```python
# ✅ Good: Custom exceptions
class RAGError(Exception):
    """Base exception for RAG errors."""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class DocumentNotFoundError(RAGError):
    """Raised when document is not found."""
    def __init__(self, doc_id: str):
        super().__init__(f"Document {doc_id} not found", 404)

# ✅ Good: Try/catch with specific exceptions
async def process_document(file_path: str) -> Embeddings:
    try:
        return await embed_document(file_path)
    except FileNotFoundError:
        raise DocumentNotFoundError(file_path)
    except ValueError as e:
        raise RAGError(f"Invalid document format: {e}", 400)
```

### Database Patterns

```python
# ✅ Good: Context managers for resource management
from contextlib import asynccontextmanager

@asynccontextmanager
async def get_db_session():
    """Context manager for database sessions."""
    session = DatabaseSession()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()

# Usage
async with get_db_session() as session:
    result = await session.query(...)
```

### Logging

```python
import logging

# ✅ Good: Structured logging setup
logger = logging.getLogger(__name__)

def process_query(query: str, session_id: str) -> Response:
    logger.info("Processing query", extra={
        "session_id": session_id,
        "query_length": len(query)
    })
    
    try:
        result = perform_query(query)
        logger.debug("Query processed successfully")
        return result
    except Exception as e:
        logger.error("Query failed", exc_info=True)
        raise
```

## Best Practices

1. **Use async/await** for I/O operations
2. **Validate all inputs** with Pydantic models
3. **Use dependency injection** for services
4. **Write docstrings** for all public functions
5. **Use logging** instead of print statements
6. **Handle errors gracefully** with proper HTTP status codes

## Testing

```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@pytest.fixture
def test_client():
    return TestClient(app)

@pytest.mark.asyncio
async def test_upload_document(test_client):
    response = await client.post(
        "/api/upload",
        json={"filename": "test.pdf", "content_type": "application/pdf"}
    )
    assert response.status_code == 200
```

---

**Generated with [Continue](https://continue.dev)**

Co-Authored-By: Continue <noreply@continue.dev>
