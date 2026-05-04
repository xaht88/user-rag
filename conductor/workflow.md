# Workflow — RAG Chat Application

## 🔄 Development Methodology

**Методология:** Context-Driven Development (CDD)  
**Параметризация:** Agile / Scrum (2-week sprints)  
**Качество:** Test-Driven Development (TDD) preferred

---

## 🌿 Git Workflow

### Branch Strategy

```
main (production)
  │
  ├── develop (staging)
  │     │
  │     ├── feature/td-001-persistent-sessions
  │     ├── feature/llm-integration-openai
  │     ├── feature/jwt-authentication
  │     └── bugfix/session-memory-leak
  │
  └── hotfix/production-critical
```

### Branch Naming Conventions

| Тип | Префикс | Пример |
|-----|---------|--------|
| Feature | `feature/` | `feature/td-001-persistent-sessions` |
| Bugfix | `bugfix/` | `bugfix/session-memory-leak` |
| Hotfix | `hotfix/` | `hotfix/production-critical` |
| Chore | `chore/` | `chore/update-dependencies` |
| Docs | `docs/` | `docs/update-readme` |

### Commit Message Convention

**Формат:** `<type>(<scope>): <description>`

**Types:**
- `feat`: Новая фича
- `fix`: Исправление бага
- `docs`: Изменения в документации
- `style`: Форматирование (не меняет логику)
- `refactor`: Рефакторинг (не меняет поведение)
- `test`: Добавление/обновление тестов
- `chore`: Изменения конфигурации, зависимости

**Примеры:**
```bash
feat(sessions): add postgresql persistent storage
fix(backend): resolve session memory leak on restart
docs(conductor): initialize context artifacts
test(frontend): add E2E test for document upload
refactor(backend): extract LLM connector to separate module
chore(deps): update chromadb to 0.4.22
```

**Commit Message Template:**
```
<type>(<scope>): <description>

[Optional body with context]

[Optional footer with references]

Generated with [Continue](https://continue.dev)

Co-Authored-By: Continue <noreply@continue.dev>
```

---

## 🔍 Code Review Requirements

### Review Checklist

**Before requesting review:**
- [ ] Code follows styleguides (Python/TypeScript)
- [ ] All tests pass locally
- [ ] Self-review completed
- [ ] No debug code or console.log statements
- [ ] Documentation updated if needed

**Reviewer responsibilities:**
- [ ] Verify code quality and readability
- [ ] Check for security vulnerabilities
- [ ] Ensure test coverage is adequate
- [ ] Validate against product requirements
- [ ] Confirm ADR alignment if applicable

### Review Process

1. **Create PR** from feature branch to `develop`
2. **Assign reviewers** (minimum 1, recommended 2)
3. **Automated checks** run (linting, tests, type checking)
4. **Reviewers provide feedback** (approve / request changes)
5. **Address feedback** and push updates
6. **Merge** when all approvals received

### Approval Requirements

| Изменение | Минимум approvals |
|-----------|-------------------|
| Bugfix | 1 |
| Feature | 2 |
| Architecture change | 3 + ADR approval |
| Security-related | 2 + security lead |

---

## 🧪 Testing Requirements

### Coverage Targets

| Слой | Минимум | Цель | Текущее |
|------|---------|------|---------|
| **Backend Unit** | 70% | 85% | ⚠️ Не измерено |
| **Frontend Unit** | 70% | 85% | ⚠️ Не измерено |
| **Frontend E2E** | 50% | 80% | ⚠️ Не измерено |

### Test Types

**Unit Tests:**
- **Backend:** pytest (`rag_app/backend/tests/`)
- **Frontend:** Vitest (`rag_app/frontend_next/`)
- **Coverage:** `--cov` flag, generate HTML report

**Integration Tests:**
- API endpoint testing
- Database operations
- External service mocking

**E2E Tests:**
- Playwright (`rag_app/frontend_next/e2e/`)
- Critical user workflows
- Cross-browser testing (Chrome, Firefox, Safari)

### Test Execution

```bash
# Backend
pytest rag_app/backend/tests/ -v --cov=rag_app/backend --cov-report=html

# Frontend Unit
npm run test -- --coverage

# Frontend E2E
npx playwright test
```

---

## 🚦 Quality Gates

### Pre-Commit Gates

