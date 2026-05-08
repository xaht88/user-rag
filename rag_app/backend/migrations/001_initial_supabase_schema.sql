-- ============================================
-- Supabase Initial Schema for RAG Chat Application
-- ============================================
-- This migration sets up the complete database schema for the RAG application
-- using PostgreSQL with pg_vector extension for vector similarity search.
--
-- Extensions Required:
-- - uuid-ossp: For UUID generation
-- - pgvector: For vector similarity search
--
-- Tables:
-- - profiles: User profiles (extends auth.users)
-- - sessions: Conversation sessions
-- - messages: Message history
-- - documents: Uploaded documents metadata
-- - document_chunks: Vector embeddings for RAG
--
-- Security:
-- - Row Level Security (RLS) enabled on all tables
-- - Storage bucket with access policies
-- ============================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgvector";

-- ============================================
-- TABLES
-- ============================================

-- Profiles table (extends Supabase auth.users)
-- Stores additional user information beyond auth.users
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
    email TEXT,
    full_name TEXT,
    avatar_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Sessions table for RAG conversations
-- Each session represents a unique conversation with its own document context
CREATE TABLE IF NOT EXISTS public.sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
    title TEXT NOT NULL DEFAULT 'New Conversation',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Messages table for conversation history
-- Stores the complete conversation history for each session
CREATE TABLE IF NOT EXISTS public.messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES public.sessions(id) ON DELETE CASCADE NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Documents table for uploaded files
-- Tracks metadata about uploaded documents and their storage location
CREATE TABLE IF NOT EXISTS public.documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
    session_id UUID REFERENCES public.sessions(id) ON DELETE SET NULL,
    filename TEXT NOT NULL,
    file_type TEXT,
    file_size BIGINT,
    storage_path TEXT,
    status TEXT DEFAULT 'processing' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Document chunks for vector search
-- Stores text chunks with their vector embeddings for similarity search
-- Uses pg_vector extension for efficient vector operations
CREATE TABLE IF NOT EXISTS public.document_chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID REFERENCES public.documents(id) ON DELETE CASCADE NOT NULL,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    embedding VECTOR(1536), -- OpenAI embedding dimension (1536 for text-embedding-ada-002)
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(document_id, chunk_index)
);

-- ============================================
-- INDEXES
-- ============================================

-- Indexes for sessions (optimize user session queries)
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON public.sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_updated_at ON public.sessions(updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_sessions_user_created ON public.sessions(user_id, created_at DESC);

-- Indexes for messages (optimize message history queries)
CREATE INDEX IF NOT EXISTS idx_messages_session_id ON public.messages(session_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON public.messages(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_messages_session_created ON public.messages(session_id, created_at DESC);

-- Indexes for documents (optimize document queries)
CREATE INDEX IF NOT EXISTS idx_documents_user_id ON public.documents(user_id);
CREATE INDEX IF NOT EXISTS idx_documents_session_id ON public.documents(session_id);
CREATE INDEX IF NOT EXISTS idx_documents_status ON public.documents(status);
CREATE INDEX IF NOT EXISTS idx_documents_user_created ON public.documents(user_id, created_at DESC);

-- Indexes for document chunks (optimize vector search)
CREATE INDEX IF NOT EXISTS idx_document_chunks_document_id ON public.document_chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_document_chunks_embedding ON public.document_chunks USING hnsw (embedding vector_cosine_ops) 
    WITH (ef_construction = 200);
CREATE INDEX IF NOT EXISTS idx_document_chunks_document_embedding ON public.document_chunks(document_id, embedding);

-- ============================================
-- TRIGGERS
-- ============================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION public.handle_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply triggers to tables with updated_at column
CREATE TRIGGER trg_profiles_updated_at
    BEFORE UPDATE ON public.profiles
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_updated_at();

CREATE TRIGGER trg_sessions_updated_at
    BEFORE UPDATE ON public.sessions
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_updated_at();

CREATE TRIGGER trg_documents_updated_at
    BEFORE UPDATE ON public.documents
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_updated_at();

-- ============================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================

-- Enable RLS on all tables (critical for multi-tenant security)
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.document_chunks ENABLE ROW LEVEL SECURITY;

-- Profiles policies
-- Users can only view and update their own profile
CREATE POLICY "Users can view own profile"
    ON public.profiles FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
    ON public.profiles FOR UPDATE
    USING (auth.uid() = id)
    WITH CHECK (auth.uid() = id);

-- Sessions policies
-- Users can only access their own sessions
CREATE POLICY "Users can view own sessions"
    ON public.sessions FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can create own sessions"
    ON public.sessions FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own sessions"
    ON public.sessions FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own sessions"
    ON public.sessions FOR DELETE
    USING (auth.uid() = user_id);

-- Messages policies
-- Users can only access messages from their own sessions
CREATE POLICY "Users can view own messages"
    ON public.messages FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.sessions
            WHERE sessions.id = messages.session_id
            AND sessions.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can create own messages"
    ON public.messages FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.sessions
            WHERE sessions.id = messages.session_id
            AND sessions.user_id = auth.uid()
        )
    );

-- Documents policies
-- Users can only access their own documents
CREATE POLICY "Users can view own documents"
    ON public.documents FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can create own documents"
    ON public.documents FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own documents"
    ON public.documents FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own documents"
    ON public.documents FOR DELETE
    USING (auth.uid() = user_id);

-- Document chunks policies
-- Users can only view chunks from their own documents
CREATE POLICY "Users can view own chunks"
    ON public.document_chunks FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.documents
            WHERE documents.id = document_chunks.document_id
            AND documents.user_id = auth.uid()
        )
    );

