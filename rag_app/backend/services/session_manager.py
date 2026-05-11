"""Session manager for RAG Chat Application."""

from typing import Optional, List, Dict, Any
from fastapi import Depends
from sqlalchemy.orm import Session

from database import get_db
from models import Session as SessionModel
from .session_store import PostgreSQLSessionStore


class SessionManager:
    """Manages session lifecycle and operations.
    
    Provides high-level session operations including creation,
    retrieval, update, and deletion.
    """
    
    def __init__(self, db: Session = Depends(get_db)):
        """Initialize session manager.
        
        Args:
            db: Database session from FastAPI dependency
        """
        self.store = PostgreSQLSessionStore(db)
    
    def create_session(
        self,
        user_id: Optional[str] = None,
        ttl_hours: int = 24
    ) -> SessionModel:
        """Create a new session.
        
        Args:
            user_id: Optional user identifier
            ttl_hours: Time to live in hours
            
        Returns:
            Created session model
        """
        return self.store.create(user_id=user_id, ttl_hours=ttl_hours)
    
    def get_session(self, session_id: str) -> Optional[SessionModel]:
        """Get a session by ID.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session model or None if not found/expired
        """
        return self.store.get(session_id)
    
    def update_session(
        self,
        session_id: str,
        llm_config: Optional[Dict[str, Any]] = None,
        session_metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[SessionModel]:
        """Update a session.
        
        Args:
            session_id: Session identifier
            llm_config: Optional LLM configuration to update
            session_metadata: Optional metadata to update
            
        Returns:
            Updated session model or None
        """
        return self.store.update(
            session_id=session_id,
            llm_config=llm_config,
            session_metadata=session_metadata
        )
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if deleted, False if not found
        """
        return self.store.delete(session_id)
    
    def list_sessions(self, user_id: Optional[str] = None) -> List[SessionModel]:
        """List all sessions.
        
        Args:
            user_id: Optional user filter
            
        Returns:
            List of session models
        """
        return self.store.list(user_id)
    
    def cleanup_expired_sessions(self) -> int:
        """Remove all expired sessions.
        
        Returns:
            Number of sessions deleted
        """
        return self.store.cleanup_expired()
