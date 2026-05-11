"""Chat message model for Supabase PostgreSQL."""

from datetime import datetime
from typing import Optional, List
from uuid import uuid4
from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer, Float, JSON, ForeignKey, CheckConstraint, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func as sql_func

Base = declarative_base()


class ChatMessage(Base):
    """Chat messages within a session.
    
    Attributes:
        id: Unique message identifier
        session_id: Parent session identifier
        role: Message role (user, assistant, system)
        content: Message content
        created_at: Creation timestamp
        metadata: Additional message metadata
    """
    
    __tablename__ = 'chat_messages'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey('sessions.id'), nullable=False)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=sql_func.now())
    metadata = Column(JSON, nullable=True, default=dict)
    
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
