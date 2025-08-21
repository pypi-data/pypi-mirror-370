# ChunkQuery: Типизированная система фильтров

## 📋 Общее описание

**ChunkQuery** - это типизированная система построения запросов для поиска и фильтрации семантических чанков. Система обеспечивает строгий контроль типов через Pydantic и предотвращает использование неподдерживаемых операций для конкретных типов полей.

## 🎯 Архитектурные принципы

1. **Строгая типизация**: Каждое поле поддерживает только допустимые для его типа операции
2. **Pydantic валидация**: Автоматическая проверка правильности запросов на этапе создания
3. **Расширяемость**: Легко добавлять новые типы операций и поля
4. **Читаемость**: Интуитивно понятный синтаксис запросов
5. **Безопасность**: Невозможно создать некорректный запрос
6. **🔥 Автоматическое определение операций**: Доступные операции определяются типом поля автоматически

## 🤖 Автоматическое сопоставление типов с операциями

### Принцип работы
Система анализирует тип поля в `SemanticChunk` и автоматически определяет, какой тип фильтра применим:

```python
def get_filter_type_for_field(field_type: Type) -> Type[BaseFilter]:
    """Автоматически определяет тип фильтра для поля по его типу"""
    
    # Убираем Optional обертку
    base_type = get_origin(field_type) or field_type
    if base_type is Union:
        args = get_args(field_type)
        if len(args) == 2 and type(None) in args:
            base_type = next(arg for arg in args if arg is not type(None))
    
    # UUID поля (ChunkId)
    if base_type is ChunkId:
        return ExactFilter
        
    # Enum поля
    if isinstance(base_type, type) and issubclass(base_type, Enum):
        return ExactFilter
        
    # Булевы поля
    if base_type is bool:
        return ExactFilter
        
    # Числовые поля  
    if base_type in (int, float):
        return NumericFilter
        
    # Текстовые поля
    if base_type is str:
        return TextFilter
        
    # Списковые поля
    if get_origin(base_type) is list:
        return ListFilter
        
    # Dict поля (block_meta)
    if base_type is dict:
        return DictFilter  # Специальный фильтр для JSON
        
    # По умолчанию - точное совпадение
    return ExactFilter
```

### 🗂️ Автоматическое сопоставление полей SemanticChunk

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

### 🏭 Автоматическая генерация ChunkQuery

```python
def generate_chunk_query_class() -> Type[BaseModel]:
    """Автоматически генерирует ChunkQuery класс на основе полей SemanticChunk"""
    
    query_fields = {}
    
    # Анализируем все поля SemanticChunk
    for field_name, field_info in SemanticChunk.model_fields.items():
        field_type = field_info.annotation
        filter_class = get_filter_type_for_field(field_type)
        
        # Добавляем поле в ChunkQuery как Optional[FilterClass]
        query_fields[field_name] = (Optional[filter_class], None)
        
    # Создаем динамический класс
    ChunkQueryGenerated = create_model(
        'ChunkQuery',
        __base__=BaseModel,
        **query_fields
    )
    
    return ChunkQueryGenerated
```

## 🔧 Классы операций

### 1. **ExactFilter** - Точное совпадение
**Автоматически применяется к:**
- `ChunkId` полям (uuid, source_id, task_id, etc.)
- `Enum` полям (type, role, status, language, block_type)  
- `bool` полям (is_public, used_in_generation)

**Поддерживаемые операции:**
- `value` - точное равенство
- `in` - значение входит в список

**Синтаксис:**
```python
# Простое значение
type = ExactFilter(value="DocBlock")

# Множественный выбор  
status = ExactFilter(in_=["new", "processed"])
```

### 2. **NumericFilter** - Числовые операции
**Автоматически применяется к:**
- `int` полям: ordinal, start, end, year, feedback_*, block_index, source_lines_*
- `float` полям: quality_score, coverage, cohesion, boundary_prev, boundary_next

**Поддерживаемые операции:**
- `value` - точное равенство
- `gt`, `gte`, `lt`, `lte` - операторы сравнения
- `in_` - значение входит в список
- `between` - диапазон [min, max]

**Синтаксис:**
```python
# Точное значение
year = NumericFilter(value=2024)

# Операторы сравнения
quality_score = NumericFilter(gte=0.8, lte=1.0)

# Диапазон
ordinal = NumericFilter(between=(10, 100))

# Множественный выбор
year = NumericFilter(in_=[2023, 2024, 2025])
```

### 3. **TextFilter** - Текстовый поиск
**Автоматически применяется к:**
- `str` полям: project, body, text, summary, source_path, category, title, source, chunking_version, sha256, created_at

**Поддерживаемые операции:**
- `value` - точное равенство
- `in_` - значение входит в список  
- `contains` - содержит подстроку
- `startswith` - начинается с
- `endswith` - заканчивается на
- `regex` - регулярное выражение

**Синтаксис:**
```python
# Точное совпадение
project = TextFilter(value="my_project")

# Поиск по подстроке
body = TextFilter(contains="python")

# Начинается с
title = TextFilter(startswith="Chapter")

# Регулярное выражение  
sha256 = TextFilter(regex=r"^a[0-9a-f]{63}$")
```

### 4. **ListFilter** - Операции со списками
**Автоматически применяется к:**
- `List[str]` полям: tags, links

**Поддерживаемые операции:**
- `contains` - список содержит элемент
- `contains_any` - список содержит любой из элементов
- `contains_all` - список содержит все элементы  
- `size` - размер списка
- `empty` - список пустой
- `not_empty` - список не пустой