CREATE POLICY "System can insert chunks"
    ON public.document_chunks FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.documents
            WHERE documents.id = document_chunks.document_id
            AND documents.user_id = auth.uid()
        )
    );

-- ============================================
-- STORAGE BUCKETS
-- ============================================

-- Create storage bucket for documents (private bucket)
INSERT INTO storage.buckets (id, name, public)
VALUES ('documents', 'documents', false)
ON CONFLICT (id) DO NOTHING;

-- Storage policies (users can only access their own files)
CREATE POLICY "Users can upload documents"
    ON storage.objects FOR INSERT
    WITH CHECK (
        bucket_id = 'documents'
        AND auth.uid()::text = (storage.foldername(name))[1]
    );

CREATE POLICY "Users can view own documents"
    ON storage.objects FOR SELECT
    USING (
        bucket_id = 'documents'
        AND auth.uid()::text = (storage.foldername(name))[1]
    );

CREATE POLICY "Users can update own documents"
    ON storage.objects FOR UPDATE
    WITH CHECK (
        bucket_id = 'documents'
        AND auth.uid()::text = (storage.foldername(name))[1]
    );

CREATE POLICY "Users can delete own documents"
    ON storage.objects FOR DELETE
    USING (
        bucket_id = 'documents'
        AND auth.uid()::text = (storage.foldername(name))[1]
    );

-- ============================================
-- FUNCTIONS
-- ============================================

-- Function to search document chunks using vector similarity
-- Uses cosine similarity for vector comparison
-- Optimized with HNSW index for fast retrieval
CREATE OR REPLACE FUNCTION search_document_chunks(
    query_embedding VECTOR(1536),
    match_count INTEGER DEFAULT 10,
    filter_json JSONB DEFAULT '{}'::jsonb
)
RETURNS TABLE (
    id UUID,
    document_id UUID,
    chunk_index INTEGER,
    content TEXT,
    similarity FLOAT
)
LANGUAGE sql
STABLE
AS $$
    SELECT
        dc.id,
        dc.document_id,
        dc.chunk_index,
        dc.content,
        1 - (dc.embedding <=> query_embedding) AS similarity
    FROM document_chunks dc
    WHERE dc.embedding IS NOT NULL
    AND dc.embedding <=> query_embedding < 1
    ORDER BY dc.embedding <=> query_embedding
    LIMIT match_count;
$$;

