# TD-001: Persistent Session Storage - Specification

## Overview

Миграция с in-memory session storage на PostgreSQL для обеспечения persistence сессий, горизонтального масштабирования и production-ready архитектуры.

---

## Problem Statement

### Current State

Сессии хранятся в памяти backend-сервера:

```python
# ❌ Current implementation (in-memory)
sessions: Dict[str, Session] = {}

def get_session(session_id: str) -> Optional[Session]:
    return sessions.get(session_id)

def create_session() -> Session:
    session_id = str(uuid.uuid4())
    session = Session(id=session_id, created_at=datetime.utcnow())
    sessions[session_id] = session
    return session
```

### Problems

1. **Data Loss on Restart** — Все сессии теряются при перезапуске backend
2. **No Horizontal Scaling** — Сессии привязаны к конкретному инстансу
3. **No Persistence** — Невозможно production deployment
4. **Memory Constraints** — Ограничено доступной RAM

### Acceptance Criteria

- [ ] Сессии сохраняются в PostgreSQL и доступны после перезапуска
- [ ] Данные сессий изолированы (одна сессия недоступна другой)
- [ ] Автоматическая очистка старых сессий (> 30 дней)
- [ ] Поддержка горизонтального масштабирования (multiple backend instances)
- [ ] Unit-тесты для session storage с покрытием > 80%
- [ ] Документация обновлена

---

## Technical Requirements

### Database Schema

```sql
-- Sessions table
CREATE TABLE sessions (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE,
    llm_config JSONB NOT NULL DEFAULT '{}',
    metadata JSONB DEFAULT '{}'
);

-- Session documents table
CREATE TABLE session_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES sessions(id) ON DELETE CASCADE,
    document_id UUID NOT NULL,
    filename VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'processing',
    chunks_count INTEGER DEFAULT 0,
    pages_count INTEGER DEFAULT 0,
    selected BOOLEAN DEFAULT FALSE,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(session_id, document_id)
);

-- Chat messages table
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES sessions(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Message sources table
CREATE TABLE message_sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id UUID REFERENCES chat_messages(id) ON DELETE CASCADE,
    document_id UUID NOT NULL,
    filename VARCHAR(255) NOT NULL,
    page INTEGER,
    chunk_id VARCHAR(100),
    snippet TEXT,
    relevance_score FLOAT
);

-- Indexes
CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_expires_at ON sessions(expires_at);
CREATE INDEX idx_session_documents_session_id ON session_documents(session_id);
CREATE INDEX idx_chat_messages_session_id ON chat_messages(session_id);
CREATE INDEX idx_chat_messages_created_at ON chat_messages(created_at);

-- Function for auto-updating updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_sessions_updated_at BEFORE UPDATE ON sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### Python Models (SQLAlchemy)

```python
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from uuid import uuid4
from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer, Float, JSON, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class Session(Base):
    __tablename__ = 'sessions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    llm_config = Column(JSON, nullable=False, default=dict)
    metadata = Column(JSON, nullable=True, default=dict)
    
    # Relationships
    documents = relationship('SessionDocument', back_populates='session', cascade='all, delete-orphan')
    messages = relationship('ChatMessage', back_populates='session', cascade='all, delete-orphan')
    
    @property
    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at
    
    @property
    def ttl_seconds(self) -> int:
        """Time to live in seconds."""
        if self.expires_at is None:
            return 0
        delta = self.expires_at - datetime.utcnow()
        return int(delta.total_seconds())
    
    def extend_ttl(self, hours: int = 24) -> None:
        """Extend session TTL."""
        self.expires_at = datetime.utcnow() + timedelta(hours=hours)


