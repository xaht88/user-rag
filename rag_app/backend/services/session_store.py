"""
PostgreSQL Session Store implementation.

Provides persistent session storage using PostgreSQL database.
"""

import logging
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from uuid import uuid4

from sqlalchemy.orm import Session as DBSession

from models import Session as SessionModel

logger = logging.getLogger(__name__)


class PostgreSQLSessionStore:
    """
    PostgreSQL implementation of session storage.
    
    Provides CRUD operations for sessions with automatic TTL management.
    """
    
    def __init__(self, db: DBSession):
        """
        Initialize session store.
        
        Args:
            db: Database session from SQLAlchemy
        """
        self.db = db
    
    def create(
        self,
        user_id: Optional[str] = None,
        ttl_hours: int = 24,
        llm_config: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> SessionModel:
        """
        Create a new session.
        
        Args:
            user_id: Optional user ID for authenticated sessions
            ttl_hours: Time to live in hours (default: 24)
            llm_config: LLM configuration dictionary
            metadata: Additional session metadata
            
        Returns:
            Created Session model instance
        """
        expires_at = datetime.utcnow() + timedelta(hours=ttl_hours)
        
        session = SessionModel(
            id=uuid4(),
            user_id=user_id,
            expires_at=expires_at,
            llm_config=llm_config or {},
            metadata=metadata or {}
        )
        
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        
        logger.info(f"Created session {session.id} with TTL={ttl_hours}h")
        return session
    
    def get(self, session_id: str) -> Optional[SessionModel]:
        """
        Get a session by ID.
        
        Automatically removes expired sessions.
        
        Args:
            session_id: Session UUID
            
        Returns:
            Session model instance or None if not found/expired
        """
        session = self.db.query(SessionModel).filter(
            SessionModel.id == session_id
        ).first()
        
        if session:
            if session.is_expired:
                logger.info(f"Removing expired session {session_id}")
                self.db.delete(session)
                self.db.commit()
                return None
            # Extend TTL on access
            session.extend_ttl(hours=1)
        
        return session
    
    def update(
        self,
        session_id: str,
        llm_config: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[SessionModel]:
        """
        Update session configuration.
        
        Args:
            session_id: Session UUID
            llm_config: New LLM configuration
            metadata: New metadata
            
        Returns:
            Updated Session model or None if not found
        """
        session = self.get(session_id)
        
        if session:
            if llm_config is not None:
                session.llm_config = llm_config
            if metadata is not None:
                session.metadata = metadata
            
            self.db.commit()
            self.db.refresh(session)
            
            logger.info(f"Updated session {session_id}")
        
        return session
    
    def delete(self, session_id: str) -> bool:
        """
        Delete a session.
        
        Args:
            session_id: Session UUID
            
        Returns:
            True if session was deleted, False if not found
        """
        session = self.db.query(SessionModel).filter(
            SessionModel.id == session_id
        ).first()
        
        if session:
            self.db.delete(session)
            self.db.commit()
            logger.info(f"Deleted session {session_id}")
            return True
        
        return False
    
    def list(self, user_id: Optional[str] = None) -> List[SessionModel]:
        """
        List all active sessions.
        
        Args:
            user_id: Optional filter by user ID
            
        Returns:
            List of active Session model instances
        """
        query = self.db.query(SessionModel)
        
        if user_id:
            query = query.filter(SessionModel.user_id == user_id)
        
        # Exclude expired sessions
        now = datetime.utcnow()
        query = query.filter(
            (SessionModel.expires_at.is_(None)) |
            (SessionModel.expires_at > now)
        )
        
        return query.all()
    
    def cleanup_expired(self, days: int = 30) -> int:
        """
        Clean up expired sessions older than specified days.
        
        Args:
            days: Number of days to keep sessions (default: 30)
            
        Returns:
            Number of deleted sessions
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        result = self.db.query(SessionModel).filter(
            SessionModel.expires_at < cutoff_date
        ).delete()
        
        self.db.commit()
        
        logger.info(f"Cleaned up {result} sessions older than {days} days")
        return result
