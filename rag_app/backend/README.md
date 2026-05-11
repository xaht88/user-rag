# RAG Chat Backend

FastAPI backend для RAG (Retrieval-Augmented Generation) чат-приложения с **Supabase PostgreSQL** и **persistent session storage**.

## 📋 Описание

Бэкенд предоставляет REST API для:
- Загрузки документов (PDF, DOCX, TXT, MD)
- Управления сессиями чата с **постоянным хранением в PostgreSQL**
- Обработки запросов к документам с использованием LLM
- Хранения векторных представлений документов в **Supabase pg_vector**
- Аутентификации пользователей через **Supabase Auth**

### 🎯 Ключевые особенности

- ✅ **Persistent Session Storage** — сессии сохраняются в PostgreSQL и доступны после перезапуска
- ✅ **Supabase Integration** — PostgreSQL + pg_vector + Storage + Auth
- ✅ **Vector Search** — семантический поиск через pg_vector
- ✅ **Scalable Architecture** — поддержка горизонтального масштабирования
- ✅ **TTL Management** — автоматическое управление временем жизни сессий

---

## 🚀 Быстрый старт

### Требования

- Python 3.10-3.12
- **Supabase проект** с расширением `pg_vector`
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
# Supabase Configuration
SUPABASE_URL=https://ibnzhdgjfihhjvbfimpu.supabase.co
SUPABASE_ANON_KEY=sb_publishable_e7GM8wcJBwC9W4aj7-dzWw_kLUE6Rxw
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_DB_PASSWORD=your-database-password

# OpenAI API ключ (опционально, если используете OpenAI)
OPENAI_API_KEY=your-openai-api-key

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434

# Database Configuration
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20
DEBUG=false
```

### Запуск

```bash
# Запуск сервера разработки
uvicorn main:app --reload --port 8000

# Запуск в продакшене
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

Сервер запустится на `http://localhost:8000`

---

## 🗄️ База данных и миграции

### Подключение к Supabase PostgreSQL

Проект Supabase уже настроен:
- **Project ID:** `ibnzhdgjfihhjvbfimpu`
- **Region:** `eu-west-1`
- **Database:** PostgreSQL 17 с расширением `pg_vector`

### Таблицы базы данных

Проект использует следующие таблицы:

#### `sessions`
Хранение сессий чата с TTL и конфигурацией LLM.

```sql
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    title TEXT DEFAULT 'New Conversation',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'
);
```

#### `documents`
Метаданные загруженных документов.

```sql
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    session_id UUID REFERENCES sessions(id) ON DELETE CASCADE,
    filename TEXT NOT NULL,
    file_type TEXT,
    file_size BIGINT,
    storage_path TEXT,
    status TEXT CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
```

#### `document_chunks`
Векторные эмбеддинги для семантического поиска.

```sql
CREATE TABLE document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER,
    content TEXT,
    embedding vector(1536),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
```

#### `messages`
История сообщений чата.

```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES sessions(id) ON DELETE CASCADE,
    role TEXT CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'
);
```

#### `profiles`
Профили пользователей (расширение `auth.users`).

```sql
CREATE TABLE profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT,
    full_name TEXT,
    avatar_url TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
```

### SQL миграции

Файл схемы доступен в `supabase_schema.sql`. Для применения миграций:

```bash
# Подключиться к базе данных
psql -h db.ibnzhdgjfihhjvbfimpu.supabase.co -U postgres -d postgres

# Применить схему
\i supabase_schema.sql
```

---

## 📁 Структура проекта

```
backend/
├── main.py                              # Основной файл приложения, API endpoints
├── requirements.txt                     # Python зависимости
├── .env                                 # Конфигурация окружения (не коммитить)
├── uploads/                             # Папка для загруженных документов
├── static/                              # Статические файлы (для экспорта frontend)
├── templates/                           # HTML шаблоны
├── services/                            # Сервисы
│   ├── __init__.py
│   ├── session_manager.py              # Управление сессиями
│   ├── session_store.py                # PostgreSQLSessionStore
│   ├── auth_service.py                 # Аутентификация
│   ├── storage_service.py              # Работа с Supabase Storage
│   └── vector_store.py                 # Векторный поиск
├── config/                              # Конфигурация
│   ├── __init__.py
│   └── supabase_config.py              # Supabase client
├── models/                              # SQLAlchemy модели
│   ├── __init__.py
│   ├── session.py                      # Session model
│   ├── session_document.py             # SessionDocument model
│   ├── chat_message.py                 # ChatMessage model
│   └── message_source.py               # MessageSource model
├── database.py                          # Database connection и engine
├── supabase_schema.sql                  # Схема БД Supabase
└── tests/                               # Тесты
    ├── __init__.py
    ├── test_main.py                    # Базовые тесты
    ├── test_session_store.py           # Unit тесты для session_store
    └── integration/                    # Интеграционные тесты
        ├── __init__.py
        ├── test_session_api.py         # Session API tests
        ├── test_document_api.py        # Document API tests
        └── test_auth_api.py            # Auth API tests
```

