"""Session document model for Supabase PostgreSQL."""

from datetime import datetime
from typing import Optional
from uuid import uuid4
from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer, Float, JSON, ForeignKey, CheckConstraint, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func as sql_func

# Import Base from session module to ensure single declarative base
from .session import Base


class SessionDocument(Base):
    """Documents associated with a session.
    
    Attributes:
        id: Unique document identifier
        session_id: Parent session identifier
        document_id: Document identifier (UUID)
        filename: Original filename
        status: Processing status (processing, ready, failed)
        chunks_count: Number of chunks created
        pages_count: Number of pages in document
        selected: Whether document is selected for search
        uploaded_at: Upload timestamp
    """
    
    __tablename__ = 'session_documents'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey('sessions.id'), nullable=False)
    document_id = Column(UUID(as_uuid=True), nullable=False)
    filename = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False, default='processing')
    chunks_count = Column(Integer, default=0)
    pages_count = Column(Integer, default=0)
    selected = Column(Boolean, default=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=sql_func.now())
    
    __table_args__ = (
        UniqueConstraint('session_id', 'document_id', name='uq_session_document'),
    )
    
    # Relationships
    session = relationship('Session', back_populates='session_documents')
    
    @property
    def is_ready(self) -> bool:
        """Check if document is ready for search."""
        return self.status == 'ready'
    
    @property
    def is_processing(self) -> bool:
        """Check if document is being processed."""
        return self.status == 'processing'
