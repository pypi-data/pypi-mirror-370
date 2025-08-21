# ChunkQuery: Техническая спецификация

## 🏗️ Структура модулей

### 1. **query_filters.py** - Базовые классы фильтров
```python
# Базовые классы: BaseFilter, ExactFilter, NumericFilter, TextFilter, ListFilter, VectorFilter
# Валидаторы и helper методы
```

### 2. **chunk_query_v2.py** - Обновленный ChunkQuery  
```python
# Новая версия ChunkQuery с типизированными полями
# Методы компиляции запросов
# Backward compatibility с текущей версией
```

### 3. **query_compilers.py** - Компиляторы запросов
```python
# SQLCompiler, MongoCompiler, RedisCompiler
# Генерация запросов для разных БД
```

## 🔧 Детали реализации

### BaseFilter - базовый класс

```python
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union, List
from pydantic import BaseModel, Field, validator

class BaseFilter(BaseModel, ABC):
    """Базовый класс для всех типов фильтров"""
    
    class Config:
        extra = "forbid"  # Запрещаем лишние поля
        
    @abstractmethod
    def to_sql_condition(self, field_name: str) -> str:
        """Генерирует SQL условие для поля"""
        pass
        
    @abstractmethod  
    def to_mongo_condition(self, field_name: str) -> Dict[str, Any]:
        """Генерирует MongoDB условие для поля"""
        pass
        
    @abstractmethod
    def get_parameters(self) -> List[Any]:
        """Возвращает параметры для подстановки в запрос"""
        pass
        
    def is_empty(self) -> bool:
        """Проверяет, что фильтр пустой (все поля None)"""
        return all(v is None for v in self.dict().values())
```

### ExactFilter - точное совпадение

```python
class ExactFilter(BaseFilter):
    """Фильтр для точного совпадения и множественного выбора"""
    
    value: Optional[Union[str, int, float, bool]] = None
    in_: Optional[List[Union[str, int, float, bool]]] = Field(None, alias="in")
    
    @validator('in_')
    def validate_in_not_empty(cls, v):
        if v is not None and len(v) == 0:
            raise ValueError("'in' list cannot be empty")
        return v
        
    @validator('value')  
    def validate_mutual_exclusion(cls, v, values):
        if v is not None and values.get('in_') is not None:
            raise ValueError("Cannot specify both 'value' and 'in' simultaneously")
        return v
        
    def to_sql_condition(self, field_name: str) -> str:
        if self.value is not None:
            return f"{field_name} = ?"
        elif self.in_ is not None:
            placeholders = ",".join("?" * len(self.in_))
            return f"{field_name} IN ({placeholders})"
        return "1=1"
        
    def to_mongo_condition(self, field_name: str) -> Dict[str, Any]:
        if self.value is not None:
            return {field_name: self.value}
        elif self.in_ is not None:
            return {field_name: {"$in": self.in_}}
        return {}
        
    def get_parameters(self) -> List[Any]:
        if self.value is not None:
            return [self.value]
        elif self.in_ is not None:
            return list(self.in_)
        return []
```

### NumericFilter - числовые операции