---

## 🔧 API Documentation

Полная документация API доступна по умолчанию при запуске:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Основные endpoints

#### Аутентификация

##### Регистрация пользователя

```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "full_name": "User Name"
}
```

**Response:**
```json
{
  "message": "Пользователь успешно зарегистрирован",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "User Name"
  }
}
```

##### Вход пользователя

```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response:**
```json
{
  "message": "Вход выполнен успешно",
  "session": {
    "access_token": "jwt-token",
    "refresh_token": "refresh-token",
    "user": {...}
  }
}
```

##### Получить профиль текущего пользователя

```http
GET /api/auth/me
Authorization: Bearer <jwt-token>
```

#### Сессии

##### Создать новую сессию

```http
POST /api/sessions
Authorization: Bearer <jwt-token>
```

**Response:**
```json
{
  "session_id": "uuid",
  "message": "Сессия создана"
}
```

##### Получить список сессий пользователя

```http
GET /api/sessions
Authorization: Bearer <jwt-token>
```

**Response:**
```json
{
  "sessions": [
    {
      "id": "session-uuid",
      "user_id": "user-uuid",
      "title": "New Conversation",
      "created_at": "2026-05-11T10:00:00Z",
      "updated_at": "2026-05-11T10:00:00Z",
      "metadata": {}
    }
  ]
}
```

##### Получить информацию о сессии

```http
GET /api/sessions/{session_id}
Authorization: Bearer <jwt-token>
```

**Response:**
```json
{
  "session": {
    "id": "session-uuid",
    "user_id": "user-uuid",
    "title": "New Conversation",
    "created_at": "2026-05-11T10:00:00Z",
    "updated_at": "2026-05-11T10:00:00Z",
    "metadata": {}
  },
  "documents": [...],
  "messages": [...]
}
```

#### Документы

##### Загрузить документ в сессию

```http
POST /api/sessions/{session_id}/documents/upload
Authorization: Bearer <jwt-token>
Content-Type: multipart/form-data

file: <document_file>
```

**Response:**
```json
{
  "document_id": "uuid",
  "message": "Документ загружен и обрабатывается"
}
```

##### Получить список документов сессии

```http
GET /api/sessions/{session_id}/documents
Authorization: Bearer <jwt-token>
```

**Response:**
```json
{
  "documents": [
    {
      "id": "doc-uuid",
      "session_id": "session-uuid",
      "user_id": "user-uuid",
      "filename": "document.pdf",
      "file_type": "application/pdf",
      "file_size": 102400,
      "storage_path": "user-uuid/doc-uuid_document.pdf",
      "status": "ready",
      "metadata": {},
      "created_at": "2026-05-11T10:00:00Z",
      "updated_at": "2026-05-11T10:00:00Z"
    }
  ]
}
```

##### Удалить документ

```http
POST /api/sessions/{session_id}/documents/{doc_id}/delete
Authorization: Bearer <jwt-token>
```

**Response:**
```json
{
  "message": "Документ удалён"
}
```

#### Чат

##### Отправить запрос к LLM

```http
POST /api/sessions/{session_id}/query
Authorization: Bearer <jwt-token>
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
  "history": [
    {
      "id": "msg-uuid",
      "session_id": "session-uuid",
      "role": "user",
      "content": "Какая информация...",
      "created_at": "2026-05-11T10:00:00Z",
      "metadata": {}
    },
    {
      "id": "msg-uuid",
      "session_id": "session-uuid",
      "role": "assistant",
      "content": "Ответ...",
      "created_at": "2026-05-11T10:01:00Z",
      "metadata": {
        "sources": [
          {
            "filename": "document.pdf",
            "page": 1
          }
        ]
      }
    }
  ]
}
```

##### Получить историю чата

```http
GET /api/sessions/{session_id}/chat
Authorization: Bearer <jwt-token>
```

**Response:**
```json
{
  "history": [
    {
      "id": "msg-uuid",
      "session_id": "session-uuid",
      "role": "user",
      "content": "Привет",
      "created_at": "2026-05-11T10:00:00Z",
      "metadata": {}
    },
    {
      "id": "msg-uuid",
      "session_id": "session-uuid",
      "role": "assistant",
      "content": "Здравствуйте!",
      "created_at": "2026-05-11T10:00:30Z",
      "metadata": {}
    }
  ]
}
```

#### LLM

##### Получить список доступных LLM

```http
GET /api/llm/providers
```

**Response:**
```json
{
  "providers": [
    {
      "name": "OpenAI",
      "models": ["gpt-4o", "gpt-4o-mini"]
    },
    {
      "name": "Ollama",
      "models": ["llama2", "mistral", "gemma"]
    }
  ]
}
```

---

## 🔐 Безопасность

### Текущее состояние

✅ **Реализовано:**
- JWT аутентификация через Supabase Auth
- Защита endpoints через `get_current_user` dependency
- RLS policies для изоляции данных пользователей

⚠️ **Планируется:**
- Rate limiting (SlowAPI)
- HTTPS шифрование
- Additional security headers

### RLS Policies

Supabase использует Row Level Security для изоляции данных:

```sql
-- Сессии доступны только владельцу
CREATE POLICY "Users can view own sessions" ON sessions
  FOR SELECT USING (auth.uid() = user_id);

