# RAG Chat Application — Документация

## 📚 О проекте

**RAG Chat Application** — Full-stack веб-приложение для работы с документами на основе Retrieval-Augmented Generation (RAG).

**Основное назначение:**
- Загрузка документов (PDF, DOCX, TXT, MD)
- Интеллектуальный поиск и ответы на вопросы по загруженным документам
- Контекстно-зависимые ответы с указанием источников

## 🗂 Структура документации

### [API](./api/README.md)
- OpenAPI спецификация
- Endpoints для работы с документами, сессиями и чатом
- Форматы запросов и ответов

### [Архитектура](./architecture/README.md)
- Обзор системы
- Компоненты и их взаимодействие
- Поток данных

### [Разработка](./development/README.md)
- Настройка окружения
- Запуск разработки
- Тестирование
- Линтинг и форматирование

### [Развёртывание](./deployment/README.md)
- Production окружение
- Docker конфигурация
- Мониторинг и логирование

### [ADR (Architecture Decision Records)](./decisions/README.md)
- Архитектурные решения проекта

## 🚀 Быстрый старт

### Установка

**Backend:**
```bash
cd rag_app/backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Frontend:**
```bash
cd rag_app/frontend_next
npm install
npm run dev  # Runs on http://localhost:5173
```

### Доступ

- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs (Swagger UI)

## 📋 Основные команды

| Команда | Описание |
|---------|----------|
| `npm run dev` | Запуск frontend в режиме разработки |
| `uvicorn main:app --reload` | Запуск backend в режиме разработки |
| `npm run test` | Запуск тестов (frontend) |
| `pytest tests/` | Запуск тестов (backend) |
| `npm run lint` | Проверка кода (ESLint) |
| `npm run export:backend` | Экспорт frontend для интеграции с backend |

## 🏗 Архитектура

```
┌─────────────┐         ┌──────────────┐
│   Vite +    │         │   FastAPI    │
│   React     │◄───────►│    Backend   │
│  (5173)     │  HTTP   │   (8000)     │
└─────────────┘  API    └──────────────┘
                               │
                    ┌──────────┴──────────┐
                    │                     │
              ┌─────▼─────┐       ┌──────▼─────┐
              │ ChromaDB  │       │   Ollama   │
              │ (Vectors) │       │   /OpenAI  │
              └───────────┘       └────────────┘
```

## 🔑 Ключевые файлы

### Backend
- `rag_app/backend/main.py` — API endpoints
- `rag_app/backend/rag_engine.py` — RAG логика (эмбеддинги, поиск)
- `rag_app/backend/requirements.txt` — Python зависимости
- `rag_app/backend/uploads/` — Хранилище загруженных документов
- `rag_app/backend/chroma_db/` — ChromaDB векторное хранилище

### Frontend
- `rag_app/frontend_next/app/page.tsx` — Главная страница (чат)
- `rag_app/frontend_next/shared/api/client.ts` — API клиент
- `rag_app/frontend_next/shared/types.ts` — TypeScript типы
- `rag_app/frontend_next/components/` — React компоненты

## 🧪 Тестирование

### Frontend (Vitest)
```bash
cd rag_app/frontend_next
npm run test
```

**Тесты:**
- `components/document-panel.test.tsx`
- `components/chat-panel.test.tsx`
- `components/llm-selector.test.tsx`

### Backend (pytest)
```bash
cd rag_app/backend
pytest tests/
```

## 🔧 Конфигурация

### Переменные окружения

Создайте `.env` файл:

```env
OPENAI_API_KEY=your_openai_api_key
OLLAMA_BASE_URL=http://localhost:11434
```

### Поддерживаемые форматы

- PDF
- DOCX
- TXT
- MD

**Максимальный размер файла:** 50 MB

## ⚠️ Известные ограничения

- In-memory хранение сессий (не для production)
- Mock LLM ответы (реализация в разработке)
- Асинхронная обработка документов (симулирована)
- Нет аутентификации (требуется для production)

## 📝 Лицензия

MIT

---

**Следующие шаги:**
1. Прочитайте [Technical Specification](../technical_specification.md) для требований
2. Изучите [Frontend Specification](../frontend_specification.md) для frontend деталей
3. Ознакомьтесь с [User Stories](../stories/user_stories.md) для сценариев использования
