"""Pytest configuration and fixtures for RAG Chat Application tests."""

import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Add backend and tests to path
backend_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
tests_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_path)
sys.path.insert(0, tests_path)

from mocks.supabase_mock import create_mock_supabase_client


@pytest.fixture(autouse=True)
def mock_supabase_client():
    """Mock Supabase client for all tests."""
    mock_client = create_mock_supabase_client()
    
    # Patch both possible import paths
    with patch('config.supabase_config.get_supabase_client', return_value=mock_client):
        yield mock_client


@pytest.fixture
def mock_user():
    """Create mock user data."""
    return {
        "id": "test-user-id",
        "email": "test@example.com",
        "aud": "authenticated"
    }


@pytest.fixture
def mock_session():
    """Create mock session data."""
    return {
        "id": "test-session-id",
        "user_id": "test-user-id",
        "title": "Test Session",
        "created_at": "2024-01-01T00:00:00Z",
        "session_metadata": {}
    }


@pytest.fixture
def mock_document():
    """Create mock document data."""
    return {
        "id": "test-doc-id",
        "session_id": "test-session-id",
        "user_id": "test-user-id",
        "filename": "test.pdf",
        "status": "ready",
        "chunks_count": 10,
        "pages_count": 5
    }


@pytest.fixture
def mock_message():
    """Create mock message data."""
    return {
        "id": "test-msg-id",
        "session_id": "test-session-id",
        "role": "user",
        "content": "Test message",
        "created_at": "2024-01-01T00:00:00Z"
    }
