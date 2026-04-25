# RAG Frontend Homework

## Описание

Репозиторий содержит backend (`FastAPI`) и frontend-часть ДЗ на `Next.js + Tailwind CSS` для сценария RAG-приложения.

## Структура

- `rag_app/backend` — API, шаблоны и статика
- `rag_app/frontend_next` — frontend source of truth
- `stories` — user stories
- `technical_specification.md` — техническое задание
- `frontend_specification.md` — спецификация frontend-реализации

## Запуск локально

### Backend

```bash
cd rag_app/backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd rag_app/frontend_next
npm install
npm run dev
```

Frontend: `http://localhost:3000`  
Backend API: `http://localhost:8000`

## Тесты

```bash
cd rag_app/frontend_next
npm run test
```

В проекте добавлены тесты:
- `components/document-panel.test.tsx`
- `components/chat-panel.test.tsx`
- `components/llm-selector.test.tsx`

## Build и интеграция в FastAPI static/templates

```bash
cd rag_app/frontend_next
npm run export:backend
```

Команда экспортирует артефакты в:
- `rag_app/backend/static/next`
- `rag_app/backend/templates/next_index.html`

## Артефакты сдачи

- Код проекта в репозитории
- README с инструкциями
- `development_report.md` с описанием процесса
- Автотесты (>= 3) в репозитории
