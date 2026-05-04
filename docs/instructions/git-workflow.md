# Git Workflow

## Overview

Structured git workflow for collaborative development with clear commit conventions.

## Branch Strategy

```
main                          # Production-ready code
├── develop                   # Integration branch
├── feature/user-auth         # Feature branches
├── bugfix/session-storage    # Bugfix branches
└── hotfix/security-patch     # Hotfix branches
```

### Branch Naming Conventions

```bash
# ✅ Good branch names
git checkout -b feature/user-authentication
git checkout -b bugfix/session-memory-leak
git checkout -b hotfix/api-rate-limiting
git checkout -b docs/update-readme
git checkout -b test/add-e2e-tests
```

## Commit Conventions

### Format

```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

### Types

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation changes |
| `style` | Code style changes (formatting) |
| `refactor` | Code refactoring |
| `test` | Adding or updating tests |
| `chore` | Maintenance tasks |

### Examples

```bash
# ✅ Good commits
git commit -m "feat(auth): add JWT token refresh mechanism"
git commit -m "fix(session): resolve memory leak in session cleanup"
git commit -m "docs(api): update OpenAPI specification"
git commit -m "refactor(query): optimize embedding cache lookup"
git commit -m "test(frontend): add ChatPanel integration tests"
```

### Commit Message Guidelines

1. **Subject line:** Max 50 characters, imperative mood
2. **Body:** Wrap at 72 characters, explain WHY not WHAT
3. **Footer:** Reference issues/PRs

```bash
# ✅ Good commit message
git commit -m "feat(auth): implement JWT authentication

Add JWT token-based authentication with refresh tokens.

- Add AuthService with login/logout methods
- Implement token validation middleware
- Add protected route decorator
- Update API documentation

Closes #42"
```

## Pull Request Process

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] E2E tests added/updated
- [ ] Manually tested

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-reviewed code
- [ ] Commented complex code
- [ ] Updated documentation
- [ ] No new warnings
- [ ] Tests pass locally
```

### PR Review Guidelines

1. **Reviewers:** At least 1 approval required
2. **CI:** All checks must pass
3. **Tests:** Minimum 80% coverage maintained
4. **Documentation:** Updated if needed

## Git Commands Reference

### Daily Workflow

```bash
# Start from latest main
git checkout main
git pull origin main

# Create feature branch
git checkout -b feature/my-feature

# Make changes and commit
git add .
git commit -m "feat: implement feature"

# Update from main before pushing
git fetch origin
git rebase origin/main

# Push to remote
git push -u origin feature/my-feature
```

### Useful Commands

```bash
# View commit history
git log --oneline --graph

# Stash changes
git stash
git stash pop

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Amend last commit
git commit --amend

# Cherry-pick commit
git cherry-pick <commit-hash>
```

## Best Practices

1. **Commit frequently** — small, atomic commits
2. **Write clear commit messages** — explain the why
3. **Rebase before pushing** — keep linear history
4. **Pull before push** — resolve conflicts early
5. **Use descriptive branch names** — understand purpose at a glance
6. **Keep PRs small** — easier to review
7. **Run tests before committing** — catch issues early
8. **Reference issues** — link to tickets/PRs

---

**Generated with [Continue](https://continue.dev)**

Co-Authored-By: Continue <noreply@continue.dev>
