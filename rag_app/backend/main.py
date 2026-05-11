"""
RAG Chat Application - FastAPI Backend

Production-ready backend with Supabase integration for:
- User authentication (JWT)
- Vector search (pg_vector)
- Document storage (Supabase Storage)
- Session management (PostgreSQL)

Architecture:
- Authentication: Supabase Auth with JWT
- Database: PostgreSQL with pg_vector extension
- Storage: Supabase Storage (S3-compatible)
- Session Management: Persistent PostgreSQL storage
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, Request, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from supabase import create_client, Client
from supabase.lib.client_options import ClientOptions
import os
import uuid
from datetime import datetime
import asyncio
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Инициализация FastAPI
app = FastAPI(
    title="RAG Chat Application",
    version="2.0.0",
    description="Production-ready RAG application with Supabase integration"
)

# Database initialization
from database import engine, Base

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Константы
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Зависимости
security = HTTPBearer()

# Session manager dependency
from services.session_manager import SessionManager

# Модели данных
class DocumentInfo(BaseModel):
    """Информация о документе"""
    id: str
    filename: str
    upload_date: str
    chunks_count: int
    pages_count: int
    status: str  # "processing", "ready", "error"
    selected: bool = True
    file_size: Optional[int] = None

class ChatMessage(BaseModel):
    """Сообщение чата"""
    role: str  # "user", "assistant", "system"
    content: str
    sources: Optional[List[dict]] = None

class QueryRequest(BaseModel):
    """Запрос к LLM"""
    query: str
    session_id: str
    document_ids: Optional[List[str]] = None

class LLMConfig(BaseModel):
    """Конфигурация LLM"""
    provider: str  # "openai", "ollama"
    model: str
    api_key: Optional[str] = None

class UserRegistration(BaseModel):
    """Регистрация пользователя"""
    email: str
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    """Вход пользователя"""
    email: str
    password: str


def get_supabase_client():
    """Получить Supabase клиент"""
    from config.supabase_config import get_supabase_client as config_client
    return config_client()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    Получить текущего пользователя из JWT токена.
    
    Validates JWT token and returns user data.
    Used as dependency for protected endpoints.
    """
    try:
        supabase = get_supabase_client()
        options = ClientOptions(auth_token=credentials.credentials)
        client = create_client(
            supabase.url,
            supabase.api_key,
            options=options
        )
        
        user_response = client.auth.get_user()
        if not user_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        
        return user_response.user.model_dump()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )


# API Endpoints - Authentication
@app.post("/api/auth/register")
async def register_user(registration: UserRegistration):
    """
    Регистрация нового пользователя.
    
    Creates user account and profile.
    """
    try:
        from services.auth_service import AuthService
        supabase = get_supabase_client()
        auth = AuthService(supabase)
        
        result = auth.sign_up(
            email=registration.email,
            password=registration.password,
            full_name=registration.full_name
        )
        
        return JSONResponse({
            "message": "Пользователь успешно зарегистрирован",
            "user": result.get("user")
        })
        
    except Exception as e:
        logger.error(f"Registration failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/auth/login")
async def login_user(login: UserLogin):
    """
    Вход пользователя.
    
    Authenticates user and returns session tokens.
    """
    try:
        from services.auth_service import AuthService
        supabase = get_supabase_client()
        auth = AuthService(supabase)
        
        result = auth.sign_in(
            email=login.email,
            password=login.password
        )
        
        return JSONResponse({
            "message": "Вход выполнен успешно",
            "session": result.get("session")
        })
        
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise HTTPException(status_code=401, detail="Неверный email или пароль")


