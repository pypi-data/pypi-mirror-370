# AST Парсер выражений для Vector Store

## Обзор

Vector Store поддерживает парсер выражений (AST - Abstract Syntax Tree) для создания типизированных и безопасных запросов фильтрации. Это позволяет передавать серверу готовые разобранные выражения вместо простых словарей с операторами.

## Архитектурные принципы

### 1. **Pydantic как основа запросов**
- Все запросы строятся на Pydantic моделях
- Автоматическая валидация типов и значений
- Встроенная сериализация/десериализация
- Генерация JSON Schema

### 2. **Автоматическое определение операций по типам**
- Анализ типов полей `SemanticChunk`
- Автоматическое сопоставление с классами фильтров
- Исключение ошибок ручного назначения

### 3. **Единая иерархия классов операций**
- Общий базовый класс `BaseFilter` для всех операций
- Полиморфизм через единый интерфейс
- Типизированные поля с общим предком

## Классы фильтров

### ExactFilter - Точное совпадение
**Автоматически применяется к:**
- `ChunkId` полям (uuid, source_id, task_id, etc.)
- `Enum` полям (type, role, status, language, block_type)
- `bool` полям (is_public, used_in_generation)

**Поддерживаемые операции:**
- `value` - точное равенство
- `in_` - значение входит в список

```python
from chunk_metadata_adapter.chunk_query import ExactFilter

# Простое значение
type_filter = ExactFilter(value="DocBlock")

# Множественный выбор
status_filter = ExactFilter(in_=["new", "processed"])
```

### NumericFilter - Числовые операции
**Автоматически применяется к:**
- `int` полям: ordinal, start, end, year, feedback_*, block_index, source_lines_*
- `float` полям: quality_score, coverage, cohesion, boundary_prev, boundary_next

**Поддерживаемые операции:**
- `value` - точное равенство
- `gt`, `gte`, `lt`, `lte` - операторы сравнения
- `in_` - значение входит в список
- `between` - диапазон [min, max]

```python
from chunk_metadata_adapter.chunk_query import NumericFilter

# Точное значение
year_filter = NumericFilter(value=2024)

# Операторы сравнения
quality_filter = NumericFilter(gte=0.8, lte=1.0)

# Диапазон
ordinal_filter = NumericFilter(between=(10, 100))

# Множественный выбор
year_filter = NumericFilter(in_=[2023, 2024, 2025])
```

### TextFilter - Текстовый поиск
**Автоматически применяется к:**
- `str` полям: project, body, text, summary, source_path, category, title, source, chunking_version, sha256, created_at

**Поддерживаемые операции:**
- `value` - точное равенство
- `in_` - значение входит в список
- `contains` - содержит подстроку
- `startswith` - начинается с
- `endswith` - заканчивается на
- `regex` - регулярное выражение

```python
from chunk_metadata_adapter.chunk_query import TextFilter

# Точное совпадение
project_filter = TextFilter(value="my_project")

# Поиск по подстроке
body_filter = TextFilter(contains="python")

# Начинается с
title_filter = TextFilter(startswith="Chapter")

# Регулярное выражение
sha256_filter = TextFilter(regex=r"^a[0-9a-f]{63}$")
```

### ListFilter - Операции со списками
**Автоматически применяется к:**
- `List[str]` полям: tags, links

**Поддерживаемые операции:**
- `contains` - список содержит элемент
- `contains_any` - список содержит любой из элементов
- `contains_all` - список содержит все элементы
- `size` - размер списка
- `empty` - список пустой
- `not_empty` - список не пустой

```python
from chunk_metadata_adapter.chunk_query import ListFilter

# Содержит элемент
tags_filter = ListFilter(contains="python")

# Содержит любой из элементов
tags_filter = ListFilter(contains_any=["python", "java"])

# Содержит все элементы
tags_filter = ListFilter(contains_all=["web", "frontend"])

# Размер списка
tags_filter = ListFilter(size=NumericFilter(gte=2))

# Пустой/не пустой
links_filter = ListFilter(empty=True)
```

### DictFilter - Операции с JSON объектами
**Автоматически применяется к:**
- `dict` полям: block_meta

**Поддерживаемые операции:**
- `has_key` - содержит ключ
- `key_value` - ключ имеет значение
- `empty` - объект пустой

```python
from chunk_metadata_adapter.chunk_query import DictFilter

# Содержит ключ
block_meta_filter = DictFilter(has_key="author")

# Ключ имеет значение
block_meta_filter = DictFilter(key_value={"author": "John"})
```

