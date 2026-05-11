"""PostgreSQL session store implementation."""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from uuid import uuid4
from sqlalchemy.orm import Session as DBSession
from sqlalchemy import and_

from models import Session as SessionModel


class PostgreSQLSessionStore:
    """PostgreSQL implementation of session storage.
    
    Provides CRUD operations for sessions using SQLAlchemy ORM.
    """
    
    def __init__(self, db: DBSession):
        """Initialize session store.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
    
    def create(
        self,
        user_id: Optional[str] = None,
        ttl_hours: int = 24,
        llm_config: Optional[Dict[str, Any]] = None
    ) -> SessionModel:
        """Create a new session.
        
        Args:
            user_id: Optional user identifier
            ttl_hours: Time to live in hours
            llm_config: Optional LLM configuration
            
        Returns:
            Created session model
        """
        expires_at = datetime.utcnow() + timedelta(hours=ttl_hours)
        
        session = SessionModel(
            id=uuid4(),
            user_id=user_id,
            expires_at=expires_at,
            llm_config=llm_config or {},
            session_metadata={}
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        
        return session
    
    def get(self, session_id: str) -> Optional[SessionModel]:
        """Get a session by ID.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session model or None if not found/expired
        """
        session = self.db.query(SessionModel).filter(
            SessionModel.id == session_id
        ).first()
        
        if session and session.is_expired:
            self.db.delete(session)
            self.db.commit()
            return None
        
        return session if session else None
    
    def update(
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
        session = self.get(session_id)
        if not session:
            return None
        
        if llm_config is not None:
            session.llm_config = llm_config
        if session_metadata is not None:
            session.session_metadata = session_metadata
        
        self.db.commit()
        self.db.refresh(session)
        return session
    
    def delete(self, session_id: str) -> bool:
        """Delete a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if deleted, False if not found
        """
        session = self.db.query(SessionModel).filter(
            SessionModel.id == session_id
        ).first()
        
        if session:
            self.db.delete(session)
            self.db.commit()
            return True
        return False
    
    def list(self, user_id: Optional[str] = None) -> List[SessionModel]:
        """List all sessions.
        
        Args:
            user_id: Optional user filter
            
        Returns:
            List of session models
        """
        query = self.db.query(SessionModel)
        
        if user_id:
            query = query.filter(SessionModel.user_id == user_id)
        
        return query.all()
    
    def cleanup_expired(self, days: Optional[int] = None) -> int:
        """Remove all expired sessions.
        
        Args:
            days: Optional filter for sessions older than N days
            
        Returns:
            Number of sessions deleted
        """
        query = self.db.query(SessionModel)
        
        if days:
            cutoff = datetime.utcnow() - timedelta(days=days)
            query = query.filter(SessionModel.expires_at < cutoff)
        else:
            query = query.filter(SessionModel.expires_at < datetime.utcnow())
        
        result = query.delete(synchronize_session=False)
        
        self.db.commit()
        return result
