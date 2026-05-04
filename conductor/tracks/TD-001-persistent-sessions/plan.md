# TD-001: Persistent Session Storage - Implementation Plan

## Sprint Overview

**Sprint:** Technical Debt Cleanup (Week 1-2)  
**Duration:** 3 days  
**Assignee:** Backend Developer  
**Status:** 🔄 In Progress

---

## Day 1: Database Setup

### Morning (2-3 hours)

#### 1.1 Alembic Configuration
- [ ] Initialize Alembic in backend directory
- [ ] Configure `alembic.ini` with PostgreSQL URL
- [ ] Set up `env.py` for SQLAlchemy models
- [ ] Test migration commands

```bash
cd rag_app/backend
alembic init alembic
# Edit alembic.ini and env.py
```

#### 1.2 Create Initial Migration
- [ ] Generate initial migration script
- [ ] Add all tables (sessions, session_documents, chat_messages, message_sources)
- [ ] Add indexes and constraints
- [ ] Run migration to test database

```bash
alembic revision --autogenerate -m "Initial schema"
alembic upgrade head
```

#### 1.3 Update SQLAlchemy Models
- [ ] Create `models/__init__.py`
- [ ] Implement all ORM models (Session, SessionDocument, ChatMessage, MessageSource)
- [ ] Add relationships and properties
- [ ] Add validation and helper methods

```python
# rag_app/backend/models/__init__.py
from .session import Session
from .session_document import SessionDocument
from .chat_message import ChatMessage
from .message_source import MessageSource
```

### Afternoon (2-3 hours)

#### 1.4 Database Connection Setup
- [ ] Create `database.py` with engine and session factory
- [ ] Implement `get_db()` dependency
- [ ] Configure connection pooling
- [ ] Add health check endpoint

```python
# rag_app/backend/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

engine = create_engine(DATABASE_URL, pool_size=10, max_overflow=20)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

#### 1.5 Update Main Application
- [ ] Import database dependency in `main.py`
- [ ] Add database initialization on startup
- [ ] Add database cleanup on shutdown
- [ ] Update API dependencies

```python
# rag_app/backend/main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
from .database import engine, Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables
    Base.metadata.create_all(bind=engine)
    yield
    # Cleanup
    await engine.dispose()

app = FastAPI(lifespan=lifespan)
```

---

## Day 2: Session Manager Refactoring

### Morning (2-3 hours)

#### 2.1 Create PostgreSQLSessionStore
- [ ] Define `SessionStore` interface/protocol
- [ ] Implement `PostgreSQLSessionStore` class
- [ ] Implement `create()` method
- [ ] Implement `get()` method
- [ ] Implement `update()` method
- [ ] Implement `delete()` method
- [ ] Implement `list()` method

```python
# rag_app/backend/services/session_store.py
from typing import Optional, List
from sqlalchemy.orm import Session as DBSession
from ..models import Session as SessionModel