class SessionDocument(Base):
    __tablename__ = 'session_documents'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey('sessions.id'), nullable=False)
    document_id = Column(UUID(as_uuid=True), nullable=False)
    filename = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False, default='processing')
    chunks_count = Column(Integer, default=0)
    pages_count = Column(Integer, default=0)
    selected = Column(Boolean, default=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        UniqueConstraint('session_id', 'document_id', name='uq_session_document'),
    )
    
    # Relationships
    session = relationship('Session', back_populates='documents')
    
    @property
    def is_ready(self) -> bool:
        return self.status == 'ready'
    
    @property
    def is_processing(self) -> bool:
        return self.status == 'processing'


class ChatMessage(Base):
    __tablename__ = 'chat_messages'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey('sessions.id'), nullable=False)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    session = relationship('Session', back_populates='messages')
    sources = relationship('MessageSource', back_populates='message', cascade='all, delete-orphan')
    
    @property
    def is_user(self) -> bool:
        return self.role == 'user'
    
    @property
    def is_assistant(self) -> bool:
        return self.role == 'assistant'


class MessageSource(Base):
    __tablename__ = 'message_sources'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    message_id = Column(UUID(as_uuid=True), ForeignKey('chat_messages.id'), nullable=False)
    document_id = Column(UUID(as_uuid=True), nullable=False)
    filename = Column(String(255), nullable=False)
    page = Column(Integer, nullable=True)
    chunk_id = Column(String(100), nullable=True)
    snippet = Column(Text, nullable=True)
    relevance_score = Column(Float, nullable=True)
    
    # Relationships
    message = relationship('ChatMessage', back_populates='sources')
```

---

## Implementation Plan

### Phase 1: Database Setup (Day 1)

1. **Create migration scripts**
   - Alembic configuration
   - Initial migration with all tables
   - Data types and constraints

2. **Update SQLAlchemy models**
   - Replace in-memory storage with ORM models
   - Add relationships and properties

3. **Create database connection**
   - SQLAlchemy engine configuration
   - Session factory
   - Connection pooling

### Phase 2: Session Manager Refactoring (Day 2)

1. **Create PostgreSQLSessionStore**
   - Implement `SessionStore` interface
   - CRUD operations for sessions
   - TTL management

2. **Update existing code**
   - Replace in-memory calls with DB calls
   - Add error handling
   - Add logging

3. **Testing**
   - Unit tests for session operations
   - Integration tests with test database

### Phase 3: Cleanup & Optimization (Day 3)

1. **Auto-cleanup of old sessions**
   - Background task (Celery beat or cron)
   - Delete sessions older than 30 days

2. **Performance optimization**
   - Add indexes
   - Query optimization
   - Connection pooling configuration

3. **Documentation**
   - Update API documentation
   - Add deployment instructions
   - Create runbook

---

## Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/rag_app
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20

# Session configuration
SESSION_TTL_HOURS=24
SESSION_CLEANUP_DAYS=30
SESSION_CLEANUP_INTERVAL_HOURS=24
```

### SQLAlchemy Configuration

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://localhost/rag_app')

