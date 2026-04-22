# План реализации: RAG Веб-приложение

## Обзор

Реализация RAG-приложения на стеке FastAPI (Python) + Next.js (TypeScript).
Порядок: инфраструктура → модели данных → backend-сервисы → API → frontend → интеграция.

---

## Задачи

- [ ] 1. Инфраструктура и структура проекта
  - Создать структуру директорий: `backend/`, `frontend/`, `tests/`
  - Создать `backend/requirements.txt`: fastapi, uvicorn, chromadb, sentence-transformers, pypdf2, python-docx, openai, httpx, hypothesis, pytest
  - Создать `frontend/package.json` с зависимостями: next, react, tailwindcss, axios
  - Создать `backend/config.py` с настройками: CHUNK_SIZE=512, OVERLAP=50, MAX_FILE_MB=50, MAX_DOCS=10, LLM_TIMEOUT=30
  - Создать `docker-compose.yml` для запуска backend + frontend
  - _Requirements: 1.1, 2.3, 7.4_

- [ ] 2. Модели данных
  - [ ] 2.1 Реализовать dataclasses в `backend/models.py`
    - Реализовать: `Session`, `Document`, `Chunk`, `Message`, `SourceRef`, `ModelInfo`
    - Добавить Pydantic-схемы: `QueryRequest`, `QueryResponse`, `UploadResponse`
    - _Requirements: 1.7, 2.2, 3.4, 3.5_

  - [ ]* 2.2 Property-тест: полнота метаданных документа
    - **Property 3: Полнота метаданных документа**
    - **Validates: Requirements 1.7**
    - Файл: `tests/test_properties.py`

- [ ] 3. Document Processor
  - [ ] 3.1 Реализовать `backend/document_processor.py`
    - Метод `parse()`: PDF (pypdf2), DOCX (python-docx), TXT/MD (plain read)
    - Метод `chunk()`: токенизация tiktoken, размер 512, overlap 50
    - Обработка ошибок: повреждённый файл → `ParseError` с описанием
    - _Requirements: 1.2, 5.1, 5.2, 5.3, 5.4, 5.5_

  - [ ]* 3.2 Property-тест: инвариант размера чанка
    - **Property 1: Инвариант размера чанка**
    - **Validates: Requirements 1.2**
    - `@given(text=st.text(min_size=1, max_size=10000))`

  - [ ]* 3.3 Property-тест: round-trip парсинга
    - **Property 5: Round-trip парсинга документа**
    - **Validates: Requirements 5.5**
    - `@given` по валидным TXT/MD документам

  - [ ]* 3.4 Unit-тесты document_processor
    - Парсинг PDF/DOCX/TXT/MD с валидными файлами
    - Граничные случаи: пустой файл, файл ровно 50 МБ, один чанк
    - Ошибки: повреждённый PDF, неверный DOCX
    - _Requirements: 5.1–5.4_

- [ ] 4. Embedding Service
  - [ ] 4.1 Реализовать `backend/embedding_service.py`
    - Метод `encode(texts)` через `sentence-transformers` (модель `all-MiniLM-L6-v2`)
    - Ленивая инициализация модели при первом вызове
    - _Requirements: 1.3_

- [ ] 5. Vector Store
  - [ ] 5.1 Реализовать `backend/vector_store.py`
    - Методы: `upsert()`, `search()`, `delete_document()`, `delete_session()`
    - Изоляция по `session_id` через ChromaDB collection namespace
    - `search()` возвращает не более `top_k=5` результатов
    - _Requirements: 1.3, 3.1, 4.2, 7.1, 7.2_

  - [ ]* 5.2 Property-тест: round-trip хранения чанков
    - **Property 4: Round-trip хранения чанков**
    - **Validates: Requirements 1.3**
    - Загрузить чанк → поиск по его эмбеддингу → чанк в топ-результатах

  - [ ]* 5.3 Property-тест: инвариант количества результатов поиска
    - **Property 6: Инвариант количества результатов поиска**
    - **Validates: Requirements 3.1**
    - `search(..., top_k=5)` → `len(result) <= 5`

  - [ ]* 5.4 Property-тест: изоляция данных между сессиями
    - **Property 11: Изоляция данных между сессиями**
    - **Validates: Requirements 7.1**
    - Данные сессии A не видны при поиске с session_id=B

  - [ ]* 5.5 Property-тест: удаление документа очищает чанки
    - **Property 9: Удаление документа очищает чанки**
    - **Validates: Requirements 4.2**

  - [ ]* 5.6 Property-тест: очистка данных при завершении сессии
    - **Property 12: Очистка данных при завершении сессии**
    - **Validates: Requirements 7.2**