@app.get("/api/auth/me")
async def get_current_user_profile(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Получить профиль текущего пользователя.
    
    Returns user profile data.
    """
    try:
        from services.auth_service import AuthService
        supabase = get_supabase_client()
        auth = AuthService(supabase)
        
        profile = auth.get_profile(current_user["id"])
        
        return JSONResponse({
            "user": current_user,
            "profile": profile
        })
        
    except Exception as e:
        logger.error(f"Failed to get profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# API Endpoints - Sessions
@app.post("/api/sessions")
async def create_session(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Создать новую сессию.
    
    Creates a new conversation session for the authenticated user.
    """
    try:
        supabase = get_supabase_client()
        
        session_id = str(uuid.uuid4())
        
        # Сохраняем сессию в БД
        response = supabase.table("sessions").insert({
            "id": session_id,
            "user_id": current_user["id"],
            "title": "New Conversation",
            "session_metadata": {}
        }).execute()
        
        return JSONResponse({
            "session_id": session_id,
            "message": "Сессия создана"
        })
        
    except Exception as e:
        logger.error(f"Failed to create session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sessions")
async def list_sessions(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Получить список сессий пользователя.
    
    Returns all sessions for the authenticated user.
    """
    try:
        supabase = get_supabase_client()
        
        response = supabase.table("sessions").select("*").eq(
            "user_id", current_user["id"]
        ).order("created_at", desc=True).execute()
        
        return JSONResponse({
            "sessions": response.data
        })
        
    except Exception as e:
        logger.error(f"Failed to list sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sessions/{session_id}")
async def get_session(
    session_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Получить информацию о сессии.
    
    Returns session details including documents and messages.
    """
    try:
        supabase = get_supabase_client()
        
        # Проверка доступа
        session_response = supabase.table("sessions").select("*").eq(
            "id", session_id
        ).eq("user_id", current_user["id"]).execute()
        
        if not session_response.data:
            raise HTTPException(status_code=404, detail="Сессия не найдена")
        
        session = session_response.data[0]
        
        # Получаем документы
        docs_response = supabase.table("documents").select("*").eq(
            "session_id", session_id
        ).execute()
        
        # Получаем сообщения
        msgs_response = supabase.table("messages").select("*").eq(
            "session_id", session_id
        ).order("created_at").execute()
        
        return JSONResponse({
            "session": session,
            "documents": docs_response.data,
            "messages": msgs_response.data
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# API Endpoints - Documents
@app.post("/api/sessions/{session_id}/documents/upload")
async def upload_document(
    session_id: str,
    file: UploadFile = File(...),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Загрузить документ в сессию.
    
    Uploads file to Supabase Storage and creates database record.
    """
    # Валидация
    allowed_extensions = {".pdf", ".docx", ".txt", ".md"}
    if not any(file.filename.lower().endswith(ext) for ext in allowed_extensions):
        raise HTTPException(
            status_code=400,
            detail="Неподдерживаемый формат. Допустимые: PDF, DOCX, TXT, MD"
        )
    
    if file.size and file.size > 50 * 1024 * 1024:  # 50 MB
        raise HTTPException(status_code=400, detail="Файл превышает 50 МБ")
    
    try:
        from services.storage_service import StorageService
        from services.vector_store import VectorStoreService
        
        supabase = get_supabase_client()
        
        # Проверка доступа к сессии
        session_response = supabase.table("sessions").select("*").eq(
            "id", session_id
        ).eq("user_id", current_user["id"]).execute()
        
        if not session_response.data:
            raise HTTPException(status_code=404, detail="Сессия не найдена")
        
        # Генерация ID
        doc_id = str(uuid.uuid4())
        filename = f"{doc_id}_{file.filename}"
        storage_path = f"{current_user['id']}/{filename}"
        
        # Загрузка файла в Supabase Storage
        storage = StorageService(supabase)
        upload_result = storage.upload_file(
            file.file,
            current_user["id"],
            filename
        )
        
        # Создание записи в БД
        response = supabase.table("documents").insert({
            "id": doc_id,
            "user_id": current_user["id"],
            "session_id": session_id,
            "filename": file.filename,
            "file_type": file.content_type,
            "file_size": file.size,
            "storage_path": storage_path,
            "status": "processing"
        }).execute()
        
        # Асинхронная обработка
        asyncio.create_task(
            process_document_async(
                supabase, doc_id, storage_path, file.file, file.filename
            )
        )
        
        return JSONResponse({
            "document_id": doc_id,
            "message": "Документ загружен и обрабатывается"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def process_document_async(
    supabase: Client,
    doc_id: str,
    storage_path: str,
    file_content: Any,
    filename: str
):
    """Асинхронная обработка документа (эмбеддинги)"""
    try:
        from services.vector_store import VectorStoreService
        
        # TODO: Реализовать парсинг файла и создание эмбеддингов
        # Для пока - имитация
        await asyncio.sleep(2)
        
        # Обновить статус
        supabase.table("documents").update({
            "status": "ready",
            "chunks_count": 10,
            "pages_count": 5
        }).eq("id", doc_id).execute()
        
        logger.info(f"Document {doc_id} processed successfully")
        
    except Exception as e:
        logger.error(f"Document processing failed: {e}")
        supabase.table("documents").update({
            "status": "error"
        }).eq("id", doc_id).execute()


@app.get("/api/sessions/{session_id}/documents")
async def get_documents(
    session_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Получить список документов сессии"""
    try:
        supabase = get_supabase_client()
        
        response = supabase.table("documents").select("*").eq(
            "session_id", session_id
        ).execute()
        
        return JSONResponse({
            "documents": response.data
        })
        
    except Exception as e:
        logger.error(f"Failed to get documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/sessions/{session_id}/documents/{doc_id}/toggle")
async def toggle_document(
    session_id: str,
    doc_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Включить/выключить документ для поиска"""
    try:
        supabase = get_supabase_client()
        
        # Переключить selected флаг в metadata
        supabase.table("documents").update({
            "metadata": supabase.table("documents").select("metadata").eq(
                "id", doc_id
            )
        }).eq("id", doc_id).execute()
        
        return JSONResponse({"message": "Статус документа обновлён"})
        
    except Exception as e:
        logger.error(f"Failed to toggle document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/sessions/{session_id}/documents/{doc_id}/delete")
async def delete_document(
    session_id: str,
    doc_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Удалить документ"""
    try:
        from services.storage_service import StorageService
        
        supabase = get_supabase_client()
        
        # Получить информацию о документе
        doc_response = supabase.table("documents").select("*").eq(
            "id", doc_id
        ).eq("session_id", session_id).execute()
        
        if not doc_response.data:
            raise HTTPException(status_code=404, detail="Документ не найден")
        
        doc = doc_response.data[0]
        
        # Удалить файл из Storage
        storage = StorageService(supabase)
        storage.delete_file(current_user["id"], doc["filename"])
        
        # Удалить чанки из векторной базы
        vector_store = VectorStoreService(supabase)
        vector_store.delete_by_document_id(doc_id)
        
        # Удалить запись из БД
        supabase.table("documents").delete().eq("id", doc_id).execute()
        
        # Очистить историю если документов больше нет
        docs_response = supabase.table("documents").select("*").eq(
            "session_id", session_id
        ).execute()
        
        if not docs_response.data:
            supabase.table("messages").delete().eq("session_id", session_id).execute()
        
        return JSONResponse({"message": "Документ удалён"})
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# API Endpoints - Chat
@app.post("/api/sessions/{session_id}/query")
async def query_llm(
    request: QueryRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Обработка запроса пользователя"""
    try:
        supabase = get_supabase_client()
        
        # Проверка доступа к сессии
        session_response = supabase.table("sessions").select("*").eq(
            "id", request.session_id
        ).eq("user_id", current_user["id"]).execute()
        
        if not session_response.data:
            raise HTTPException(status_code=404, detail="Сессия не найдена")
        
        # Получить выбранные документы
        if request.document_ids:
            docs_response = supabase.table("documents").select("*").in_(
                "id", request.document_ids
            ).execute()
        else:
            docs_response = supabase.table("documents").select("*").eq(
                "session_id", request.session_id
            ).execute()
        
        if not docs_response.data:
            raise HTTPException(
                status_code=400,
                detail="Загрузите документ для начала работы"
            )
        
        # Добавить сообщение пользователя в БД
        supabase.table("messages").insert({
            "session_id": request.session_id,
            "role": "user",
            "content": request.query
        }).execute()
        
        # TODO: Реализовать реальный запрос к LLM
        # Для пока - имитация
        await asyncio.sleep(1)
        
        response_message = f"Ответ на вопрос: {request.query}\n\nЭто имитация ответа LLM."
        
        # Добавить ответ ассистента в БД
        supabase.table("messages").insert({
            "session_id": request.session_id,
            "role": "assistant",
            "content": response_message,
            "metadata": {
                "sources": [
                    {"filename": doc["filename"], "page": 1}
                    for doc in docs_response.data[:2]
                ]
            }
        }).execute()
        
        # Получить обновлённую историю
        msgs_response = supabase.table("messages").select("*").eq(
            "session_id", request.session_id
        ).order("created_at").execute()
        
        return JSONResponse({
            "message": response_message,
            "history": msgs_response.data
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sessions/{session_id}/chat")
async def get_chat_history(
    session_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Получить историю чата"""
    try:
        supabase = get_supabase_client()
        
        response = supabase.table("messages").select("*").eq(
            "session_id", session_id
        ).order("created_at").execute()
        
        return JSONResponse({
            "history": response.data
        })
        
    except Exception as e:
        logger.error(f"Failed to get chat history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/llm/providers")
async def get_llm_providers():
    """Получить список доступных LLM"""
    return JSONResponse({
        "providers": [
            {"name": "OpenAI", "models": ["gpt-4o", "gpt-4o-mini"]},
            {"name": "Ollama", "models": ["llama2", "mistral", "gemma"]}
        ]
    })


@app.get("/")
async def index():
    """Главная страница"""
    with open("templates/index.html", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


# Scheduler integration
from scheduler import start_scheduler, stop_scheduler, get_scheduler

# Lifespan context manager for startup/shutdown
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan."""
    # Startup: Create tables
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
    
    # Start background scheduler
    logger.info("Starting background task scheduler...")
    start_scheduler()
    logger.info("Background task scheduler started")
    
    yield
    
    # Shutdown: Dispose engine
    logger.info("Cleaning up database connections...")
    await engine.dispose()
    
    # Stop scheduler
    logger.info("Stopping background task scheduler...")
    stop_scheduler()
    logger.info("Database cleanup complete")

app = FastAPI(
    title="RAG Chat Application",
    version="2.0.0",
    description="Production-ready RAG application with Supabase integration",
    lifespan=lifespan
)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
