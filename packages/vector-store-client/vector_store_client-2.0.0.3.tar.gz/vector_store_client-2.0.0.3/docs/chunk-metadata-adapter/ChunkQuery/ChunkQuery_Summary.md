# ChunkQuery: Архитектурные принципы

## 🎯 Ключевые принципы архитектуры

### 1. **Pydantic как основа запросов**
- Все запросы строятся на Pydantic моделях
- Автоматическая валидация типов и значений
- Встроенная сериализация/десериализация
- Генерация JSON Schema

```python
class ChunkQuery(BaseModel):
    """Pydantic модель для типизированных запросов"""
    uuid: Optional[ExactFilter] = None
    ordinal: Optional[NumericFilter] = None
    body: Optional[TextFilter] = None
    tags: Optional[ListFilter] = None
```

### 2. **Автоматическое определение операций по типам**
- Анализ типов полей `SemanticChunk` 
- Автоматическое сопоставление с классами фильтров
- Исключение ошибок ручного назначения

```python
def get_filter_type_for_field(field_type: Type) -> Type[BaseFilter]:
    """Автоматически определяет тип фильтра для поля"""
    if field_type is ChunkId: return ExactFilter
    if field_type in (int, float): return NumericFilter  
    if field_type is str: return TextFilter
    if get_origin(field_type) is list: return ListFilter
    return ExactFilter
```

### 3. **Единая иерархия классов операций**
- Общий базовый класс `BaseFilter` для всех операций
- Полиморфизм через единый интерфейс
- Типизированные поля с общим предком

```python
class BaseFilter(BaseModel, ABC):
    """Базовый класс для всех фильтров"""
    
    @abstractmethod
    def to_sql_condition(self, field_name: str) -> str: pass
    
    @abstractmethod  
    def to_mongo_condition(self, field_name: str) -> Dict: pass

# Все поля имеют тип BaseFilter или его наследников
class ChunkQuery(BaseModel):
    uuid: Optional[BaseFilter] = None  # Фактически ExactFilter
    ordinal: Optional[BaseFilter] = None  # Фактически NumericFilter
```

### 4. **Автоматическая валидация операций**
- Pydantic проверяет допустимость операций на этапе создания
- Валидация конфликтующих параметров в фильтрах
- Проверка корректности типов до выполнения запроса

```python
# ✅ Корректно - автоматически определенный тип
query = ChunkQuery(ordinal=NumericFilter(gte=10))

# ❌ Ошибка валидации - неправильный тип операции
query = ChunkQuery(ordinal=TextFilter(contains="test"))  # ValidationError

# ❌ Ошибка валидации - конфликт операторов
NumericFilter(value=10, gt=5)  # ValidationError
```

## 🏗️ Архитектурная схема

```
SemanticChunk (Pydantic модель)
    ↓ анализ типов полей
get_filter_type_for_field()
    ↓ автоматическое сопоставление
ChunkQuery (Pydantic модель)
    ↓ типизированные поля
BaseFilter (абстрактный класс)
    ├── ExactFilter (UUID, Enum, bool)
    ├── NumericFilter (int, float)  
    ├── TextFilter (str)
    ├── ListFilter (List[str])
    └── DictFilter (dict)
        ↓ валидация операций
Pydantic ValidationError
    ↓ успешная валидация
SQL/MongoDB/Redis запрос
```

## 🔍 Детали реализации

### Типы операций и их применение
```python
# Автоматическое сопоставление типов
FIELD_TYPE_MAPPING = {
    ChunkId: ExactFilter,          # UUID поля
    ChunkType: ExactFilter,        # Enum поля  
    bool: ExactFilter,             # Булевы поля
    int: NumericFilter,            # Целые числа
    float: NumericFilter,          # Дроби
    str: TextFilter,               # Текстовые поля
    List[str]: ListFilter,         # Списки строк
    dict: DictFilter,              # JSON объекты
}
```

### Валидация на разных уровнях
```python
# 1. Уровень Pydantic модели
class ChunkQuery(BaseModel):
    ordinal: Optional[NumericFilter] = None  # Тип определен автоматически

# 2. Уровень фильтра операций
class NumericFilter(BaseFilter):
    @validator('value')
    def validate_no_conflicts(cls, v, values):
        if v is not None and any(values.get(op) for op in ['gt', 'gte']):
            raise ValueError("Cannot use 'value' with comparison operators")

# 3. Уровень выполнения запроса
def execute_query(query: ChunkQuery):
    # Дополнительная валидация перед выполнением
    for field_name, filter_obj in query.dict(exclude_none=True).items():
        if not filter_obj.is_valid_for_field(field_name):
            raise ValidationError(f"Invalid operation for field {field_name}")
```

## 💡 Преимущества архитектуры

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

## 🚀 Пример использования

```python
# Автоматически сгенерированный запрос
query = ChunkQuery(
    # ChunkType (enum) → ExactFilter  
    type=ExactFilter(in_=["DocBlock", "Draft"]),
    
    # int → NumericFilter
    year=NumericFilter(between=(2020, 2024)),
    
    # float → NumericFilter
    quality_score=NumericFilter(gte=0.8),
    
    # str → TextFilter
    body=TextFilter(contains="python"),
    
    # List[str] → ListFilter
    tags=ListFilter(contains_all=["web", "api"]),
    
    # bool → ExactFilter
    is_public=ExactFilter(value=True)
)

# Валидация происходит автоматически при создании
# Компиляция в SQL/MongoDB/Redis
sql, params = query.to_sql()
mongo_query = query.to_mongo()
```

## 🎯 Итоговые принципы

1. **Pydantic модели** - основа всех запросов
2. **Автоматическое определение** - типы операций по типам полей  
3. **Единая иерархия** - общий BaseFilter для всех операций
4. **Автоматическая валидация** - проверка операций до выполнения

Эта архитектура обеспечивает **максимальную безопасность**, **простоту использования** и **автоматическую согласованность** между моделью данных и системой запросов. 