-- Документы доступны только владельцу сессии
CREATE POLICY "Users can view own documents" ON documents
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM sessions 
      WHERE sessions.id = documents.session_id 
      AND sessions.user_id = auth.uid()
    )
  );
```

---

## 🧪 Тестирование

### Запуск тестов

```bash
# Все тесты
pytest tests/ -v

# Только unit тесты
pytest tests/test_session_store.py -v

# Интеграционные тесты
pytest tests/integration/ -v

# Тесты с покрытием
pytest tests/ --cov=. --cov-report=html --cov-report=term-missing
```

### Coverage report

Откройте `htmlcov/index.html` в браузере для просмотра отчета.

### Написание тестов

#### Unit тесты

Пример unit теста для `PostgreSQLSessionStore`:

```python
import pytest
from unittest.mock import Mock
from services.session_store import PostgreSQLSessionStore
from models import Session as SessionModel

class TestPostgreSQLSessionStore:
    @pytest.fixture
    def mock_db(self):
        return Mock()
    
    @pytest.fixture
    def session_store(self, mock_db):
        return PostgreSQLSessionStore(mock_db)
    
    def test_create_session(self, session_store, mock_db):
        session = session_store.create(user_id="test-user")
        
        assert session is not None
        assert session.user_id == "test-user"
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
```

#### Интеграционные тесты

Пример интеграционного теста для API:

```python
import pytest
from fastapi.testclient import TestClient
from main import app
from database import Base, get_db

@pytest.fixture
def client():
    # Create test database
    Base.metadata.create_all(bind=engine)
    
    # Override database dependency
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    # Cleanup
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)

def test_create_session(client):
    response = client.post("/api/sessions")
    
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
```

---

## 🐳 Docker (в разработке)

### Build image

```bash
docker build -t rag-backend .
```

### Run container

```bash
docker run -p 8000:8000 \
  -v $(pwd)/uploads:/app/uploads \
  -e SUPABASE_URL=https://ibnzhdgjfihhjvbfimpu.supabase.co \
  -e SUPABASE_ANON_KEY=sb_publishable_e7GM8wcJBwC9W4aj7-dzWw_kLUE6Rxw \
  -e SUPABASE_SERVICE_ROLE_KEY=your-service-role-key \
  -e OPENAI_API_KEY=your-key \
  rag-backend
```

---

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
  "version": "2.0.0"
}
```

---

## ⏱️ Background Tasks и Cleanup

### Автоматическая очистка сессий

Приложение включает встроенный scheduler для автоматической очистки старых сессий.

#### Как это работает

- **Scheduler** запускается автоматически при старте приложения
- **Cleanup task** выполняется каждые 1 час
- Удаляются сессии старше 30 дней
- Логируются все операции очистки

#### Ручной запуск cleanup

```bash
# Очистить сессии старше 30 дней
python -m tasks.session_cleanup --days 30

# Очистить ВСЕ expired сессии (независимо от возраста)
python -m tasks.session_cleanup --all

# Показать помощь
python -m tasks.session_cleanup --help
```

