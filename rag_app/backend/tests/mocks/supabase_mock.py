"""Mock Supabase client for testing."""

from unittest.mock import MagicMock, Mock
from datetime import datetime
from uuid import uuid4


class MockSupabaseClient:
    """Mock Supabase client that simulates real Supabase behavior."""
    
    def __init__(self, url: str = "http://test.supabase.co", api_key: str = "test-key"):
        self.url = url
        self.api_key = api_key
        self._data = {}
    
    def table(self, table_name: str):
        """Get table reference."""
        if table_name not in self._data:
            self._data[table_name] = []
        return MockTable(self, table_name)
    
    def rpc(self, function_name: str, params: dict = None):
        """Call RPC function."""
        return {"result": []}
    
    @property
    def auth(self):
        """Get auth helper."""
        return MockAuth(self)
    
    @property
    def storage(self):
        """Get storage helper."""
        return MockStorage(self)


class MockTable:
    """Mock table reference."""
    
    def __init__(self, client: MockSupabaseClient, table_name: str):
        self.client = client
        self.table_name = table_name
        self._filters = {}
        self._order = None
        self._limit = None
    
    def select(self, columns: str = "*"):
        """Start SELECT query."""
        self._select_columns = columns
        return self
    
    def eq(self, column: str, value: any):
        """Filter by equality."""
        self._filters[column] = {"$eq": value}
        return self
    
    def in_(self, column: str, values: list):
        """Filter by IN clause."""
        self._filters[column] = {"$in": values}
        return self
    
    def neq(self, column: str, value: any):
        """Filter by not equal."""
        self._filters[column] = {"$neq": value}
        return self
    
    def is_(self, column: str, value: any):
        """Filter by IS clause."""
        self._filters[column] = {"$is": value}
        return self
    
    def gt(self, column: str, value: any):
        """Filter by greater than."""
        self._filters[column] = {"$gt": value}
        return self
    
    def gte(self, column: str, value: any):
        """Filter by greater than or equal."""
        self._filters[column] = {"$gte": value}
        return self
    
    def lt(self, column: str, value: any):
        """Filter by less than."""
        self._filters[column] = {"$lt": value}
        return self
    
    def lte(self, column: str, value: any):
        """Filter by less than or equal."""
        self._filters[column] = {"$lte": value}
        return self
    
    def like(self, column: str, value: str):
        """Filter by LIKE."""
        self._filters[column] = {"$like": value}
        return self
    
    def order(self, column: str, desc: bool = False):
        """Order results."""
        self._order = {"column": column, "desc": desc}
        return self
    
    def limit(self, count: int):
        """Limit results."""
        self._limit = count
        return self
    
    def single(self):
        """Get single result."""
        return self
    
    def execute(self):
        """Execute query and return results."""
        table_data = self.client._data.get(self.table_name, [])
        
        # Apply filters
        results = []
        for row in table_data:
            match = True
            for col, filter_expr in self._filters.items():
                row_value = row.get(col)
                
                if "$eq" in filter_expr:
                    if row_value != filter_expr["$eq"]:
                        match = False
                        break
                elif "$in" in filter_expr:
                    if row_value not in filter_expr["$in"]:
                        match = False
                        break
                elif "$neq" in filter_expr:
                    if row_value == filter_expr["$neq"]:
                        match = False
                        break
                elif "$is" in filter_expr:
                    if filter_expr["$is"] is True:
                        if row_value is not None:
                            match = False
                            break
                    elif filter_expr["$is"] is False:
                        if row_value is None:
                            match = False
                            break
                elif "$gt" in filter_expr:
                    if row_value is None or row_value <= filter_expr["$gt"]:
                        match = False
                        break
                elif "$gte" in filter_expr:
                    if row_value is None or row_value < filter_expr["$gte"]:
                        match = False
                        break
                elif "$lt" in filter_expr:
                    if row_value is None or row_value >= filter_expr["$lt"]:
                        match = False
                        break
                elif "$lte" in filter_expr:
                    if row_value is None or row_value > filter_expr["$lte"]:
                        match = False
                        break
            
            if match:
                results.append(row)
        
        # Apply ordering
        if self._order:
            reverse = self._order.get("desc", False)
            results.sort(
                key=lambda x: x.get(self._order["column"], ""),
                reverse=reverse
            )
        
        # Apply limit
        if self._limit:
            results = results[:self._limit]
        
        return MockResponse(results)
    
    def insert(self):
        """Start INSERT."""
        return MockInsert(self)
    
    def update(self):
        """Start UPDATE."""
        return MockUpdate(self)
    
    def delete(self):
        """Start DELETE."""
        return MockDelete(self)


