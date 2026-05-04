# Tracks — Work Unit Registry

Registry всех work units (фичи, багфиксы, технический долг) с их статусом и метаданными.

---

## 📊 Summary

| Статус | Количество |
|--------|------------|
| 🔄 In Progress | 1 |
| ⏳ Planned | 3 |
| ✅ Completed | 0 |
| 🚫 Blocked | 0 |

**Всего tracks:** 4

---

## 🔴 High Priority

### TD-001: Persistent Session Storage

**Тип:** Technical Debt  
**Статус:** 🔄 In Progress  
**Приоритет:** 🔴 High  
**Assignee:** TBD  
**Created:** 2026-05-04  
**Due:** 2026-05-11

#### Problem Statement
Сессии хранятся в памяти и теряются при перезапуске backend-сервера. Это делает невозможным:
- Продолжение работы после перезапуска
- Горизонтальное масштабирование
- Production deployment

#### Acceptance Criteria
- [ ] Сессии сохраняются в PostgreSQL
- [ ] Данные сессии доступны после перезапуска
- [ ] Изоляция сессий (данные одной сессии недоступны другой)
- [ ] Автоматическая очистка старых сессий (> 30 дней)
- [ ] Unit-тесты для session storage
- [ ] Документация обновлена

#### Technical Approach
1. Создать модель `Session` в SQLAlchemy
2. Добавить миграции Alembic
3. Рефакторинг `session_manager.py` для использования БД
4. Добавить индексы для производительности
5. Настроить автоматическую очистку (Celery beat или cron)

#### Dependencies
- ⏳ TD-003: JWT Authentication (для аутентификации пользователей)

#### Links
- [ADR-002: Session Management Strategy](../docs/decisions/ADR-002-session-management.md)
- [Track directory](./tracks/TD-001-persistent-sessions/)

---

### TD-002: Real LLM Integration

**Тип:** Technical Debt  
**Статус:** ⏳ Planned  
**Приоритет:** 🔴 High  
**Assignee:** TBD  
**Created:** 2026-05-04  
**Due:** 2026-05-18

#### Problem Statement
Система использует mock-ответы вместо реальных LLM. Это делает невозможным:
- Тестирование реальной производительности
- Валидацию качества ответов
- Production deployment

#### Acceptance Criteria
- [ ] Интеграция с OpenAI API (GPT-4o, GPT-4o-mini)
- [ ] Интеграция с Ollama (локальные модели)
- [ ] Обработка ошибок API (таймауты, ошибки авторизации)
- [ ] Поддержка пользовательского API-ключа
- [ ] Логирование запросов/ответов
- [ ] Unit-тесты с моками
- [ ] Документация конфигурации

#### Technical Approach
1. Создать абстракцию `LLMConnector`
2. Реализовать `OpenAIConnector` и `OllamaConnector`
3. Добавить конфигурацию через environment variables
4. Реализовать кэширование ответов (Redis)
5. Добавить rate limiting

#### Dependencies
- None

#### Links
- [Track directory](./tracks/TD-002-real-llm-integration/)

---

### TD-003: JWT Authentication

**Тип:** Technical Debt  
**Статус:** ⏳ Planned  
**Приоритет:** 🔴 High  
**Assignee:** TBD  
**Created:** 2026-05-04  
**Due:** 2026-05-25

#### Problem Statement
Отсутствует аутентификация и авторизация. Это создаёт риски:
- Неавторизованный доступ к API
- Отсутствие аудита действий пользователей
- Невозможность multi-tenancy

#### Acceptance Criteria
- [ ] JWT token-based authentication
- [ ] Регистрация/вход пользователей
- [ ] Refresh token mechanism
- [ ] Password hashing (bcrypt)
- [ ] Role-based access control (admin, user)
- [ ] Protected API endpoints
- [ ] Frontend integration (login form, token storage)
- [ ] Security tests

#### Technical Approach
1. Создать модель `User` в SQLAlchemy
2. Реализовать endpoints `/auth/register`, `/auth/login`
3. Настроить JWT (access + refresh tokens)
4. Добавить decorators для защиты endpoints
5. Реализовать frontend login flow
6. Добавить OAuth2 (Google, GitHub) - optional

#### Dependencies
- ⏳ TD-001: Persistent Session Storage (для хранения пользователей)

#### Links
- [Security Guidelines](../docs/instructions/security.md)
- [Track directory](./tracks/TD-003-jwt-authentication/)

---

## 🟡 Medium Priority

### TD-004: API Rate Limiting

