"""Integration tests for session API endpoints.

Tests the actual FastAPI endpoints with a test database.
"""

import pytest
import sys
import os
from datetime import datetime, timedelta
from uuid import uuid4

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from database import Base, get_db
from models import Session as SessionModel


# Create test database
TEST_DATABASE_URL = "sqlite:///./test_rag_app.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def client():
    """Create test client with test database."""
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Override database dependency
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    # Cleanup
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def test_db():
    """Provide test database session."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


class TestSessionCreation:
    """Tests for session creation endpoints."""
    
    def test_create_session(self, client, test_db):
        """Test session creation endpoint."""
        # Create a test user
        user_id = str(uuid4())
        
        # Mock the current user dependency
        def mock_get_current_user():
            return {"id": user_id}
        
        app.dependency_overrides[app.dependency_overrides.get(get_current_user, lambda: None)] = mock_get_current_user
        
        response = client.post("/api/sessions")
        
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert "message" in data
        
        # Verify session was created in database
        session = test_db.query(SessionModel).filter(
            SessionModel.id == data["session_id"]
        ).first()
        
        assert session is not None
        assert session.user_id == user_id
        
        app.dependency_overrides.clear()
    
    def test_create_session_anonymous(self, client, test_db):
        """Test creation of anonymous session (no user_id)."""
        # Mock without user_id
        def mock_get_current_user():
            return {}
        
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        response = client.post("/api/sessions")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify session was created without user_id
        session = test_db.query(SessionModel).filter(
            SessionModel.id == data["session_id"]
        ).first()
        
        assert session is not None
        assert session.user_id is None
        
        app.dependency_overrides.clear()


class TestSessionRetrieval:
    """Tests for session retrieval endpoints."""
    
    def test_get_session(self, client, test_db):
        """Test getting a session by ID."""
        # Create a session
        user_id = str(uuid4())
        session_id = str(uuid4())
        
        session = SessionModel(
            id=session_id,
            user_id=user_id,
            title="Test Session",
            metadata={"test": "value"}
        )
        test_db.add(session)
        test_db.commit()
        
        # Mock current user
        def mock_get_current_user():
            return {"id": user_id}
        
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        response = client.get(f"/api/sessions/{session_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["session"]["id"] == session_id
        assert data["session"]["user_id"] == user_id
        assert "documents" in data
        assert "messages" in data
        
        app.dependency_overrides.clear()
    
    def test_get_session_not_found(self, client, test_db):
        """Test getting non-existent session."""
        def mock_get_current_user():
            return {"id": str(uuid4())}
        
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        response = client.get("/api/sessions/non-existent-id")
        
        assert response.status_code == 404
        assert "detail" in response.json()
        
        app.dependency_overrides.clear()
    
    def test_get_session_wrong_user(self, client, test_db):
        """Test getting session that belongs to another user."""
        user1_id = str(uuid4())
        user2_id = str(uuid4())
        session_id = str(uuid4())
        
        # Create session for user1
        session = SessionModel(
            id=session_id,
            user_id=user1_id,
            title="User1 Session"
        )
        test_db.add(session)
        test_db.commit()
        
        # Try to access as user2
        def mock_get_current_user():
            return {"id": user2_id}
        
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        response = client.get(f"/api/sessions/{session_id}")
        
        assert response.status_code == 404
        
        app.dependency_overrides.clear()


class TestSessionList:
    """Tests for session listing endpoints."""
    
    def test_list_sessions(self, client, test_db):
        """Test listing all sessions for a user."""
        user_id = str(uuid4())
        
        # Create multiple sessions
        for i in range(3):
            session = SessionModel(
                id=str(uuid4()),
                user_id=user_id,
                title=f"Session {i}"
            )
            test_db.add(session)
        
        test_db.commit()
        
        def mock_get_current_user():
            return {"id": user_id}
        
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        response = client.get("/api/sessions")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "sessions" in data
        assert len(data["sessions"]) == 3
        
        app.dependency_overrides.clear()
    
    def test_list_sessions_empty(self, client, test_db):
        """Test listing sessions when user has no sessions."""
        user_id = str(uuid4())
        
        def mock_get_current_user():
            return {"id": user_id}
        
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        response = client.get("/api/sessions")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "sessions" in data
        assert len(data["sessions"]) == 0
        
        app.dependency_overrides.clear()


class TestSessionDocuments:
    """Tests for session document endpoints."""
    
    def test_get_session_documents(self, client, test_db):
        """Test getting documents for a session."""
        user_id = str(uuid4())
        session_id = str(uuid4())
        
        # Create session
        session = SessionModel(id=session_id, user_id=user_id)
        test_db.add(session)
        
        # Create documents
        for i in range(2):
            doc = {
                "id": str(uuid4()),
                "session_id": session_id,
                "user_id": user_id,
                "filename": f"test_{i}.pdf",
                "status": "ready"
            }
            test_db.execute(
                test_db.bind.table("documents").insert().values(**doc)
            )
        
        test_db.commit()
        
        def mock_get_current_user():
            return {"id": user_id}
        
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        response = client.get(f"/api/sessions/{session_id}/documents")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "documents" in data
        assert len(data["documents"]) == 2
        
        app.dependency_overrides.clear()


class TestChatHistory:
    """Tests for chat history endpoints."""
    
    def test_get_chat_history(self, client, test_db):
        """Test getting chat history for a session."""
        user_id = str(uuid4())
        session_id = str(uuid4())
        
        # Create session
        session = SessionModel(id=session_id, user_id=user_id)
        test_db.add(session)
        
        # Create messages
        messages = [
            {"session_id": session_id, "role": "user", "content": "Hello"},
            {"session_id": session_id, "role": "assistant", "content": "Hi there!"},
            {"session_id": session_id, "role": "user", "content": "How are you?"},
        ]
        
        for msg in messages:
            test_db.execute(
                test_db.bind.table("messages").insert().values(**msg)
            )
        
        test_db.commit()
        
        def mock_get_current_user():
            return {"id": user_id}
        
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        response = client.get(f"/api/sessions/{session_id}/chat")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "history" in data
        assert len(data["history"]) == 3
        
        # Verify order
        assert data["history"][0]["role"] == "user"
        assert data["history"][1]["role"] == "assistant"
        assert data["history"][2]["role"] == "user"
        
        app.dependency_overrides.clear()


def get_current_user():
    """Mock dependency for current user."""
    return {"id": str(uuid4())}


# Cleanup test database
@pytest.fixture(scope="session", autouse=True)
def cleanup_test_db():
    """Cleanup test database after all tests."""
    yield
    if os.path.exists(TEST_DATABASE_URL.replace("sqlite:///", "")):
        os.remove(TEST_DATABASE_URL.replace("sqlite:///", ""))