**Git Hooks (recommended):**
```bash
# .git/hooks/pre-commit
#!/bin/bash
npm run lint          # Frontend
pytest --maxfail=1    # Backend quick checks
```

### Pre-Merge Gates

**Required checks before merge:**
- [ ] All unit tests pass
- [ ] All E2E tests pass (for features)
- [ ] Code coverage ≥ target
- [ ] No linting errors
- [ ] Type checking passes (TypeScript)
- [ ] At least 1 approval (see above)
- [ ] No merge conflicts

### CI/CD Gates (Planned)

**GitHub Actions workflow:**
```yaml
# .github/workflows/ci.yml
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd rag_app/backend
          pip install -r requirements.txt
      - name: Run tests
        run: pytest rag_app/backend/tests/ -v --cov
```

---

## 📦 Deployment Procedures

### Development Deployment

```bash
# Backend
cd rag_app/backend
uvicorn main:app --reload --port 8000

# Frontend (separate terminal)
cd rag_app/frontend_next
npm run dev
```

### Production Deployment (Planned)

**Phase 1: Docker**
```bash
# Build images
docker build -t rag-backend:latest -f Dockerfile.backend .
docker build -t rag-frontend:latest -f Dockerfile.frontend .

# Run with compose
docker-compose up -d
```

**Phase 2: Kubernetes**
```bash
# Deploy to cluster
kubectl apply -f k8s/
kubectl rollout status deployment/rag-app
```

### Rollback Procedure

1. Identify problematic deployment
2. Rollback to previous version:
   ```bash
   kubectl rollout undo deployment/rag-app
   ```
3. Verify service health
4. Investigate issue
5. Deploy fix

---

## 📝 Documentation Standards

### When to Update Documentation

- [ ] New API endpoints added
- [ ] New features implemented
- [ ] Architecture changes made
- [ ] Dependencies updated (major versions)
- [ ] Environment variables changed
- [ ] Configuration options modified

### Documentation Files

| Файл | Описание | Когда обновлять |
|------|----------|-----------------|
| `README.md` | Project overview | Initial setup, major changes |
| `technical_specification.md` | Requirements | Feature planning |
| `conductor/product.md` | Product vision | Feature completion |
| `conductor/tech-stack.md` | Dependencies | Dependency updates |
| `conductor/workflow.md` | Processes | Workflow changes |
| `docs/api/README.md` | API reference | API changes |
| `docs/decisions/ADR-XXX.md` | Architecture decisions | Major decisions |

---

## 🔄 Continuous Integration

### Daily Tasks

- [ ] Pull latest changes from `develop`
- [ ] Run full test suite locally
- [ ] Check for dependency updates
- [ ] Review open PRs

### Weekly Tasks

- [ ] Update sprint progress in `conductor/tracks.md`
- [ ] Review technical debt items
- [ ] Plan next sprint
- [ ] Update documentation

### Monthly Tasks

- [ ] Dependency security audit
- [ ] Code quality review
- [ ] Performance benchmarking
- [ ] Architecture review

---

## 🚨 Incident Response

### Severity Levels

| Уровень | Описание | Время реакции |
|---------|----------|---------------|
| **P0 - Critical** | Production down, data loss | < 15 минут |
| **P1 - High** | Major feature broken | < 1 час |
| **P2 - Medium** | Minor feature broken | < 24 часа |
| **P3 - Low** | Cosmetic, enhancement | Next sprint |

### Incident Response Process

1. **Detect** issue (monitoring/alerts)
2. **Assess** severity and impact
3. **Communicate** to stakeholders
4. **Fix** in hotfix branch
5. **Test** thoroughly
6. **Deploy** to production
7. **Post-mortem** and document lessons learned

---

## 📊 Metrics & Monitoring

### Development Metrics

| Метрика | Цель | Инструмент |
|---------|------|------------|
| Cycle time | < 3 days | GitHub Projects |
| PR review time | < 4 hours | GitHub Insights |
| Test pass rate | > 95% | CI/CD |
| Code coverage | > 80% | Coverage reports |

### Production Metrics (Planned)

| Метрика | Цель | Инструмент |
|---------|------|------------|
| API response time | < 500ms | Prometheus |
| Error rate | < 1% | Sentry |
| Uptime | > 99.9% | Uptime Robot |
| Active users | - | Analytics |

---

**Последнее обновление:** 2026-05-04  
**Версия workflow:** 1.0.0
