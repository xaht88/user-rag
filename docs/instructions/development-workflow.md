# Development Workflow

## Overview

Standard development workflow for efficient collaboration and code quality.

## Setup

### Prerequisites

- **Backend:** Python 3.10+, pip
- **Frontend:** Node.js 18+, npm 9+
- **Testing:** Playwright (for E2E tests)

### Initial Setup

```bash
# Clone repository
git clone <repo-url>
cd otus_dz2

# Setup backend
cd rag_app/backend
python -m venv .venv
.venv\Scripts\activate  # Windows
# or source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt

# Setup frontend
cd ../frontend_next
npm install
```

## Development Environment

### Running Services

```bash
# Terminal 1: Backend
cd rag_app/backend
uvicorn main:app --reload --port 8000

# Terminal 2: Frontend
cd rag_app/frontend_next
npm run dev  # Runs on http://localhost:5173
```

### Environment Variables

**Backend (.env):**
```env
OPENAI_API_KEY=your_openai_api_key
OLLAMA_BASE_URL=http://localhost:11434
PORT=8000
DEBUG=true
```

**Frontend (.env.local):**
```env
VITE_API_URL=http://localhost:8000
VITE_OPENAI_API_KEY=your_openai_api_key
VITE_OLLAMA_BASE_URL=http://localhost:11434
```

## Development Process

### 1. Create Feature Branch

```bash
git checkout main
git pull origin main
git checkout -b feature/your-feature-name
```

### 2. Implement Feature

Follow these steps:

1. **Write tests first** (TDD approach)
2. **Implement the feature**
3. **Run tests** to verify implementation
4. **Update documentation** if needed

### 3. Code Quality Checks

```bash
# Frontend
npm run lint
npm run format

# Backend
black rag_app/backend/
flake8 rag_app/backend/
isort rag_app/backend/
```

### 4. Run Tests

```bash
# Frontend unit tests
npm run test

# Frontend E2E tests
npx playwright test

# Backend tests
pytest rag_app/backend/tests/ -v
```

### 5. Commit Changes

```bash
git add .
git commit -m "feat: implement your feature"
```

### 6. Update from Main

```bash
git fetch origin
git rebase origin/main
```

### 7. Push and Create PR

```bash
git push -u origin feature/your-feature-name
```

## Testing Workflow

### Unit Tests

```bash
# Frontend
npm run test

# Backend
pytest rag_app/backend/tests/ -v
```

### Integration Tests

```bash
# Start services
cd rag_app/backend && uvicorn main:app --reload &
cd rag_app/frontend_next && npm run dev &

# Run tests
npx playwright test
```

### E2E Tests

```bash
# Run all tests
npx playwright test

# Run specific test
npx playwright test smoke-test.spec.ts

# Generate HTML report
npx playwright test --reporter=html
npx playwright show-report
```

## Build and Deployment

### Frontend Export for Backend

```bash
cd rag_app/frontend_next
npm run export:backend
```

This exports static assets to `rag_app/backend/static/next` and template to `rag_app/backend/templates/next_index.html`.

### Production Build

```bash
# Backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000

# Frontend (if using standalone)
npm run build
npm run preview
```

## Debugging

### Frontend Debugging

```bash
# Add debugger statements
console.log('Debug:', variable);

# Use browser DevTools
# - Network tab for API calls
# - Console for logs
# - Sources for breakpoints
```

### Backend Debugging

```python
# Add debug prints
import logging
logger = logging.getLogger(__name__)
logger.debug(f"Debug: {variable}")

# Use pdb
import pdb; pdb.set_trace()

# Enable FastAPI debug mode
uvicorn main:app --reload --log-level debug
```

## Common Tasks

### Adding a New API Endpoint

1. Create Pydantic models for request/response
2. Add route handler in `rag_app/backend/main.py`
3. Add service method in appropriate service file
4. Write tests
5. Update API documentation

### Adding a New Component

1. Create component in `rag_app/frontend_next/components/`
2. Add TypeScript types in `rag_app/frontend_next/shared/types.ts`
3. Write tests in `*.test.tsx`
4. Update component documentation

### Running Specific Tests

```bash
# Backend
pytest rag_app/backend/tests/test_file.py::test_function_name -v

# Frontend
npm run test -- components/component-name.test.tsx
```

## Best Practices

1. **Write tests before implementation** (TDD)
2. **Keep commits atomic** — one logical change per commit
3. **Run tests frequently** — catch issues early
4. **Update documentation** as you code
5. **Review your own code** before submitting
6. **Keep branches small** — easy to review
7. **Communicate** — ask for help when stuck
8. **Document decisions** — add ADRs for major changes

---

**Generated with [Continue](https://continue.dev)**

Co-Authored-By: Continue <noreply@continue.dev>
