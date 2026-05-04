# Documentation Standards

## Overview

Consistent documentation ensures maintainability and knowledge transfer.

## Documentation Principles

1. **Document the WHY, not the WHAT** — code shows what, docs explain why
2. **Keep it up to date** — outdated docs are worse than no docs
3. **Be concise** — clear and brief is better than verbose
4. **Use examples** — show, don't just tell
5. **Write for your audience** — consider who will read it

## File Organization

```
otus_dz2/
├── .agents/
│   └── instructions/
│       ├── README.md           # Index of agent instructions
│       ├── typescript.md       # TypeScript conventions
│       ├── python.md           # Python conventions
│       ├── testing.md          # Testing guidelines
│       ├── code-style.md       # Code style rules
│       ├── git-workflow.md     # Git workflow
│       ├── architecture.md     # Architecture patterns
│       ├── security.md         # Security guidelines
│       └── development-workflow.md  # Development workflow
│
├── docs/
│   ├── index.md                # Documentation index
│   ├── api/
│   │   └── README.md           # API documentation
│   ├── architecture/
│   │   └── system-overview.md  # System architecture
│   ├── development/
│   │   └── README.md           # Development guide
│   ├── deployment/
│   │   └── README.md           # Deployment guide
│   └── decisions/
│       ├── README.md           # ADR index
│       ├── ADR-001-*.md        # Architecture Decision Records
│       ├── ADR-002-*.md
│       └── ADR-003-*.md
│
├── AGENTS.md                   # Root agent instructions
├── README.md                   # Project README
├── technical_specification.md  # Technical requirements
└── stories/
    └── user_stories.md         # User stories
```

## Documentation Types

### 1. README Files

**Purpose:** Quick start and project overview

**Structure:**
```markdown
# Project Name

## Description
Brief description (1-2 sentences)

## Quick Start
Basic commands to get running

## Documentation
Links to detailed docs

## Contributing
How to contribute
```

### 2. API Documentation

**Purpose:** Complete API reference

**Structure:**
```markdown
# API Documentation

## Overview
Brief description

## Authentication
Auth requirements

## Endpoints
### GET /endpoint
Description

**Request:**
```json
{...}
```

**Response:**
```json
{...}
```
```

### 3. Architecture Decision Records (ADRs)

**Purpose:** Document architectural decisions

**Template:**
```markdown
# ADR-XXX: Decision Title

## Status
Proposed | Accepted | Deprecated | Superseded

## Context
Problem description, constraints, considerations

## Decision
What we decided and why

## Consequences
Positive, negative, and neutral consequences
```

### 4. Agent Instructions

**Purpose:** Guidelines for AI agents working on the project

**Structure:**
```markdown
# Topic Guidelines

## Overview
Brief context

## Rules
### Rule Category 1
- Specific instruction
- Another instruction

## Examples

### Good
```code
// Example
```

### Avoid
```code
// Bad example
```
```

## Code Documentation

### Python Docstrings

```python
def calculate_similarity(query: str, documents: List[Document]) -> List[Tuple[Document, float]]:
    """Calculate similarity between query and documents.
    
    Uses cosine similarity on embedding vectors.
    
    Args:
        query: User query string
        documents: List of documents to compare against
        
    Returns:
        List of (document, similarity_score) tuples, sorted by score
        
    Raises:
        ValueError: If documents list is empty
        
    Example:
        >>> results = calculate_similarity("what is RAG?", docs)
        >>> len(results)
        10
    """
```

### TypeScript JSDoc

```typescript
/**
 * Calculate similarity between query and documents.
 * 
 * @param query - User query string
 * @param documents - List of documents to compare against
 * @returns List of [document, similarity_score] tuples, sorted by score
 * @throws {ValueError} If documents list is empty
 * 
 * @example
 * const results = calculateSimilarity("what is RAG?", docs);
 * console.log(results.length); // 10
 */
function calculateSimilarity(
  query: string,
  documents: Document[]
): [Document, number][] {
  // Implementation
}
```

### Component Documentation

```typescript
/**
 * ChatPanel component for displaying chat messages.
 * 
 * @example
 * <ChatPanel sessionId="session-123" />
 */
export function ChatPanel({ sessionId }: { sessionId: string }) {
  // Implementation
}
```

## Documentation Updates

### When to Update Documentation

1. **Adding new features** — update relevant docs
2. **Changing APIs** — update API documentation
3. **Refactoring** — update if architecture changes
4. **Fixing bugs** — update if behavior changes
5. **Adding tests** — update testing docs if patterns change

### Documentation Review

- Review docs alongside code changes
- Check for outdated information
- Verify examples work correctly
- Ensure links are valid

## Tools

### Markdown Linting

```bash
# Install
npm install -g markdownlint-cli

# Run
markdownlint **/*.md
```

### API Documentation Generation

```bash
# Generate from OpenAPI spec
# (Use your preferred tool)
```

## Best Practices

1. **Write docs first** — clarify requirements before coding
2. **Keep docs close to code** — easier to maintain
3. **Use auto-generation** where possible (API docs)
4. **Review docs** in code reviews
5. **Test examples** in documentation
6. **Link related docs** — create navigation
7. **Version docs** with code changes
8. **Use consistent formatting** across all docs

---

**Generated with [Continue](https://continue.dev)**

Co-Authored-By: Continue <noreply@continue.dev>
