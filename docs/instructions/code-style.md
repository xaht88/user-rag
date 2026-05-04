# Code Style Guidelines

## Overview

Consistent code style across the project ensures maintainability and readability.

## Frontend (TypeScript/React)

### Formatting

- **Use ESLint** with project configuration
- **2-space indentation**
- **Semicolons required**
- **Single quotes for strings**
- **Trailing commas** in multi-line objects/arrays
- **Max line length:** 100 characters

### Naming Conventions

```typescript
// ✅ Good: Clear naming
const userSession = 'active';
const calculateTotalPrice = (items: Item[]): number => { ... };
const UserAvatar: React.FC<UserAvatarProps> = ({ user }) => { ... };

// ❌ Avoid: Ambiguous names
const d = 'active';
const calc = (i: any) => { ... };
```

### Component Structure

```typescript
// ✅ Good: Organized component
import React from 'react';
import { cn } from '@/lib/utils';

// 1. Types
interface ButtonProps {
  label: string;
  onClick: () => void;
  variant?: 'primary' | 'secondary';
}

// 2. Constants
const VARIANT_CLASSES = {
  primary: 'bg-blue-500 text-white',
  secondary: 'bg-gray-200 text-gray-800',
};

// 3. Component
export function Button({ label, onClick, variant = 'primary' }: ButtonProps) {
  return (
    <button
      className={cn(VARIANT_CLASSES[variant], 'px-4 py-2 rounded')}
      onClick={onClick}
    >
      {label}
    </button>
  );
}
```

### Import Organization

```typescript
// ✅ Good: Organized imports
// 1. External imports
import React, { useState, useEffect } from 'react';
import { Router } from 'react-router-dom';

// 2. Internal imports
import { Button } from '@/components/Button';
import { useSession } from '@/hooks/useSession';

// 3. Styles
import './Component.css';
```

## Backend (Python)

### Formatting

- **Use `black`** for formatting (88 char line length)
- **Use `isort`** for import sorting
- **Use `flake8`** for linting

### Import Organization

```python
# ✅ Good: Organized imports
# 1. Standard library
import logging
from typing import Optional, List
from contextlib import asynccontextmanager

# 2. Third-party
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# 3. Local imports
from rag_app.backend.models import Document
from rag_app.backend.utils import embed_document
```

### Function Structure

```python
# ✅ Good: Well-structured function
def process_document(
    file_path: str,
    session_id: str,
    chunk_size: int = 512
) -> List[Embedding]:
    """Process document and generate embeddings.
    
    Args:
        file_path: Path to the document file
        session_id: Associated session ID
        chunk_size: Size of text chunks for embedding
        
    Returns:
        List of embedding vectors
        
    Raises:
        DocumentNotFoundError: If file doesn't exist
        InvalidFormatError: If file format is not supported
    """
    # Validate input
    if not os.path.exists(file_path):
        raise DocumentNotFoundError(file_path)
    
    # Process document
    chunks = chunk_text(file_path, chunk_size)
    embeddings = [embed_chunk(chunk) for chunk in chunks]
    
    return embeddings
```

## Documentation

### Code Comments

```typescript
// ✅ Good: Explain WHY, not WHAT
// Cache the result to avoid repeated API calls on re-renders
const memoizedData = useMemo(() => fetchUserData(), []);

// ❌ Avoid: Redundant comments
const x = 5; // x is 5
```

### Docstrings (Python)

```python
def calculate_similarity(query: str, documents: List[Document]) -> List[Tuple[Document, float]]:
    """Calculate similarity between query and documents.
    
    Uses cosine similarity on embedding vectors.
    
    Args:
        query: User query string
        documents: List of documents to compare against
        
    Returns:
        List of (document, similarity_score) tuples, sorted by score
        
    Example:
        >>> results = calculate_similarity("what is RAG?", docs)
        >>> len(results)
        10
    """
```

## Best Practices

1. **Keep functions small** (< 50 lines)
2. **Single responsibility** — one thing per function/component
3. **DRY principle** — don't repeat yourself
4. **Use meaningful variable names**
5. **Add type hints** for all functions
6. **Write tests** for all public APIs
7. **Document complex logic** with comments
8. **Consistent error handling** patterns

## Tools

### Frontend

```bash
# Install
npm install -D eslint prettier

# Run
npm run lint          # ESLint
npm run format        # Prettier
```

### Backend

```bash
# Install
pip install black flake8 isort

# Run
black rag_app/backend/
flake8 rag_app/backend/
isort rag_app/backend/
```

---

**Generated with [Continue](https://continue.dev)**

Co-Authored-By: Continue <noreply@continue.dev>
