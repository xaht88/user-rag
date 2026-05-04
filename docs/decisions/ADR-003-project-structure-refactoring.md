# ADR-003: Project Structure Refactoring

**Status:** Accepted  
**Date:** 2026-05-04  
**Authors:** AI Agent

---

## Context

The project had structural inconsistencies that needed to be addressed:

1. **Duplicate files**: Both `rag_app/backend/main.py` and `rag_app/backend/rag_app.py` existed with overlapping functionality
2. **Inconsistent frontend naming**: Directory named `frontend_next` but using Vite + React (not Next.js)
3. **Duplicate directories in root**: `frontend` and `chroma_db` directories existed in project root alongside `rag_app/`
4. **Documentation mismatch**: Documentation referenced Next.js (port 3000) while actual setup used Vite (port 5173)

## Decision

### 1. Remove Duplicate Files

- **Keep**: `rag_app/backend/main.py` (current implementation)
- **Remove**: `rag_app/backend/rag_app.py` and `rag_app/backend/_rag_app.py` [DEPRECATED]
- **Rationale**: `main.py` contains the current working implementation with mock LLM responses

### 2. Clean Root Directory Structure

- **Remove**: `frontend/` directory (contained design mockups, not actual frontend code)
- **Remove**: `chroma_db/` directory in root (empty, ChromaDB storage is in `rag_app/backend/chroma_db/`)
- **Keep**: `stories/` directory in root (user stories)
- **Keep**: `rag_app/` as the main application directory

### 3. Update Documentation

- Update all references from "Next.js" to "Vite + React"
- Change frontend port from 3000 to 5173
- Update environment variable prefixes from `NEXT_PUBLIC_*` to `VITE_*`
- Add note about frontend technology mismatch in export scripts

### 4. Directory Structure Standardization

```
otus_dz2/
├── rag_app/
│   ├── backend/                    # FastAPI backend
│   │   ├── main.py                 # API entry point
│   │   ├── rag_engine.py           # RAG core logic
│   │   ├── rag/                    # RAG services (deprecated)
│   │   ├── requirements.txt
│   │   ├── .env
│   │   ├── uploads/
│   │   ├── chroma_db/
│   │   ├── static/
│   │   ├── templates/
│   │   └── tests/
│   │
│   └── frontend_next/              # Vite + React frontend
│       ├── app/
│       ├── components/
│       ├── features/
│       ├── shared/
│       ├── package.json
│       ├── tsconfig.json
│       ├── tailwind.config.ts
│       ├── vitest.config.ts
│       ├── vite.config.ts
│       ├── .env.local
│       └── scripts/
│
├── docs/                           # Documentation
├── stories/                        # User stories
├── AGENTS.md
└── [other project files]
```

## Consequences

### Positive

1. **Cleaner structure**: No duplicate files or directories
2. **Accurate documentation**: Documentation now matches actual technology stack
3. **Reduced confusion**: Clear separation between backend and frontend
4. **Consistent naming**: Environment variables follow Vite conventions

### Negative

1. **Breaking changes**: Any external references to removed files/directories will break
2. **Documentation updates**: All documentation must be updated to reflect new structure
3. **Frontend naming**: Directory still named `frontend_next` but uses Vite (potential confusion)

### Future Considerations

1. Consider renaming `frontend_next` to `frontend` or `client` to avoid confusion
2. Add migration guide if this is a breaking change for team members
3. Update CI/CD pipelines to reflect new structure

---

**References:**
- [AGENTS.md](../../AGENTS.md)
- [docs/index.md](./README.md)
- [development/README.md](../development/README.md)

---

**Generated with [Continue](https://continue.dev)**

Co-Authored-By: Continue <noreply@continue.dev>
