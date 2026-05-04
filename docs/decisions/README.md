# Architecture Decision Records (ADRs)

## Overview

This directory contains Architecture Decision Records (ADRs) for the RAG Chat Application.

ADRs capture the reasoning behind significant technical decisions. They're the highest-value documentation you can write.

## ADRs

| ID | Title | Status | Date |
|----|-------|--------|------|
| [ADR-001](./ADR-001-architecture-pattern.md) | Client-Server Architecture Pattern | Accepted | 2024-01-15 |
| [ADR-002](./ADR-002-session-management.md) | Session Management Strategy | Accepted | 2024-01-15 |
| [ADR-003](./ADR-003-project-structure-refactoring.md) | Project Structure Refactoring | Accepted | 2026-05-04 |

## ADR Template

When creating new ADRs, use this template:

```markdown
# ADR-XXX: Title

## Status
Accepted | Superseded by ADR-XXX | Deprecated

## Date
YYYY-MM-DD

## Context
Describe the problem and constraints.

## Decision
Describe the chosen solution.

## Alternatives Considered
List and evaluate alternatives.

## Consequences
- Positive consequences
- Negative consequences
- Technical debt

## References
Links to related documentation
```

## ADR Lifecycle

```
PROPOSED → ACCEPTED → (SUPERSEDED or DEPRECATED)
```

- Don't delete old ADRs. They capture historical context.
- When a decision changes, write a new ADR that references and supersedes the old one.

## When to Write an ADR

- Choosing a framework, library, or major dependency
- Designing a data model or database schema
- Selecting an authentication strategy
- Deciding on an API architecture (REST vs. GraphQL vs. tRPC)
- Choosing between build tools, hosting platforms, or infrastructure
- Any decision that would be expensive to reverse

## When NOT to Write an ADR

- Obvious decisions
- Implementation details
- Temporary solutions
- Things that will change soon

---

**See also:**
- [System Architecture](../architecture/README.md)
- [Development Guide](../development/README.md)
