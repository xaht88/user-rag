"""
SQLAlchemy ORM models for RAG Chat Application.

Models:
- Session: User session with TTL
- SessionDocument: Documents associated with a session
- ChatMessage: Chat messages within a session
- MessageSource: Source documents for chat messages
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import uuid4
from sqlalchemy import (
    Column, String, Text, DateTime, Boolean, Integer, Float, JSON,
    ForeignKey, CheckConstraint, UniqueConstraint, func
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class Session(Base):
    """User session with TTL and LLM configuration."""
    
    __tablename__ = 'sessions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    llm_config = Column(JSON, nullable=False, default=dict)
    session_metadata = Column(JSON, nullable=True, default=dict)
    
    # Relationships
    documents = relationship('SessionDocument', back_populates='session', cascade='all, delete-orphan')
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
        """Extend session TTL."""
        from datetime import timedelta
        self.expires_at = datetime.utcnow() + timedelta(hours=hours)


class SessionDocument(Base):
    """Documents associated with a session."""
    
    __tablename__ = 'session_documents'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey('sessions.id'), nullable=False)
    document_id = Column(UUID(as_uuid=True), nullable=False)
    filename = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False, default='processing')
    chunks_count = Column(Integer, default=0)
    pages_count = Column(Integer, default=0)
    selected = Column(Boolean, default=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        UniqueConstraint('session_id', 'document_id', name='uq_session_document'),
    )
    
    # Relationships
    session = relationship('Session', back_populates='documents')
    
    @property
    def is_ready(self) -> bool:
        """Check if document is ready for search."""
        return self.status == 'ready'
    
    @property
    def is_processing(self) -> bool:
        """Check if document is being processed."""
        return self.status == 'processing'


class ChatMessage(Base):
    """Chat messages within a session."""
    
    __tablename__ = 'chat_messages'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey('sessions.id'), nullable=False)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    session = relationship('Session', back_populates='messages')
    sources = relationship('MessageSource', back_populates='message', cascade='all, delete-orphan')
    
    @property
    def is_user(self) -> bool:
        """Check if message is from user."""
        return self.role == 'user'
    
    @property
    def is_assistant(self) -> bool:
        """Check if message is from assistant."""
        return self.role == 'assistant'


class MessageSource(Base):
    """Source documents for chat messages."""
    
    __tablename__ = 'message_sources'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    message_id = Column(UUID(as_uuid=True), ForeignKey('chat_messages.id'), nullable=False)
    document_id = Column(UUID(as_uuid=True), nullable=False)
    filename = Column(String(255), nullable=False)
    page = Column(Integer, nullable=True)
    chunk_id = Column(String(100), nullable=True)
    snippet = Column(Text, nullable=True)
    relevance_score = Column(Float, nullable=True)
    
    # Relationships
    message = relationship('ChatMessage', back_populates='sources')