#### Настройка интервала очистки

Редактируйте файл `celery_config.py`:

```python
app.conf.update(
    beat_schedule={
        'cleanup-expired-sessions': {
            'task': 'tasks.session_cleanup.cleanup_expired_sessions',
            'schedule': timedelta(hours=1),  # Измените интервал
            'options': {'args': (30,)}
        },
    },
)
```

#### Использование Celery (Production)

Для production рекомендуется использовать Celery с Redis:

```bash
# Установите зависимости
pip install celery[redis]

# Запустите worker
celery -A celery_config worker --loglevel=info

# Запустите beat scheduler
celery -A celery_config beat --loglevel=info
```

#### Мониторинг scheduler

```python
from scheduler import get_scheduler

status = get_scheduler().get_status()
print(status)
```

---

## 🔄 Миграция с ChromaDB на Supabase

### Предыстория

Ранее приложение использовало ChromaDB для хранения векторных эмбеддингов. Теперь используется **Supabase pg_vector** для:
- Унификации хранилища данных
- Упрощения инфраструктуры
- Улучшения производительности
- Поддержки горизонтального масштабирования

---

## 🧪 Тестирование Background Tasks

### Запуск тестов cleanup

```bash
# Тесты для session cleanup
pytest tests/integration/test_session_cleanup.py -v

# Все интеграционные тесты
pytest tests/integration/ -v
```

### Примеры тестов

```python
def test_cleanup_expired_sessions(test_db):
    """Test cleanup of expired sessions."""
    # Create expired session
    expired_session = SessionModel(
        id=uuid4(),
        user_id=str(uuid4()),
        expires_at=datetime.utcnow() - timedelta(days=31)
    )
    test_db.add(expired_session)
    
    # Create recent session (should not be cleaned)
    recent_session = SessionModel(
        id=uuid4(),
        user_id=str(uuid4()),
        expires_at=datetime.utcnow() + timedelta(days=10)
    )
    test_db.add(recent_session)
    
    test_db.commit()
    
    # Run cleanup
    deleted = cleanup_expired_sessions(days_threshold=30)
    
    # Verify
    assert deleted == 1
```

### Шаг 1: Подготовка Supabase проекта

1. Убедитесь, что проект Supabase создан и настроен
2. Включите расширение `pg_vector`:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

3. Примените схему базы данных:
   ```bash
   psql -h db.ibnzhdgjfihhjvbfimpu.supabase.co -U postgres -d postgres -f supabase_schema.sql
   ```

### Шаг 2: Обновление конфигурации

1. Добавьте переменные окружения в `.env`:
   ```env
   SUPABASE_URL=https://ibnzhdgjfihhjvbfimpu.supabase.co
   SUPABASE_ANON_KEY=sb_publishable_e7GM8wcJBwC9W4aj7-dzWw_kLUE6Rxw
   SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
   SUPABASE_DB_PASSWORD=your-database-password
   ```

2. Установите зависимости:
   ```bash
   pip install supabase psycopg2-binary
   ```

### Шаг 3: Удаление ChromaDB артефактов

```bash
# Удалите старые артефакты
rm -rf chroma_db/
rm -f rag_engine.py
rm -f test_paths.py
```

### Шаг 4: Обновление зависимостей

```bash
# Удалите chromadb из requirements.txt
# Добавьте supabase и psycopg2-binary
pip install -r requirements.txt
```

### Шаг 5: Тестирование миграции

```bash
# Запустите тесты
pytest tests/ -v

# Проверьте подключение к базе данных
python -c "from database import engine; print(engine.connect())"
```

### Шаг 6: Развертывание

1. Запустите backend:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

2. Проверьте Swagger UI: http://localhost:8000/docs

3. Протестируйте создание сессии и загрузку документа

---

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

---

## 📝 License

MIT License

---

## 📞 Поддержка

Для вопросов и предложений создайте issue в репозитории.

---

## 📚 Дополнительная документация

- [Кондуктор проекта](../../../conductor/) — контекст и артефакты проекта
- [TD-001: Persistent Session Storage](../../../conductor/tracks/TD-001-persistent-sessions/) — спецификация и план
- [Supabase Documentation](https://supabase.com/docs) — официальная документация
- [pg_vector Documentation](https://github.com/pgvector/pgvector) — документация векторного расширения

---

**Версия:** 2.0.0  
**Последнее обновление:** 2026-05-11