engine = create_engine(
    DATABASE_URL,
    pool_size=int(os.getenv('DATABASE_POOL_SIZE', 10)),
    max_overflow=int(os.getenv('DATABASE_MAX_OVERFLOW', 20)),
    pool_pre_ping=True,
    echo=os.getenv('DEBUG', 'false').lower() == 'true'
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

## API Changes

### Current API (In-Memory)

```python
# Current endpoints
POST /api/sessions              # Create session
GET  /api/sessions/{id}         # Get session
DELETE /api/sessions/{id}       # Delete session
```

### New API (PostgreSQL)

No API changes required — the interface remains the same. Only the storage layer changes.

---

## Testing Strategy

### Unit Tests

```python
# tests/test_session_store.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base, Session
from app.services.session_store import PostgreSQLSessionStore


@pytest.fixture
def test_db():
    """Create test database."""
    engine = create_engine('postgresql://test:test@localhost/test_db')
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


class TestPostgreSQLSessionStore:
    def test_create_session(self, test_db):
        store = PostgreSQLSessionStore(test_db)
        session = store.create()
        
        assert session is not None
        assert session.id is not None
        assert session.created_at is not None
    
    def test_get_session(self, test_db):
        store = PostgreSQLSessionStore(test_db)
        session = store.create()
        retrieved = store.get(session.id)
        
        assert retrieved is not None
        assert retrieved.id == session.id
    
    def test_delete_session(self, test_db):
        store = PostgreSQLSessionStore(test_db)
        session = store.create()
        store.delete(session.id)
        
        retrieved = store.get(session.id)
        assert retrieved is None
    
    def test_session_ttl(self, test_db):
        store = PostgreSQLSessionStore(test_db)
        session = store.create(ttl_hours=1)
        
        assert session.ttl_seconds == 3600
        assert session.is_expired is False
        
        # Extend TTL
        session.extend_ttl(hours=2)
        assert session.ttl_seconds == 7200
```

### Integration Tests

```python
# tests/integration/test_session_api.py
import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client(test_db):
    """Create test client with test database."""
    client = TestClient(app)
    yield client


def test_create_session(client, test_db):
    """Test session creation with PostgreSQL storage."""
    response = client.post('/api/sessions')
    
    assert response.status_code == 200
    data = response.json()
    assert 'session_id' in data
    assert 'created_at' in data


def test_get_session(client, test_db):
    """Test session retrieval from PostgreSQL."""
    # First create a session
    create_response = client.post('/api/sessions')
    session_id = create_response.json()['session_id']
    
    # Then retrieve it
    response = client.get(f'/api/sessions/{session_id}')
    
    assert response.status_code == 200
    data = response.json()
    assert data['session_id'] == session_id
```

---

## Migration Guide

### For Developers

1. **Install PostgreSQL**
   ```bash
   # macOS
   brew install postgresql
   
   # Ubuntu/Debian
   sudo apt-get install postgresql postgresql-contrib
   
   # Windows
   # Download from https://www.postgresql.org/download/windows/
   ```

2. **Create database**
   ```bash
   createdb rag_app
   ```

3. **Run migrations**
   ```bash
   cd rag_app/backend
   alembic upgrade head
   ```

4. **Update .env**
   ```bash
   DATABASE_URL=postgresql://user:password@localhost/rag_app
   ```

### For Production

1. **Use managed PostgreSQL** (AWS RDS, Google Cloud SQL, etc.)
2. **Enable backups**
3. **Configure connection pooling** (PgBouncer)
4. **Set up monitoring** (query performance, connection count)

---

## Rollback Plan

If issues occur:

1. **Keep in-memory store as fallback**
   ```python
   # Add feature flag
   USE_POSTGRESQL = os.getenv('USE_POSTGRESQL', 'true').lower() == 'true'
   
   if USE_POSTGRESQL:
       store = PostgreSQLSessionStore(db)
   else:
       store = InMemorySessionStore()
   ```

2. **Quick rollback**
   ```bash
   # Set environment variable
   export USE_POSTGRESQL=false
   
   # Restart backend
   uvicorn main:app --reload
   ```

3. **Data migration back** (if needed)
   ```python
   # Export PostgreSQL data to JSON
   # Import JSON to in-memory store
   ```

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Session persistence | 100% | Sessions survive restart |
| Query latency | < 10ms | Average DB query time |
| Connection pool usage | < 80% | Max connections / pool_size |
| Test coverage | > 80% | Coverage report |
| Cleanup efficiency | 100% | Old sessions removed |

---

## Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Database connection issues | Medium | High | Connection pooling, retry logic |
| Data loss during migration | Low | Critical | Backup before migration |
| Performance degradation | Medium | Medium | Indexes, query optimization |
| Schema migration failures | Low | High | Rollback plan, version control |

---

## References

- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [ADR-002: Session Management Strategy](../../../docs/decisions/ADR-002-session-management.md)

---

**Last Updated:** 2026-05-04  
**Version:** 1.0.0
