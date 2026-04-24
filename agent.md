# agent.md — RAG Web Application

## Описание проекта
RAG (Retrieval-Augmented Generation) веб-приложение для диалога с документами.
Пользователь загружает PDF/DOCX/TXT/MD, система создаёт эмбеддинги через sentence-transformers,
выполняет векторный поиск (ChromaDB) и генерирует ответ через выбранную LLM (OpenAI / Ollama).

## Структура
```
rag_app/backend/
├── main.py          # FastAPI — заглушка без RAG
├── rag_app.py       # FastAPI + RAGEngine (полная версия)
├── rag_engine.py    # RAGEngine + OllamaClient
├── templates/index.html   # UI (Jinja2)
├── static/
│   ├── app.js       # Frontend логика (stub mode)
│   └── styles.css   # Design system (dark theme)
├── requirements.txt
└── venv/            # Виртуальная среда Python 3.12
```

## Запуск

### Быстрый просмотр UI (без бэкенда)
```bash
# из папки rag_app/backend/
py -m http.server 8080 --directory .
# открыть: http://localhost:8080/templates/index.html
```

### Полный запуск (FastAPI)
```bash
cd rag_app/backend
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
# открыть: http://localhost:8000
```

## Зависимости (venv)
- fastapi, uvicorn[standard] — установлены
- chromadb, sentence-transformers — требуют установки (тяжёлые)
- pypdf, python-docx, langchain-text-splitters

## User Stories (US-01..US-09)
Все реализованы как визуальные заглушки в app.js:
- US-01: загрузка файла с валидацией формата/размера + прогресс
- US-02: выбор LLM (OpenAI/Ollama) с индикатором доступности
- US-03: диалог с документом (stub ответы)
- US-04: история диалога в сессии
- US-05: удаление документов
- US-06: выбор активных документов (чекбоксы)
- US-07: ввод API-ключа (только в памяти)
- US-08: responsive layout (mobile 768px)
- US-09: source cards с фрагментами текста

## Спецификация
- `.kiro/specs/rag-web-app/requirements.md`
- `.kiro/specs/rag-web-app/design.md`
- `.kiro/specs/rag-web-app/tasks.md`

## Статус
- [x] UI/UX дизайн (dark theme, stub mode)
- [x] venv создан (rag_app/backend/venv)
- [x] fastapi + uvicorn установлены
- [ ] chromadb + sentence-transformers (установка ~10 мин)
- [ ] Интеграция RAGEngine с UI
