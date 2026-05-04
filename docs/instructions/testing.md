# Testing Guidelines

## Overview

Comprehensive testing strategy covering unit tests, integration tests, and E2E tests.

## Frontend Testing

### Unit Tests (Vitest)

**Setup:**
```bash
cd rag_app/frontend_next
npm run test          # Run all tests
npm run test:watch    # Watch mode
npm run test:coverage # With coverage report
```

**Patterns:**

```typescript
// ✅ Good: Component test with proper setup
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, beforeEach } from 'vitest';
import { ChatPanel } from './ChatPanel';

describe('ChatPanel', () => {
  const mockSessionId = 'test-session-123';

  beforeEach(() => {
    // Reset mocks before each test
    vi.clearAllMocks();
  });

  it('renders chat messages', () => {
    const { container } = render(<ChatPanel sessionId={mockSessionId} />);
    expect(container).toBeInTheDocument();
  });

  it('handles user input', async () => {
    render(<ChatPanel sessionId={mockSessionId} />);
    const input = screen.getByPlaceholderText('Enter your query...');
    fireEvent.change(input, { target: { value: 'Test query' } });
    expect(input.value).toBe('Test query');
  });
});
```

### E2E Tests (Playwright)

**Setup:**
```bash
npx playwright test           # Run all tests
npx playwright test smoke-test.spec.ts  # Run specific test
npx playwright test --reporter=html     # Generate HTML report
npx playwright show-report  # Open HTML report
```

**Patterns:**

```typescript
// ✅ Good: E2E test with proper assertions
import { test, expect } from '@playwright/test';

test('user can upload document and query', async ({ page }) => {
  // Navigate to app
  await page.goto('http://localhost:5173');
  
  // Upload document
  const fileInput = page.locator('input[type="file"]');
  await fileInput.setInputFiles('tests/fixtures/sample.pdf');
  
  // Wait for upload to complete
  await expect(page.locator('.document-list')).toContainText('sample.pdf');
  
  // Send query
  await page.fill('[placeholder="Enter your query..."]', 'What is this document about?');
  await page.click('button:has-text("Send")');
  
  // Verify response
  await expect(page.locator('.chat-response')).toContainText('Document content');
});
```

## Backend Testing

### Unit Tests (pytest)

**Setup:**
```bash
cd rag_app/backend
pytest tests/ -v
pytest tests/ --cov=. --cov-report=html  # With coverage
```

**Patterns:**

```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@pytest.fixture
def test_client():
    """Create test client."""
    return TestClient(app)

@pytest.mark.asyncio
async def test_upload_document_success(test_client):
    """Test successful document upload."""
    response = await client.post(
        "/api/upload",
        json={
            "filename": "test.pdf",
            "content_type": "application/pdf",
            "session_id": "test-session"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "doc_id" in data

@pytest.mark.asyncio
async def test_upload_document_invalid_type(test_client):
    """Test upload with invalid content type."""
    response = await client.post(
        "/api/upload",
        json={
            "filename": "test.exe",
            "content_type": "application/x-executable",
            "session_id": "test-session"
        }
    )
    assert response.status_code == 400
```

## Test Coverage Requirements

- **Frontend:** Minimum 80% coverage
- **Backend:** Minimum 80% coverage
- **Critical paths:** 100% coverage required

## Test Categories

### 1. Unit Tests
- Test individual functions/components in isolation
- Mock external dependencies
- Fast execution

### 2. Integration Tests
- Test interactions between components
- Use test databases
- Moderate execution time

### 3. E2E Tests
- Test complete user flows
- Real browser environment
- Slower execution, run in CI

## Best Practices

1. **Write tests before implementation** (TDD)
2. **One assertion per test** where possible
3. **Use descriptive test names** that explain the scenario
4. **Mock external services** (APIs, databases)
5. **Keep tests independent** and order-independent
6. **Test both happy paths and error cases**
7. **Use fixtures** for common setup
8. **Run tests frequently** during development

## Test File Organization

```
rag_app/
├── backend/
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py          # Shared fixtures
│       ├── test_api.py          # API tests
│       ├── test_services.py     # Service tests
│       └── test_utils.py        # Utility tests
│
└── frontend_next/
    └── components/
        ├── ChatPanel.test.tsx
        ├── DocumentPanel.test.tsx
        └── LLMLSelector.test.tsx
```

---

**Generated with [Continue](https://continue.dev)**

Co-Authored-By: Continue <noreply@continue.dev>
