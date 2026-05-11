"""
Session Manager - High-level session management.

Coordinates session operations with database and vector store.
"""

import logging
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Optional, List, Dict, Any

from fastapi import Depends

from database import get_db
from models import Session as SessionModel
from .session_store import PostgreSQLSessionStore

logger = logging.getLogger(__name__)


class SessionManager:
    """
    High-level session manager.
    
    Provides convenient methods for session operations.
    Uses PostgreSQLSessionStore for persistence.
    """
    
    def __init__(self, db=Depends(get_db)):
        """
        Initialize session manager.
        
        Args:
            db: Database session (injected via FastAPI Depends)
        """
        self.store = PostgreSQLSessionStore(db)
    
    def create_session(
        self,
        user_id: Optional[str] = None,
        ttl_hours: int = 24,
        llm_config: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> SessionModel:
        """
        Create a new session.
        
        Args:
            user_id: Optional user ID
            ttl_hours: Session TTL in hours
            llm_config: LLM configuration
            metadata: Additional metadata
            
        Returns:
            Created Session model
        """
        return self.store.create(
            user_id=user_id,
            ttl_hours=ttl_hours,
            llm_config=llm_config,
            metadata=metadata
        )
    
    def get_session(self, session_id: str) -> Optional[SessionModel]:
        """
        Get a session by ID.
        
        Args:
            session_id: Session UUID
            
        Returns:
            Session model or None
        """
        return self.store.get(session_id)
    
    def update_session(
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
            Updated Session model or None
        """
        return self.store.update(
            session_id=session_id,
            llm_config=llm_config,
            metadata=metadata
        )
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.
        
        Args:
            session_id: Session UUID
            
        Returns:
            True if deleted, False if not found
        """
        return self.store.delete(session_id)
    
    def list_sessions(self, user_id: Optional[str] = None) -> List[SessionModel]:
        """
        List all active sessions.
        
        Args:
            user_id: Optional filter by user ID
            
        Returns:
            List of active sessions
        """
        return self.store.list(user_id=user_id)
    
    def cleanup_old_sessions(self, days: int = 30) -> int:
        """
        Clean up old expired sessions.
        
        Args:
            days: Delete sessions older than this many days
            
        Returns:
            Number of deleted sessions
        """
        return self.store.cleanup_expired(days=days)
