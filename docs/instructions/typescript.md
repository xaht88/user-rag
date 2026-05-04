# TypeScript Conventions

## Overview

TypeScript is used throughout the frontend with strict mode enabled. Follow these conventions for consistency.

## Core Rules

### Type Safety

- **Always use explicit types** for function parameters, return values, and variables
- **Avoid `any` type** — use `unknown` when type is truly unknown
- **Use interfaces for object shapes**, types for unions/aliases
- **Enable strict mode** in `tsconfig.json`

### Function Patterns

```typescript
// ✅ Good: Explicit return type
function calculateTotal(items: Item[]): number {
  return items.reduce((sum, item) => sum + item.price, 0);
}

// ✅ Good: Type inference with explicit parameter types
const multiply = (a: number, b: number): number => a * b;

// ❌ Avoid: Implicit any
const badFunction = (a, b) => a + b;
```

### Component Patterns

```typescript
// ✅ Good: Typed props interface
interface ButtonProps {
  label: string;
  onClick: () => void;
  variant?: 'primary' | 'secondary';
}

const Button: React.FC<ButtonProps> = ({ label, onClick, variant = 'primary' }) => {
  return <button className={`btn btn-${variant}`} onClick={onClick}>
    {label}
  </button>;
};

// ✅ Good: Functional component with proper typing
export function ChatPanel({ sessionId }: { sessionId: string }) {
  // Implementation
}
```

### State Management

```typescript
// ✅ Good: Use React hooks with proper typing
const [data, setData] = useState<Item[] | null>(null);
const [loading, setLoading] = useState<boolean>(false);

// ✅ Good: Use const for immutable references
const config: AppConfig = {
  apiUrl: import.meta.env.VITE_API_URL,
  timeout: 5000,
};
```

### Error Handling

```typescript
// ✅ Good: Use Result pattern or try/catch with typed errors
async function fetchData(url: string): Promise<Data> {
  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    // Type guard for error
    if (error instanceof Error) {
      console.error('Fetch failed:', error.message);
    }
    throw error;
  }
}
```

## Best Practices

1. **Use `readonly`** for properties that shouldn't change
2. **Prefer composition over inheritance**
3. **Use generics** for reusable, type-safe utilities
4. **Export types explicitly** — don't rely on inference across modules
5. **Use `React.FC`** consistently for component typing

## Common Patterns

### API Client

```typescript
// shared/api/client.ts
export class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  async get<T>(endpoint: string): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`);
    return response.json();
  }

  async post<T>(endpoint: string, data: unknown): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return response.json();
  }
}
```

### Type Guards

```typescript
function isItem(value: unknown): value is Item {
  return (
    typeof value === 'object' &&
    value !== null &&
    'id' in value &&
    'name' in value
  );
}
```

---

**Generated with [Continue](https://continue.dev)**

Co-Authored-By: Continue <noreply@continue.dev>
