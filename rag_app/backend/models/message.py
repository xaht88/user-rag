"""
Message model - maps to public.messages table.

Represents chat messages within a session.
"""

from datetime import datetime
from typing import Literal, Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, String, Text, TIMESTAMP, ForeignKey, CheckConstraint, JSON
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship

from .base import Base


RoleType = Literal["user", "assistant", "system"]


class Message(Base):
    """Chat message model."""
    
    __tablename__ = "messages"
    
    __table_args__ = (
        CheckConstraint(
            "role IN ('user', 'assistant', 'system')",
            name="check_message_role"
        ),
    )
    
    id: Column[UUID] = Column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        comment="Message ID"
    )
    session_id: Column[UUID] = Column(
        PGUUID(as_uuid=True),
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Session ID"
    )
    role: Column[RoleType] = Column(
        String(20),
        nullable=False,
        comment="Message role (user/assistant/system)"
    )
    content: Column[str] = Column(
        Text,
        nullable=False,
        comment="Message content"
    )
    created_at: Column[datetime] = Column(
        TIMESTAMP(timezone=True),
        default=datetime.utcnow,
        nullable=False,
        index=True,
        comment="Creation timestamp"
    )
    metadata: Column[dict] = Column(
        JSON,
        nullable=False,
        default=dict,
        comment="Additional metadata (JSONB)"
    )
    
    # Relationships
    session: relationship = relationship(
        "Session",
        back_populates="messages"
    )
    
    def to_dict(self) -> dict:
        """Convert model to dictionary."""
        return {
            "id": str(self.id),
            "session_id": str(self.session_id),
            "role": self.role,
            "content": self.content,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "metadata": self.metadata,
        }