```python
from typing import Tuple

class NumericFilter(BaseFilter):
    """Фильтр для числовых полей с операторами сравнения"""
    
    value: Optional[Union[int, float]] = None
    gt: Optional[Union[int, float]] = None
    gte: Optional[Union[int, float]] = None
    lt: Optional[Union[int, float]] = None
    lte: Optional[Union[int, float]] = None
    in_: Optional[List[Union[int, float]]] = Field(None, alias="in")
    between: Optional[Tuple[Union[int, float], Union[int, float]]] = None
    
    @validator('between')
    def validate_between_order(cls, v):
        if v is not None and v[0] >= v[1]:
            raise ValueError("In 'between' tuple, first value must be less than second")
        return v
        
    @validator('value')
    def validate_no_conflicts_with_value(cls, v, values):
        conflicts = ['gt', 'gte', 'lt', 'lte', 'in_', 'between']
        if v is not None:
            for field in conflicts:
                if values.get(field) is not None:
                    raise ValueError(f"Cannot specify both 'value' and '{field}' simultaneously")
        return v
        
    @validator('between')
    def validate_no_conflicts_with_between(cls, v, values):
        conflicts = ['gt', 'gte', 'lt', 'lte', 'in_']
        if v is not None:
            for field in conflicts:
                if values.get(field) is not None:
                    raise ValueError(f"Cannot specify both 'between' and '{field}' simultaneously")
        return v
        
    def to_sql_condition(self, field_name: str) -> str:
        conditions = []
        
        if self.value is not None:
            return f"{field_name} = ?"
        if self.gt is not None:
            conditions.append(f"{field_name} > ?")
        if self.gte is not None:
            conditions.append(f"{field_name} >= ?")
        if self.lt is not None:
            conditions.append(f"{field_name} < ?")
        if self.lte is not None:
            conditions.append(f"{field_name} <= ?")
        if self.between is not None:
            conditions.append(f"{field_name} BETWEEN ? AND ?")
        if self.in_ is not None:
            placeholders = ",".join("?" * len(self.in_))
            conditions.append(f"{field_name} IN ({placeholders})")
            
        return " AND ".join(conditions) if conditions else "1=1"
        
    def to_mongo_condition(self, field_name: str) -> Dict[str, Any]:
        condition = {}
        
        if self.value is not None:
            return {field_name: self.value}
        
        mongo_condition = {}
        if self.gt is not None:
            mongo_condition["$gt"] = self.gt
        if self.gte is not None:
            mongo_condition["$gte"] = self.gte
        if self.lt is not None:
            mongo_condition["$lt"] = self.lt
        if self.lte is not None:
            mongo_condition["$lte"] = self.lte
        if self.between is not None:
            mongo_condition["$gte"] = self.between[0]
            mongo_condition["$lte"] = self.between[1]
        if self.in_ is not None:
            mongo_condition["$in"] = self.in_
            
        return {field_name: mongo_condition} if mongo_condition else {}
        
    def get_parameters(self) -> List[Any]:
        params = []
        
        if self.value is not None:
            return [self.value]
        if self.gt is not None:
            params.append(self.gt)
        if self.gte is not None:
            params.append(self.gte)
        if self.lt is not None:
            params.append(self.lt)
        if self.lte is not None:
            params.append(self.lte)
        if self.between is not None:
            params.extend(self.between)
        if self.in_ is not None:
            params.extend(self.in_)
            
        return params
```

### TextFilter - текстовый поиск

```python
import re
from typing import Pattern

class TextFilter(BaseFilter):
    """Фильтр для текстовых полей"""
    
    value: Optional[str] = None
    in_: Optional[List[str]] = Field(None, alias="in")
    contains: Optional[str] = None
    startswith: Optional[str] = None
    endswith: Optional[str] = None
    regex: Optional[str] = None
    icontains: Optional[str] = None  # case-insensitive contains
    
    @validator('regex')
    def validate_regex_pattern(cls, v):
        if v is not None:
            try:
                re.compile(v)
            except re.error as e:
                raise ValueError(f"Invalid regex pattern: {e}")
        return v
        
    @validator('value')
    def validate_no_conflicts_with_value(cls, v, values):
        conflicts = ['in_', 'contains', 'startswith', 'endswith', 'regex', 'icontains']
        if v is not None:
            for field in conflicts:
                if values.get(field) is not None:
                    raise ValueError(f"Cannot specify both 'value' and '{field}' simultaneously")
        return v
        
    def to_sql_condition(self, field_name: str) -> str:
        if self.value is not None:
            return f"{field_name} = ?"
        elif self.in_ is not None:
            placeholders = ",".join("?" * len(self.in_))
            return f"{field_name} IN ({placeholders})"
        elif self.contains is not None:
            return f"{field_name} LIKE ?"
        elif self.icontains is not None:
            return f"LOWER({field_name}) LIKE LOWER(?)"
        elif self.startswith is not None:
            return f"{field_name} LIKE ?"
        elif self.endswith is not None:
            return f"{field_name} LIKE ?"
        elif self.regex is not None:
            # SQL regex syntax varies by database
            return f"{field_name} ~ ?"  # PostgreSQL syntax
        return "1=1"
        
    def to_mongo_condition(self, field_name: str) -> Dict[str, Any]:
        if self.value is not None:
            return {field_name: self.value}
        elif self.in_ is not None:
            return {field_name: {"$in": self.in_}}
        elif self.contains is not None:
            return {field_name: {"$regex": re.escape(self.contains)}}
        elif self.icontains is not None:
            return {field_name: {"$regex": re.escape(self.icontains), "$options": "i"}}
        elif self.startswith is not None:
            return {field_name: {"$regex": f"^{re.escape(self.startswith)}"}}
        elif self.endswith is not None:
            return {field_name: {"$regex": f"{re.escape(self.endswith)}$"}}
        elif self.regex is not None:
            return {field_name: {"$regex": self.regex}}
        return {}
        
    def get_parameters(self) -> List[Any]:
        if self.value is not None:
            return [self.value]
        elif self.in_ is not None:
            return list(self.in_)
        elif self.contains is not None:
            return [f"%{self.contains}%"]
        elif self.icontains is not None:
            return [f"%{self.icontains}%"]
        elif self.startswith is not None:
            return [f"{self.startswith}%"]
        elif self.endswith is not None:
            return [f"%{self.endswith}"]
        elif self.regex is not None:
            return [self.regex]
        return []
```

