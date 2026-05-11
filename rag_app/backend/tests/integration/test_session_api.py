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
    # Create mock Supabase client
    mock_supabase = MagicMock()
    
    # Mock table responses
    mock_table = MagicMock()
    mock_supabase.table.return_value = mock_table
    
    # Mock select
    mock_select = MagicMock()
    mock_table.select.return_value = mock_select
    mock_select.eq.return_value = mock_select
    mock_select.in_.return_value = mock_select
    mock_select.order.return_value = mock_select
    mock_select.execute.return_value = MagicMock(data=[])
    
    # Mock insert
    mock_insert = MagicMock()
    mock_table.insert.return_value = mock_insert
    mock_insert.execute.return_value = MagicMock(data=[{
        "id": str(uuid4()),
        "user_id": "test-user",
        "title": "New Conversation",
        "created_at": datetime.utcnow().isoformat(),
        "session_metadata": {}
    }])
    
    # Mock update
    mock_update = MagicMock()
    mock_table.update.return_value = mock_update
    mock_update.eq.return_value = mock_update
    mock_update.execute.return_value = MagicMock(data=[])
    
    # Mock delete
    mock_delete = MagicMock()
    mock_table.delete.return_value = mock_delete
    mock_delete.eq.return_value = mock_delete
    mock_delete.execute.return_value = MagicMock(data=[])
    
    with patch('config.supabase_config.get_supabase_client', return_value=mock_supabase):
        client = TestClient(app)
        yield client


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
        # Override the get_current_user dependency to bypass JWT
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        response = client.post("/api/sessions")
        
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert "message" in data
        
        app.dependency_overrides.clear()
    
    def test_create_session_anonymous(self, client, mock_current_user):
        """Test creation of anonymous session (no user_id)."""
        async def mock_get_current_user():
            return {}
        
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
        user_id = str(uuid4())
        session_id = str(uuid4())
        
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
        async def mock_get_current_user():
            return {"id": str(uuid4())}
        
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        response = client.get("/api/sessions/non-existent-id")
        
        # Should return 404
        assert response.status_code == 404
        
        app.dependency_overrides.clear()
    
    def test_get_session_wrong_user(self, client, mock_current_user):
        """Test getting session that belongs to another user."""
        user1_id = str(uuid4())
        user2_id = str(uuid4())
        session_id = str(uuid4())
        
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
        user_id = str(uuid4())
        
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
        user_id = str(uuid4())
        session_id = str(uuid4())
        
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
        user_id = str(uuid4())
        session_id = str(uuid4())
        
        async def mock_get_current_user():
            return {"id": user_id}
        
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        response = client.get(f"/api/sessions/{session_id}/chat")
        
        assert response.status_code == 200
        data = response.json()
        assert "history" in data
        
        app.dependency_overrides.clear()
