from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional
import os
import uuid
from datetime import datetime
import asyncio

from rag_engine import RAGEngine, OllamaClient

app = FastAPI(title="RAG Web Application", version="1.0.0")

# Конфигурация
UPLOAD_DIR = "uploads"
CHROMA_DIR = "chroma_db"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(CHROMA_DIR, exist_ok=True)

# Шаблоны и статика
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Инициализация RAG движка
rag_engine = RAGEngine(chroma_dir=CHROMA_DIR)
ollama_client = OllamaClient()

# Хранилище сессий
sessions = {}

# Модели данных
class DocumentInfo(BaseModel):
    id: str
    filename: str
    upload_date: str
    chunks_count: int
    pages_count: int
    status: str
    selected: bool = True

class ChatMessage(BaseModel):
    role: str
    content: str
    sources: Optional[List[dict]] = None

class QueryRequest(BaseModel):
    query: str
    session_id: str
    document_ids: Optional[List[str]] = None

class LLMConfig(BaseModel):
    provider: str
    model: str
    api_key: Optional[str] = None

# API Endpoints
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...)):
    allowed_extensions = {".pdf", ".docx", ".txt", ".md"}
    if not any(file.filename.lower().endswith(ext) for ext in allowed_extensions):
        raise HTTPException(status_code=400, detail="Неподдерживаемый формат")
    
    if file.size and file.size > 50 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Файл превышает 50 МБ")
    
    doc_id = str(uuid.uuid4())
    filename = f"{doc_id}_{file.filename}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    
    with open(filepath, "wb") as f:
        f.write(await file.read())
    
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
        "llm_config": {"provider": "ollama", "model": "llama2"},
        "chat_history": []
    }
    
    # Асинхронная обработка
    asyncio.create_task(process_document_async(session_id, doc_id, filepath))
    
    return JSONResponse({
        "session_id": session_id,
        "document_id": doc_id,
        "message": "Документ загружен и обрабатывается"
    })

async def process_document_async(session_id: str, doc_id: str, filepath: str):
    try:
        doc_info = next((d for d in sessions[session_id]["documents"] if d["id"] == doc_id), None)
        if not doc_info:
            return
        
        # Парсинг и добавление в ChromaDB
        result = rag_engine.add_document(doc_id, filepath, doc_info["filename"])
        
        # Оценка страниц (примерно)
        pages = result["text_length"] // 3000
        
        doc_info["status"] = "ready"
        doc_info["chunks_count"] = result["chunks_count"]
        doc_info["pages_count"] = pages
        
    except Exception as e:
        doc_info["status"] = "error"
        print(f"Ошибка обработки: {e}")

@app.get("/api/sessions/{session_id}/documents")
async def get_documents(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Сессия не найдена")
    return JSONResponse({"documents": sessions[session_id]["documents"]})

@app.post("/api/sessions/{session_id}/documents/{doc_id}/toggle")
async def toggle_document(session_id: str, doc_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Сессия не найдена")
    
    for doc in sessions[session_id]["documents"]:
        if doc["id"] == doc_id:
            doc["selected"] = not doc["selected"]
            return JSONResponse({"selected": doc["selected"]})
    
    raise HTTPException(status_code=404, detail="Документ не найден")

@app.post("/api/sessions/{session_id}/documents/{doc_id}/delete")
async def delete_document(session_id: str, doc_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Сессия не найдена")
    
    docs = sessions[session_id]["documents"]
    doc = next((d for d in docs if d["id"] == doc_id), None)
    
    if not doc:
        raise HTTPException(status_code=404, detail="Документ не найден")
    
    if os.path.exists(doc["filepath"]):
        os.remove(doc["filepath"])
    
    rag_engine.delete_document(doc_id)
    
    sessions[session_id]["documents"] = [d for d in docs if d["id"] != doc_id]
    
    if not sessions[session_id]["documents"]:
        sessions[session_id]["chat_history"] = []
    
    return JSONResponse({"message": "Документ удалён"})

@app.post("/api/sessions/{session_id}/llm/config")
async def set_llm_config(session_id: str, config: LLMConfig):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Сессия не найдена")
    
    sessions[session_id]["llm_config"] = config.dict()
    return JSONResponse({"message": "Конфигурация LLM обновлена"})

@app.post("/api/sessions/{session_id}/query")
async def query_llm(request: QueryRequest):
    if request.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Сессия не найдена")
    
    session = sessions[request.session_id]
    
    if not session["documents"]:
        raise HTTPException(status_code=400, detail="Загрузите документ")
    
    selected_docs = [d for d in session["documents"] if d["selected"]]
    if not selected_docs:
        raise HTTPException(status_code=400, detail="Выберите хотя бы один документ")
    
    # Поиск контекста
    context_chunks = []
    for doc in selected_docs:
        results = rag_engine.search(request.query, top_k=3)
        for doc_text, metadata, distance in results:
            if metadata["doc_id"] == doc["id"]:
                context_chunks.append(doc_text)
    
    context = "\n\n".join(context_chunks[:3])
    
    # Генерация ответа
    try:
        response_text = ollama_client.generate(request.query, context)
    except ConnectionError:
        response_text = "Ollama сервер недоступен. Убедитесь, что Ollama запущен."
    except Exception as e:
        response_text = f"Ошибка генерации: {str(e)}"
    
    response_message = ChatMessage(
        role="assistant",
        content=response_text,
        sources=[
            {"filename": doc["filename"], "page": 1, "snippet": context_chunks[i][:200] if i < len(context_chunks) else ""}
            for i, doc in enumerate(selected_docs[:2])
        ]
    )
    
    session["chat_history"].append({"role": "user", "content": request.query})
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