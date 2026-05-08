"""
Storage Service using Supabase Storage.

This service provides file upload, download, and deletion operations
using Supabase Storage (S3-compatible object storage).

Features:
- File upload with MIME type detection
- File download
- File deletion
- Folder-based organization by user ID
"""

from typing import Dict, Any, Optional
from supabase import create_client, Client
import os
import logging

logger = logging.getLogger(__name__)


class StorageService:
    """
    Storage service using Supabase Storage.
    
    Provides file upload, download, and deletion operations.
    Organizes files in folders by user ID for isolation.
    
    Attributes:
        supabase: Supabase client instance
        bucket_name: Name of the storage bucket
    """
    
    def __init__(self, supabase: Client, bucket_name: str = "documents"):
        """
        Initialize StorageService.
        
        Args:
            supabase: Supabase client instance
            bucket_name: Name of the storage bucket (default: "documents")
        
        Example:
            >>> from supabase import create_client
            >>> supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
            >>> storage = StorageService(supabase)
        """
        self.supabase = supabase
        self.bucket_name = bucket_name
        self.storage = supabase.storage.from_(bucket_name)
    
    def upload_file(
        self, 
        file_content: Any, 
        user_id: str, 
        filename: str,
        file_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Upload file to storage.
        
        Args:
            file_content: File content (bytes or file object)
            user_id: User ID for folder organization
            filename: Original filename
            file_options: Optional file options (content-type, etc.)
        
        Returns:
            Dictionary with path and public URL
        
        Example:
            >>> result = storage.upload_file(
            ...     file_content=file_data,
            ...     user_id="user-uuid",
            ...     filename="document.pdf"
            ... )
            >>> print(result["path"])
            "user-uuid/document.pdf"
        """
        try:
            # Generate unique filename
            file_name = f"{user_id}/{filename}"
            
            # Default file options
            options = file_options or {
                "content-type": self._get_content_type(filename)
            }
            
            # Upload file
            response = self.storage.upload(
                file_name,
                file_content,
                file_options=options
            )
            
            logger.info(f"File uploaded: {file_name}")
            return {
                "path": file_name,
                "url": self._get_public_url(file_name)
            }
            
        except Exception as e:
            logger.error(f"Failed to upload file: {e}")
            raise
    
    def download_file(self, user_id: str, filename: str) -> bytes:
        """
        Download file from storage.
        
        Args:
            user_id: User ID
            filename: Filename
        
        Returns:
            File content as bytes
        
        Example:
            >>> file_data = storage.download_file("user-uuid", "document.pdf")
            >>> with open("downloaded.pdf", "wb") as f:
            ...     f.write(file_data)
        """
        try:
            file_name = f"{user_id}/{filename}"
            return self.storage.download(file_name)
        except Exception as e:
            logger.error(f"Failed to download file: {e}")
            raise
    
    def delete_file(self, user_id: str, filename: str) -> None:
        """
        Delete file from storage.
        
        Args:
            user_id: User ID
            filename: Filename
        
        Example:
            >>> storage.delete_file("user-uuid", "document.pdf")
        """
        try:
            file_name = f"{user_id}/{filename}"
            self.storage.remove([file_name])
            logger.info(f"File deleted: {file_name}")
        except Exception as e:
            logger.error(f"Failed to delete file: {e}")
            raise
    
    def list_files(self, user_id: str, prefix: str = "") -> list:
        """
        List files in user's folder.
        
        Args:
            user_id: User ID
            prefix: Optional prefix for filtering
        
        Returns:
            List of file metadata
        """
        try:
            folder_path = f"{user_id}/{prefix}" if prefix else user_id
            return self.storage.list(folder_path)
        except Exception as e:
            logger.error(f"Failed to list files: {e}")
            return []
    
    def get_public_url(self, user_id: str, filename: str) -> str:
        """
        Get public URL for a file.
        
        Args:
            user_id: User ID
            filename: Filename
        
        Returns:
            Public URL string
        """
        file_name = f"{user_id}/{filename}"
        return self._get_public_url(file_name)
    
    def _get_content_type(self, filename: str) -> str:
        """
        Determine MIME type from filename extension.
        
        Args:
            filename: Filename with extension
        
        Returns:
            MIME type string
        """
        ext = os.path.splitext(filename)[1].lower()
        types = {
            '.pdf': 'application/pdf',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.txt': 'text/plain',
            '.md': 'text/markdown',
            '.json': 'application/json',
            '.csv': 'text/csv',
            '.html': 'text/html',
            '.css': 'text/css',
            '.js': 'application/javascript',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.svg': 'image/svg+xml'
        }
        return types.get(ext, 'application/octet-stream')
    
    def _get_public_url(self, file_path: str) -> str:
        """
        Get public URL for a file path.
        
        Args:
            file_path: File path in bucket
        
        Returns:
            Public URL string
        """
        return self.storage.get_public_url(file_path)