**Синтаксис:**
```python
# Содержит элемент
tags = ListFilter(contains="python")

# Содержит любой из элементов
tags = ListFilter(contains_any=["python", "java"])

# Содержит все элементы
tags = ListFilter(contains_all=["web", "frontend"])

# Размер списка
tags = ListFilter(size=NumericFilter(gte=2))

# Пустой/не пустой
links = ListFilter(empty=True)
```

### 5. **DictFilter** - Операции с JSON объектами
**Автоматически применяется к:**
- `dict` полям: block_meta

**Поддерживаемые операции:**
- `has_key` - содержит ключ
- `key_value` - ключ имеет значение
- `empty` - объект пустой

```python
# Содержит ключ
block_meta = DictFilter(has_key="author")

# Ключ имеет значение
block_meta = DictFilter(key_value={"author": "John"})
```

## 💡 Примеры автоматической генерации

### Автоматически сгенерированный ChunkQuery
```python
# Этот класс генерируется автоматически на основе SemanticChunk
class ChunkQuery(BaseModel):
    # ChunkId поля → ExactFilter
    uuid: Optional[ExactFilter] = None
    source_id: Optional[ExactFilter] = None
    task_id: Optional[ExactFilter] = None
    # ... остальные UUID поля
    
    # Enum поля → ExactFilter  
    type: Optional[ExactFilter] = None        # ChunkType
    role: Optional[ExactFilter] = None        # ChunkRole
    status: Optional[ExactFilter] = None      # ChunkStatus
    language: Optional[ExactFilter] = None    # LanguageEnum
    block_type: Optional[ExactFilter] = None  # BlockType
    
    # bool поля → ExactFilter
    is_public: Optional[ExactFilter] = None
    used_in_generation: Optional[ExactFilter] = None
    
    # int поля → NumericFilter
    ordinal: Optional[NumericFilter] = None
    start: Optional[NumericFilter] = None
    end: Optional[NumericFilter] = None
    year: Optional[NumericFilter] = None
    # ... остальные числовые поля
    
    # float поля → NumericFilter
    quality_score: Optional[NumericFilter] = None
    coverage: Optional[NumericFilter] = None
    cohesion: Optional[NumericFilter] = None
    # ... остальные float поля
    
    # str поля → TextFilter
    project: Optional[TextFilter] = None
    body: Optional[TextFilter] = None
    text: Optional[TextFilter] = None
    # ... остальные текстовые поля
    
    # List[str] поля → ListFilter
    tags: Optional[ListFilter] = None
    links: Optional[ListFilter] = None
    
    # dict поля → DictFilter
    block_meta: Optional[DictFilter] = None
```

### Простой запрос с автоопределением
```python
query = ChunkQuery(
    type=ExactFilter(value="DocBlock"),      # Автоматически определено как ExactFilter
    quality_score=NumericFilter(gte=0.8),   # Автоматически определено как NumericFilter  
    tags=ListFilter(contains="python")      # Автоматически определено как ListFilter
)
```

### Сложный запрос с автоопределением
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

## 🔍 Валидация и обработка ошибок

### Автоматическая валидация Pydantic
```python
# ✅ Корректно - автоматически определено правильно
query = ChunkQuery(ordinal=NumericFilter(gt=5))  # int поле

# ❌ Ошибка - неправильный тип фильтра для поля  
try:
    # Это невозможно, так как класс генерируется автоматически
    # и ordinal уже имеет тип Optional[NumericFilter]
    query = ChunkQuery(ordinal=TextFilter(contains="test"))
except ValidationError as e:
    # Pydantic выдаст ошибку типа
    pass
```

## 🚀 Процесс выполнения запроса

### 1. Автоматическая генерация класса
```python
# При импорте модуля автоматически генерируется ChunkQuery
ChunkQuery = generate_chunk_query_class()
```

### 2. Парсинг и валидация
```python
query = ChunkQuery.parse_obj(request_data)  # Pydantic валидация
```

### 3. Компиляция в SQL/MongoDB/Redis запрос
```python
sql_query = query.to_sql()
mongo_query = query.to_mongo() 
redis_query = query.to_redis()
```

### 4. Выполнение
```python
results = database.execute(sql_query)
chunks = [SemanticChunk.from_dict(row) for row in results]
```

## 📈 Преимущества автоматического подхода

1. **🛡️ Безопасность типов**: Невозможно создать некорректный запрос
2. **📝 Самодокументируемость**: Код сам показывает доступные операции  
3. **🔍 IDE поддержка**: Автокомплит и проверка типов
4. **⚡ Производительность**: Ранняя валидация предотвращает ошибки
5. **🧪 Тестируемость**: Легко писать unit-тесты
6. **🔧 Расширяемость**: Простое добавление новых операций
7. **🤖 Автоматизация**: Новые поля автоматически получают правильные фильтры
8. **🎯 Согласованность**: Исключены ошибки ручного назначения типов фильтров

## 🎯 Следующие шаги

1. Реализовать функцию автоматического определения типов фильтров
2. Создать автоматический генератор ChunkQuery класса
3. Реализовать базовые классы фильтров с валидаторами
4. Добавить поддержку DictFilter для JSON полей
5. Реализовать методы компиляции в SQL/MongoDB/Redis  
6. Написать comprehensive unit-тесты
7. Добавить примеры использования в документацию 