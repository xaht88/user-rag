# Security Guidelines

## Overview

Security considerations and patterns for the RAG Chat Application.

## Current Security State

⚠️ **No authentication or authorization implemented**

## Authentication Patterns

### JWT Implementation

```python
# ✅ Good: JWT authentication pattern
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    """Verify JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### Password Hashing

```python
# ✅ Good: Password hashing with bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash password with bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    return pwd_context.verify(plain_password, hashed_password)
```

## Input Validation

### File Upload Security

```python
# ✅ Good: File upload validation
from fastapi import UploadFile
from typing import List

ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.txt', '.md'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

async def validate_file(file: UploadFile) -> None:
    """Validate uploaded file."""
    # Check extension
    if not file.filename or not any(
        file.filename.lower().endswith(ext) 
        for ext in ALLOWED_EXTENSIONS
    ):
        raise HTTPException(
            status_code=400,
            detail="File type not allowed"
        )
    
    # Check file size
    file.seek(0, 2)  # Seek to end
    file_size = file.tell()
    file.seek(0)  # Reset position
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File too large"
        )
```

### SQL Injection Prevention

```python
# ✅ Good: Use ORM to prevent SQL injection
# ❌ Avoid: Raw SQL with string interpolation
# query = f"SELECT * FROM users WHERE name = '{user_input}'"

# ✅ Use: Parameterized queries
from sqlalchemy import select

stmt = select(User).where(User.name == user_input)
result = await session.execute(stmt)
```

## Rate Limiting

```python
# ✅ Good: Rate limiting with slowapi
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)

@limiter.limit("100 per minute")
@app.post("/api/upload")
async def upload(request: Request, file: UploadFile):
    return {"status": "uploaded"}

# Handle rate limit errors
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)
```

## CORS Configuration

```python
# ✅ Good: Secure CORS configuration
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Whitelist specific origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

## Environment Variables

```bash
# ✅ Good: Use environment variables for secrets
# .env file (NOT committed to git)
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:pass@localhost/db
OPENAI_API_KEY=your-openai-key
```

```python
# ✅ Good: Load from environment
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    secret_key: str
    database_url: str
    openai_api_key: str
    
    class Config:
        env_file = ".env"

settings = Settings()
```

## Security Best Practices

1. **Never commit secrets** to version control
2. **Use HTTPS** in production
3. **Validate all inputs** — client and server
4. **Implement rate limiting** to prevent abuse
5. **Use prepared statements** for database queries
6. **Hash passwords** with bcrypt orargon2
7. **Set secure cookies** with HttpOnly and Secure flags
8. **Implement CSRF protection** for state-changing operations
9. **Use Content Security Policy** headers
10. **Regular security audits** and dependency updates

## Dependency Security

```bash
# ✅ Good: Check for vulnerabilities
pip install safety
safety check

# Frontend
npm audit
npm audit fix
```

---

**Generated with [Continue](https://continue.dev)**

Co-Authored-By: Continue <noreply@continue.dev>
