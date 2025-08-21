# Дерево каталогов и файлов проекта

```
vector_store_client/
├── 📄 LICENSE                     # MIT License
├── 📄 README.md                   # Основная документация (EN)
├── 📄 README.ru.md               # Документация на русском
├── 📄 pyproject.toml             # Конфигурация проекта
├── 📄 setup.py                   # Альтернативная конфигурация
├── 📄 requirements.txt           # Зависимости для разработки
├── 📄 .gitignore                 # Исключения Git
├── 📄 .pytest.ini               # Конфигурация pytest
├── 📄 .coveragerc               # Конфигурация coverage
├── 📄 MANIFEST.in               # Файлы для PyPI
│
├── 📁 requirements/              # Зависимости по категориям
│   ├── 📄 base.txt              # Базовые зависимости
│   ├── 📄 dev.txt               # Зависимости для разработки
│   └── 📄 test.txt              # Зависимости для тестирования
│
├── 📁 vector_store_client/       # Основной пакет
│   ├── 📄 __init__.py           # Экспорт публичного API
│   ├── 📄 client.py             # Основной класс клиента
│   ├── 📄 base_client.py        # Базовый класс клиента
│   ├── 📄 models.py             # Модели данных
│   ├── 📄 types.py              # Типы данных
│   ├── 📄 exceptions.py         # Исключения
│   ├── 📄 validation.py         # Валидация
│   ├── 📄 utils.py              # Утилиты
│   │
│   └── 📁 examples/             # Примеры использования
│       ├── 📄 __init__.py
│       ├── 📄 basic_usage.py
│       ├── 📄 advanced_usage.py
│       ├── 📄 docstore_demo.py
│       ├── 📄 logger_demo.py
│       ├── 📄 memory_demo.py
│       │
│       ├── 📁 integration_examples/
│       │   ├── 📄 fastapi_integration.py
│       │   └── 📄 jupyter_example.ipynb
│       │
│       └── 📁 use_cases/
│           ├── 📄 content_recommender.py
│           ├── 📄 document_clustering.py
│           ├── 📄 qa_system.py
│           └── 📄 semantic_search_engine.py
│
├── 📁 tests/                    # Тесты
│   ├── 📄 __init__.py
│   ├── 📄 test_client.py
│   ├── 📄 test_models.py
│   ├── 📄 test_validation.py
│   ├── 📄 test_exceptions.py
│   ├── 📄 test_utils.py
│   ├── 📄 conftest.py
│   │
│   ├── 📁 integration/          # Интеграционные тесты
│   │   ├── 📄 test_real_server.py
│   │   └── 📄 test_commands.py
│   │
│   └── 📁 fixtures/             # Тестовые данные
│       ├── 📄 sample_chunks.json
│       └── 📄 mock_responses.json
│
├── 📁 docs/                     # Документация
│   ├── 📄 README.md
│   ├── 📄 api.md               # API Reference
│   ├── 📄 development.md       # Руководство разработчика
│   │
│   ├── 📁 standards/           # Стандарты разработки
│   │   ├── 📄 project_structure.md
│   │   ├── 📄 naming_conventions.md
│   │   ├── 📄 code_style.md
│   │   └── 📄 directory_tree.md
│   │
│   ├── 📁 commands/            # Документация команд API
│   │   ├── 📄 help_all.json
│   │   ├── 📄 chunk_create.json
│   │   ├── 📄 search.json
│   │   ├── 📄 chunk_delete.json
│   │   ├── 📄 config.json
│   │   ├── 📄 health.json
│   │   ├── 📄 find_duplicate_uuids.json
│   │   ├── 📄 force_delete_by_uuids.json
│   │   ├── 📄 chunk_hard_delete.json
│   │   ├── 📄 chunk_deferred_cleanup.json
│   │   ├── 📄 clean_faiss_orphans.json
│   │   └── 📄 reindex_missing_embeddings.json
│   │
│   └── 📁 chunk-metadata-adapter/  # Документация адаптера
│       ├── 📄 README.md
│       ├── 📄 INDEX.md
│       ├── 📄 Metadata.md
│       ├── 📄 Usage.md
│       ├── 📄 Component_Interaction.md
│       └── 📄 data_lifecycle.md
│
├── 📁 examples/                 # Примеры использования (корневой уровень)
│   ├── 📄 basic_usage.py
│   ├── 📄 advanced_usage.py
│   ├── 📄 write_all_types.py
│   │
│   └── 📁 updated_api/
│       ├── 📄 basic_usage.py
│       └── 📄 batch_operations.py
│
├── 📁 dist/                     # Собранные пакеты (автогенерируется)
├── 📁 build/                    # Временные файлы сборки (автогенерируется)
├── 📁 vector_store_client.egg-info/  # Метаданные пакета (автогенерируется)
├── 📁 .pytest_cache/           # Кэш pytest (автогенерируется)
├── 📁 .coverage                # Отчет о покрытии (автогенерируется)
└── 📁 .venv/                   # Виртуальное окружение (автогенерируется)
```

## Описание каталогов

### 📁 vector_store_client/
Основной пакет с исходным кодом клиента.

### 📁 tests/
Модульные и интеграционные тесты.

### 📁 docs/
Документация проекта, включая стандарты разработки.

### 📁 examples/
Примеры использования клиента.

### 📁 requirements/
Зависимости проекта, разделенные по категориям.

## Автогенерируемые каталоги

- `dist/` - собранные пакеты для PyPI
- `build/` - временные файлы сборки
- `vector_store_client.egg-info/` - метаданные пакета
- `.pytest_cache/` - кэш тестов
- `.coverage` - отчет о покрытии кода
- `.venv/` - виртуальное окружение

## Файлы конфигурации

- `pyproject.toml` - основная конфигурация проекта
- `setup.py` - альтернативная конфигурация
- `.gitignore` - исключения для Git
- `.pytest.ini` - конфигурация тестов
- `.coveragerc` - конфигурация покрытия
- `MANIFEST.in` - файлы для включения в PyPI 