**Тип:** Technical Debt  
**Статус:** ⏳ Planned  
**Приоритет:** 🟡 Medium  
**Assignee:** TBD  
**Created:** 2026-05-04  
**Due:** 2026-06-01

#### Problem Statement
API не имеет rate limiting, что делает его уязвимым к:
- DDoS атакам
- Abuse (бесконечные запросы)
- Resource exhaustion

#### Acceptance Criteria
- [ ] Rate limiting per IP address
- [ ] Rate limiting per user (after auth)
- [ ] Configurable limits (different for endpoints)
- [ ] Proper HTTP 429 responses
- [ ] Rate limit headers in responses
- [ ] Redis backend for distributed rate limiting
- [ ] Documentation of limits

#### Technical Approach
1. Использовать `slowapi` для FastAPI
2. Настроить Redis для shared state
3. Определить лимиты для разных endpoints
4. Добавить middleware для логирования
5. Реализовать whitelist для trusted IPs

#### Dependencies
- ⏳ TD-003: JWT Authentication (для user-based limiting)

#### Links
- [Track directory](./tracks/TD-004-api-rate-limiting/)

---

## 🟢 Low Priority

### FE-001: Frontend Unit Test Coverage

**Тип:** Quality  
**Статус:** ⏳ Planned  
**Приоритет:** 🟢 Low  
**Assignee:** TBD  
**Created:** 2026-05-04  
**Due:** 2026-06-15

#### Problem Statement
Frontend не имеет достаточного покрытия unit-тестами.

#### Acceptance Criteria
- [ ] Coverage > 80% для React components
- [ ] Tests для всех critical paths
- [ ] Mock API calls с MSW
- [ ] CI integration

#### Links
- [Track directory](./tracks/FE-001-frontend-unit-test-coverage/)

---

## 📋 Track Directory Structure

Каждый track имеет собственную директорию:

```
conductor/tracks/<TRACK-ID>-<slug>/
├── spec.md              # Detailed specification
├── plan.md              # Implementation plan
├── metadata.json        # Track metadata (JSON)
└── index.md             # Track overview
```

### Example: TD-001

```bash
conductor/tracks/TD-001-persistent-sessions/
├── spec.md
├── plan.md
├── metadata.json
└── index.md
```

---

## 🔄 Track Lifecycle

### Status Definitions

| Статус | Описание |
|--------|----------|
| ⏳ **Planned** | Track создан, но не начался |
| 🔄 **In Progress** | Работа активно ведётся |
| 🚧 **In Review** | PR создан, ждёт ревью |
| ✅ **Completed** | Задача завершена, merged |
| 🚫 **Blocked** | Блокирована зависимостями |
| 🗑️ **Archived** | Задача отменена/архивирована |

### Status Transitions

```
Planned → In Progress → In Review → Completed
   ↑              ↓           ↓
   └──────────────┴───────────┘
         Blocked / Archived
```

---

## 📊 Track Metrics

### By Priority

| Приоритет | В работе | Запланировано | Завершено |
|-----------|----------|---------------|-----------|
| 🔴 High | 1 | 2 | 0 |
| 🟡 Medium | 0 | 1 | 0 |
| 🟢 Low | 0 | 1 | 0 |

### By Type

| Тип | В работе | Запланировано | Завершено |
|-----|----------|---------------|-----------|
| Technical Debt | 1 | 3 | 0 |
| Feature | 0 | 0 | 0 |
| Bugfix | 0 | 0 | 0 |
| Quality | 0 | 1 | 0 |

---

## 📝 Creating New Tracks

### Template

```markdown
# TRACK-ID: Title

**Тип:** [Technical Debt | Feature | Bugfix | Quality]  
**Статус:** ⏳ Planned  
**Приоритет:** 🔴 High | 🟡 Medium | 🟢 Low  
**Assignee:** [Name]  
**Created:** [Date]  
**Due:** [Date]

## Problem Statement
[Описание проблемы]

## Acceptance Criteria
- [ ] Критерий 1
- [ ] Критерий 2
- [ ] Критерий 3

## Technical Approach
[Описание подхода]

## Dependencies
- [TRACK-ID]: [Dependency title]

## Links
- [Track directory](./tracks/TRACK-ID-slug/)
```

### Steps to Create Track

1. Создать директорию: `conductor/tracks/TRACK-ID-slug/`
2. Создать `spec.md` с детальным описанием
3. Создать `plan.md` с планом реализации
4. Создать `metadata.json` с метаданными
5. Добавить запись в `tracks.md`
6. Создать feature branch в git

---

**Последнее обновление:** 2026-05-04  
**Версия registry:** 1.0.0
