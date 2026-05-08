"""
Vector Store Service using Supabase pg_vector.

This service provides vector similarity search capabilities using PostgreSQL
with the pg_vector extension. It replaces ChromaDB for production deployments.

Features:
- Vector similarity search using cosine distance
- HNSW indexing for fast retrieval
- Integration with Supabase client
- Support for filtering and metadata queries
"""

from typing import List, Dict, Any, Optional
from supabase import create_client, Client
import logging
import uuid

logger = logging.getLogger(__name__)


class VectorStoreService:
    """
    Vector store service using Supabase pg_vector extension.
    
    Provides vector similarity search, chunk management, and document operations.
    Uses PostgreSQL with pg_vector for production-grade vector storage.
    
    Attributes:
        supabase: Supabase client instance
        embedding_dim: Dimension of embeddings (default: 1536 for OpenAI)
        collection_name: Name of the document_chunks table
    """
    
    def __init__(self, supabase: Client, embedding_dim: int = 1536):
        """
        Initialize VectorStoreService.
        
        Args:
            supabase: Supabase client instance
            embedding_dim: Dimension of vector embeddings (default: 1536)
        
        Example:
            >>> from supabase import create_client
            >>> supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
            >>> store = VectorStoreService(supabase, embedding_dim=1536)
        """
        self.supabase = supabase
        self.embedding_dim = embedding_dim
        self.collection_name = "document_chunks"
    
    def add_chunks(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Add document chunks to the vector store.
        
        Each chunk must contain:
        - document_id: UUID of the parent document
        - chunk_index: Integer index of the chunk
        - content: Text content of the chunk
        - embedding: List of floats (vector embedding)
        
        Args:
            chunks: List of chunk dictionaries with embeddings
            
        Returns:
            Dictionary with insertion statistics
            
        Raises:
            Exception: If insertion fails
            
        Example:
            >>> chunks = [
            ...     {
            ...         "document_id": doc_id,
            ...         "chunk_index": 0,
            ...         "content": "Text content...",
            ...         "embedding": [0.1, 0.2, ...]  # 1536 floats
            ...     }
            ... ]
            >>> result = store.add_chunks(chunks)
            >>> print(result["inserted"])
            1
        """
        try:
            data = []
            for chunk in chunks:
                data.append({
                    "document_id": chunk["document_id"],
                    "chunk_index": chunk["chunk_index"],
                    "content": chunk["content"],
                    "embedding": chunk["embedding"],  # List[float]
                    "created_at": chunk.get("created_at")
                })
            
            response = self.supabase.table(self.collection_name).insert(data).execute()
            logger.info(f"Inserted {len(data)} chunks into vector store")
            return {"inserted": len(data)}
            
        except Exception as e:
            logger.error(f"Failed to add chunks: {e}")
            raise
    
    def search(
        self, 
        query_embedding: List[float], 
        top_k: int = 5, 
        filters: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar chunks using vector similarity.
        
        Uses cosine similarity via the <=> operator in pg_vector.
        Leverages HNSW index for efficient retrieval.
        
        Args:
            query_embedding: Query vector as list of floats
            top_k: Number of results to return (default: 5)
            filters: Optional JSONB filters for additional conditions
            
        Returns:
            List of matching chunks with similarity scores
            
        Example:
            >>> query_vec = [0.1, 0.2, ...]  # 1536 floats
            >>> results = store.search(query_vec, top_k=5)
            >>> for result in results:
            ...     print(f"Similarity: {result['similarity']:.4f}")
            ...     print(f"Content: {result['content'][:100]}...")
        """
        try:
            query = self.supabase.rpc(
                "search_document_chunks",
                {
                    "query_embedding": query_embedding,
                    "match_count": top_k,
                    "filter_json": filters or {}
                }
            )
            
            results = query.execute().data
            logger.debug(f"Found {len(results)} similar chunks")
            return results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def delete_by_document_id(self, doc_id: str) -> None:
        """
        Delete all chunks for a given document.
        
        Args:
            doc_id: UUID of the document to delete
            
        Example:
            >>> store.delete_by_document_id("550e8400-e29b-41d4-a716-446655440000")
        """
        try:
            self.supabase.table(self.collection_name).delete().eq(
                "document_id", doc_id
            ).execute()
            logger.info(f"Deleted chunks for document {doc_id}")
        except Exception as e:
            logger.error(f"Failed to delete chunks for document {doc_id}: {e}")
            raise
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get statistics about the vector store.
        
        Returns:
            Dictionary with store statistics
            
        Example:
            >>> stats = store.get_stats()
            >>> print(f"Total chunks: {stats['total_chunks']}")
        """
        try:
            response = self.supabase.table(
                self.collection_name
            ).select("*", count="exact").execute()
            return {"total_chunks": response.count}
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {"total_chunks": 0}
    
    def get_chunks_by_document(self, doc_id: str) -> List[Dict[str, Any]]:
        """
        Get all chunks for a specific document.
        
        Args:
            doc_id: UUID of the document
            
        Returns:
            List of chunk dictionaries
        """
        try:
            response = self.supabase.table(
                self.collection_name
            ).select("*").eq("document_id", doc_id).order(
                "chunk_index"
            ).execute()
            return response.data
        except Exception as e:
            logger.error(f"Failed to get chunks for document {doc_id}: {e}")
            return []
    
    def bulk_search_with_filters(
        self, 
        query_embedding: List[float], 
        top_k: int = 5,
        document_ids: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform vector search with additional document filtering.
        
        Args:
            query_embedding: Query vector
            top_k: Number of results
            document_ids: Optional list of document IDs to filter by
            
        Returns:
            List of matching chunks
        """
        try:
            # Build filter parameters
            params = {
                "query_embedding": query_embedding,
                "match_count": top_k
            }
            
            # Add document filter if provided
            if document_ids:
                params["filter_json"] = {"document_id": {"in": document_ids}}
            else:
                params["filter_json"] = {}
            
            query = self.supabase.rpc("search_document_chunks", params)
            results = query.execute().data
            return results
            
        except Exception as e:
            logger.error(f"Filtered search failed: {e}")
            return []
