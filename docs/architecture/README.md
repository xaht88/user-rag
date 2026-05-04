# Architecture Documentation

## Overview

This directory contains architectural documentation for the RAG Chat Application.

## Documents

| File | Description |
|------|-------------|
| [system-overview.md](./system-overview.md) | Complete system architecture overview |

## Quick Reference

### Technology Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 14, React 18, TypeScript, Tailwind CSS |
| Backend | FastAPI, Python 3.10+, Pydantic |
| Vector DB | ChromaDB |
| LLM | OpenAI, Ollama |
| Testing | Vitest, pytest |

### Ports

- Frontend: `3000`
- Backend: `8000`
- ChromaDB: `8000` (embedded)
- Ollama: `11434`

### Key Components

1. **Next.js Frontend** — User interface and client-side logic
2. **FastAPI Backend** — REST API and business logic
3. **RAG Engine** — Document processing and retrieval
4. **ChromaDB** — Vector storage for embeddings
5. **LLM Providers** — OpenAI and Ollama integration

---

**See also:**
- [API Documentation](../api/README.md)
- [Development Guide](../development/README.md)
- [Deployment Guide](../deployment/README.md)
