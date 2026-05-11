"""
Create initial Alembic migration manually.
"""

from sqlalchemy import text
from datetime import datetime
from uuid import uuid4

# Migration content
migration_sql = """
-- Create enum types
CREATE TYPE IF NOT EXISTS message_role AS ENUM ('user', 'assistant', 'system');
CREATE TYPE IF NOT EXISTS document_status AS ENUM ('processing', 'ready', 'error');

-- Sessions table
CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE,
    llm_config JSONB NOT NULL DEFAULT '{}'::jsonb,
    session_metadata JSONB DEFAULT '{}'::jsonb
);

-- Session documents table
CREATE TABLE IF NOT EXISTS session_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    document_id UUID NOT NULL,
    filename VARCHAR(255) NOT NULL,
    status document_status NOT NULL DEFAULT 'processing'::document_status,
    chunks_count INTEGER DEFAULT 0,
    pages_count INTEGER DEFAULT 0,
    selected BOOLEAN DEFAULT FALSE,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(session_id, document_id)
);

-- Chat messages table
CREATE TABLE IF NOT EXISTS chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    role message_role NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Message sources table
CREATE TABLE IF NOT EXISTS message_sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id UUID NOT NULL REFERENCES chat_messages(id) ON DELETE CASCADE,
    document_id UUID NOT NULL,
    filename VARCHAR(255) NOT NULL,
    page INTEGER,
    chunk_id VARCHAR(100),
    snippet TEXT,
    relevance_score FLOAT
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_expires_at ON sessions(expires_at);
CREATE INDEX IF NOT EXISTS idx_session_documents_session_id ON session_documents(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id ON chat_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_created_at ON chat_messages(created_at);

-- Function for auto-updating updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_sessions_updated_at BEFORE UPDATE ON sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
"""

print("Migration SQL generated successfully!")
print("\nRun this SQL against your Supabase database to create tables:")
print(migration_sql)
