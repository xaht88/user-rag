# Conductor — Project Context Hub

Централизованный хаб проектного контекста для RAG Chat Application.

## 📚 Артефакты контекста

| Документ | Описание | Ссылка |
|----------|----------|--------|
| **Product** | Продуктовое видение, цели, функции | [product.md](./product.md) |
| **Tech Stack** | Технологический стек, зависимости | [tech-stack.md](./tech-stack.md) |
| **Workflow** | Процессы разработки, quality gates | [workflow.md](./workflow.md) |
| **Tracks** | Registry работ и задач | [tracks.md](./tracks.md) |

## 🎯 Product Context

**Продукт:** RAG Chat Application  
**Описание:** Полнофункциональное веб-приложение для работы с документами через диалоговый интерфейс с использованием Retrieval-Augmented Generation (RAG) архитектуры.  
**Целевая аудитория:** Аналитики, юристы, исследователи, разработчики.

👉 Подробнее: [product.md](./product.md)

## 🛠️ Tech Stack

**Frontend:** Vite 5.0.8, React 18, TypeScript 5.3.3, Tailwind CSS 3.3.5  
**Backend:** FastAPI 0.104.1, Python 3.10+, Pydantic 2.5.2  
**Vector DB:** ChromaDB 0.4.22  
**LLM:** OpenAI API, Ollama  
**Testing:** Vitest, Playwright, pytest

👉 Подробнее: [tech-stack.md](./tech-stack.md)

## ⚙️ Workflow

**Методология:** Context-Driven Development  
**Git Flow:** Feature branches, PR-based workflow  
**Code Quality:** ESLint, Prettier, type checking  
**Testing:** Unit tests (Vitest/pytest), E2E tests (Playwright)

👉 Подробнее: [workflow.md](./workflow.md)

## 📋 Active Tracks

| Track ID | Название | Статус | Приоритет |
|----------|----------|--------|-----------|
| TD-001 | Persistent Session Storage | 🔄 In Progress | 🔴 High |
| TD-002 | Real LLM Integration | ⏳ Planned | 🔴 High |
| TD-003 | JWT Authentication | ⏳ Planned | 🔴 High |
| TD-004 | API Rate Limiting | ⏳ Planned | 🟡 Medium |

👉 Подробнее: [tracks.md](./tracks.md)

## 📖 Code Styleguides

| Язык | Документ |
|------|----------|
| Python | [code_styleguides/python.md](./code_styleguides/python.md) |
| TypeScript | [code_styleguides/typescript.md](./code_styleguides/typescript.md) |

## 🔗 Ссылки

- [Документация проекта](../docs/)
- [Architecture Decision Records](../docs/decisions/)
- [User Stories](../stories/)
- [Technical Specification](../technical_specification.md)

---

**Последнее обновление:** 2026-05-04  
**Версия контекста:** 1.0.0