### ListFilter - операции со списками

```python
class ListFilter(BaseFilter):
    """Фильтр для списковых полей (tags, links)"""
    
    contains: Optional[str] = None
    contains_any: Optional[List[str]] = None
    contains_all: Optional[List[str]] = None
    size: Optional[NumericFilter] = None
    empty: Optional[bool] = None
    not_empty: Optional[bool] = None
    
    @validator('empty', 'not_empty')
    def validate_empty_mutual_exclusion(cls, v, values, field):
        if v is not None:
            other_field = 'not_empty' if field.name == 'empty' else 'empty'
            if values.get(other_field) is not None:
                raise ValueError("Cannot specify both 'empty' and 'not_empty' simultaneously")
        return v
        
    def to_sql_condition(self, field_name: str) -> str:
        # Предполагаем, что списки хранятся как JSON или comma-separated
        conditions = []
        
        if self.contains is not None:
            # JSON contains
            conditions.append(f"JSON_CONTAINS({field_name}, ?)")
        if self.contains_any is not None:
            # OR conditions for each element
            or_conditions = [f"JSON_CONTAINS({field_name}, ?)" for _ in self.contains_any]
            conditions.append(f"({' OR '.join(or_conditions)})")
        if self.contains_all is not None:
            # AND conditions for each element
            and_conditions = [f"JSON_CONTAINS({field_name}, ?)" for _ in self.contains_all]
            conditions.append(f"({' AND '.join(and_conditions)})")
        if self.size is not None:
            size_condition = self.size.to_sql_condition(f"JSON_LENGTH({field_name})")
            conditions.append(f"({size_condition})")
        if self.empty is True:
            conditions.append(f"(JSON_LENGTH({field_name}) = 0 OR {field_name} IS NULL)")
        if self.not_empty is True:
            conditions.append(f"JSON_LENGTH({field_name}) > 0")
            
        return " AND ".join(conditions) if conditions else "1=1"
        
    def to_mongo_condition(self, field_name: str) -> Dict[str, Any]:
        mongo_conditions = []
        
        if self.contains is not None:
            mongo_conditions.append({field_name: self.contains})
        if self.contains_any is not None:
            mongo_conditions.append({field_name: {"$in": self.contains_any}})
        if self.contains_all is not None:
            mongo_conditions.append({field_name: {"$all": self.contains_all}})
        if self.size is not None:
            size_condition = self.size.to_mongo_condition(f"{field_name}")
            # Replace field_name with $size operator
            for key, value in size_condition.items():
                mongo_conditions.append({field_name: {"$size": value}})
        if self.empty is True:
            mongo_conditions.append({field_name: {"$size": 0}})
        if self.not_empty is True:
            mongo_conditions.append({field_name: {"$not": {"$size": 0}}})
            
        if len(mongo_conditions) == 1:
            return mongo_conditions[0]
        elif len(mongo_conditions) > 1:
            return {"$and": mongo_conditions}
        return {}
        
    def get_parameters(self) -> List[Any]:
        params = []
        
        if self.contains is not None:
            params.append(f'"{self.contains}"')  # JSON string
        if self.contains_any is not None:
            params.extend([f'"{item}"' for item in self.contains_any])
        if self.contains_all is not None:
            params.extend([f'"{item}"' for item in self.contains_all])
        if self.size is not None:
            params.extend(self.size.get_parameters())
            
        return params
```

## 🔍 Валидация на уровне ChunkQuery

