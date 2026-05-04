# Architecture Decision Records (ADRs)

This directory contains Architecture Decision Records (ADRs) that document significant architectural decisions in the RAG Chat Application project.

## ADR Index

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| [ADR-001](./docs/decisions/ADR-001-architecture-pattern.md) | Client-Server Architecture Pattern | Accepted | 2026-05-04 |
| [ADR-002](./docs/decisions/ADR-002-session-management.md) | Session Management Strategy | Accepted | 2026-05-04 |
| [ADR-003](./docs/decisions/ADR-003-project-structure-refactoring.md) | Project Structure Refactoring | Accepted | 2026-05-04 |

## How to Write an ADR

### Template

```markdown
# ADR-XXX: Decision Title

## Status
Proposed | Accepted | Deprecated | Superseded

## Context
Describe the context and problem you're trying to solve.

## Decision
Describe the decision and the reasoning behind it.

## Consequences
- Positive consequences
- Negative consequences
- Neutral consequences
```

### Guidelines

1. **Number ADRs sequentially** — ADR-001, ADR-002, etc.
2. **Use clear, descriptive titles**
3. **Document the status** — track the lifecycle of each decision
4. **Include date** — when was the decision made
5. **Explain the WHY** — not just what was decided
6. **List consequences** — both positive and negative
7. **Reference related ADRs** — if decisions are connected

## Creating a New ADR

1. Create a new file: `docs/decisions/ADR-XXX-title.md`
2. Follow the template above
3. Update this index with the new ADR
4. Reference the ADR in relevant documentation

## ADR Status Definitions

- **Proposed**: Decision is under consideration
- **Accepted**: Decision has been made and approved
- **Deprecated**: Decision is no longer valid
- **Superseded**: Decision has been replaced by a newer one

---

**Generated with [Continue](https://continue.dev)**

Co-Authored-By: Continue <noreply@continue.dev>
