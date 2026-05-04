# RAG Chat Frontend

Next.js 14 frontend для RAG (Retrieval-Augmented Generation) чат-приложения.

## 📋 Описание

Интерфейс пользователя для взаимодействия с RAG системой:
- Загрузка и управление документами
- Чат-интерфейс для вопросов к документам
- Конфигурация LLM (OpenAI/Ollama)
- Отображение источников ответов

## 🚀 Быстрый старт

### Требования

- Node.js 18+
- npm 9+ или yarn 1.22+

### Установка

```bash
# Перейдите в директорию frontend
cd rag_app/frontend_next

# Установите зависимости
npm install

# Или с yarn
yarn install
```

### Запуск разработки

```bash
# Запуск dev сервера
npm run dev

# Или с yarn
yarn dev
```

Фронтенд запустится на `http://localhost:3000`

### Экспорт для продакшена

```bash
# Экспорт статических файлов
npm run export

# Экспорт для интеграции с backend
npm run export:backend
```

## 📁 Структура проекта

```
frontend_next/
├── app/                    # Next.js App Router pages
│   ├── page.tsx           # Главная страница (чат)
│   ├── layout.tsx         # Корневой layout
│   └── globals.css        # Глобальные стили
├── components/            # React компоненты
│   ├── chat-panel.tsx     # Панель чата
│   ├── document-panel.tsx # Панель документов
│   ├── llm-selector.tsx   # Выбор LLM
│   └── ui/                # Базовые UI компоненты
├── features/              # Feature modules
│   └── rag/              # RAG функциональность
├── shared/                # Общие модули
│   ├── api/              # API клиент
│   │   └── client.ts     # HTTP клиент к backend
│   └── types.ts          # TypeScript типы
├── scripts/              # Скрипты
│   └── export-to-backend.ps1  # Скрипт экспорта
├── public/               # Статические ассеты
├── package.json          # Зависимости и скрипты
├── tsconfig.json         # TypeScript конфигурация
├── tailwind.config.ts    # Tailwind CSS конфигурация
├── vitest.config.ts      # Vitest конфигурация
└── .env.local            # Локальная конфигурация (не коммитить)
```

## 🔧 Конфигурация

### Environment Variables

Создайте файл `.env.local`:

```env
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# OpenAI API ключ (опционально)
NEXT_PUBLIC_OPENAI_API_KEY=your-openai-api-key

# Ollama базовый URL
NEXT_PUBLIC_OLLAMA_BASE_URL=http://localhost:11434
```

### Tailwind CSS

Конфигурация Tailwind в `tailwind.config.ts`:

```typescript
import type { Config } from "tailwindcss"

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
      },
    },
  },
  plugins: [],
}
export default config
```

## 🎨 Компоненты

### ChatPanel

Основной компонент чата.

**Props:**
```typescript
interface ChatPanelProps {
  sessionId: string;
  messages: ChatMessage[];
  onSendMessage: (query: string) => void;
  isLoading: boolean;
}
```

### DocumentPanel

Панель управления документами.

**Props:**
```typescript
interface DocumentPanelProps {
  sessionId: string;
  documents: DocumentInfo[];
  onToggleDocument: (docId: string) => void;
  onDeleteDocument: (docId: string) => void;
  onUploadDocument: (file: File) => void;
}
```

### LLMS selector

Компонент выбора LLM провайдера.

**Props:**
```typescript
interface LLMS selectorProps {
  currentConfig: LLMConfig;
  providers: LLMProvider[];
  onConfigChange: (config: LLMConfig) => void;
}
```

## 🔌 API Клиент

### Использование

```typescript
import { apiClient } from '@/shared/api/client';

// Загрузка документа
const response = await apiClient.uploadDocument(file);
const { session_id, document_id } = response;

// Отправка запроса
const result = await apiClient.query(sessionId, query, documentIds);
const { message, sources, history } = result;

// Получение истории чата
const history = await apiClient.getChatHistory(sessionId);
```

### Типы данных

