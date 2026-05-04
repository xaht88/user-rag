# RAG Chat Backend

FastAPI backend для RAG (Retrieval-Augmented Generation) чат-приложения.

## 📋 Описание

Бэкенд предоставляет REST API для:
- Загрузки документов (PDF, DOCX, TXT, MD)
- Управления сессиями чата
- Обработки запросов к документам с использованием LLM
- Хранения векторных представлений документов в ChromaDB

## 🚀 Быстрый старт

### Требования

- Python 3.10+
- ChromaDB (векторная база данных)
- Ollama или OpenAI API ключ

### Установка

```bash
# Перейдите в директорию backend
cd rag_app/backend

# Создайте виртуальное окружение
python -m venv .venv

# Активируйте окружение
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Установите зависимости
pip install -r requirements.txt
```

### Конфигурация

Создайте файл `.env` в корне проекта:

```env
# OpenAI API ключ (опционально, если используете OpenAI)
OPENAI_API_KEY=your-openai-api-key

# Базовый URL Ollama (по умолчанию)
OLLAMA_BASE_URL=http://localhost:11434
```

### Запуск

```bash
# Запуск сервера разработки
uvicorn main:app --reload --port 8000

# Запуск в продакшене
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

Сервер запустится на `http://localhost:8000`

## 📁 Структура проекта

```
backend/
├── main.py                 # Основной файл приложения, API endpoints
├── rag_engine.py           # RAG логика: эмбеддинги, поиск, генерация ответов
├── requirements.txt        # Python зависимости
├── .env                    # Конфигурация окружения (не коммитить)
├── uploads/                # Папка для загруженных документов
├── chroma_db/              # База данных ChromaDB для векторов
├── static/                 # Статические файлы (для экспорта frontend)
├── templates/              # HTML шаблоны
└── tests/                  # Тесты
    ├── __init__.py
    ├── conftest.py         # Конфигурация тестов
    ├── test_upload.py      # Тесты загрузки документов
    ├── test_query.py       # Тесты обработки запросов
    └── test_sessions.py    # Тесты управления сессиями
```

## 🔧 API Documentation

Полная документация API доступна по умолчанию при запуске:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Основные endpoints

#### Загрузка документа

```http
POST /api/upload
Content-Type: multipart/form-data

file: <document_file>
```

**Response:**
```json
{
  "session_id": "uuid-string",
  "document_id": "uuid-string",
  "message": "Документ загружен и обрабатывается"
}
```

#### Получение списка документов

```http
GET /api/sessions/{session_id}/documents
```

**Response:**
```json
{
  "documents": [
    {
      "id": "doc-uuid",
      "filename": "document.pdf",
      "upload_date": "2026-05-03T10:00:00",
      "chunks_count": 10,
      "pages_count": 5,
      "status": "ready",
      "selected": true
    }
  ]
}
```

#### Отправка запроса

```http
POST /api/sessions/{session_id}/query
Content-Type: application/json

{
  "query": "Какая информация содержится в документе?",
  "session_id": "session-uuid",
  "document_ids": ["doc-uuid-1", "doc-uuid-2"]
}
```

**Response:**
```json
{
  "message": "Ответ на вопрос...",
  "sources": [
    {
      "filename": "document.pdf",
      "page": 1,
      "snippet": "Релевантный фрагмент..."
    }
  ],
  "history": [
    {
      "role": "user",
      "content": "Какая информация..."
    },
    {
      "role": "assistant",
      "content": "Ответ...",
      "sources": [...]
    }
  ]
}
```

#### Настройка LLM

```http
POST /api/sessions/{session_id}/llm/config
Content-Type: application/json

{
  "provider": "ollama",
  "model": "llama2",
  "api_key": null
}
```

## 🔐 Безопасность

### Текущее состояние

⚠️ **Внимание:** В текущей версии отсутствуют:
- Аутентификация пользователей
- Авторизация запросов
- HTTPS шифрование
- Rate limiting

### Рекомендации для продакшена

1. **Добавить аутентификацию:**
   ```bash
   pip install PyJWT python-jose[cryptography] passlib
   ```

2. **Включить CORS:**
   ```python
   from fastapi.middleware.cors import CORSMiddleware
   
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["http://localhost:3000"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

3. **Добавить rate limiting:**
   ```bash
   pip install slowapi
   ```

4. **Использовать PostgreSQL вместо in-memory storage**

## 🧪 Тестирование

### Запуск тестов

```bash
# Все тесты
pytest tests/ -v

# Конкретный тест
pytest tests/test_upload.py -v

# Тесты с покрытием
pytest tests/ --cov=. --cov-report=html
```

### Написание тестов

Пример теста:

```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_upload_document():
    response = client.post(
        "/api/upload",
        files={"file": ("test.txt", b"Test content", "text/plain")}
    )
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert "document_id" in data
```

## 🐳 Docker (в разработке)

### Build image

```bash
docker build -t rag-backend .
```

### Run container

```bash
docker run -p 8000:8000 \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/chroma_db:/app/chroma_db \
  -e OPENAI_API_KEY=your-key \
  rag-backend
```

## 📊 Мониторинг и логирование

### Логи

Логи записываются в консоль по умолчанию. Для сохранения в файл:

```bash
uvicorn main:app --reload --port 8000 > logs/app.log 2>&1
```

### Health check

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

## 🤝 Вклад

### Правила коммитов

Используйте conventional commits:

```
feat: добавить новую функциональность
fix: исправление бага
docs: обновление документации
style: форматирование кода
refactor: рефакторинг
test: добавление тестов
chore: обновление зависимостей
```

### Процесс разработки

1. Создайте feature branch от `main`
   ```bash
   git checkout -b feature/новая-фича
   ```

2. Внесите изменения и протестируйте

3. Запустите тесты
   ```bash
   pytest tests/ -v
   ```

4. Закоммитьте изменения
   ```bash
   git add .
   git commit -m "feat: добавить новую функциональность"
   ```

5. Создайте Pull Request

## 📝 License

MIT License

## 📞 Поддержка

Для вопросов и предложений создайте issue в репозитории.
