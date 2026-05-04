# Development Setup Guide

Полное руководство по настройке окружения для разработки RAG Chat Application.

## 📋 Требования

### Системные требования

- **ОС:** Windows 10+, macOS 10.15+, Linux (Ubuntu 20.04+)
- **RAM:** Минимум 4 GB (рекомендуется 8+ GB)
- **Disk:** Минимум 2 GB свободного места

### Программное обеспечение

| Компонент | Версия | Примечание |
|-----------|--------|------------|
| Python | 3.10+ | Для backend |
| Node.js | 18+ | Для frontend |
| npm/yarn | 9+/1.22+ | Менеджер пакетов |
| Git | 2.0+ | Система контроля версий |
| Docker | 20.0+ | Опционально, для контейнеризации |
| Ollama | 0.1.0+ | Опционально, для локальных LLM |

---

## 🐍 Backend Setup

### 1. Установка Python

#### Windows

1. Скачайте установщик с [python.org](https://www.python.org/downloads/)
2. Запустите установщик
3. ✅ Отметьте галочку "Add Python to PATH"
4. Завершите установку

Проверка:
```powershell
python --version
# Output: Python 3.10.x
```

#### macOS

```bash
# Через Homebrew
brew install python@3.10

# Или через официальный installer
curl https://www.python.org/ftp/python/3.10.0/Python-3.10.0.pkg -o python.pkg
open python.pkg
```

#### Linux (Ubuntu)

```bash
sudo apt update
sudo apt install python3.10 python3.10-venv python3-pip
```

### 2. Создание виртуального окружения

```bash
# Перейдите в директорию backend
cd rag_app/backend

# Создайте виртуальное окружение
python -m venv .venv

# Активируйте окружение
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
```

Вы должны увидеть `(.venv)` в начале строки терминала.

### 3. Установка зависимостей

```bash
# Установите зависимости из requirements.txt
pip install -r requirements.txt

# Проверьте установку
pip list
```

### 4. Настройка ChromaDB

ChromaDB используется для хранения векторных представлений документов.

```bash
# ChromaDB работает "из коробки", просто создайте директорию
mkdir -p chroma_db
```

### 5. Настройка Ollama (опционально)

Если вы хотите использовать локальные LLM вместо OpenAI:

#### Установка Ollama

**Windows:**
1. Скачайте installer с [ollama.com](https://ollama.com/download/windows)
2. Запустите установщик
3. Запустите Ollama из меню "Пуск"

**macOS:**
```bash
brew install ollama
ollama serve
```

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
sudo systemctl start ollama
```

#### Загрузка моделей

```bash
# Llama 2 (рекомендуется)
ollama pull llama2

# Mistral
ollama pull mistral

# Gemma
ollama pull gemma
```

### 6. Настройка OpenAI (опционально)

Если вы используете OpenAI API:

1. Зарегистрируйтесь на [platform.openai.com](https://platform.openai.com/)
2. Создайте API ключ в dashboard
3. Добавьте ключ в `.env` файл

### 7. Создание .env файла

```bash
# Создайте файл .env в директории backend
cd rag_app/backend
touch .env
```

Содержимое `.env`:

```env
# OpenAI API ключ (если используете OpenAI)
OPENAI_API_KEY=sk-your-openai-api-key-here

# Ollama базовый URL (по умолчанию)
OLLAMA_BASE_URL=http://localhost:11434

# Порт сервера (по умолчанию 8000)
PORT=8000

# Режим отладки
DEBUG=true
```

### 8. Запуск backend

```bash
# Запуск в режиме разработки с автоперезагрузкой
uvicorn main:app --reload --port 8000

# Запуск в продакшене
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

Backend запустится на: http://localhost:8000

Документация API: http://localhost:8000/docs

---

## 🎨 Frontend Setup

### 1. Установка Node.js

#### Windows

1. Скачайте installer с [nodejs.org](https://nodejs.org/)
2. Запустите установщик
3. Выберите "Automatically install necessary tools"

Проверка:
```powershell
node --version
npm --version
```

#### macOS

```bash
# Через Homebrew
brew install node@18

# Или через official installer
curl https://nodejs.org/dist/v18.0.0/node-v18.0.0.pkg -o node.pkg
open node.pkg
```

#### Linux (Ubuntu)

```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### 2. Установка зависимостей

```bash
# Перейдите в директорию frontend
cd rag_app/frontend_next

# Установите зависимости
npm install

# Или с yarn
yarn install
```

### 3. Настройка environment переменных

```bash
# Создайте .env.local
touch .env.local
```

Содержимое `.env.local`:

```env
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# OpenAI API ключ (опционально, предпочтительно через backend proxy)
NEXT_PUBLIC_OPENAI_API_KEY=sk-your-openai-api-key-here

# Ollama базовый URL
NEXT_PUBLIC_OLLAMA_BASE_URL=http://localhost:11434
```

### 4. Запуск frontend

```bash
# Запуск dev сервера
npm run dev

# Или с yarn
yarn dev
```

Frontend запустится на: http://localhost:3000

---

## 🔄 Запуск всего приложения

### Способ 1: Терминалы

**Terminal 1 - Backend:**
```bash
cd rag_app/backend
python -m venv .venv
.venv\Scripts\activate  # Windows
# или source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd rag_app/frontend_next
npm install
npm run dev
```

### Способ 2: Docker Compose (в разработке)

Создайте `docker-compose.yml`:

```yaml
version: '3.8'

services:
  backend:
    build: ./rag_app/backend
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - OLLAMA_BASE_URL=http://host.docker.internal:11434
    volumes:
      - ./rag_app/backend/uploads:/app/uploads
      - ./rag_app/backend/chroma_db:/app/chroma_db
    depends_on:
      - ollama

  frontend:
    build: ./rag_app/frontend_next
    ports:
      - "3000:3000"
    depends_on:
      - backend

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    command: ["ollama", "serve"]

volumes:
  ollama_data:
```

Запуск:
```bash
docker-compose up --build
```

---

## 🧪 Тестирование

### Backend тесты

```bash
cd rag_app/backend

# Активируйте venv
.venv\Scripts\activate  # Windows
# или source .venv/bin/activate  # macOS/Linux

# Запуск всех тестов
pytest tests/ -v

# Конкретный тест
pytest tests/test_upload.py -v

# Тесты с покрытием
pytest tests/ --cov=. --cov-report=html
```

### Frontend тесты

```bash
cd rag_app/frontend_next

# Запуск всех тестов
npm run test

# Конкретный тест
npm run test -- components/chat-panel.test.tsx

# Watch режим
npm run test:watch

# Тесты с покрытием
npm run test:coverage
```

---

## 🔧 Дополнительные инструменты

### Linting и форматирование

#### Backend

```bash
# Установка
pip install black flake8 isort

# Форматирование
black rag_app/backend/

# Проверка стиля
flake8 rag_app/backend/

# Сортировка импортов
isort rag_app/backend/
```

#### Frontend

```bash
# ESLint (встроен в package.json)
npm run lint

# Prettier (если настроен)
npm run format
```

### Pre-commit hooks

Установите pre-commit hooks для автоматической проверки перед коммитом:

```bash
# Установка pre-commit
pip install pre-commit

# Инициализация
pre-commit install

# Запуск вручную
pre-commit run --all-files
```

Создайте `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        language_version: python3

  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        additional_dependencies: [flake8-docstrings]

  - repo: https://github.com/pre-commit/mirrors-eslint
    rev: v8.56.0
    hooks:
      - id: eslint
        types: [file]
        files: \.(js|jsx|ts|tsx)$
        additional_dependencies:
          - eslint
          - eslint-plugin-react
          - eslint-plugin-next
```

---

## 🐛 Troubleshooting

### Common Backend Issues

#### Port 8000 already in use

```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux
lsof -ti:8000 | xargs kill -9
```

#### ImportError: No module named 'fastapi'

```bash
# Проверьте активацию venv
# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

# Переустановите зависимости
pip install -r requirements.txt
```

#### ChromaDB connection error

```bash
# Удалите поврежденную базу данных
rm -rf rag_app/backend/chroma_db/*

# Перезапустите backend
uvicorn main:app --reload
```

### Common Frontend Issues

#### Port 3000 already in use

```bash
# Запуск на другом порту
PORT=3001 npm run dev
```

#### Module not found errors

```bash
# Удалите node_modules и переустановите
rm -rf node_modules package-lock.json
npm install
```

#### TypeScript errors

```bash
# Проверка типов
npm run type-check

# Исправление автоматических ошибок
npm run fix
```

---

## 📚 Полезные ссылки

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Ollama Documentation](https://github.com/ollama/ollama/blob/main/docs/api.md)
- [OpenAI API Documentation](https://platform.openai.com/docs/api-reference)

---

## ✅ Checklist для новой разработки

- [ ] Установлен Python 3.10+
- [ ] Установлен Node.js 18+
- [ ] Создано виртуальное окружение для backend
- [ ] Установлены все зависимости backend
- [ ] Установлены все зависимости frontend
- [ ] Создан .env файл с необходимыми переменными
- [ ] Backend запущен и доступен на http://localhost:8000
- [ ] Frontend запущен и доступен на http://localhost:3000
- [ ] Протестирована загрузка документа
- [ ] Протестирован чат с LLM
- [ ] Установлены pre-commit hooks
- [ ] Запущены все тесты и они проходят