class MockResponse:
    """Mock response object."""
    
    def __init__(self, data: list):
        self.data = data


class MockInsert:
    """Mock INSERT builder."""
    
    def __init__(self, table: MockTable):
        self.table = table
        self._values = []
    
    def values(self, *args, **kwargs):
        """Set values to insert."""
        if args:
            self._values.extend(args)
        if kwargs:
            self._values.append(kwargs)
        return self
    
    def select(self, columns: str = "*"):
        """Return inserted data."""
        self._returning = columns
        return self
    
    def execute(self):
        """Execute insert."""
        results = []
        for values in self._values:
            if isinstance(values, dict):
                # Add default fields
                row = {
                    "id": str(uuid4()),
                    "created_at": datetime.utcnow().isoformat(),
                    **values
                }
                # Remove None values
                row = {k: v for k, v in row.items() if v is not None}
                self.table.client._data.setdefault(self.table.table_name, []).append(row)
                results.append(row)
        
        return MockResponse(results)


class MockUpdate:
    """Mock UPDATE builder."""
    
    def __init__(self, table: MockTable):
        self.table = table
        self._values = {}
        self._filters = {}
    
    def values(self, *args, **kwargs):
        """Set values to update."""
        if args:
            self._values.update(args[0] if isinstance(args[0], dict) else args[0])
        if kwargs:
            self._values.update(kwargs)
        return self
    
    def eq(self, column: str, value: any):
        """Filter by equality."""
        self._filters[column] = value
        return self
    
    def execute(self):
        """Execute update."""
        results = []
        table_data = self.table.client._data.get(self.table.table_name, [])
        
        for row in table_data:
            # Check if row matches filters
            match = True
            for col, value in self._filters.items():
                if row.get(col) != value:
                    match = False
                    break
            
            if match:
                # Update row
                row.update(self._values)
                row["updated_at"] = datetime.utcnow().isoformat()
                results.append(row)
        
        return MockResponse(results)


class MockDelete:
    """Mock DELETE builder."""
    
    def __init__(self, table: MockTable):
        self.table = table
        self._filters = {}
    
    def eq(self, column: str, value: any):
        """Filter by equality."""
        self._filters[column] = value
        return self
    
    def execute(self):
        """Execute delete."""
        table_data = self.table.client._data.get(self.table.table_name, [])
        
        # Find matching rows
        to_delete = []
        for i, row in enumerate(table_data):
            match = True
            for col, value in self._filters.items():
                if row.get(col) != value:
                    match = False
                    break
            
            if match:
                to_delete.append(i)
        
        # Delete in reverse order to maintain indices
        for i in reversed(to_delete):
            table_data.pop(i)
        
        return MockResponse([])


class MockAuth:
    """Mock auth helper."""
    
    def __init__(self, client: MockSupabaseClient):
        self.client = client
        self._users = {}
        self._sessions = {}
    
    def sign_in_with_password(self, email: str, password: str):
        """Sign in user."""
        return {
            "user": {"id": str(uuid4()), "email": email},
            "session": {"access_token": "test-token"}
        }
    
    def sign_up(self, email: str, password: str):
        """Sign up new user."""
        user_id = str(uuid4())
        self._users[user_id] = {"id": user_id, "email": email}
        return {
            "user": {"id": user_id, "email": email},
            "session": None
        }
    
    def get_user(self):
        """Get current user."""
        return {"user": {"id": str(uuid4()), "email": "test@example.com"}}
    
    def sign_out(self):
        """Sign out user."""
        pass


class MockStorage:
    """Mock storage helper."""
    
    def __init__(self, client: MockSupabaseClient):
        self.client = client
        self._buckets = {}
    
    def from_(self, bucket_name: str):
        """Get bucket reference."""
        if bucket_name not in self._buckets:
            self._buckets[bucket_name] = []
        return MockBucket(self, bucket_name)


class MockBucket:
    """Mock bucket reference."""
    
    def __init__(self, storage: MockStorage, bucket_name: str):
        self.storage = storage
        self.bucket_name = bucket_name
    
    def upload(self, path: str, file_content: bytes = b""):
        """Upload file."""
        return {"path": path}
    
    def download(self, path: str):
        """Download file."""
        return b"file content"
    
    def remove(self, paths: list):
        """Remove files."""
        return []
    
    def list(self, path: str = ""):
        """List files."""
        return []


def create_mock_supabase_client():
    """Create a mock Supabase client."""
    return MockSupabaseClient()