- [ ] 6. Session Manager
  - [ ] 6.1 Реализовать `backend/session_manager.py`
    - Методы: `create_session()`, `get_session()`, `terminate_session()`
    - In-memory хранилище (dict), thread-safe через `asyncio.Lock`
    - `terminate_session()` вызывает `vector_store.delete_session()`
    - _Requirements: 7.1, 7.2, 7.3_

  - [ ]* 6.2 Property-тест: выбор модели сохраняется в сессии
    - **Property 13: Выбор модели сохраняется в сессии**
    - **Validates: Requirements 2.2**

  - [ ]* 6.3 Property-тест: сохранение истории диалога
    - **Property 8: Сохранение истории диалога**
    - **Validates: Requirements 3.5**
    - Последовательность сообщений сохраняется в правильном порядке

- [ ] 7. LLM Connector
  - [ ] 7.1 Реализовать `backend/llm_connector.py`
    - Метод `get_available_models()`: читает конфиг, проверяет доступность Ollama
    - Метод `generate()`: строит prompt с context + history, вызывает OpenAI или Ollama
    - Таймаут 30 секунд, при превышении → `LLMTimeoutError`
    - API-ключ передаётся только в запрос, не логируется
    - _Requirements: 2.1, 2.3, 2.5, 2.6, 3.2, 3.7_

  - [ ]* 7.2 Unit-тесты llm_connector
    - Мок OpenAI/Ollama, проверка таймаута, недоступная модель
    - _Requirements: 2.5, 3.7_

- [ ] 8. Checkpoint — backend-сервисы
  - Убедиться, что все тесты проходят: `pytest tests/ -v`
  - Проверить импорты и зависимости между модулями
  - Спросить пользователя, если есть вопросы.

- [ ] 9. API Routes
  - [ ] 9.1 Реализовать `backend/api/routes.py` — все 9 endpoints
    - `POST /api/sessions` → `session_manager.create_session()`
    - `DELETE /api/sessions/{id}` → `session_manager.terminate_session()`
    - `POST /api/sessions/{id}/documents` → валидация файла → `document_processor` → `embedding_service` → `vector_store.upsert()`
    - `GET /api/sessions/{id}/documents` → список документов сессии
    - `DELETE /api/sessions/{id}/documents/{doc_id}` → `vector_store.delete_document()`
    - `POST /api/sessions/{id}/query` → `embedding_service.encode()` → `vector_store.search()` → `llm_connector.generate()`
    - `GET /api/sessions/{id}/messages` → история из сессии
    - `GET /api/models` → `llm_connector.get_available_models()`
    - `PUT /api/sessions/{id}/model` → обновить `session.selected_model`
    - _Requirements: 1.1, 1.4, 1.5, 1.6, 2.1, 2.2, 3.1, 3.2, 3.6, 4.1, 4.2, 4.5_

  - [ ] 9.2 Реализовать обработку ошибок в `backend/api/error_handlers.py`
    - HTTP 413 (FILE_TOO_LARGE), 415 (UNSUPPORTED_FORMAT), 422 (PARSE_ERROR)
    - HTTP 409 (DOCUMENT_LIMIT_EXCEEDED), 503 (LLM_UNAVAILABLE), 504 (LLM_TIMEOUT)
    - HTTP 404 (SESSION_NOT_FOUND), 400 (NO_DOCUMENTS)
    - _Requirements: 1.4, 1.5, 2.5, 3.6, 3.7, 4.5_

  - [ ]* 9.3 Property-тест: валидация файлов отклоняет недопустимые входные данные
    - **Property 2: Валидация файлов**
    - **Validates: Requirements 1.4, 1.5**
    - `@given` по файлам с неверным расширением или размером > 50 МБ

  - [ ]* 9.4 Property-тест: лимит документов в сессии
    - **Property 10: Лимит документов в сессии**
    - **Validates: Requirements 4.5**
    - Загрузить 10 документов → 11-й возвращает 409

  - [ ]* 9.5 Property-тест: источники содержат обязательные поля
    - **Property 7: Источники содержат обязательные поля**
    - **Validates: Requirements 3.4**
    - Каждый `SourceRef` в ответе имеет непустой `filename` и `page_number >= 1`

  - [ ]* 9.6 Unit-тесты API endpoints
    - Все коды ошибок из таблицы обработки ошибок
    - Успешные сценарии для каждого endpoint
    - _Requirements: 1.1–1.7, 2.1–2.6, 3.1–3.8, 4.1–4.5_