class PostgreSQLSessionStore:
    def __init__(self, db: DBSession):
        self.db = db
    
    def create(self, user_id: Optional[str] = None, ttl_hours: int = 24) -> Session:
        from datetime import datetime, timedelta
        from uuid import uuid4
        
        expires_at = datetime.utcnow() + timedelta(hours=ttl_hours)
        
        session = SessionModel(
            id=uuid4(),
            user_id=user_id,
            expires_at=expires_at,
            llm_config={}
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        
        return self._to_domain_model(session)
    
    def get(self, session_id: str) -> Optional[Session]:
        session = self.db.query(SessionModel).filter(
            SessionModel.id == session_id
        ).first()
        
        if session and session.is_expired:
            self.db.delete(session)
            self.db.commit()
            return None
        
        return self._to_domain_model(session) if session else None
    
    def delete(self, session_id: str) -> bool:
        session = self.db.query(SessionModel).filter(
            SessionModel.id == session_id
        ).first()
        
        if session:
            self.db.delete(session)
            self.db.commit()
            return True
        return False
    
    def _to_domain_model(self, model: SessionModel) -> Session:
        return Session(
            id=model.id,
            user_id=model.user_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            expires_at=model.expires_at,
            llm_config=model.llm_config,
            metadata=model.metadata
        )
```

#### 2.2 Update Session Manager
- [ ] Refactor `session_manager.py` to use PostgreSQLStore
- [ ] Remove in-memory storage code
- [ ] Add error handling
- [ ] Add logging

```python
# rag_app/backend/services/session_manager.py
from typing import Optional
from fastapi import Depends
from ..database import get_db
from .session_store import PostgreSQLSessionStore

class SessionManager:
    def __init__(self, db=Depends(get_db)):
        self.store = PostgreSQLSessionStore(db)
    
    def create_session(self, user_id: Optional[str] = None) -> Session:
        return self.store.create(user_id=user_id)
    
    def get_session(self, session_id: str) -> Optional[Session]:
        return self.store.get(session_id)
    
    def delete_session(self, session_id: str) -> bool:
        return self.store.delete(session_id)
```

### Afternoon (2-3 hours)

#### 2.3 Update API Routes
- [ ] Update `/api/sessions` endpoint to use new manager
- [ ] Update `/api/sessions/{id}` endpoint
- [ ] Update `/api/sessions/{id}/documents` endpoints
- [ ] Update `/api/sessions/{id}/query` endpoint
- [ ] Update `/api/sessions/{id}/chat` endpoint

```python
# rag_app/backend/api/routes/sessions.py
from fastapi import APIRouter, Depends
from ..services.session_manager import SessionManager

router = APIRouter()

@router.post("/sessions")
async def create_session(
    manager: SessionManager = Depends()
):
    session = manager.create_session()
    return {"session_id": str(session.id), "created_at": session.created_at}

@router.get("/sessions/{session_id}")
async def get_session(
    session_id: str,
    manager: SessionManager = Depends()
):
    session = manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session
```

#### 2.4 Testing
- [ ] Write unit tests for PostgreSQLSessionStore
- [ ] Write integration tests for session API
- [ ] Run full test suite
- [ ] Fix any failing tests

```bash
pytest rag_app/backend/tests/ -v --cov=rag_app/backend
```

---

## Day 3: Cleanup & Optimization

### Morning (2-3 hours)

#### 3.1 Auto-Cleanup Implementation
- [ ] Create cleanup task (Celery beat or cron)
- [ ] Implement session expiration check
- [ ] Implement old session deletion
- [ ] Add logging for cleanup operations

```python
# rag_app/backend/tasks/session_cleanup.py
from datetime import datetime, timedelta
from sqlalchemy import text

def cleanup_old_sessions(db):
    """Delete sessions older than configured days."""
    cutoff_date = datetime.utcnow() - timedelta(days=30)
    
    result = db.execute(
        text("DELETE FROM sessions WHERE expires_at < :cutoff"),
        {"cutoff": cutoff_date}
    )
    
    db.commit()
    print(f"Cleaned up {result.rowcount} old sessions")
```

#### 3.2 Performance Optimization
- [ ] Add missing indexes
- [ ] Optimize slow queries
- [ ] Configure connection pooling parameters
- [ ] Add query performance logging

```sql
-- Add indexes if not present
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_expires_at ON sessions(expires_at);
CREATE INDEX IF NOT EXISTS idx_session_documents_session_id ON session_documents(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id ON chat_messages(session_id);
```

#### 3.3 Documentation
- [ ] Update API documentation (Swagger/OpenAPI)
- [ ] Update deployment guide
- [ ] Create runbook for database maintenance
- [ ] Update README with database setup instructions

```markdown
# Database Setup

## Development
```bash
createdb rag_app
cd rag_app/backend
alembic upgrade head
```

## Production
Use managed PostgreSQL (AWS RDS, Google Cloud SQL, etc.)
```

### Afternoon (2-3 hours)

#### 3.4 Final Testing
- [ ] Run full test suite
- [ ] Performance testing (load test)
- [ ] Integration testing with frontend
- [ ] Smoke test in staging environment

#### 3.5 Code Review
- [ ] Self-review all changes
- [ ] Request peer review
- [ ] Address feedback
- [ ] Update documentation

#### 3.6 Deployment Preparation
- [ ] Create migration script for production
- [ ] Document rollback procedure
- [ ] Prepare deployment checklist
- [ ] Schedule deployment window

---

## Checklist

### Pre-Deployment
- [ ] All tests passing
- [ ] Code review completed
- [ ] Documentation updated
- [ ] Migration tested on staging
- [ ] Rollback plan documented

### Deployment
- [ ] Backup production database
- [ ] Run migrations
- [ ] Restart backend services
- [ ] Verify session creation
- [ ] Verify session persistence
- [ ] Monitor error logs

### Post-Deployment
- [ ] Monitor performance metrics
- [ ] Check for errors in logs
- [ ] Verify cleanup task running
- [ ] Update monitoring dashboards
- [ ] Document lessons learned

---

## Success Criteria

- [x] Sessions persist after backend restart
- [ ] All unit tests passing (>80% coverage)
- [ ] All integration tests passing
- [ ] Query latency < 10ms
- [ ] Documentation complete
- [ ] Code review approved
- [ ] Deployed to staging
- [ ] Deployed to production

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Database connection issues | Connection pooling, retry logic |
| Data loss during migration | Backup before migration |
| Performance issues | Indexes, query optimization |
| Schema migration failures | Rollback plan, version control |

---

## Notes

- **Database:** PostgreSQL 15+ required
- **Dependencies:** SQLAlchemy 2.0+, Alembic 1.13+
- **Testing:** Use test database for all tests
- **Migration:** Run migrations before starting backend

---

**Last Updated:** 2026-05-04  
**Version:** 1.0.0
