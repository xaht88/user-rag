"""Initial schema with sessions, documents, messages tables

Revision ID: 20260511125148
Revises: 
Create Date: 2026-05-11 12:51:48.123456

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20260511125148'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create tables and indexes for session management."""
    # Create enum types
    op.execute("""
        CREATE TYPE IF NOT EXISTS message_role AS ENUM ('user', 'assistant', 'system');
        CREATE TYPE IF NOT EXISTS document_status AS ENUM ('processing', 'ready', 'error');
    """)
    
    # Sessions table
    op.create_table(
        'sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=sa.func.gen_random_uuid()),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('llm_config', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('session_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'),
    )
    
    # Session documents table
    op.create_table(
        'session_documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=sa.func.gen_random_uuid()),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('status', sa.Enum('processing', 'ready', 'error', name='document_status'), nullable=False, server_default='processing'),
        sa.Column('chunks_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('pages_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('selected', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('uploaded_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint('session_id', 'document_id', name='uq_session_document'),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.id'], ondelete='CASCADE'),
    )
    
    # Chat messages table
    op.create_table(
        'chat_messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=sa.func.gen_random_uuid()),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.Enum('user', 'assistant', 'system', name='message_role'), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.id'], ondelete='CASCADE'),
    )
    
    # Message sources table
    op.create_table(
        'message_sources',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=sa.func.gen_random_uuid()),
        sa.Column('message_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('page', sa.Integer(), nullable=True),
        sa.Column('chunk_id', sa.String(length=100), nullable=True),
        sa.Column('snippet', sa.Text(), nullable=True),
        sa.Column('relevance_score', sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(['message_id'], ['chat_messages.id'], ondelete='CASCADE'),
    )
    
    # Create indexes
    op.create_index('idx_sessions_user_id', 'sessions', ['user_id'])
    op.create_index('idx_sessions_expires_at', 'sessions', ['expires_at'])
    op.create_index('idx_session_documents_session_id', 'session_documents', ['session_id'])
    op.create_index('idx_chat_messages_session_id', 'chat_messages', ['session_id'])
    op.create_index('idx_chat_messages_created_at', 'chat_messages', ['created_at'])
    
    # Create trigger function
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ language 'plpgsql';
        
        CREATE TRIGGER update_sessions_updated_at BEFORE UPDATE ON sessions
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    """)


def downgrade() -> None:
    """Drop tables and indexes."""
    # Drop tables in reverse order (foreign key dependencies)
    op.drop_table('message_sources')
    op.drop_table('chat_messages')
    op.drop_table('session_documents')
    op.drop_table('sessions')
    
    # Drop enum types
    op.execute("DROP TYPE IF EXISTS document_status;")
    op.execute("DROP TYPE IF EXISTS message_role;")
    
    # Drop indexes (will be dropped with tables, but explicit for clarity)
    op.drop_index('idx_sessions_user_id', table_name='sessions')
    op.drop_index('idx_sessions_expires_at', table_name='sessions')
    op.drop_index('idx_session_documents_session_id', table_name='session_documents')
    op.drop_index('idx_chat_messages_session_id', table_name='chat_messages')
    op.drop_index('idx_chat_messages_created_at', table_name='chat_messages')
