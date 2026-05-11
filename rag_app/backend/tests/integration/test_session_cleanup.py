"""Integration tests for session cleanup task."""

import pytest
import sys
import os
from datetime import datetime, timedelta
from uuid import uuid4

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tasks.session_cleanup import cleanup_expired_sessions, cleanup_all_expired_sessions
from database import engine, SessionLocal
from models import Session as SessionModel


@pytest.fixture
def test_db():
    """Create test database session."""
    # Create tables
    from database import Base
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    yield db
    db.close()
    
    # Cleanup
    Base.metadata.drop_all(bind=engine)


class TestSessionCleanup:
    """Tests for session cleanup functionality."""
    
    def test_cleanup_expired_sessions(self, test_db):
        """Test cleanup of expired sessions."""
        # Create expired session
        expired_session = SessionModel(
            id=uuid4(),
            user_id=str(uuid4()),
            expires_at=datetime.utcnow() - timedelta(days=31)
        )
        test_db.add(expired_session)
        
        # Create recent session (should not be cleaned)
        recent_session = SessionModel(
            id=uuid4(),
            user_id=str(uuid4()),
            expires_at=datetime.utcnow() + timedelta(days=10)
        )
        test_db.add(recent_session)
        
        test_db.commit()
        
        # Run cleanup
        deleted = cleanup_expired_sessions(days_threshold=30)
        
        # Verify
        assert deleted == 1
        
        # Verify recent session still exists
        remaining = test_db.query(SessionModel).all()
        assert len(remaining) == 1
        assert remaining[0].id == recent_session.id
    
    def test_cleanup_all_expired_sessions(self, test_db):
        """Test cleanup of all expired sessions."""
        # Create two expired sessions
        expired1 = SessionModel(
            id=uuid4(),
            user_id=str(uuid4()),
            expires_at=datetime.utcnow() - timedelta(days=31)
        )
        expired2 = SessionModel(
            id=uuid4(),
            user_id=str(uuid4()),
            expires_at=datetime.utcnow() - timedelta(hours=1)
        )
        test_db.add(expired1)
        test_db.add(expired2)
        
        # Create non-expired session
        active_session = SessionModel(
            id=uuid4(),
            user_id=str(uuid4()),
            expires_at=datetime.utcnow() + timedelta(days=10)
        )
        test_db.add(active_session)
        
        test_db.commit()
        
        # Run cleanup
        deleted = cleanup_all_expired_sessions()
        
        # Verify
        assert deleted == 2
        
        # Verify active session still exists
        remaining = test_db.query(SessionModel).all()
        assert len(remaining) == 1
        assert remaining[0].id == active_session.id
    
    def test_cleanup_no_expired_sessions(self, test_db):
        """Test cleanup when no sessions are expired."""
        # Create only active sessions
        for _ in range(3):
            session = SessionModel(
                id=uuid4(),
                user_id=str(uuid4()),
                expires_at=datetime.utcnow() + timedelta(days=10)
            )
            test_db.add(session)
        
        test_db.commit()
        
        # Run cleanup
        deleted = cleanup_expired_sessions(days_threshold=30)
        
        # Verify
        assert deleted == 0
        
        # Verify all sessions still exist
        remaining = test_db.query(SessionModel).all()
        assert len(remaining) == 3
    
    def test_cleanup_boundary_condition(self, test_db):
        """Test cleanup with sessions exactly at threshold."""
        # Create session exactly 30 days old
        exact_session = SessionModel(
            id=uuid4(),
            user_id=str(uuid4()),
            expires_at=datetime.utcnow() - timedelta(days=30)
        )
        test_db.add(exact_session)
        
        # Create session 29 days old (should not be cleaned)
        recent_session = SessionModel(
            id=uuid4(),
            user_id=str(uuid4()),
            expires_at=datetime.utcnow() - timedelta(days=29)
        )
        test_db.add(recent_session)
        
        test_db.commit()
        
        # Run cleanup
        deleted = cleanup_expired_sessions(days_threshold=30)
        
        # Verify
        assert deleted == 1
        
        # Verify recent session still exists
        remaining = test_db.query(SessionModel).all()
        assert len(remaining) == 1
        assert remaining[0].id == recent_session.id
