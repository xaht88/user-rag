# Persistent Session Storage - Documentation

## Overview

This document describes the persistent session storage implementation for RAG Chat Application using PostgreSQL (Supabase).

## Architecture

```
┌─────────────────┐
│   FastAPI App   │
└────────┬────────┘
         │ Depends(get_db)
         ▼
┌─────────────────┐
│  SessionManager │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│PostgreSQLStore  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  PostgreSQL DB  │
│  (Supabase)     │
└─────────────────┘
```

## Components

### 1. Database Models (`models/__init__.py`)

#### Session
- **id**: UUID - Primary key
- **user_id**: UUID - Optional user reference
- **created_at**: TIMESTAMP - Session creation time
- **updated_at**: TIMESTAMP - Last update time (auto-updated)
- **expires_at**: TIMESTAMP - Session expiration time
- **llm_config**: JSONB - LLM configuration
- **session_metadata**: JSONB - Additional metadata

**Properties:**
- `is_expired`: Check if session has expired
- `ttl_seconds`: Time to live in seconds
- `extend_ttl(hours)`: Extend session TTL

#### SessionDocument
- **id**: UUID - Primary key
- **session_id**: UUID - Foreign key to sessions
- **document_id**: UUID - Document reference
- **filename**: VARCHAR(255) - Original filename
- **status**: ENUM - 'processing', 'ready', 'error'
- **chunks_count**: INTEGER - Number of chunks
- **pages_count**: INTEGER - Number of pages
- **selected**: BOOLEAN - Whether document is selected for search
- **uploaded_at**: TIMESTAMP - Upload time

**Properties:**
- `is_ready`: Check if document is ready
- `is_processing`: Check if document is being processed

#### ChatMessage
- **id**: UUID - Primary key
- **session_id**: UUID - Foreign key to sessions
- **role**: ENUM - 'user', 'assistant', 'system'
- **content**: TEXT - Message content
- **created_at**: TIMESTAMP - Creation time

**Properties:**
- `is_user`: Check if message is from user
- `is_assistant`: Check if message is from assistant

#### MessageSource
- **id**: UUID - Primary key
- **message_id**: UUID - Foreign key to chat_messages
- **document_id**: UUID - Document reference
- **filename**: VARCHAR(255) - Source filename
- **page**: INTEGER - Page number
- **chunk_id**: VARCHAR(100) - Chunk identifier
- **snippet**: TEXT - Relevant text snippet
- **relevance_score**: FLOAT - Relevance score

### 2. Database Connection (`database.py`)

```python
from database import get_db, init_db, cleanup_db

# Get database session (FastAPI dependency)
def some_endpoint(db: Session = Depends(get_db)):
    # Use db session
    pass

# Initialize tables on startup
init_db()

# Cleanup on shutdown
cleanup_db()
```

### 3. Session Store (`services/session_store.py`)

```python
from services.session_store import PostgreSQLSessionStore

# Create store
store = PostgreSQLSessionStore(db)

# Create session
session = store.create(
    user_id="user-uuid",
    ttl_hours=24,
    llm_config={"provider": "openai", "model": "gpt-4o"}
)

# Get session
session = store.get(session_id)

# Update session
store.update(
    session_id=session_id,
    llm_config={"provider": "ollama"}
)

# Delete session
deleted = store.delete(session_id)

# List sessions
sessions = store.list(user_id="user-uuid")

# Cleanup old sessions
deleted_count = store.cleanup_expired(days=30)
```

### 4. Session Manager (`services/session_manager.py`)

```python
from fastapi import Depends
from services.session_manager import SessionManager

# Create manager (FastAPI dependency)
def get_session_manager(db=Depends(get_db)):
    return SessionManager(db)

# Use in endpoints
@app.post("/sessions")
async def create_session(manager: SessionManager = Depends()):
    session = manager.create_session()
    return {"session_id": str(session.id)}
```

## Database Schema

### Tables

#### sessions
```sql
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE,
    llm_config JSONB NOT NULL DEFAULT '{}',
    session_metadata JSONB DEFAULT '{}'
);
```

#### session_documents
```sql
CREATE TABLE session_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    document_id UUID NOT NULL,
    filename VARCHAR(255) NOT NULL,
    status document_status NOT NULL DEFAULT 'processing',
    chunks_count INTEGER DEFAULT 0,
    pages_count INTEGER DEFAULT 0,
    selected BOOLEAN DEFAULT FALSE,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(session_id, document_id)
);
```

#### chat_messages
```sql
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    role message_role NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

#### message_sources
```sql
CREATE TABLE message_sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id UUID NOT NULL REFERENCES chat_messages(id) ON DELETE CASCADE,
    document_id UUID NOT NULL,
    filename VARCHAR(255) NOT NULL,
    page INTEGER,
    chunk_id VARCHAR(100),
    snippet TEXT,
    relevance_score FLOAT
);
```

### Indexes

- `idx_sessions_user_id` ON sessions(user_id)
- `idx_sessions_expires_at` ON sessions(expires_at)
- `idx_session_documents_session_id` ON session_documents(session_id)
- `idx_chat_messages_session_id` ON chat_messages(session_id)
- `idx_chat_messages_created_at` ON chat_messages(created_at)

### Triggers

```sql
CREATE TRIGGER update_sessions_updated_at BEFORE UPDATE ON sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

## Running Migrations

```bash
# Activate virtual environment
cd rag_app/backend
.\venv\Scripts\Activate.ps1

# Run migrations
alembic upgrade head

# Create new migration (if needed)
alembic revision --autogenerate -m "Description"

# Rollback one step
alembic downgrade -1
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=services --cov-report=html

# Run specific test
pytest tests/test_session_store.py::TestPostgreSQLSessionStore::test_create_session -v
```

## Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost/dbname
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20

# Supabase (if using Supabase)
SUPABASE_URL=https://project.supabase.co
SUPABASE_DB_PASSWORD=your_db_password

# Session configuration
SESSION_TTL_HOURS=24
SESSION_CLEANUP_DAYS=30
```

## Best Practices

1. **Always use session manager** for session operations
2. **Extend TTL** on active sessions to prevent premature expiration
3. **Run cleanup** regularly to remove old sessions
4. **Use transactions** for atomic operations
5. **Handle exceptions** gracefully in production

## Troubleshooting

### Session not persisting
- Check database connection
- Verify migration was run: `alembic current`
- Check logs for errors

### Slow queries
- Ensure indexes are created
- Check connection pool settings
- Monitor query performance

### Memory issues
- Reduce pool_size if memory constrained
- Run cleanup more frequently
- Monitor connection count

---

**Version:** 1.0.0  
**Last Updated:** 2026-05-11
