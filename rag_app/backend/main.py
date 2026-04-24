from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
# [DEPRECATED] from fastapi.templating import Jinja2Templates  # starlette 1.0.0 bug
from pydantic import BaseModel
from typing import List, Optional
import os
import uuid
from datetime import datetime
import asyncio

app = FastAPI(title="RAG Web Application", version="1.0.0")

# Конфигурация
UPLOAD_DIR = "uploads"
CHROMA_DIR = "chroma_db"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(CHROMA_DIR, exist_ok=True)

# Статика
app.mount("/static", StaticFiles(directory="static"), name="static")

# Временное хранилище сессий (в продакшене — Redis/PostgreSQL)
sessions = {}

# Модели данных
class DocumentInfo(BaseModel):
    id: str
    filename: str
    upload_date: str
    chunks_count: int
    pages_count: int
    status: str  # "processing", "ready", "error"
    selected: bool = True

class ChatMessage(BaseModel):
    role: str  # "user" или "assistant"
    content: str
    sources: Optional[List[dict]] = None

class QueryRequest(BaseModel):
    query: str
    session_id: str
    document_ids: Optional[List[str]] = None

class LLMConfig(BaseModel):
    provider: str  # "openai" или "ollama"
    model: str
    api_key: Optional[str] = None

# API Endpoints
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Главная страница — читает index.html напрямую (обход бага starlette 1.0.0 + jinja2)"""
    with open("templates/index.html", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...)):
    """Загрузка документа"""
    # Валидация
    allowed_extensions = {".pdf", ".docx", ".txt", ".md"}
    if not any(file.filename.lower().endswith(ext) for ext in allowed_extensions):
        raise HTTPException(status_code=400, detail="Неподдерживаемый формат. Допустимые: PDF, DOCX, TXT, MD")
    
    if file.size and file.size > 50 * 1024 * 1024:  # 50 MB
        raise HTTPException(status_code=400, detail="Файл превышает 50 МБ")
    
    # Генерация ID и сохранение
    doc_id = str(uuid.uuid4())
    filename = f"{doc_id}_{file.filename}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    
    with open(filepath, "wb") as f:
        f.write(await file.read())
    
    # Добавляем в сессию
    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        "documents": [{
            "id": doc_id,
            "filename": file.filename,
            "upload_date": datetime.now().isoformat(),
            "chunks_count": 0,
            "pages_count": 0,
            "status": "processing",
            "filepath": filepath
        }],
        "llm_config": {"provider": "openai", "model": "gpt-4o-mini"},
        "chat_history": []
    }
    
    # Асинхронная обработка (в будущем — эмбеддинги)
    asyncio.create_task(process_document_async(session_id, doc_id, filepath))
    
    return JSONResponse({
        "session_id": session_id,
        "document_id": doc_id,
        "message": "Документ загружен и обрабатывается"
    })

async def process_document_async(session_id: str, doc_id: str, filepath: str):
    """Асинхронная обработка документа"""
    await asyncio.sleep(2)  # Имитация обработки
    
    if session_id in sessions:
        for doc in sessions[session_id]["documents"]:
            if doc["id"] == doc_id:
                doc["status"] = "ready"
                doc["chunks_count"] = 10  # Имитация
                doc["pages_count"] = 5    # Имитация
                break

@app.get("/api/sessions/{session_id}/documents")
async def get_documents(session_id: str):
    """Получить список документов сессии"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Сессия не найдена")
    
    return JSONResponse({
        "documents": sessions[session_id]["documents"]
    })

@app.post("/api/sessions/{session_id}/documents/{doc_id}/toggle")
async def toggle_document(session_id: str, doc_id: str):
    """Включить/выключить документ для поиска"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Сессия не найдена")
    
    for doc in sessions[session_id]["documents"]:
        if doc["id"] == doc_id:
            doc["selected"] = not doc["selected"]
            return JSONResponse({"selected": doc["selected"]})
    
    raise HTTPException(status_code=404, detail="Документ не найден")

@app.post("/api/sessions/{session_id}/documents/{doc_id}/delete")
async def delete_document(session_id: str, doc_id: str):
    """Удалить документ"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Сессия не найдена")
    
    docs = sessions[session_id]["documents"]
    doc = next((d for d in docs if d["id"] == doc_id), None)
    
    if not doc:
        raise HTTPException(status_code=404, detail="Документ не найден")
    
    # Удаление файла
    if os.path.exists(doc["filepath"]):
        os.remove(doc["filepath"])
    
    # Удаление из списка
    sessions[session_id]["documents"] = [d for d in docs if d["id"] != doc_id]
    
    # Очистка истории при удалении всех документов
    if not sessions[session_id]["documents"]:
        sessions[session_id]["chat_history"] = []
    
    return JSONResponse({"message": "Документ удалён"})

@app.post("/api/sessions/{session_id}/llm/config")
async def set_llm_config(session_id: str, config: LLMConfig):
    """Настроить LLM для сессии"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Сессия не найдена")
    
    sessions[session_id]["llm_config"] = config.dict()
    return JSONResponse({"message": "Конфигурация LLM обновлена"})

@app.post("/api/sessions/{session_id}/query")
async def query_llm(request: QueryRequest):
    """Обработка запроса пользователя"""
    if request.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Сессия не найдена")
    
    session = sessions[request.session_id]
    
    # Проверка документов
    if not session["documents"]:
        raise HTTPException(status_code=400, detail="Загрузите документ для начала работы")
    
    # Фильтрация выбранных документов
    selected_docs = [d for d in session["documents"] if d["selected"]]
    if not selected_docs:
        raise HTTPException(status_code=400, detail="Выберите хотя бы один документ")
    
    # Имитация ответа LLM (в будущем — реальный запрос к OpenAI/Ollama)
    await asyncio.sleep(1)  # Имитация задержки
    
    response_message = ChatMessage(
        role="assistant",
        content=f"Ответ на вопрос: {request.query}\n\nЭто имитация ответа LLM. В реальном приложении здесь будет ответ, сгенерированный на основе контекста из документов.",
        sources=[
            {"filename": doc["filename"], "page": 1, "snippet": "Релевантный фрагмент из документа..."}
            for doc in selected_docs[:2]
        ]
    )
    
    # Добавление в историю
    session["chat_history"].append({
        "role": "user",
        "content": request.query
    })
    session["chat_history"].append({
        "role": "assistant",
        "content": response_message.content,
        "sources": response_message.sources
    })
    
    return JSONResponse({
        "message": response_message.content,
        "sources": response_message.sources,
        "history": session["chat_history"]
    })

@app.get("/api/sessions/{session_id}/chat")
async def get_chat_history(session_id: str):
    """Получить историю чата"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Сессия не найдена")
    
    return JSONResponse({
        "history": sessions[session_id]["chat_history"]
    })

@app.get("/api/llm/providers")
async def get_llm_providers():
    """Получить список доступных LLM"""
    return JSONResponse({
        "providers": [
            {"name": "OpenAI", "models": ["gpt-4o", "gpt-4o-mini"]},
            {"name": "Ollama", "models": ["llama2", "mistral", "gemma"]}
        ]
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)