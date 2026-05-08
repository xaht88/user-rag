# ADR-002: Миграция на Supabase

## Status
Accepted

## Date
2026-05-06

## Context
Текущая архитектура использует ChromaDB для векторного поиска и in-memory хранение сессий, что не подходит для production:
- Данные теряются при перезапуске сервера
- Нет аутентификации и авторизации
- Нет автоматических бэкапов
- Ограниченная масштабируемость

## Decision
Мигрировать на Supabase с PostgreSQL + pg_vector + Auth + Storage.

### Архитектурные изменения:
1. **ChromaDB → PostgreSQL + pg_vector**: Векторный поиск через встроенное расширение
2. **In-memory sessions → PostgreSQL таблицы**: Persistent хранение сессий, сообщений, документов
3. **Локальные файлы → Supabase Storage**: S3-compatible хранилище с RLS
4. **No Auth → Supabase Auth**: JWT аутентификация с Row Level Security

### Технологический стек:
- **Database**: PostgreSQL 15+ с расширением `pg_vector`
- **Auth**: Supabase Auth (JWT, OAuth providers)
- **Storage**: Supabase Storage (S3-compatible)
- **Vector Search**: pg_vector с индексом HNSW для cosine similarity

## Alternatives Considered

### Neon + pgvector
**Pros:**
- Serverless PostgreSQL
- Автоматическое масштабирование
- Хорошая интеграция с pg_vector

**Cons:**
- Меньшая экосистема инструментов
- Ограниченные возможности storage
- Нет встроенного auth

**Rejected:** Не хватает full-stack решения (auth + storage)

### AWS RDS + pgvector + Cognito + S3
**Pros:**
- Полный контроль над инфраструктурой
- Гибкая настройка

**Cons:**
- Высокий operational overhead
- Требуется настройка каждой услуги отдельно
- Сложнее в поддержке
- Нет встроенной интеграции между сервисами

**Rejected:** Избыточная сложность для проекта

### Firebase Firestore + Vector Search
**Pros:**
- Хорошая документация
- Встроенная аутентификация

**Cons:**
- Ограниченная поддержка векторного поиска
- Vendor lock-in
- Дороже при больших объемах данных

**Rejected:** Недостаточная поддержка векторных операций

## Implementation Plan

### Phase 1: Подготовка (Task 1) ✅ ЗАВЕРШЕНО
- [x] Создать проект в Supabase (ibnzhdgjfihhjvbfimpu)
- [x] Настроить переменные окружения (.env.local)
- [x] Установить зависимости

### Phase 2: База данных (Task 2) ✅ ЗАВЕРШЕНО
- [x] Создать миграцию с vector extension
- [x] Применить схему БД (migration 001_initial_supabase_schema_v2)
- [x] Настроить RLS политики (все таблицы защищены)
- [x] Создать хранимые функции (search_document_chunks, get_session_stats, get_user_stats)

### Phase 3: Векторный поиск (Task 3)
- [x] Реализовать VectorStoreService (файл создан)
- [ ] Обновить RAG Engine (требует реальной LLM интеграции)
- [ ] Мигрировать данные из ChromaDB

### Phase 4: Аутентификация (Task 4) ✅ ЗАВЕРШЕНО
- [x] Создать AuthService (полная реализация)
- [x] Обновить FastAPI middleware (CORS настроен)
- [x] Добавить защиту endpoints (get_current_user dependency)

## Consequences

### Positive:
- ✅ Production-ready архитектура
- ✅ Автоматические бэкапы (ежечасно)
- ✅ Встроенная аутентификация и авторизация
- ✅ Масштабируемость до millions of rows
- ✅ Векторный поиск через pg_vector (аналогичен ChromaDB)
- ✅ Row Level Security для изоляции данных пользователей
- ✅ Хранение файлов в облаке с автоматическим CDN

### Negative:
- ⚠️ Зависимость от внешнего провайдера (vendor lock-in)
- ⚠️ Cost при росте использования (free tier: 500MB DB, 1GB storage)
- ⚠️ Требуется миграция существующих данных
- ⚠️ Изменение API для работы с JWT токенами

### Mitigation:
- Использовать абстракцию для векторного хранилища (легко переключиться на другой провайдер)
- Мониторить использование и настроить алерты при приближении к лимитам
- Создать скрипты миграции для экспорта/импорта данных
- Документировать все изменения API

## Monitoring & Metrics

### Ключевые метрики для отслеживания:
- **Database size**: < 500MB (free tier limit)
- **Storage usage**: < 1GB (free tier limit)
- **Bandwidth**: < 2GB/month (free tier limit)
- **Auth requests**: < 50,000/month (free tier limit)

### Alert thresholds:
- Database size > 400MB → alert
- Storage > 800MB → alert
- Bandwidth > 1.5GB → alert

## References
- [Supabase Documentation](https://supabase.com/docs)
- [pg_vector Documentation](https://github.com/pgvector/pgvector)
- [Supabase Auth](https://supabase.com/docs/guides/auth)
- [Row Level Security](https://supabase.com/docs/guides/auth/row-level-security)

---

**Generated with [Continue](https://continue.dev)**

Co-Authored-By: Continue <noreply@continue.dev>
