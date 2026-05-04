# Tech Stack — RAG Chat Application

## 🖥️ Primary Languages & Frameworks

| Слой | Технология | Версия | Описание |
|------|------------|--------|----------|
| **Frontend** | Vite | 5.0.8 | Build tool & dev server |
| **Frontend** | React | 18.2.0 | UI library |
| **Frontend** | TypeScript | 5.3.3 | Type system |
| **Frontend** | Tailwind CSS | 3.3.5 | Utility-first CSS framework |
| **Backend** | FastAPI | 0.104.1 | Modern REST API framework |
| **Backend** | Python | 3.10+ | Programming language |
| **Backend** | Pydantic | 2.5.2 | Data validation |
| **Backend** | Uvicorn | 0.24.0 | ASGI server |

---

## 🤖 AI & LLM Dependencies

| Библиотека | Версия | Назначение | Конфигурация |
|------------|--------|------------|--------------|
| **langchain** | 0.1.0 | LLM orchestration | `langchain` |
| **langchain-community** | 0.0.13 | Community integrations | `langchain_community` |
| **langchain-core** | 0.1.9 | Core abstractions | `langchain_core` |
| **chromadb** | 0.4.22 | Vector database | `chromadb` |
| **ollama** | 0.1.6 | Local LLM server | `ollama` |
| **openai** | 1.3.0 | OpenAI API client | `openai` |

**Конфигурация LLM:**
- **OpenAI:** GPT-4o, GPT-4o-mini (API key required)
- **Ollama:** Llama2, Mistral (local server on port 11434)

---

## 📄 Document Processing

| Библиотека | Версия | Поддерживаемые форматы |
|------------|--------|------------------------|
| **pymupdf** | 1.23.8 | PDF |
| **python-docx** | 0.8.11 | DOCX |
| **pypdf** | 3.17.4 | PDF (additional) |

**Параметры обработки:**
- Chunk size: 512 токенов
- Chunk overlap: 50 токенов
- Max file size: 50 MB

---

## 🧪 Testing Frameworks

| Слой | Инструмент | Версия | Назначение |
|------|------------|--------|------------|
| **Frontend Unit** | Vitest | 1.1.0 | Unit tests (React components) |
| **Frontend E2E** | Playwright | 1.59.1 | End-to-end tests |
| **Backend Unit** | pytest | - | Unit & integration tests |

**Testing Libraries:**
- `@testing-library/react` 14.1.2
- `@testing-library/jest-dom` 6.1.5

---

## 🛠️ Development Tools

| Инструмент | Версия | Назначение |
|------------|--------|------------|
| **ESLint** | 8.55.0 | Code linting (TypeScript/JSX) |
| **TypeScript** | 5.3.3 | Type checking |
| **dotenv** | 1.0.0 | Environment variables |
| **pydantic-settings** | 2.1.0 | Pydantic config management |

---

## 🌐 Infrastructure & Deployment

### Development Environment
```
┌─────────────────┐     ┌─────────────────┐
│   Frontend      │────▶│    Backend      │
│   (Port 5173)   │     │   (Port 8000)   │
└─────────────────┘     └────────┬────────┘
                                 │
                         ┌───────┴────────┐
                         │   ChromaDB     │
                         │   (Local)      │
                         └────────────────┘
```

### Production (Planned)
```
┌─────────────────┐     ┌─────────────────┐
│   CDN / Static  │────▶│   Kubernetes    │
│   Hosting       │     │   (Backend)     │
└─────────────────┘     └────────┬────────┘
                                 │
                         ┌───────┴────────┐
                         │                │
                  ┌──────▼──────┐   ┌────▼────┐
                  │ PostgreSQL  │   │ChromaDB │
                  │(Sessions)   │   │(Vectors)│
                  └─────────────┘   └─────────┘
```

**Требования инфраструктуры:**
- **Database:** PostgreSQL 15+ (sessions), ChromaDB 0.4+ (vectors)
- **Cache:** Redis 7+ (optional, for response caching)
- **Containerization:** Docker 24+, Docker Compose
- **Orchestration:** Kubernetes 1.28+ (planned)

---

## 📦 Dependency Management

### Backend (Python)
**Файл:** `rag_app/backend/requirements.txt`

```txt
# Core Web Framework
fastapi==0.104.1
uvicorn==0.24.0
python-multipart==0.0.6

# RAG & AI
langchain==0.1.0
langchain-community==0.0.13
langchain-core==0.1.9
chromadb==0.4.22
ollama==0.1.6
openai==1.3.0

# Document Parsing
pymupdf==1.23.8
python-docx==0.8.11
pypdf==3.17.4

# Utilities
pydantic==2.5.2
pydantic-settings==2.1.0
python-dotenv==1.0.0
```

### Frontend (JavaScript/TypeScript)
**Файл:** `rag_app/frontend_next/package.json`

```json
{
  "dependencies": {
    "axios": "^1.6.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.32",
    "tailwindcss": "^3.3.5"
  },
  "devDependencies": {
    "@playwright/test": "^1.59.1",
    "@testing-library/jest-dom": "^6.1.5",
    "@testing-library/react": "^14.1.2",
    "@types/axios": "^0.14.0",
    "@types/node": "^20.10.6",
    "@types/react": "^18.2.46",
    "@types/react-dom": "^18.2.18",
    "@typescript-eslint/eslint-plugin": "^6.14.0",
    "@typescript-eslint/parser": "^6.14.0",
    "@vitejs/plugin-react": "^4.2.1",
    "eslint": "^8.55.0",
    "typescript": "^5.3.3",
    "vite": "^5.0.8",
    "vitest": "^1.1.0"
  }
}
```

---

## 🔐 Security Dependencies

| Зависимость | Статус | Примечание |
|-------------|--------|------------|
| **JWT Authentication** | ⏳ Planned | `pyjwt` not yet added |
| **Rate Limiting** | ⏳ Planned | `slowapi` not yet added |
| **HTTPS** | ⚠️ Planned | Nginx/Apache reverse proxy needed |

---

## 📋 Version Compatibility Matrix

| Компонент | Минимальная версия | Рекомендованная | Совместимость |
|-----------|-------------------|-----------------|---------------|
| Python | 3.10 | 3.11 | ✅ |
| Node.js | 18 | 20 LTS | ✅ |
| FastAPI | 0.100 | 0.104 | ✅ |
| React | 18 | 18.2 | ✅ |
| ChromaDB | 0.4 | 0.4.22 | ✅ |

---

## 🔄 Dependency Update Policy

### Update Frequency
- **Critical security patches:** Immediate
- **Minor versions:** Monthly review
- **Major versions:** Quarterly assessment

### Update Process
1. Check for security vulnerabilities (`pip audit`, `npm audit`)
2. Review changelog for breaking changes
3. Update `requirements.txt` / `package.json`
4. Update `conductor/tech-stack.md`
5. Run full test suite
6. Commit with message: `chore: update [dependency] to [version]`

---

## 📝 Configuration Requirements

### Environment Variables (Backend)
```bash
# OpenAI API
OPENAI_API_KEY=your_api_key_here

# Ollama (local)
OLLAMA_BASE_URL=http://localhost:11434

# ChromaDB
CHROMA_PERSIST_DIR=./chroma_db

# Server
PORT=8000
DEBUG=true
```

### Environment Variables (Frontend)
```bash
# API Base URL
VITE_API_BASE_URL=http://localhost:8000

# Feature Flags
VITE_ENABLE_MOCK_RESPONSES=false
```

---

**Последнее обновление:** 2026-05-04  
**Версия стека:** 1.0.0
