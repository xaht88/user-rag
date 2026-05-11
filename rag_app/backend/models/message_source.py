"""Message source model for Supabase PostgreSQL."""

from typing import Optional
from uuid import uuid4
from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer, Float, JSON, ForeignKey, CheckConstraint, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func as sql_func

# Import Base from session module to ensure single declarative base
from .session import Base


class MessageSource(Base):
    """Source documents for chat messages.
    
    Attributes:
        id: Unique source identifier
        message_id: Parent message identifier
        document_id: Source document identifier
        filename: Source filename
        page: Page number (if applicable)
        chunk_id: Chunk identifier
        snippet: Relevant text snippet
        relevance_score: Relevance score for the chunk
    """
    
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
