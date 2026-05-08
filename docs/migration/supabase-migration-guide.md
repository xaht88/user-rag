# Миграция на Supabase

## Предварительные требования

- Аккаунт на [Supabase.com](https://supabase.com)
- Установленный [Supabase CLI](https://supabase.com/docs/guides/cli/getting-started)
- Python 3.10+
- pip или poetry для управления зависимостями

## Шаг 1: Создание проекта в Supabase

1. Зарегистрируйтесь на [supabase.com](https://supabase.com)
2. Создайте новый проект:
   - Нажмите "New Project"
   - Введите имя проекта: `rag-chat-app`
   - Выберите базу данных: PostgreSQL
   - Установите сильный пароль для суперпользователя
   - Выберите регион (ближайший к вам)
   - Нажмите "Create new project"

3. После создания проекта сохраните:
   - **Project URL**: `https://xxxxx.supabase.co`
   - **API Keys**:
     - `anon` / `public` key (для клиента)
     - `service_role` key (для сервера, храните в секретах!)

## Шаг 2: Настройка окружения

Обновите файл `rag_app/backend/.env.local`:

```bash
# Supabase Configuration
SUPABASE_URL=https://ibnzhdgjfihhjvbfimpu.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here
```

**Важно:** Никогда не коммитьте `SUPABASE_SERVICE_ROLE_KEY` в репозиторий!

## Шаг 3: Установка зависимостей

```bash
cd rag_app/backend

# Установите supabase клиент
pip install supabase

# Обновите requirements.txt
pip freeze > requirements.txt
```

## Шаг 4: Применение схемы базы данных

### Вариант A: Через Supabase Dashboard (рекомендуется для начала)

1. Откройте [Supabase Dashboard](https://supabase.com/dashboard)
2. Выберите ваш проект
3. Перейдите в **SQL Editor**
4. Скопируйте содержимое файла `migrations/001_initial_supabase_schema.sql`
5. Нажмите "Run" для выполнения миграции

### Вариант B: Через Supabase CLI

```bash
# Установите Supabase CLI (если не установлен)
npm install -g supabase

# Войдите в Supabase
supabase login

# Инициализируйте проект (если еще не сделано)
supabase init

# Примените миграцию
supabase db push
```

### Вариант C: Через psql

```bash
# Получите connection string из Dashboard
# Settings > Database > Connection string > URI

psql "postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres" < migrations/001_initial_supabase_schema.sql
```

## Шаг 5: Настройка хранилища (Storage)

1. В Supabase Dashboard перейдите в **Storage**
2. Создайте новый bucket:
   - Name: `documents`
   - Public: **false** (private bucket)
   - Row Level Security: **enabled**

3. Bucket должен быть создан автоматически миграцией, но проверьте политики доступа:
   - Перейдите в **Policies** для bucket `documents`
   - Убедитесь, что созданы политики для upload/download/delete

## Шаг 6: Проверка работы

### Тестирование через Supabase Dashboard

1. Перейдите в **Table Editor**
2. Проверьте создание таблиц:
   - `profiles`
   - `sessions`
   - `messages`
   - `documents`
   - `document_chunks`

3. Проверьте индексы:
   - Перейдите в **Indexes** для каждой таблицы
   - Убедитесь, что создан индекс `idx_document_chunks_embedding` с HNSW

### Тестирование API

Запустите backend:

```bash
cd rag_app/backend
uvicorn main:app --reload --port 8000
```

Протестируйте endpoints:

```bash
# Регистрация пользователя
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123", "full_name": "Test User"}'

# Вход пользователя
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'

# Создание сессии (с токеном)
curl -X POST http://localhost:8000/api/sessions \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Шаг 7: Миграция существующих данных (опционально)

Если у вас есть данные в ChromaDB, которые нужно перенести:

### Экспорт из ChromaDB

```python
# scripts/export_chroma.py
import chromadb
import json

client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_collection(name="documents")

# Экспорт данных
data = collection.get(include=["documents", "metadatas", "embeddings"])

# Сохранение в JSON
with open("chroma_export.json", "w") as f:
    json.dump(data, f, default=str)
```

### Импорт в Supabase

```python
# scripts/import_supabase.py
from supabase import create_client
import json

supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# Загрузка данных
with open("chroma_export.json") as f:
    data = json.load(f)

# Импорт чанков
chunks = []
for i in range(len(data["documents"])):
    chunks.append({
        "document_id": data["metadatas"][i].get("doc_id", "unknown"),
        "chunk_index": i,
        "content": data["documents"][i],
        "embedding": data["embeddings"][i]
    })

# Вставка в БД
supabase.table("document_chunks").insert(chunks).execute()
```

## Шаг 8: Обновление frontend

Frontend нужно обновить для работы с аутентификацией:

1. Установите supabase клиент для React:
   ```bash
   cd rag_app/frontend_next
   npm install @supabase/supabase-js
   ```

2. Обновите `.env.local`:
   ```env
   NEXT_PUBLIC_SUPABASE_URL=https://ibnzhdgjfihhjvbfimpu.supabase.co
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key_here
   ```

3. Обновите API вызовы для отправки JWT токенов

## Troubleshooting

### Ошибка "relation does not exist"

**Причина:** Миграция не была применена

**Решение:**
```bash
supabase db push
# или через Dashboard SQL Editor
```

### Ошибка "permission denied"

**Причина:** RLS политики блокируют доступ

**Решение:**
1. Проверьте, что RLS включен на всех таблицах
2. Убедитесь, что созданы все политики
3. Для тестирования временно отключите RLS:
   ```sql
   ALTER TABLE public.sessions DISABLE ROW LEVEL SECURITY;
   ```

### Ошибка "invalid token"

**Причина:** Токен истёк или невалиден

**Решение:**
1. Проверьте expiry time токена (обычно 1 час)
2. Реализуйте refresh token механизм
3. Убедитесь, что отправляете токен в заголовке `Authorization: Bearer <token>`

### Ошибка "bucket not found"

**Причина:** Bucket не создан

**Решение:**
```sql
INSERT INTO storage.buckets (id, name, public)
VALUES ('documents', 'documents', false)
ON CONFLICT (id) DO NOTHING;
```

## Следующие шаги

1. ✅ База данных настроена
2. ✅ Хранилище настроено
3. ✅ API с аутентификацией работает
4. ⏳ Реализовать парсинг документов и эмбеддинги
5. ⏳ Интегрировать реальный LLM (OpenAI/Ollama)
6. ⏳ Обновить frontend для работы с аутентификацией
7. ⏳ Настроить CI/CD для автоматического применения миграций

## Дополнительные ресурсы

- [Supabase Documentation](https://supabase.com/docs)
- [pg_vector Documentation](https://github.com/pgvector/pgvector)
- [Row Level Security Guide](https://supabase.com/docs/guides/auth/row-level-security)
- [Storage Guide](https://supabase.com/docs/guides/storage)

---

**Generated with [Continue](https://continue.dev)**

Co-Authored-By: Continue <noreply@continue.dev>
