# ChunkQuery: Типизированная система фильтров

## 📚 Документация

Документация по типизированной системе построения запросов для поиска и фильтрации семантических чанков.

## 📋 Содержание

### 🎯 Архитектурные документы
- **[ChunkQuery_Summary.md](./ChunkQuery_Summary.md)** - Ключевые принципы архитектуры
- **[ChunkQuery_Architecture.md](./ChunkQuery_Architecture.md)** - Полная архитектурная документация

### 🔧 Техническая документация
- **[Technical_Specification.md](./Technical_Specification.md)** - Детали реализации классов
- **[Implementation_Guide.md](./Implementation_Guide.md)** - Пошаговое руководство по реализации
- **[API_Reference.md](./API_Reference.md)** - Справочник API

### 💡 Примеры и руководства
- **[Usage_Examples.md](./Usage_Examples.md)** - Примеры использования
- **[Migration_Guide.md](./Migration_Guide.md)** - Миграция с текущего ChunkQuery
- **[Best_Practices.md](./Best_Practices.md)** - Лучшие практики

### 🧪 Тестирование
- **[Testing_Strategy.md](./Testing_Strategy.md)** - Стратегия тестирования
- **[Test_Examples.md](./Test_Examples.md)** - Примеры тестов

## 🚀 Быстрый старт

### Основные принципы
1. **Pydantic модели** - основа всех запросов
2. **Автоматическое определение** - типы операций по типам полей  
3. **Единая иерархия** - общий BaseFilter для всех операций
4. **Автоматическая валидация** - проверка операций до выполнения

### Простой пример
```python
# Автоматически типизированный запрос
query = ChunkQuery(
    type=ExactFilter(value="DocBlock"),      # enum → ExactFilter
    quality_score=NumericFilter(gte=0.8),   # float → NumericFilter  
    tags=ListFilter(contains="python")      # List[str] → ListFilter
)

# Компиляция в SQL/MongoDB
sql, params = query.to_sql()
mongo_query = query.to_mongo()
```

## 🏗️ Архитектурная схема

```
SemanticChunk (поля с типами)
    ↓
get_filter_type_for_field() (автоанализ)
    ↓
ChunkQuery (типизированные поля)
    ↓
BaseFilter (единая иерархия)
    ├── ExactFilter (UUID, Enum, bool)
    ├── NumericFilter (int, float)  
    ├── TextFilter (str)
    ├── ListFilter (List[str])
    └── DictFilter (dict)
        ↓
Pydantic ValidationError (при ошибках)
    ↓
SQL/MongoDB/Redis запрос (при успехе)
```

## 🎯 Преимущества

- ✅ **Безопасность типов** - невозможно создать некорректный запрос
- ✅ **Автоматизация** - новые поля получают правильные фильтры  
- ✅ **Согласованность** - модель данных и запросы синхронизированы
- ✅ **Расширяемость** - легко добавлять новые операции
- ✅ **IDE поддержка** - автокомплит и проверка типов

## 📝 Статус документации

| Документ | Статус | Описание |
|----------|--------|----------|
| ChunkQuery_Summary.md | ✅ Готов | Ключевые принципы |
| ChunkQuery_Architecture.md | ✅ Готов | Полная архитектура |
| Technical_Specification.md | 🔄 Планируется | Детали реализации |
| Implementation_Guide.md | 🔄 Планируется | Руководство по реализации |
| Usage_Examples.md | 🔄 Планируется | Примеры использования |
| API_Reference.md | 🔄 Планируется | Справочник API |

## 🔗 Связанные документы

- [Metadata.md](../Metadata.md) - Документация по метаданным чанков
- [Usage.md](../Usage.md) - Общее руководство по использованию пакета
- [Component_Interaction.md](../Component_Interaction.md) - Взаимодействие компонентов

## 🚀 Следующие шаги

1. Реализация базовых классов фильтров
2. Создание автогенератора ChunkQuery
3. Написание comprehensive тестов
4. Добавление примеров использования 