-- Function to get session statistics
-- Returns aggregate metrics for a session
CREATE OR REPLACE FUNCTION get_session_stats(session_id UUID)
RETURNS TABLE (
    total_messages INTEGER,
    total_documents INTEGER,
    total_chunks INTEGER,
    last_message_at TIMESTAMPTZ
)
LANGUAGE sql
STABLE
AS $$
    SELECT
        (SELECT COUNT(*) FROM messages WHERE session_id = session_id) AS total_messages,
        (SELECT COUNT(*) FROM documents WHERE session_id = session_id) AS total_documents,
        (SELECT COUNT(*) FROM document_chunks WHERE document_id IN (SELECT id FROM documents WHERE session_id = session_id)) AS total_chunks,
        (SELECT MAX(created_at) FROM messages WHERE session_id = session_id) AS last_message_at;
$$;

-- Function to get user statistics
-- Returns aggregate metrics for a user
CREATE OR REPLACE FUNCTION get_user_stats(user_id UUID)
RETURNS TABLE (
    total_sessions INTEGER,
    total_documents INTEGER,
    total_chunks INTEGER,
    total_messages INTEGER
)
LANGUAGE sql
STABLE
AS $$
    SELECT
        (SELECT COUNT(*) FROM sessions WHERE user_id = user_id) AS total_sessions,
        (SELECT COUNT(*) FROM documents WHERE user_id = user_id) AS total_documents,
        (SELECT COUNT(*) FROM document_chunks WHERE document_id IN (SELECT id FROM documents WHERE user_id = user_id)) AS total_chunks,
        (SELECT COUNT(*) FROM messages WHERE session_id IN (SELECT id FROM sessions WHERE user_id = user_id)) AS total_messages;
$$;

-- ============================================
-- VIEWS (Optional - for simplified queries)
-- ============================================

-- View for complete message history with session info
CREATE OR REPLACE VIEW public.session_messages_view AS
SELECT
    s.id AS session_id,
    s.title AS session_title,
    m.id AS message_id,
    m.role,
    m.content,
    m.created_at,
    m.metadata
FROM sessions s
JOIN messages m ON m.session_id = s.id
ORDER BY m.created_at ASC;

-- View for document details with chunk count
CREATE OR REPLACE VIEW public.document_details_view AS
SELECT
    d.id,
    d.user_id,
    d.session_id,
    d.filename,
    d.file_type,
    d.file_size,
    d.storage_path,
    d.status,
    d.created_at,
    COUNT(dc.id) AS chunk_count
FROM documents d
LEFT JOIN document_chunks dc ON dc.document_id = d.id
GROUP BY d.id;

-- ============================================
-- GRANTS
-- ============================================

-- Grant permissions to authenticated users
GRANT USAGE ON SCHEMA public TO authenticated;

-- Grant table access to authenticated users
GRANT SELECT, INSERT, UPDATE, DELETE ON public.profiles TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.sessions TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.messages TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.documents TO authenticated;
GRANT SELECT, INSERT ON public.document_chunks TO authenticated;

-- Grant sequence permissions for UUID generation
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO authenticated;

-- Grant storage bucket access (handled by policies above)
-- Storage policies are defined via RLS-like policies on storage.objects

-- ============================================
-- SEED DATA (Optional)
-- ============================================

-- Create a demo user profile (uncomment to use for testing)
-- INSERT INTO public.profiles (id, email, full_name)
-- VALUES ('00000000-0000-0000-0000-000000000001', 'demo@example.com', 'Demo User');

-- ============================================
-- MIGRATION METADATA
-- ============================================

-- Add comment to track this migration
COMMENT ON TABLE public.profiles IS 'User profiles extending auth.users';
COMMENT ON TABLE public.sessions IS 'Conversation sessions with document context';
COMMENT ON TABLE public.messages IS 'Message history for each session';
COMMENT ON TABLE public.documents IS 'Uploaded document metadata and storage info';
COMMENT ON TABLE public.document_chunks IS 'Text chunks with vector embeddings for RAG';

-- Record migration version
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = '_migrations') THEN
        CREATE TABLE _migrations (
            version INTEGER PRIMARY KEY,
            applied_at TIMESTAMPTZ DEFAULT NOW()
        );
    END IF;
    
    INSERT INTO _migrations (version) VALUES (1)
    ON CONFLICT (version) DO NOTHING;
END $$;
