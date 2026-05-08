'''
Supabase client configuration using httpx.

Environment variables required:
    SUPABASE_URL: Supabase project URL (e.g., https://xxx.supabase.co)
    SUPABASE_ANON_KEY: Supabase anon/public key
    SUPABASE_SERVICE_ROLE_KEY: Supabase service role key (for admin operations)
'''

import os
from typing import Any, Dict, Optional
from httpx import Client, Timeout
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env.local
load_dotenv('rag_app/backend/.env.local')


class SupabaseConfig(BaseSettings):
    '''Supabase configuration settings.'''
    
    supabase_url: str
    supabase_anon_key: str
    supabase_service_role_key: Optional[str] = None
    
    class Config:
        env_prefix = 'SUPABASE_'
        case_sensitive = True


class SupabaseClient:
    '''
    Supabase client using httpx.
    
    Provides methods for database operations, authentication, and storage.
    '''
    
    def __init__(self, url: str, api_key: str, timeout: float = 30.0):
        self.url = url.rstrip('/')
        self.api_key = api_key
        self.timeout = Timeout(timeout)
        self._client: Optional[Client] = None
    
    def _get_headers(self, is_service_role: bool = False) -> Dict[str, str]:
        '''Get request headers with authentication.'''
        key = self.supabase_service_role_key if is_service_role else self.supabase_anon_key
        return {
            'apikey': key,
            'Authorization': f'Bearer {key}',
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        }
    
    def _get_client(self, is_service_role: bool = False) -> Client:
        '''Get or create HTTP client.'''
        if self._client is None:
            self._client = Client(headers=self._get_headers(is_service_role), timeout=self.timeout)
        return self._client
    
    def table(self, table_name: str):
        '''Get table reference for CRUD operations.'''
        return TableReference(self, table_name)
    
    def rpc(self, function_name: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        '''Call PostgreSQL function via RPC.'''
        client = self._get_client()
        response = client.post(
            f'{self.url}/rpc/{function_name}',
            json=params or {},
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def auth(self):
        '''Get authentication helpers.'''
        return AuthHelper(self)
    
    def storage(self):
        '''Get storage bucket operations.'''
        return StorageHelper(self)


class TableReference:
    '''Reference to a database table.'''
    
    def __init__(self, client: SupabaseClient, table_name: str):
        self.client = client
        self.table_name = table_name
        self._url = f'{client.url}/rest/v1/{table_name}'
    
    def select(self, columns: str = '*', filters: Dict[str, Any] = None, 
               order: str = None, limit: int = None) -> list:
        '''Execute SELECT query.'''
        client = self.client._get_client()
        
        headers = self.client._get_headers()
        if columns != '*':
            headers['Select'] = columns
        
        params = {}
        if filters:
            for col, val in filters.items():
                if isinstance(val, (list, tuple)):
                    params[f'{col}.in'] = ','.join(map(str, val))
                else:
                    params[col] = val
        
        if order:
            params['order'] = order
        if limit:
            params['limit'] = str(limit)
        
        response = client.get(self._url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def insert(self, data: Dict[str, Any], upsert: bool = False) -> Dict[str, Any]:
        '''Insert record(s).'''
        client = self.client._get_client()
        response = client.post(
            self._url,
            json=data if isinstance(data, list) else [data],
            headers=self.client._get_headers(),
            params={'upsert': str(upsert).lower()} if upsert else None
        )
        response.raise_for_status()
        return response.json()
    
    def update(self, data: Dict[str, Any], filters: Dict[str, Any]) -> Dict[str, Any]:
        '''Update records matching filters.'''
        client = self.client._get_client()
        
        params = {}
        for col, val in filters.items():
            params[col] = val
        
        response = client.patch(
            self._url,
            json=data,
            headers=self.client._get_headers(),
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    def delete(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        '''Delete records matching filters.'''
        client = self.client._get_client()
        
        params = {}
        for col, val in filters.items():
            params[col] = val
        
        response = client.delete(
            self._url,
            headers=self.client._get_headers(),
            params=params
        )
        response.raise_for_status()
        return response.json()


class AuthHelper:
    '''Authentication helpers.'''
    
    def __init__(self, client: SupabaseClient):
        self.client = client
    
    def sign_in_with_password(self, email: str, password: str) -> Dict[str, Any]:
        '''Sign in with email and password.'''
        client = self.client._get_client()
        response = client.post(
            f'{self.client.url}/auth/v1/token?grant_type=password',
            json={'email': email, 'password': password}
        )
        response.raise_for_status()
        return response.json()
    
    def sign_up(self, email: str, password: str) -> Dict[str, Any]:
        '''Sign up new user.'''
        client = self.client._get_client()
        response = client.post(
            f'{self.client.url}/auth/v1/signup',
            json={'email': email, 'password': password}
        )
        response.raise_for_status()
        return response.json()


class StorageHelper:
    '''Storage bucket operations.'''
    
    def __init__(self, client: SupabaseClient):
        self.client = client
    
    def from_(self, bucket_name: str):
        '''Get bucket reference.'''
        return BucketReference(self.client, bucket_name)


class BucketReference:
    '''Reference to a storage bucket.'''
    
    def __init__(self, client: SupabaseClient, bucket_name: str):
        self.client = client
        self.bucket_name = bucket_name
        self._url = f'{client.url}/storage/v1/object/{bucket_name}'
    
    def list(self, path: str = '') -> list:
        '''List files in bucket.'''
        client = self.client._get_client()
        response = client.get(
            f'{self.client.url}/storage/v1/list/{self.bucket_name}',
            params={'prefix': path}
        )
        response.raise_for_status()
        return response.json()
    
    def upload(self, file_path: str, path: str) -> Dict[str, Any]:
        '''Upload file to bucket.'''
        client = self.client._get_client()
        with open(file_path, 'rb') as f:
            response = client.put(
                f'{self._url}/{path}',
                content=f.read(),
                headers=self.client._get_headers()
            )
        response.raise_for_status()
        return response.json()
    
    def download(self, path: str) -> bytes:
        '''Download file from bucket.'''
        client = self.client._get_client()
        response = client.get(f'{self._url}/{path}')
        response.raise_for_status()
        return response.content
    
    def remove(self, paths: list[str]) -> Dict[str, Any]:
        '''Delete files from bucket.'''
        client = self.client._get_client()
        response = client.delete(
            f'{self.client.url}/storage/v1/object/{self.bucket_name}',
            json={'prefixes': paths}
        )
        response.raise_for_status()
        return response.json()


def get_supabase_client() -> SupabaseClient:
    '''
    Create and return a Supabase client instance.
    
    Returns:
        SupabaseClient: Configured Supabase client
    
    Raises:
        ValueError: If required environment variables are not set
    '''
    try:
        config = SupabaseConfig()
    except Exception as e:
        raise ValueError(
            f'Supabase configuration error: {e}. '
            'Please check .env.local for SUPABASE_URL and SUPABASE_ANON_KEY'
        )
    
    if not config.supabase_url or not config.supabase_anon_key:
        raise ValueError(
            'Missing Supabase credentials. '
            'Set SUPABASE_URL and SUPABASE_ANON_KEY in .env.local'
        )
    
    return SupabaseClient(
        url=config.supabase_url,
        api_key=config.supabase_anon_key,
        timeout=30.0
    )


def get_admin_client() -> Optional[SupabaseClient]:
    '''
    Create admin client with service role key if available.
    
    Returns:
        SupabaseClient | None: Admin client or None if service role key not configured
    '''
    service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    url = os.getenv('SUPABASE_URL')
    
    if not url or not service_key:
        return None
    
    return SupabaseClient(
        url=url,
        api_key=service_key,
        timeout=30.0
    )
