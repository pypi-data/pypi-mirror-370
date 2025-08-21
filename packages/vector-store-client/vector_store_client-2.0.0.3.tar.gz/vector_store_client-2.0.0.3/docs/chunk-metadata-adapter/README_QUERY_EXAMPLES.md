# Примеры типизированных запросов ChunkQuery

Этот набор файлов демонстрирует полную мощь системы типизированных запросов `ChunkQuery` для работы с метаданными чанков.

## 📁 Структура файлов

### 1. `query_examples.py` - Базовые примеры
**Назначение**: Основы работы с запросами
- ✅ Запросы на равенство (enum поля)
- ✅ Операторы сравнения (>, <, >=, <=)
- ✅ Диапазонные запросы [min,max]
- ✅ IN запросы (только для не-enum полей)
- ✅ Валидация и обработка ошибок
- ✅ Комплексные запросы

**Запуск**: `python -m chunk_metadata_adapter.query_examples`

### 2. `query_serialization_examples.py` - Продвинутые техники
**Назначение**: Сериализация и архитектурные паттерны
- 🔄 Сериализация запросов (Redis, JSON, API)
- 🏗️ Динамическое построение запросов
- ⚡ Паттерны оптимизации для больших датасетов
- 🛡️ Продвинутая обработка ошибок
- 🔧 Композиция и билдер-паттерн

**Запуск**: `python -m chunk_metadata_adapter.query_serialization_examples`

### 3. `query_business_examples.py` - Бизнес-сценарии
**Назначение**: Реальные применения в продакшене
- 📝 Управление контентом (CMS)
- 🔍 Контроль качества
- 📊 Аналитика и отчетность
- 🔎 Поиск и обнаружение контента
- 🧹 Обслуживание и очистка данных

**Запуск**: `python -m chunk_metadata_adapter.query_business_examples`

## 🎯 Ключевые принципы

### Enum поля (ТОЛЬКО равенство)
```python
# ✅ Правильно - одиночные значения
{"type": ChunkType.DOC_BLOCK.value}
{"status": ChunkStatus.RELIABLE.value}
{"language": LanguageEnum.PYTHON.value}

# ❌ Неправильно - IN запросы для enum не поддерживаются
{"type": "in:DocBlock,CodeBlock"}  # Ошибка валидации!
```

**Enum поля**: `type`, `status`, `language`, `role`, `block_type`

### Числовые и строковые поля (полная поддержка операторов)
```python
# ✅ Все поддерживается
{"quality_score": ">=0.8"}           # Сравнение
{"year": "[2020,2024]"}              # Диапазон
{"category": "in:doc,tutorial,ref"}  # IN запрос
{"start": ">100"}                    # Больше чем
{"feedback_accepted": "<=5"}         # Меньше или равно
```

## 📋 Практические рекомендации

### 1. Валидация запросов
```python
# Всегда используйте безопасную валидацию
query, errors = ChunkQuery.from_dict_with_validation(data)
if errors:
    print(f"Ошибки: {errors}")
    return None
```

### 2. Множественные enum значения
```python
# Создавайте отдельные запросы для каждого enum значения
queries = []
for chunk_type in [ChunkType.DOC_BLOCK, ChunkType.CODE_BLOCK]:
    query, _ = ChunkQuery.from_dict_with_validation({
        "type": chunk_type.value,
        "quality_score": ">=0.8"
    })
    queries.append(query)
```

### 3. Оптимизация производительности
```python
# Приоритет индексированных полей
optimal_query = {
    "project": "SpecificProject",     # Высокая селективность
    "type": ChunkType.DOC_BLOCK.value,  # Обычно индексируется
    "status": ChunkStatus.RELIABLE.value,  # Обычно индексируется
    "quality_score": ">=0.8"         # Диапазон после точных значений
}
```

### 4. Сериализация
```python
# Для Redis (строки)
flat_dict = query.to_flat_dict(for_redis=True)

# Для API (JSON-совместимо)
json_dict = query.to_json_dict()

# Восстановление
restored = ChunkQuery.from_flat_dict(flat_dict)
```

## 🔍 Примеры по категориям

### Поиск контента
- **Высокое качество**: `quality_score >= 0.8`
- **Недавний контент**: `year >= 2023`
- **Популярный**: `feedback_accepted >= 10`
- **Активный**: `used_in_generation = True`

### Контроль качества
- **Проблемный**: `quality_score < 0.5 AND feedback_rejected > 3`
- **Недооцененный**: `quality_score >= 0.8 AND used_in_generation = False`
- **Плохие границы**: `boundary_prev < 0.4 AND boundary_next < 0.4`

### Архивирование
- **Кандидаты**: `year < 2020 AND used_in_generation = False AND quality_score < 0.6`
- **Дубли**: `cohesion < 0.5 AND boundary_prev > 0.8`

## ⚠️ Важные ограничения

1. **IN запросы**: Работают только для не-enum полей
2. **Enum поля**: Только точное равенство
3. **UUID поля**: Строгая валидация UUIDv4
4. **Операторы**: `>`, `<`, `>=`, `<=`, `[min,max]`, `in:val1,val2,val3`

## 🚀 Быстрый старт

```python
from chunk_metadata_adapter.chunk_query import ChunkQuery
from chunk_metadata_adapter.data_types import ChunkType, ChunkStatus

# Простой запрос
data = {
    "type": ChunkType.DOC_BLOCK.value,
    "quality_score": ">=0.8",
    "is_public": True
}

query, errors = ChunkQuery.from_dict_with_validation(data)
if errors is None:
    print(f"✅ Запрос создан: {query.type}")
else:
    print(f"❌ Ошибки: {errors}")
```

## 🔗 Связанные файлы

- `chunk_query.py` - Основная реализация
- `data_types.py` - Определения enum
- `semantic_chunk.py` - Модель данных
- `tests/test_*.py` - Тесты и примеры использования

---

**Все примеры протестированы и готовы к использованию в продакшене!** ✅ 