## Автоматическое сопоставление типов

| Тип поля в SemanticChunk | Автоматически определяемый фильтр | Пример |
|--------------------------|-----------------------------------|---------|
| `ChunkId` | `ExactFilter` | `uuid: ChunkId` → `uuid: Optional[ExactFilter]` |
| `ChunkType` (enum) | `ExactFilter` | `type: ChunkType` → `type: Optional[ExactFilter]` |
| `Optional[bool]` | `ExactFilter` | `is_public: Optional[bool]` → `is_public: Optional[ExactFilter]` |
| `Optional[int]` | `NumericFilter` | `ordinal: Optional[int]` → `ordinal: Optional[NumericFilter]` |
| `Optional[float]` | `NumericFilter` | `quality_score: Optional[float]` → `quality_score: Optional[NumericFilter]` |
| `Optional[str]` | `TextFilter` | `project: Optional[str]` → `project: Optional[TextFilter]` |
| `Optional[List[str]]` | `ListFilter` | `tags: Optional[List[str]]` → `tags: Optional[ListFilter]` |
| `Optional[dict]` | `DictFilter` | `block_meta: Optional[dict]` → `block_meta: Optional[DictFilter]` |

## Примеры использования

### Простой запрос
```python
from chunk_metadata_adapter.chunk_query import ChunkQuery, ExactFilter, NumericFilter, TextFilter

query = ChunkQuery(
    type=ExactFilter(value="DocBlock"),      # Автоматически определено как ExactFilter
    quality_score=NumericFilter(gte=0.8),   # Автоматически определено как NumericFilter
    tags=ListFilter(contains="python")      # Автоматически определено как ListFilter
)
```

### Сложный запрос
```python
query = ChunkQuery(
    # Enum поле → ExactFilter
    type=ExactFilter(in_=["DocBlock", "Draft"]),
    
    # int поле → NumericFilter
    year=NumericFilter(between=(2020, 2024)),
    
    # float поле → NumericFilter
    quality_score=NumericFilter(gte=0.8, lte=1.0),
    
    # List[str] поле → ListFilter
    tags=ListFilter(contains_all=["python", "web"]),
    
    # str поле → TextFilter
    body=TextFilter(contains="function"),
    
    # str поле → TextFilter
    project=TextFilter(startswith="ml_"),
    
    # bool поле → ExactFilter
    is_public=ExactFilter(value=True),
    
    # dict поле → DictFilter
    block_meta=DictFilter(has_key="version")
)
```

### Использование в клиенте
```python
# Поиск по AST запросу
results = await client.search_by_ast_query(query, limit=5)

# Автоматическое построение AST запроса
ast_query = await client.build_ast_query(
    type="DocBlock",                    # ExactFilter (enum)
    quality_score__gte=0.8,            # NumericFilter (float)
    year__between=(2020, 2024),        # NumericFilter (int)
    tags__contains="python",           # ListFilter (list)
    body__contains="function",         # TextFilter (string)
    is_public=True                     # ExactFilter (bool)
)
results = await client.search_by_ast_query(ast_query)
```

## Преимущества AST подхода

### ✅ **Безопасность типов**
- Невозможно создать некорректный запрос
- Все ошибки выявляются на этапе создания
- IDE автокомплит показывает только допустимые операции

### ✅ **Автоматизация**
- Новые поля автоматически получают правильные фильтры
- Нет необходимости в ручном назначении типов операций
- Согласованность между моделью данных и запросами

### ✅ **Расширяемость**
- Легко добавлять новые типы операций
- Простое расширение для новых типов данных
- Модульная архитектура

### ✅ **Читаемость и поддержка**
- Код сам документирует доступные операции
- Явная связь между типами данных и операциями
- Удобная отладка и тестирование

## Процесс выполнения запроса

### 1. Создание типизированного запроса
```python
query = ChunkQuery(
    type=ExactFilter(value="DocBlock"),
    quality_score=NumericFilter(gte=0.8)
)
```

### 2. Преобразование в AST
```python
ast_expression = query.to_ast()
```

### 3. Передача серверу
```python
metadata_filter = {"ast_expression": ast_expression}
response = await client.search_chunks(metadata_filter=metadata_filter)
```

### 4. Выполнение на сервере
Сервер парсит AST выражение и выполняет оптимизированный запрос к базе данных.

---

*Последнее обновление: 2024-12-19* 