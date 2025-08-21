# Стандарт расположения и именования файлов для PyPI

## Структура проекта для публикации

```
vector_store_client/
├── LICENSE                     # MIT License
├── README.md                   # Основная документация на английском
├── README.ru.md               # Документация на русском
├── pyproject.toml             # Конфигурация проекта (основной)
├── setup.py                   # Альтернативная конфигурация (для совместимости)
├── requirements.txt           # Зависимости для разработки
├── requirements/
│   ├── base.txt              # Базовые зависимости
│   ├── dev.txt               # Зависимости для разработки
│   └── test.txt              # Зависимости для тестирования
├── vector_store_client/       # Основной пакет
│   ├── __init__.py           # Экспорт публичного API
│   ├── client.py             # Основной класс клиента
│   ├── base_client.py        # Базовый класс клиента
│   ├── models.py             # Модели данных
│   ├── types.py              # Типы данных
│   ├── exceptions.py         # Исключения
│   ├── validation.py         # Валидация
│   ├── utils.py              # Утилиты
│   └── examples/             # Примеры использования
│       ├── __init__.py
│       ├── basic_usage.py
│       ├── advanced_usage.py
│       └── integration_examples/
├── tests/                    # Тесты
│   ├── __init__.py
│   ├── test_client.py
│   ├── test_models.py
│   ├── test_validation.py
│   └── conftest.py
├── docs/                     # Документация
│   ├── README.md
│   ├── api.md
│   ├── development.md
│   ├── standards/            # Стандарты разработки
│   │   ├── project_structure.md
│   │   ├── naming_conventions.md
│   │   └── code_style.md
│   └── commands/             # Документация команд API
├── examples/                 # Примеры использования (корневой уровень)
│   ├── basic_usage.py
│   ├── advanced_usage.py
│   └── updated_api/
├── .gitignore               # Исключения Git
├── .pytest.ini             # Конфигурация pytest
├── .coveragerc             # Конфигурация coverage
└── MANIFEST.in             # Дополнительные файлы для PyPI
```

## Обязательные файлы для PyPI

### pyproject.toml
```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "vector-store-client"
version = "1.0.0"
description = "Async client for Vector Store API"
readme = "README.md"
license = {text = "MIT"}
authors = [
    {name = "Vasily Zdanovskiy", email = "vasilyvz@gmail.com"}
]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]
requires-python = ">=3.8"
dependencies = [
    "httpx>=0.24.0",
    "pydantic>=2.0.0",
    "chunk_metadata_adapter>=2.3.0",
    "typing-extensions>=4.5.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.0.0",
    "black>=23.0.0",
    "isort>=5.12.0",
    "mypy>=1.0.0",
]

[project.urls]
Homepage = "https://github.com/vasilyvz/vector_store_client"
Documentation = "https://github.com/vasilyvz/vector_store_client/docs"
Repository = "https://github.com/vasilyvz/vector_store_client.git"
Issues = "https://github.com/vasilyvz/vector_store_client/issues"
```

### MANIFEST.in
```
include LICENSE
include README.md
include README.ru.md
include requirements.txt
include requirements/*.txt
include pyproject.toml
include setup.py
recursive-include vector_store_client *.py
recursive-include tests *.py
recursive-include docs *.md
recursive-include examples *.py
```

### .gitignore
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Testing
.coverage
.pytest_cache/
.tox/
htmlcov/

# OS
.DS_Store
Thumbs.db
```

## Правила именования

### Файлы
- **snake_case** для всех файлов Python: `client.py`, `base_client.py`
- **kebab-case** для документации: `technical-specification.md`
- **UPPER_CASE** для конфигурационных файлов: `LICENSE`, `README.md`

### Пакеты
- **snake_case** для пакетов: `vector_store_client`
- **snake_case** для подпакетов: `integration_examples`

### Модули
- **snake_case** для модулей: `semantic_chunk.py`, `data_types.py`
- Описательные имена: `client.py`, `exceptions.py`, `validation.py` 