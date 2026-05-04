# TypeScript Styleguide

## 📚 Основы

**Стандарт:** Airbnb TypeScript Styleguide (https://github.com/airbnb/typescript-styleguide)  
**Форматер:** Prettier (https://prettier.io/)  
**Линтер:** ESLint (https://eslint.org/)  
**Type Checking:** TypeScript Compiler (tsc)

---

## 🎯 Основные принципы

1. **Type Safety First** — использовать типы везде где возможно
2. **Explicit over Implicit** — явные типы лучше выводимых
3. **Component Composition** — композиция лучше наследования
4. **Functional Patterns** — чистые функции, иммутабельность
5. **Developer Experience** — хороший DX важнее микро-оптимизаций

---

## 📐 Форматирование

### Отступы и кавычки

```typescript
// ✅ Правильно
const name = 'Alice';
const age = 30;

function greet(name: string): string {
  return `Hello, ${name}!`;
}

// ❌ Неправильно
const name = "Alice";  // Одинарные кавычки предпочтительнее
function greet(name: string) { // Явный тип обязателен
  return `Hello, ${name}!`;
}
```

- **Отступы:** 2 пробела
- **Кавычки:** Одинарные (' ') для строк
- **Максимальная длина строки:** 100 символов
- **Запятки:** trailing commas в объектах/массивах

### Imports

```typescript
// ✅ Правильно - порядок импортов
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

import axios from 'axios';
import { format } from 'date-fns';

import { Button } from '@/components/ui/button';
import { useAuth } from '@/hooks/useAuth';
import { createUser } from '@/features/users/api';
```

**Порядок импортов:**
1. React и плагины React
2. Внешние библиотеки (по алфавиту)
3. Локальные импорты (с группировкой по папкам)

**Импорты из одной папки:**
```typescript
// ✅ Правильно
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';

// ❌ Неправильно
import { Button, Input, Card } from '@/components/ui';
```

### Файлы и экспорты

```typescript
// ✅ Правильно - named exports
export const MAX_ITEMS = 100;
export function calculateTotal(items: Item[]): number {
  return items.reduce((sum, item) => sum + item.price, 0);
}

export default function App() {
  return <div>App</div>;
}

// ✅ Правильно - export as
import { ReactComponent as Logo } from './logo.svg';

// ❌ Неправильно - default export для функций
export default function calculateTotal() { }
```

---

## 🏗️ Структура проекта

```
frontend_next/
├── app/                    # Next.js App Router
│   ├── page.tsx           # Home page
│   ├── layout.tsx         # Root layout
│   └── globals.css        # Global styles
│
├── components/             # Reusable components
│   ├── ui/                # Base UI components
│   │   ├── button.tsx
│   │   ├── input.tsx
│   │   └── card.tsx
│   ├── chat-panel.tsx     # Feature components
│   ├── document-panel.tsx
│   └── llm-selector.tsx
│
├── features/               # Feature modules
│   ├── documents/         # Document management
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── api.ts
│   │   └── types.ts
│   ├── chat/              # Chat functionality
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── api.ts
│   │   └── types.ts
│   └── llm/               # LLM configuration
│       ├── components/
│       ├── hooks/
│       └── types.ts
│
├── shared/                # Shared utilities
│   ├── api/               # API client
│   │   └── client.ts
│   ├── types/             # Shared types
│   │   └── index.ts
│   └── utils/             # Utilities
│       ├── formatters.ts
│       └── validators.ts
│
├── hooks/                 # Custom hooks
│   ├── useAuth.ts
│   ├── useDocuments.ts
│   └── useChat.ts
│
├── tests/                 # Tests
│   ├── components/
│   ├── features/
│   └── utils/
│
└── vitest.setup.ts        # Vitest configuration
```

---

## 🧩 Компоненты React

### Функциональные компоненты

```typescript
// ✅ Правильно - типизированные props
interface ButtonProps {
  /** Button label */
  children: React.ReactNode;
  /** Button variant */
  variant?: 'primary' | 'secondary' | 'ghost';
  /** Button size */
  size?: 'sm' | 'md' | 'lg';
  /** Disabled state */
  disabled?: boolean;
  /** Click handler */
  onClick?: () => void;
}

export function Button({
  children,
  variant = 'primary',
  size = 'md',
  disabled = false,
  onClick,
}: ButtonProps): JSX.Element {
  return (
    <button
      className={`btn btn-${variant} btn-${size} ${disabled ? 'disabled' : ''}`}
      onClick={onClick}
      disabled={disabled}
    >
      {children}
    </button>
  );
}

// ✅ Правильно - компонент с ref
interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, className, ...props }, ref) => {
    return (
      <div className="input-group">
        {label && <label>{label}</label>}
        <input
          ref={ref}
          className={`input ${error ? 'input-error' : ''} ${className}`}
          {...props}
        />
        {error && <span className="error-message">{error}</span>}
      </div>
    );
  }
);

Input.displayName = 'Input';
```

### Hooks

```typescript
// ✅ Правильно - кастомные хуки
interface UseDocumentOptions {
  onSuccess?: (documents: Document[]) => void;
  onError?: (error: Error) => void;
}

export function useDocuments(options?: UseDocumentOptions) {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const fetchDocuments = async () => {
    setLoading(true);
    try {
      const response = await api.getDocuments();
      setDocuments(response.data);
      options?.onSuccess?.(response.data);
    } catch (err) {
      setError(err as Error);
      options?.onError?.(err as Error);
    } finally {
      setLoading(false);
    }
  };

  return { documents, loading, error, refetch: fetchDocuments };
}

// ✅ Правильно - useDebounce
export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}
```

### Context

```typescript
// ✅ Правильно - Context с провайдерами
interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    // Load user from localStorage
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
  }, []);

  const login = async (credentials: LoginCredentials) => {
    const response = await api.login(credentials);
    setUser(response.user);
    localStorage.setItem('user', JSON.stringify(response.user));
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('user');
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
```

---

## 🧪 Тестирование

### Vitest конвенции

```typescript
// ✅ Правильно - тесты с описанием
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from './button';

describe('Button', () => {
  it('renders children correctly', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  it('calls onClick when clicked', () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Click</Button>);
    
    fireEvent.click(screen.getByText('Click'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('is disabled when disabled prop is true', () => {
    render(<Button disabled>Click</Button>);
    expect(screen.getByText('Click')).toBeDisabled();
  });
});

// ✅ Правильно - тесты хуков
import { renderHook, act } from '@testing-library/react';
import { useCounter } from './useCounter';

describe('useCounter', () => {
  it('initializes with count 0', () => {
    const { result } = renderHook(() => useCounter());
    expect(result.current.count).toBe(0);
  });

  it('increments count on increment', () => {
    const { result } = renderHook(() => useCounter());
    
    act(() => {
      result.current.increment();
    });
    
    expect(result.current.count).toBe(1);
  });
});
```

### Testing Library паттерны

```typescript
// ✅ Правильно - тестирование форм
describe('LoginForm', () => {
  it('shows validation errors for invalid email', async () => {
    render(<LoginForm />);
    
    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole('button', { name: /login/i });
    
    fireEvent.change(emailInput, { target: { value: 'invalid-email' } });
    fireEvent.change(passwordInput, { target: { value: '123' } });
    
    fireEvent.click(submitButton);
    
    expect(screen.getByText(/invalid email/i)).toBeInTheDocument();
    expect(screen.getByText(/password too short/i)).toBeInTheDocument();
  });
});
```

---

## 📋 Типизация

### Interfaces vs Types

```typescript
// ✅ Правильно - interface для объектов
interface User {
  id: string;
  name: string;
  email: string;
  createdAt: Date;
}

// ✅ Правильно - type для union types
type Status = 'loading' | 'success' | 'error';

// ✅ Правильно - type для function types
type EventHandler = (event: React.FormEvent) => void;

// ❌ Неправильно - использовать type вместо interface
type User = {
  id: string;
  name: string;
};
```

### Generics

```typescript
// ✅ Правильно - типизированные функции
function identity<T>(arg: T): T {
  return arg;
}

// ✅ Правильно - generics с constraints
function getProperty<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}

// ✅ Правильно - React generics
function useLocalStorage<T>(key: string): [T, (value: T) => void] {
  // Implementation...
}
```

### Utility Types

```typescript
// ✅ Правильно - использование utility types
type PartialUser = Partial<User>;
type RequiredUser = Required<User>;
type PickUser = Pick<User, 'id' | 'name'>;
type OmitUser = Omit<User, 'password'>;

// ✅ Правильно - создание типов
type ApiResponse<T> = {
  data: T;
  status: number;
  message: string;
};

type AsyncState<T> = {
  data: T | null;
  loading: boolean;
  error: Error | null;
};
```

---

## 🔐 Безопасность

### XSS Protection

```typescript
// ✅ Правильно - React автоматически экранирует
function UserGreeting({ name }: { name: string }) {
  return <h1>Hello, {name}</h1>; // Безопасно!
}

// ❌ Неправильно - никогда не используйте dangerouslySetInnerHTML
function DangerousComponent({ html }: { html: string }) {
  return <div dangerouslySetInnerHTML={{ __html: html }} />;
}
```

### API Security

```typescript
// ✅ Правильно - обработка ошибок API
async function fetchUserData(userId: string): Promise<User> {
  try {
    const response = await api.get(`/users/${userId}`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return response.data;
  } catch (error) {
    if (error instanceof Error) {
      console.error('Failed to fetch user:', error.message);
      throw new UserFetchError('Failed to fetch user data');
    }
    throw error;
  }
}
```

---

## 🚀 Производительность

### Оптимизация рендера

```typescript
// ✅ Правильно - useMemo для тяжелых вычислений
function ExpensiveComponent({ data }: { data: LargeDataset }) {
  const processedData = useMemo(() => {
    return processData(data); // Тяжелое вычисление
  }, [data]);

  return <div>{processedData}</div>;
}

// ✅ Правильно - useCallback для стабильных функций
function ParentComponent() {
  const [count, setCount] = useState(0);
  
  const handleClick = useCallback(() => {
    setCount(prev => prev + 1);
  }, []);

  return (
    <div>
      <Child onClick={handleClick} />
      <p>Count: {count}</p>
    </div>
  );
}

// ✅ Правильно - React.memo для предотвращения лишних рендеров
const MemoizedChild = React.memo(({ value }: { value: number }) => {
  return <div>{value * 2}</div>;
});
```

### Code Splitting

```typescript
// ✅ Правильно - lazy loading компонентов
import { lazy, Suspense } from 'react';

const DocumentPanel = lazy(() => import('./features/documents/components/DocumentPanel'));
const ChatPanel = lazy(() => import('./features/chat/components/ChatPanel'));

function AppLayout() {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <DocumentPanel />
      <ChatPanel />
    </Suspense>
  );
}
```

---

## 📝 Checklist перед коммитом

- [ ] Код отформатирован Prettier'ом
- [ ] Нет linting ошибок (`npm run lint`)
- [ ] Type checking проходит (`tsc --noEmit`)
- [ ] Все тесты проходят (`npm run test`)
- [ ] Компоненты типизированы
- [ ] Hooks имеют правильные зависимости
- [ ] Нет `any` типов (использовать `unknown` если нужно)
- [ ] Нет debug console.log statements
- [ ] Коммит сообщение следует конвенции

---

## 🛠️ Инструменты

### Установка

```bash
# Development dependencies
npm install -D @types/react @types/react-dom \
  eslint-plugin-react eslint-plugin-react-hooks \
  prettier @typescript-eslint/parser @typescript-eslint/eslint-plugin \
  vitest @testing-library/react @testing-library/jest-dom
```

### Команды

```bash
# Format code
npx prettier --write .

# Lint code
npm run lint

# Type checking
npx tsc --noEmit

# Run tests
npm run test

# Run tests with coverage
npm run test:coverage
```

---

**Последнее обновление:** 2026-05-04  
**Версия styleguide:** 1.0.0