```python
class ChunkQuery(BaseModel):
    """Типизированный запрос для поиска семантических чанков"""
    
    # UUID поля - ExactFilter
    uuid: Optional[ExactFilter] = None
    source_id: Optional[ExactFilter] = None
    task_id: Optional[ExactFilter] = None
    subtask_id: Optional[ExactFilter] = None
    unit_id: Optional[ExactFilter] = None
    block_id: Optional[ExactFilter] = None
    link_related: Optional[ExactFilter] = None
    link_parent: Optional[ExactFilter] = None
    
    # Enum поля - ExactFilter
    type: Optional[ExactFilter] = None
    role: Optional[ExactFilter] = None
    status: Optional[ExactFilter] = None
    language: Optional[ExactFilter] = None
    block_type: Optional[ExactFilter] = None
    
    # Булевы поля - ExactFilter
    is_public: Optional[ExactFilter] = None
    used_in_generation: Optional[ExactFilter] = None
    
    # Числовые поля - NumericFilter
    ordinal: Optional[NumericFilter] = None
    start: Optional[NumericFilter] = None
    end: Optional[NumericFilter] = None
    year: Optional[NumericFilter] = None
    quality_score: Optional[NumericFilter] = None
    coverage: Optional[NumericFilter] = None
    cohesion: Optional[NumericFilter] = None
    boundary_prev: Optional[NumericFilter] = None
    boundary_next: Optional[NumericFilter] = None
    feedback_accepted: Optional[NumericFilter] = None
    feedback_rejected: Optional[NumericFilter] = None
    feedback_modifications: Optional[NumericFilter] = None
    block_index: Optional[NumericFilter] = None
    source_lines_start: Optional[NumericFilter] = None
    source_lines_end: Optional[NumericFilter] = None
    
    # Текстовые поля - TextFilter
    project: Optional[TextFilter] = None
    body: Optional[TextFilter] = None
    text: Optional[TextFilter] = None
    summary: Optional[TextFilter] = None
    sha256: Optional[TextFilter] = None
    created_at: Optional[TextFilter] = None
    source_path: Optional[TextFilter] = None
    category: Optional[TextFilter] = None
    title: Optional[TextFilter] = None
    source: Optional[TextFilter] = None
    chunking_version: Optional[TextFilter] = None
    
    # Списковые поля - ListFilter
    tags: Optional[ListFilter] = None
    links: Optional[ListFilter] = None
    
    class Config:
        extra = "forbid"
        
    def to_sql(self, table_name: str = "chunks") -> Tuple[str, List[Any]]:
        """Генерирует SQL запрос с параметрами"""
        conditions = []
        parameters = []
        
        for field_name, filter_obj in self.dict(exclude_none=True).items():
            if not filter_obj.is_empty():
                condition = filter_obj.to_sql_condition(field_name)
                conditions.append(condition)
                parameters.extend(filter_obj.get_parameters())
                
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        sql = f"SELECT * FROM {table_name} WHERE {where_clause}"
        
        return sql, parameters
        
    def to_mongo(self) -> Dict[str, Any]:
        """Генерирует MongoDB запрос"""
        mongo_query = {}
        
        for field_name, filter_obj in self.dict(exclude_none=True).items():
            if not filter_obj.is_empty():
                condition = filter_obj.to_mongo_condition(field_name)
                mongo_query.update(condition)
                
        return mongo_query
        
    def count_active_filters(self) -> int:
        """Подсчитывает количество активных фильтров"""
        return len([f for f in self.dict(exclude_none=True).values() if not f.is_empty()])
```

## 🧪 Стратегия тестирования

### 1. Unit тесты фильтров
```python
def test_exact_filter_value():
    filter = ExactFilter(value="test")
    assert filter.to_sql_condition("field") == "field = ?"
    assert filter.get_parameters() == ["test"]

def test_numeric_filter_range():
    filter = NumericFilter(gte=10, lte=20)
    assert "field >= ?" in filter.to_sql_condition("field")
    assert "field <= ?" in filter.to_sql_condition("field")
    assert filter.get_parameters() == [10, 20]
```

### 2. Integration тесты ChunkQuery
```python
def test_complex_query():
    query = ChunkQuery(
        type=ExactFilter(value="DocBlock"),
        quality_score=NumericFilter(gte=0.8),
        tags=ListFilter(contains="python")
    )
    
    sql, params = query.to_sql()
    assert "type = ?" in sql
    assert "quality_score >= ?" in sql
    assert "JSON_CONTAINS(tags, ?)" in sql
```

### 3. Валидация тесты
```python
def test_conflicting_operators():
    with pytest.raises(ValidationError):
        NumericFilter(value=10, gt=5)  # Конфликт операторов
```

## 📚 Backward Compatibility

### Миграция с текущего ChunkQuery
```python
class ChunkQueryLegacy:
    """Wrapper для современного API"""
    
    @classmethod
    def from_legacy_dict(cls, data: dict) -> ChunkQuery:
        """Конвертирует старый формат в новый"""
        converted = {}
        
        for field, value in data.items():
            if isinstance(value, str) and ">" in value:
                # Парсим строковые операторы: ">=5", "<=10"
                converted[field] = cls._parse_string_operator(value)
            elif isinstance(value, list):
                # Список значений -> ExactFilter(in_=...)
                converted[field] = ExactFilter(in_=value)
            else:
                # Простое значение
                field_type = cls._get_field_type(field)
                if field_type == "exact":
                    converted[field] = ExactFilter(value=value)
                elif field_type == "numeric":
                    converted[field] = NumericFilter(value=value)
                elif field_type == "text":
                    converted[field] = TextFilter(value=value)
                    
        return ChunkQuery(**converted)
```

Эта архитектура обеспечивает:
- ✅ **Строгую типизацию** всех операций
- ✅ **Автоматическую валидацию** Pydantic  
- ✅ **Расширяемость** для новых типов фильтров
- ✅ **Современный API** с новым интерфейсом
- ✅ **Универсальность** для разных БД (SQL, MongoDB, Redis) 