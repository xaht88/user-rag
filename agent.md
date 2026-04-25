# Project Agent Documentation

## Project Overview

**Name:** RAG Chat Application
**Status:** Active Development (Migration Phase)
**Goal:** Modernize architecture from legacy HTML/JS to Next.js + FastAPI.

## Current Architecture

- **Backend:** Python (FastAPI), `rag_app/backend/main.py`
- **RAG Engine:** `rag_app/backend/rag_engine.py` (Core logic: ChromaDB, Ollama, Embeddings)
- **Frontend:** Next.js (TypeScript, Tailwind CSS), `rag_app/frontend_next/`
- **Vector DB:** ChromaDB (`chroma_db`)
- **LLM:** Ollama (local)

## Active Files

- `rag_app/backend/main.py` - API Entry Point
- `rag_app/backend/rag_engine.py` - RAG Logic
- `rag_app/frontend_next/app/page.tsx` - Main UI
- `rag_app/frontend_next/shared/types.ts` - Type Definitions
- `rag_app/frontend_next/shared/api/client.ts` - API Client

## Deprecated Files (Mark as [DEPRECATED])

- `rag_app/backend/rag_app.py` - [DEPRECATED] Use `main.py`
- `rag_app/backend/static/` - [DEPRECATED] Use Next.js
- `frontend/` - [DEPRECATED] Legacy UI

## Recent Changes

- Fixed `rag_engine.py` (syntax errors, `OllamaClient` implementation).
- Created TypeScript interfaces for frontend.
- Created API client for frontend.

## Next Steps

1. Integrate frontend with real API (remove mocks).
2. Clean up duplicate backend files.
3. Add user stories and analytics.

## Commands

- Run Backend: `uvicorn rag_app.backend.main:app --reload`
- Run Frontend: `cd rag_app/frontend_next && npm run dev`
- Run Tests: `pytest rag_app/backend/tests/`