```typescript
// shared/types.ts
export interface DocumentInfo {
  id: string;
  filename: string;
  upload_date: string;
  chunks_count: number;
  pages_count: number;
  status: 'processing' | 'ready' | 'error';
  selected: boolean;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  sources?: Array<{
    filename: string;
    page: number;
    snippet: string;
  }>;
}

export interface LLMConfig {
  provider: 'openai' | 'ollama';
  model: string;
  api_key?: string;
}

export interface LLMProvider {
  name: string;
  models: string[];
}
```

## 🧪 Тестирование

### Запуск тестов

```bash
# Все тесты
npm run test

# Конкретный тест
npm run test -- components/chat-panel.test.tsx

# Тесты в watch режиме
npm run test:watch

# Тесты с покрытием
npm run test:coverage
```

### Написание тестов

Пример теста с Vitest и Testing Library:

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import ChatPanel from '@/components/chat-panel';

describe('ChatPanel', () => {
  it('отображает поле ввода сообщения', () => {
    render(<ChatPanel sessionId="test" messages={[]} onSendMessage={() => {}} isLoading={false} />);
    
    const input = screen.getByPlaceholderText('Введите ваш вопрос...');
    expect(input).toBeInTheDocument();
  });

  it('отправляет сообщение при нажатии Enter', () => {
    const onSendMessage = vi.fn();
    render(<ChatPanel sessionId="test" messages={[]} onSendMessage={onSendMessage} isLoading={false} />);
    
    const input = screen.getByPlaceholderText('Введите ваш вопрос...');
    fireEvent.change(input, { target: { value: 'Test message' } });
    fireEvent.keyDown(input, { key: 'Enter' });
    
    expect(onSendMessage).toHaveBeenCalledWith('Test message');
  });
});
```

## 🎯 Скрипты

### Development

```bash
npm run dev          # Запуск dev сервера
npm run build        # Сборка для продакшена
npm run start        # Запуск production сервера
npm run lint         # ESLint проверка
```

### Testing

```bash
npm run test         # Запуск всех тестов
npm run test:watch   # Watch режим
npm run test:coverage # Тесты с покрытием
```

### Export

```bash
npm run export              # Экспорт статических файлов
npm run export:backend      # Экспорт для интеграции с backend
npm run export:check        # Проверка экспорта
```

## 🌐 Браузерная совместимость

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 📱 Mobile Support

Приложение адаптивно и поддерживает мобильные устройства через Tailwind CSS responsive utilities.

## 🔒 Безопасность

### Рекомендации

1. **Не храните API ключи в клиентском коде**
   ```env
   # BAD: NEXT_PUBLIC_OPENAI_API_KEY=sk-...
   # GOOD: Используйте backend proxy
   ```

2. **Включите HTTPS в продакшене**

3. **Настройте Content Security Policy**
   ```html
   <meta http-equiv="Content-Security-Policy" 
         content="default-src 'self'; script-src 'self' 'unsafe-inline';">
   ```

4. **Валидируйте все пользовательские данные**

## 🐛 Отладка

### Development tools

- **React DevTools:** https://react.dev/reference/react-dom/client/createRoot#ref
- **Next.js DevTools:** Включены по умолчанию при запуске `npm run dev`

### Common issues

#### Порт 3000 занят

```bash
# Запуск на другом порту
PORT=3001 npm run dev
```

#### CORS ошибки

Убедитесь, что backend запущен и CORS настроен правильно.

#### TypeScript ошибки

```bash
# Проверка типов
npm run type-check
```

## 🤝 Вклад

### Правила коммитов

```
feat: новая функциональность
fix: исправление бага
docs: документация
style: форматирование
refactor: рефакторинг
test: тесты
chore: обновление зависимостей
```

### Процесс разработки

1. Создайте feature branch
   ```bash
   git checkout -b feature/новая-фича
   ```

2. Внесите изменения

3. Запустите тесты и линтер
   ```bash
   npm run test
   npm run lint
   ```

4. Закоммитьте изменения
   ```bash
   git add .
   git commit -m "feat: добавить новую функциональность"
   ```

5. Создайте Pull Request

## 📝 License

MIT License
