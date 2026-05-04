# Development Guide

## Overview

This directory contains development documentation for the RAG Chat Application.

## Documents

| File | Description |
|------|-------------|
| [setup.md](./setup.md) | Complete development environment setup guide |

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- Git
- Docker (optional)

### 1. Clone Repository

```bash
git clone <repository-url>
cd otus_dz2
```

### 2. Setup Backend

```bash
cd rag_app/backend

# Create virtual environment
python -m venv .venv

# Activate
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
touch .env
```

Add to `.env`:
```env
OPENAI_API_KEY=your_key_here
OLLAMA_BASE_URL=http://localhost:11434
```

### 3. Setup Frontend

```bash
cd rag_app/frontend_next

# Install dependencies
npm install

# Create .env.local
touch .env.local
```

Add to `.env.local`:
```env
VITE_API_URL=http://localhost:8000
```

### 4. Run Application

**Terminal 1 - Backend:**
```bash
cd rag_app/backend
uvicorn main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd rag_app/frontend_next
npm run dev  # Runs on http://localhost:5173
```

Access:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## Development Workflow

### Running Tests

**Backend:**
```bash
cd rag_app/backend
pytest tests/ -v
```

**Frontend:**
```bash
cd rag_app/frontend_next
npm run test
```

### Linting

**Backend:**
```bash
pip install black flake8 isort
black rag_app/backend/
flake8 rag_app/backend/
```

**Frontend:**
```bash
cd rag_app/frontend_next
npm run lint
```

### Building for Production

**Export Frontend for Backend:**
```bash
cd rag_app/frontend_next
npm run export:backend
```

This exports static assets to `rag_app/backend/static/next` and template to `rag_app/backend/templates/next_index.html`.

---

## Environment Variables

### Backend (.env)

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | - |
| `OLLAMA_BASE_URL` | Ollama server URL | `http://localhost:11434` |
| `PORT` | Backend port | `8000` |
| `DEBUG` | Debug mode | `false` |

### Frontend (.env.local)

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API URL | `http://localhost:8000` |
| `VITE_OPENAI_API_KEY` | OpenAI key (optional) | - |
| `VITE_OLLAMA_BASE_URL` | Ollama URL | `http://localhost:11434` |

---

## Project Structure

```
otus_dz2/
├── rag_app/
│   ├── backend/                    # FastAPI backend
│   │   ├── main.py                 # API entry point
│   │   ├── rag_engine.py           # RAG core logic
│   │   ├── requirements.txt        # Python deps
│   │   ├── uploads/                # Uploaded files
│   │   ├── chroma_db/              # ChromaDB storage
│   │   ├── static/                 # Static assets
│   │   ├── templates/              # HTML templates
│   │   └── tests/                  # Backend tests
│   │
│   └── frontend_next/              # Vite + React frontend
│       ├── app/                    # React pages
│       ├── components/             # React components
│       ├── features/               # Feature modules
│       ├── shared/                 # Shared utilities
│       ├── package.json            # Node deps
│       ├── tsconfig.json           # TypeScript config
│       ├── tailwind.config.ts      # Tailwind config
│       ├── vitest.config.ts        # Test config
│       ├── vite.config.ts          # Vite config
│       └── scripts/                # Build scripts
│
├── docs/                           # Documentation
├── stories/                        # User stories
└── AGENTS.md                       # Agent instructions
```

---

## Common Tasks

### Adding a New API Endpoint

1. Create route handler in `rag_app/backend/main.py`
2. Add Pydantic models for request/response
3. Update OpenAPI documentation
4. Add tests
5. Document in API README

### Adding a New Component

1. Create component in `rag_app/frontend_next/components/`
2. Add TypeScript types in `rag_app/frontend_next/shared/types.ts`
3. Write tests in `*.test.tsx`
4. Update component documentation

### Running Specific Tests

**Backend:**
```bash
pytest tests/test_file.py::test_function_name -v
```

**Frontend:**
```bash
npm run test -- components/component-name.test.tsx
```

---

## Troubleshooting

See [setup.md](./setup.md) for detailed troubleshooting guide.

---

**See also:**
- [API Documentation](../api/README.md)
- [Architecture](../architecture/README.md)
- [Deployment](../deployment/README.md)
