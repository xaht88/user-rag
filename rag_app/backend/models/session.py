"""Session model for Supabase PostgreSQL."""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from uuid import uuid4
from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer, Float, JSON, ForeignKey, CheckConstraint, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declarative_base, deferred
from sqlalchemy.sql import func as sql_func

Base = declarative_base()


class Session(Base):
    """User session with TTL and LLM configuration.
    
    Attributes:
        id: Unique session identifier
        user_id: Optional user identifier for authenticated sessions
        created_at: Session creation timestamp
        updated_at: Last update timestamp
        expires_at: Session expiration timestamp
        llm_config: LLM configuration (model, temperature, etc.)
        session_metadata: Additional session metadata
    """
    
    __tablename__ = 'sessions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=True)
    title = Column(String(255), nullable=True, default="New Conversation")
    created_at = Column(DateTime(timezone=True), server_default=sql_func.now())
    updated_at = Column(DateTime(timezone=True), server_default=sql_func.now(), onupdate=sql_func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    llm_config = Column(JSON, nullable=False, default=dict)
    session_metadata = Column(JSON, nullable=True, default=dict)
    
    # Relationships
    session_documents = relationship('SessionDocument', back_populates='session', cascade='all, delete-orphan')
    messages = relationship('ChatMessage', back_populates='session', cascade='all, delete-orphan')
    
    @property
    def is_expired(self) -> bool:
        """Check if session has expired."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at
    
    @property
    def ttl_seconds(self) -> int:
        """Time to live in seconds."""
        if self.expires_at is None:
            return 0
        delta = self.expires_at - datetime.utcnow()
        return int(delta.total_seconds())
    
    def extend_ttl(self, hours: int = 24) -> None:
        """Extend session TTL.
        
        Args:
            hours: Number of hours to extend
        """
        self.expires_at = datetime.utcnow() + timedelta(hours=hours)
