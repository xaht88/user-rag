"""
Tests for PostgreSQLSessionStore.

Tests session creation, retrieval, update, deletion, and cleanup.
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock
from uuid import uuid4

from models import Session as SessionModel
from services.session_store import PostgreSQLSessionStore


class TestPostgreSQLSessionStore:
    """Tests for PostgreSQLSessionStore class."""
    
    @pytest.fixture
    def mock_db(self):
        """Create mock database session."""
        db = Mock()
        return db
    
    @pytest.fixture
    def session_store(self, mock_db):
        """Create session store instance."""
        return PostgreSQLSessionStore(mock_db)
    
    def test_create_session(self, session_store, mock_db):
        """Test session creation."""
        # Arrange
        user_id = str(uuid4())
        llm_config = {"provider": "openai", "model": "gpt-4o"}
        
        # Act
        session = session_store.create(
            user_id=user_id,
            ttl_hours=24,
            llm_config=llm_config
        )
        
        # Assert
        assert session is not None
        assert session.id is not None
        assert session.user_id == user_id
        assert session.llm_config == llm_config
        assert session.expires_at is not None
        assert session.is_expired is False
        
        # Verify database operations
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
    
    def test_create_session_default_ttl(self, session_store, mock_db):
        """Test session creation with default TTL (24 hours)."""
        session = session_store.create()
        
        expected_expires = datetime.utcnow() + timedelta(hours=24)
        time_diff = abs((session.expires_at - expected_expires).total_seconds())
        
        assert time_diff < 60  # Within 1 minute
    
    def test_create_session_no_user_id(self, session_store, mock_db):
        """Test session creation without user ID (anonymous session)."""
        session = session_store.create()
        
        assert session.user_id is None
        assert session.is_expired is False
    
    def test_get_session(self, session_store, mock_db):
        """Test session retrieval."""
        # Arrange
        session = SessionModel(
            id=uuid4(),
            user_id=str(uuid4()),
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )
        mock_db.query().filter().first.return_value = session
        
        # Act
        retrieved = session_store.get(str(session.id))
        
        # Assert
        assert retrieved is not None
        assert retrieved.id == session.id
        assert retrieved.user_id == session.user_id
    
    def test_get_session_not_found(self, session_store, mock_db):
        """Test retrieval of non-existent session."""
        mock_db.query().filter().first.return_value = None
        
        result = session_store.get(str(uuid4()))
        
        assert result is None
    
    def test_get_session_expired(self, session_store, mock_db):
        """Test retrieval of expired session (should be deleted)."""
        # Arrange
        expired_session = SessionModel(
            id=uuid4(),
            user_id=str(uuid4()),
            expires_at=datetime.utcnow() - timedelta(hours=1)
        )
        mock_db.query().filter().first.return_value = expired_session
        
        # Act
        result = session_store.get(str(expired_session.id))
        
        # Assert
        assert result is None
        mock_db.delete.assert_called_once()
        mock_db.commit.assert_called_once()
    
    def test_update_session(self, session_store, mock_db):
        """Test session update."""
        # Arrange
        session = SessionModel(
            id=uuid4(),
            user_id=str(uuid4()),
            llm_config={"provider": "openai"},
            session_metadata={}
        )
        mock_db.query().filter().first.return_value = session
        
        new_config = {"provider": "ollama", "model": "llama3"}
        
        # Act
        updated = session_store.update(
            session_id=str(session.id),
            llm_config=new_config
        )
        
        # Assert
        assert updated is not None
        assert updated.llm_config == new_config
        mock_db.commit.assert_called_once()
    
    def test_update_session_not_found(self, session_store, mock_db):
        """Test update of non-existent session."""
        mock_db.query().filter().first.return_value = None
        
        result = session_store.update(
            session_id=str(uuid4()),
            llm_config={"test": "value"}
        )
        
        assert result is None
    
    def test_delete_session(self, session_store, mock_db):
        """Test session deletion."""
        # Arrange
        session = SessionModel(id=uuid4())
        mock_db.query().filter().first.return_value = session
        
        # Act
        result = session_store.delete(str(session.id))
        
        # Assert
        assert result is True
        mock_db.delete.assert_called_once()
        mock_db.commit.assert_called_once()
    
    def test_delete_session_not_found(self, session_store, mock_db):
        """Test deletion of non-existent session."""
        mock_db.query().filter().first.return_value = None
        
        result = session_store.delete(str(uuid4()))
        
        assert result is False
        mock_db.delete.assert_not_called()
    
    def test_list_sessions(self, session_store, mock_db):
        """Test listing all sessions."""
        # Arrange
        sessions = [
            SessionModel(id=uuid4(), expires_at=datetime.utcnow() + timedelta(hours=1)),
            SessionModel(id=uuid4(), expires_at=datetime.utcnow() + timedelta(hours=2)),
        ]
        mock_query = Mock()
        mock_query.all.return_value = sessions
        mock_db.query.return_value = mock_query
        
        # Act
        result = session_store.list()
        
        # Assert
        assert len(result) == 2
        assert result == sessions
    
    def test_list_sessions_filtered_by_user(self, session_store, mock_db):
        """Test listing sessions filtered by user ID."""
        user_id = str(uuid4())
        sessions = [
            SessionModel(id=uuid4(), user_id=user_id),
            SessionModel(id=uuid4(), user_id=user_id),
        ]
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = sessions
        mock_db.query.return_value = mock_query
        
        # Act
        result = session_store.list(user_id=user_id)
        
        # Assert
        assert len(result) == 2
        for session in result:
            assert session.user_id == user_id
    
    def test_cleanup_expired_sessions(self, session_store, mock_db):
        """Test cleanup of old sessions."""
        # Arrange
        mock_db.query().filter().delete.return_value = 5
        
        # Act
        deleted_count = session_store.cleanup_expired(days=30)
        
        # Assert
        assert deleted_count == 5
        mock_db.commit.assert_called_once()
    
    def test_session_ttl_property(self, session_store, mock_db):
        """Test session TTL property calculation."""
        # Arrange - session expires in 1 hour
        session = SessionModel(
            id=uuid4(),
            expires_at=datetime.utcnow() + timedelta(hours=1)
        )
        mock_db.query().filter().first.return_value = session
        
        # Act
        retrieved = session_store.get(str(session.id))
        
        # Assert - TTL should be close to 1 hour (get() extends by 1 hour, so total ~2 hours)
        assert 3500 <= retrieved.ttl_seconds <= 3700  # Within 100 seconds of 1 hour
    
    def test_session_extend_ttl(self, session_store, mock_db):
        """Test session TTL extension."""
        # Arrange
        session = SessionModel(
            id=uuid4(),
            expires_at=datetime.utcnow() + timedelta(hours=1)
        )
        mock_db.query().filter().first.return_value = session
        
        # Act
        retrieved = session_store.get(str(session.id))
        retrieved.extend_ttl(hours=2)
        
        # Assert
        expected_expires = datetime.utcnow() + timedelta(hours=2)
        time_diff = abs((retrieved.expires_at - expected_expires).total_seconds())
        assert time_diff < 60  # Within 1 minute
