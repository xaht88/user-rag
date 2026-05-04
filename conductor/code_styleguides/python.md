# Python Styleguide

## 📚 Основы

**Стандарт:** PEP 8 (https://pep8.org/)  
**Форматер:** Black (https://black.readthedocs.io/)  
**Линтер:** Ruff (https://docs.astral.sh/ruff/)  
**Type Checking:** MyPy (https://mypy.readthedocs.io/)

---

## 🎯 Основные принципы

1. **Читаемость важнее хитростей** — код должен быть понятным
2. **Явность лучше неявности** (Zen of Python)
3. **DRY (Don't Repeat Yourself)** — избегать дублирования
4. **KISS (Keep It Simple, Stupid)** — простые решения лучше сложных
5. **YAGNI (You Aren't Gonna Need It)** — не добавлять функционал заранее

---

## 📐 Форматирование

### Отступы

```python
# ✅ Правильно
def calculate_total(items):
    total = 0
    for item in items:
        total += item.price
    return total

# ❌ Неправильно
def calculate_total(items):
    total=0
    for item in items:
        total+=item.price
    return total
```

- **Отступы:** 4 пробела (не табы!)
- **Максимальная длина строки:** 88 символов (Black default)
- **Максимальная длина функции:** 50 строк

### Пустые строки

```python
# ✅ Правильно
def function_a():
    pass


def function_b():
    pass


class MyClass:
    pass


# Внутри класса/функции — одна пустая строка между методами
class MyClass:
    def method_a(self):
        pass

    def method_b(self):
        pass
```

- **Между импортами и кодом:** 2 пустые строки
- **Между функциями/классами:** 2 пустые строки
- **Внутри функций/классов:** 1 пустая строка

### Imports

```python
# ✅ Правильно - порядок импортов
import os
import sys
from typing import List, Dict, Optional

import pandas as pd
import numpy as np

from django.db import models
from fastapi import APIRouter

from local_module import my_function
```

**Порядок импортов:**
1. Стандартная библиотека (os, sys, typing)
2. Третьи партии (pandas, numpy, django)
3. Локальные модули (local_module)

**Группировка:**
- Каждый импорт в отдельной строке
- От пустой строки между группами

### Форматирование строк

```python
# ✅ Правильно - f-strings
name = "Alice"
age = 30
message = f"Hello, {name}. You are {age} years old."

# ✅ Правильно - длинные строки
long_string = (
    "This is a very long string that "
    "exceeds the line length limit"
)

# ✅ Правильно - f-strings с выражениями
total = sum([1, 2, 3, 4, 5])
result = f"The sum is {total}"
```

---

## 🏗️ Структура кода

### Файлы и модули

```
backend/
├── main.py                  # Entry point
├── config.py               # Configuration
├── models.py               # Database models
├── schemas.py              # Pydantic schemas
├── routes/
│   ├── __init__.py
│   ├── documents.py        # Document endpoints
│   ├── sessions.py         # Session endpoints
│   └── llm.py              # LLM endpoints
├── services/
│   ├── __init__.py
│   ├── document_processor.py
│   ├── embedding_service.py
│   └── llm_connector.py
├── utils/
│   ├── __init__.py
│   ├── validators.py
│   └── helpers.py
└── tests/
    ├── __init__.py
    ├── test_document_processor.py
    └── test_llm_connector.py
```

### Функции и методы

```python
# ✅ Правильно - функции с понятными именами
def calculate_document_embedding(documents: List[Document]) -> List[np.ndarray]:
    """Calculate embeddings for a list of documents.
    
    Args:
        documents: List of document objects
        
    Returns:
        List of numpy arrays containing embeddings
        
    Raises:
        ValueError: If documents list is empty
    """
    if not documents:
        raise ValueError("Documents list cannot be empty")
    
    embeddings = []
    for doc in documents:
        embedding = generate_embedding(doc.content)
        embeddings.append(embedding)
    
    return embeddings


# ✅ Правильно - короткие вспомогательные функции
def is_valid_filename(filename: str) -> bool:
    """Check if filename is valid."""
    return bool(filename) and not filename.startswith('.')
```

### Классы

```python
# ✅ Правильно - классы с docstrings
class DocumentProcessor:
    """Process documents for RAG system.
    
    Handles file parsing, chunking, and metadata extraction.
    """
    
    SUPPORTED_FORMATS = ['.pdf', '.docx', '.txt', '.md']
    
    def __init__(self, chunk_size: int = 512, overlap: int = 50):
        """Initialize document processor.
        
        Args:
            chunk_size: Size of text chunks in tokens
            overlap: Overlap between chunks in tokens
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def process(self, file_path: str) -> Document:
        """Process a document file.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Processed Document object
            
        Raises:
            FileNotFoundError: If file doesn't exist
            UnsupportedFormatError: If format not supported
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Implementation...
```

---

## 🧪 Тестирование

### Структура тестов

```python
# ✅ Правильно - тесты с понятными именами
import pytest
from mymodule import calculate_total


class TestCalculateTotal:
    """Tests for calculate_total function."""
    
    def test_empty_list(self):
        """Test with empty list returns 0."""
        assert calculate_total([]) == 0
    
    def test_single_item(self):
        """Test with single item."""
        assert calculate_total([10]) == 10
    
    def test_multiple_items(self):
        """Test with multiple items."""
        assert calculate_total([1, 2, 3, 4, 5]) == 15
    
    def test_negative_numbers(self):
        """Test with negative numbers."""
        assert calculate_total([-1, -2, -3]) == -6


# ✅ Правильно - use fixtures
import pytest
from pytest import fixture


@fixture
def sample_documents():
    """Sample documents for testing."""
    return [
        Document(id="1", content="Hello world"),
        Document(id="2", content="Test document"),
    ]


class TestDocumentProcessor:
    def test_process_documents(self, sample_documents):
        """Test processing sample documents."""
        processor = DocumentProcessor()
        result = processor.process_documents(sample_documents)
        assert len(result) == 2
```

### pytest конвенции

- Тесты в файлах `test_*.py` или `*_test.py`
- Функции тестов начинаются с `test_`
- Классы тестов начинаются с `Test`
- Использовать fixtures для повторного использования тестовых данных
- Покрытие > 80%

---

## 📋 Документирование

### Docstrings (Google Style)

```python
def fetch_user_data(user_id: int) -> Dict[str, Any]:
    """Fetch user data from database.
    
    Retrieves user information including profile, preferences,
    and activity history.
    
    Args:
        user_id: The unique identifier of the user
        
    Returns:
        Dictionary containing user data with keys:
        - id: User ID
        - name: User name
        - email: User email
        - created_at: Creation timestamp
        
    Raises:
        UserNotFoundError: If user with given ID doesn't exist
        DatabaseError: If database query fails
        
    Example:
        >>> user = fetch_user_data(123)
        >>> print(user['name'])
        Alice
    """
    pass
```

**Структура docstring:**
1. Краткое описание (1 строка)
2. Разъяснение (если нужно)
3. Args: аргументы
4. Returns: возвращаемое значение
5. Raises: исключения
6. Example: пример использования (опционально)

### Type Hints

```python
# ✅ Правильно - явные type hints
from typing import List, Dict, Optional, Union, Callable

def process_items(
    items: List[Dict[str, Any]],
    processor: Callable[[Dict], Any],
    max_items: Optional[int] = None
) -> Union[List[Any], None]:
    """Process a list of items."""
    pass


# ✅ Правильно - dataclasses
from dataclasses import dataclass, field
from datetime import datetime
from typing import List


@dataclass
class Document:
    """Document model."""
    id: str
    filename: str
    content: str
    uploaded_at: datetime = field(default_factory=datetime.utcnow)
    tags: List[str] = field(default_factory=list)
```

---

## 🔐 Безопасность

### Обработка ошибок

```python
# ✅ Правильно - обработка ошибок
try:
    result = risky_operation()
except FileNotFoundError as e:
    logger.warning(f"File not found: {e}")
    return None
except ValueError as e:
    logger.error(f"Invalid value: {e}")
    raise
except Exception as e:
    logger.exception(f"Unexpected error: {e}")
    raise
```

### Секретные данные

```python
# ✅ Правильно - не хардкодить секреты
from dotenv import load_dotenv
import os

load_dotenv()  # Загружает из .env файла

API_KEY = os.getenv('API_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')

# ❌ Неправильно
API_KEY = "sk-1234567890abcdef"  # НИКОГДА так не делать!
```

---

## 🚀 Производительность

### Оптимизация

```python
# ✅ Правильно - использовать list comprehension
squares = [x**2 for x in range(1000)]

# ✅ Правильно - использовать генераторы для больших данных
squares = (x**2 for x in range(1000000))

# ✅ Правильно - использовать set для быстрых проверок
def find_duplicates(items: List[str]) -> List[str]:
    seen = set()
    duplicates = set()
    for item in items:
        if item in seen:
            duplicates.add(item)
        else:
            seen.add(item)
    return list(duplicates)
```

---

## 📝 Checklist перед коммитом

- [ ] Код отформатирован Black'ом (`black .`)
- [ ] Нет linting ошибок (`ruff check .`)
- [ ] Type checking проходит (`mypy .`)
- [ ] Все тесты проходят (`pytest`)
- [ ] Docstrings добавлены для новых функций/классов
- [ ] Type hints добавлены для новых функций
- [ ] Нет hardcoded секретов
- [ ] Нет debug print/statement
- [ ] Коммит сообщение следует конвенции

---

## 🛠️ Инструменты

### Установка

```bash
# Development dependencies
pip install black ruff mypy pytest pytest-cov
```

### Команды

```bash
# Format code
black .

# Lint code
ruff check .

# Type checking
mypy .

# Run tests
pytest -v --cov=.

# Format and lint
black . && ruff check .
```

---

**Последнее обновление:** 2026-05-04  
**Версия styleguide:** 1.0.0
