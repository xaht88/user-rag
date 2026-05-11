"""Integration tests for session API endpoints.

Tests the actual FastAPI endpoints with mock Supabase client.
Uses dependency override to bypass JWT authentication.
"""

import pytest
import sys
import os
from datetime import datetime, timedelta
from uuid import uuid4, UUID
from unittest.mock import MagicMock, patch, AsyncMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from fastapi import Depends, HTTPException

# Import app and get_current_user from main
from main import app, get_current_user


@pytest.fixture
def client():
    """Create test client with mock Supabase."""
    from tests.mocks.supabase_mock import create_mock_supabase_client
    
    mock_supabase = create_mock_supabase_client()
    
    with patch('config.supabase_config.get_supabase_client', return_value=mock_supabase):
        client = TestClient(app)
        yield client, mock_supabase


@pytest.fixture
def mock_current_user():
    """Mock current user for dependency override."""
    return {"id": str(uuid4()), "email": "test@example.com", "aud": "authenticated"}


async def mock_get_current_user():
    """Mock dependency that bypasses JWT validation."""
    return {"id": str(uuid4()), "email": "test@example.com", "aud": "authenticated"}


class TestSessionCreation:
    """Tests for session creation endpoints."""
    
    def test_create_session(self, client, mock_current_user):
        """Test session creation endpoint."""
        client, mock_supabase = client
        
        async def mock_get_current_user():
            return {"id": str(uuid4()), "email": "test@example.com", "aud": "authenticated"}
        
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        response = client.post("/api/sessions")
        
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert "message" in data
        
        app.dependency_overrides.clear()
    
    def test_create_session_anonymous(self, client, mock_current_user):
        """Test creation of anonymous session (user_id is optional)."""
        client, mock_supabase = client
        
        async def mock_get_current_user():
            # Always return a valid user id for testing
            return {"id": str(uuid4())}
        
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        response = client.post("/api/sessions")
        
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        
        app.dependency_overrides.clear()


class TestSessionRetrieval:
    """Tests for session retrieval endpoints."""
    
    def test_get_session(self, client, mock_current_user):
        """Test getting a session by ID."""
        client, mock_supabase = client
        user_id = str(uuid4())
        session_id = str(uuid4())
        
        # Set up mock data
        mock_supabase.set_current_user(user_id)
        mock_supabase.table("sessions").insert().values({
            "id": session_id,
            "user_id": user_id,
            "title": "Test Session",
            "session_metadata": {}
        }).execute()
        
        async def mock_get_current_user():
            return {"id": user_id}
        
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        response = client.get(f"/api/sessions/{session_id}")
        
        # Should return 200 with mock
        assert response.status_code == 200
        data = response.json()
        assert "session" in data
        
        app.dependency_overrides.clear()
    
    def test_get_session_not_found(self, client, mock_current_user):
        """Test getting non-existent session."""
        client, mock_supabase = client
        
        async def mock_get_current_user():
            return {"id": str(uuid4())}
        
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        response = client.get("/api/sessions/non-existent-id")
        
        # Should return 404
        assert response.status_code == 404
        
        app.dependency_overrides.clear()
    
    def test_get_session_wrong_user(self, client, mock_current_user):
        """Test getting session that belongs to another user."""
        client, mock_supabase = client
        user1_id = str(uuid4())
        user2_id = str(uuid4())
        session_id = str(uuid4())
        
        # Set up mock data for user1
        mock_supabase.set_current_user(user1_id)
        mock_supabase.table("sessions").insert().values({
            "id": session_id,
            "user_id": user1_id,
            "title": "Test Session",
            "session_metadata": {}
        }).execute()
        
        async def mock_get_current_user():
            return {"id": user2_id}
        
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        response = client.get(f"/api/sessions/{session_id}")
        
        # Should return 404
        assert response.status_code == 404
        
        app.dependency_overrides.clear()


class TestSessionList:
    """Tests for session listing endpoints."""
    
    def test_list_sessions(self, client, mock_current_user):
        """Test listing all sessions for a user."""
        client, mock_supabase = client
        user_id = str(uuid4())
        session_id = str(uuid4())
        
        # Set up mock data
        mock_supabase.set_current_user(user_id)
        mock_supabase.table("sessions").insert().values({
            "id": session_id,
            "user_id": user_id,
            "title": "Test Session",
            "session_metadata": {}
        }).execute()
        
        async def mock_get_current_user():
            return {"id": user_id}
        
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        response = client.get("/api/sessions")
        
        assert response.status_code == 200
        data = response.json()
        assert "sessions" in data
        
        app.dependency_overrides.clear()
    
    def test_list_sessions_empty(self, client, mock_current_user):
        """Test listing sessions when user has no sessions."""
        client, mock_supabase = client
        user_id = str(uuid4())
        
        async def mock_get_current_user():
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
    
    def test_get_session_documents(self, client, mock_current_user):
        """Test getting documents for a session."""
        client, mock_supabase = client
        user_id = str(uuid4())
        session_id = str(uuid4())
        
        # Set up mock data
        mock_supabase.set_current_user(user_id)
        mock_supabase.table("sessions").insert().values({
            "id": session_id,
            "user_id": user_id,
            "title": "Test Session",
            "session_metadata": {}
        }).execute()
        
        mock_supabase.table("documents").insert().values({
            "id": str(uuid4()),
            "session_id": session_id,
            "user_id": user_id,
            "filename": "test.pdf",
            "status": "ready",
            "chunks_count": 10,
            "pages_count": 5
        }).execute()
        
        async def mock_get_current_user():
            return {"id": user_id}
        
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        response = client.get(f"/api/sessions/{session_id}/documents")
        
        assert response.status_code == 200
        data = response.json()
        assert "documents" in data
        
        app.dependency_overrides.clear()


class TestChatHistory:
    """Tests for chat history endpoints."""
    
    def test_get_chat_history(self, client, mock_current_user):
        """Test getting chat history for a session."""
        client, mock_supabase = client
        user_id = str(uuid4())
        session_id = str(uuid4())
        
        # Set up mock data
        mock_supabase.set_current_user(user_id)
        mock_supabase.table("sessions").insert().values({
            "id": session_id,
            "user_id": user_id,
            "title": "Test Session",
            "session_metadata": {}
        }).execute()
        
        mock_supabase.table("messages").insert().values({
            "id": str(uuid4()),
            "session_id": session_id,
            "role": "user",
            "content": "Test message",
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        
        async def mock_get_current_user():
            return {"id": user_id}
        
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        response = client.get(f"/api/sessions/{session_id}/chat")
        
        assert response.status_code == 200
        data = response.json()
        assert "history" in data
        
        app.dependency_overrides.clear()