- [ ] 10. Checkpoint — API
  - Запустить `pytest tests/ -v --tb=short`
  - Проверить все HTTP-коды ответов
  - Спросить пользователя, если есть вопросы.

- [ ] 11. Frontend — базовая структура
  - [ ] 11.1 Создать `frontend/app/layout.tsx` — `AppLayout`
    - Двухпанельный layout: `DocumentPanel` (левая) + `ChatPanel` (правая)
    - Responsive breakpoints: мобильный (< 768px) → вертикальный стек
    - _Requirements: 6.1, 6.3_

  - [ ] 11.2 Создать `frontend/lib/api.ts` — API-клиент
    - Функции для всех 9 endpoints с типизацией TypeScript
    - Axios с базовым URL из env, обработка ошибок
    - _Requirements: 3.3, 3.7, 3.8_

- [ ] 12. Frontend — DocumentPanel
  - [ ] 12.1 Создать `frontend/components/DocumentPanel.tsx`
    - Drag-and-drop зона загрузки файлов (нативный input + drag events)
    - Список документов: имя, дата, количество чанков, статус
    - Кнопка удаления документа с подтверждением
    - Чекбоксы выбора активных документов для поиска
    - Валидация на клиенте: формат и размер файла
    - _Requirements: 1.1, 1.4, 1.5, 1.6, 4.1, 4.2, 4.3, 6.4_

- [ ] 13. Frontend — ChatPanel и SourceCard
  - [ ] 13.1 Создать `frontend/components/ChatPanel.tsx`
    - История сообщений с прокруткой вниз
    - Поле ввода + кнопка отправки
    - Индикатор загрузки (spinner) во время ожидания ответа
    - Отображение ошибок: нет документов, таймаут LLM
    - _Requirements: 3.3, 3.5, 3.6, 3.7, 3.8_

  - [ ] 13.2 Создать `frontend/components/SourceCard.tsx`
    - Отображение: имя файла, номер страницы, фрагмент текста
    - Коллапсируемый вид для мобильных
    - _Requirements: 3.4_

- [ ] 14. Frontend — LLMSelector
  - [ ] 14.1 Создать `frontend/components/LLMSelector.tsx`
    - Dropdown со списком моделей из `GET /api/models`
    - Поле ввода API-ключа (тип password, не сохраняется в localStorage)
    - Отображение текущей выбранной модели
    - _Requirements: 2.1, 2.2, 2.4, 2.6_

- [ ] 15. Checkpoint — frontend
  - Проверить responsive layout на 320px и 2560px (DevTools)
  - Убедиться, что API-ключ не попадает в localStorage/sessionStorage
  - Спросить пользователя, если есть вопросы.

- [ ] 16. Интеграция и финальное подключение
  - [ ] 16.1 Подключить управление сессией в `frontend/app/page.tsx`
    - При загрузке страницы: `POST /api/sessions` → сохранить `session_id` в памяти (не localStorage)
    - При закрытии страницы: `DELETE /api/sessions/{id}` через `beforeunload`
    - _Requirements: 7.1, 7.2_

  - [ ] 16.2 Создать `backend/main.py` — точка входа FastAPI
    - Подключить роутер, CORS для frontend, middleware логирования
    - Убедиться, что API-ключи не попадают в логи
    - _Requirements: 7.3, 7.4_

  - [ ]* 16.3 Интеграционные тесты end-to-end
    - Полный сценарий: создать сессию → загрузить документ → запрос → проверить источники → удалить документ → завершить сессию
    - _Requirements: 1.1–1.7, 3.1–3.5, 4.2, 7.1–7.2_

- [ ] 17. Финальный checkpoint
  - Запустить полный набор тестов: `pytest tests/ -v`
  - Проверить, что все property-тесты проходят с `max_examples=100`
  - Убедиться, что нет утечек данных между сессиями
  - Спросить пользователя, если есть вопросы.

---

## Примечания

- Задачи с `*` — опциональные (тесты), можно пропустить для быстрого MVP
- Каждая задача ссылается на конкретные требования для трассируемости
- Property-тесты используют `hypothesis` с `@settings(max_examples=100)`
- API-ключи никогда не логируются и не персистируются
