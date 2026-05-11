"""
Session model - maps to public.sessions table.

Represents a RAG conversation session with document context.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, String, Text, TIMESTAMP, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship

from .base import Base


class Session(Base):
    """Conversation session model."""
    
    __tablename__ = "sessions"
    
    id: Column[UUID] = Column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        comment="Session ID"
    )
    user_id: Column[UUID] = Column(
        PGUUID(as_uuid=True),
        ForeignKey("profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User ID"
    )
    title: Column[str] = Column(
        String(500),
        nullable=False,
        default="New Conversation",
        comment="Session title"
    )
    created_at: Column[datetime] = Column(
        TIMESTAMP(timezone=True),
        default=datetime.utcnow,
        nullable=False,
        comment="Creation timestamp"
    )
    updated_at: Column[datetime] = Column(
        TIMESTAMP(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="Last update timestamp"
    )
    metadata: Column[dict] = Column(
        JSON,
        nullable=False,
        default=dict,
        comment="Additional metadata (JSONB)"
    )
    
    # Relationships
    user: relationship = relationship(
        "Profile",
        back_populates="sessions"
    )
    messages: relationship = relationship(
        "Message",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="Message.created_at"
    )
    documents: relationship = relationship(
        "Document",
        back_populates="session",
        cascade="all, delete-orphan"
    )
    
    def add_message(self, role: str, content: str) -> "Message":
        """Add a message to the session."""
        from .message import Message
        
        message = Message(
            id=uuid4(),
            session_id=self.id,
            role=role,
            content=content
        )
        self.messages.append(message)
        return message
    
    def update_title(self, title: str) -> None:
        """Update session title."""
        self.title = title[:500]
    
    def to_dict(self) -> dict:
        """Convert model to dictionary."""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "title": self.title,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "metadata": self.metadata,
            "message_count": len(self.messages),
            "document_count": len(self.documents),
        }
