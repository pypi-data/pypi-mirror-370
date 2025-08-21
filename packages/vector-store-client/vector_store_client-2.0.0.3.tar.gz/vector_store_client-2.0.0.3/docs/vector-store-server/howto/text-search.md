# HOWTO: Поиск по тексту

## 🎯 Обзор

Поиск по тексту в Vector Store использует семантическую векторизацию для нахождения релевантных документов. Система автоматически преобразует текстовый запрос в вектор и выполняет поиск по сходству.

## 📋 Предварительные требования

- Сервер Vector Store запущен на `http://localhost:8007`
- В системе есть созданные чанки для поиска
- Понимание JSON-RPC 2.0 протокола

## 🔍 Базовый поиск

### Простой текстовый поиск

```bash
curl -X POST http://localhost:8007/cmd \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "search",
    "params": {
      "search_str": "машинное обучение",
      "limit": 5
    },
    "id": 1
  }'
```

**Ожидаемый ответ:**
```json
{
  "jsonrpc": "2.0",
  "result": {
    "success": true,
    "data": {
      "chunks": [
        {
          "uuid": "123e4567-e89b-12d3-a456-426614174000",
          "body": "Машинное обучение - это подраздел искусственного интеллекта...",
          "similarity": 0.85,
          "metadata": {
            "category": "ai",
            "language": "ru",
            "tags": ["ml", "ai"]
          }
        }
      ],
      "total_found": 1,
      "search_params": {
        "search_str": "машинное обучение",
        "limit": 5
      }
    }
  },
  "id": 1
}
```

### Поиск с порогом релевантности

```bash
curl -X POST http://localhost:8007/cmd \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "search",
    "params": {
      "search_str": "нейронные сети",
      "limit": 10,
      "level_of_relevance": 0.7
    },
    "id": 1
  }'
```

**Параметры:**
- `search_str` - текст для поиска
- `limit` - максимальное количество результатов (по умолчанию 10)
- `level_of_relevance` - минимальный порог сходства (0.0-1.0)

## 🎛️ Продвинутый поиск

### Поиск с фильтрацией метаданных

```bash
curl -X POST http://localhost:8007/cmd \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "search",
    "params": {
      "search_str": "векторные эмбеддинги",
      "metadata_filter": {
        "category": {"$eq": "technical"},
        "language": {"$in": ["ru", "en"]},
        "year": {"$gte": 2020}
      },
      "limit": 5,
      "level_of_relevance": 0.8
    },
    "id": 1
  }'
```

### Поиск с пагинацией

```bash
curl -X POST http://localhost:8007/cmd \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "search",
    "params": {
      "search_str": "искусственный интеллект",
      "limit": 5,
      "offset": 10
    },
    "id": 1
  }'
```

**Параметры пагинации:**
- `limit` - количество результатов на страницу
- `offset` - количество результатов для пропуска

## 🔧 Операторы фильтрации

### Операторы сравнения

| Оператор | Описание | Пример |
|----------|----------|---------|
| `$eq` | Равно | `{"category": {"$eq": "technical"}}` |
| `$ne` | Не равно | `{"language": {"$ne": "en"}}` |
| `$in` | В списке | `{"tags": {"$in": ["ai", "ml"]}}` |
| `$nin` | Не в списке | `{"status": {"$nin": ["deleted"]}}` |

### Операторы диапазона

| Оператор | Описание | Пример |
|----------|----------|---------|
| `$gt` | Больше | `{"year": {"$gt": 2020}}` |
| `$gte` | Больше или равно | `{"quality_score": {"$gte": 0.8}}` |
| `$lt` | Меньше | `{"tokens": {"$lt": 1000}}` |
| `$lte` | Меньше или равно | `{"coverage": {"$lte": 1.0}}` |
| `$range` | Диапазон | `{"year": {"$range": [2020, 2024]}}` |

### Логические операторы

```json
{
  "metadata_filter": {
    "$and": [
      {"category": {"$eq": "technical"}},
      {"language": {"$in": ["en", "ru"]}},
      {"year": {"$gte": 2020}}
    ]
  }
}
```

```json
{
  "metadata_filter": {
    "$or": [
      {"category": {"$eq": "technical"}},
      {"tags": {"$in": ["ai", "ml"]}}
    ]
  }
}
```

## 📊 Анализ результатов

### Структура результата

```json
{
  "chunks": [
    {
      "uuid": "123e4567-e89b-12d3-a456-426614174000",
      "body": "Найденный текст чанка",
      "similarity": 0.85,
      "metadata": {
        "category": "technical",
        "language": "ru",
        "tags": ["ai", "ml"],
        "quality_score": 0.95,
        "created_at": "2024-12-19T10:00:00Z"
      }
    }
  ],
  "total_found": 1,
  "search_params": {
    "search_str": "машинное обучение",
    "limit": 5,
    "level_of_relevance": 0.7
  }
}
```

### Интерпретация similarity

- **0.9-1.0**: Очень высокая релевантность
- **0.7-0.9**: Высокая релевантность
- **0.5-0.7**: Средняя релевантность
- **0.3-0.5**: Низкая релевантность
- **0.0-0.3**: Очень низкая релевантность

## 🚀 Оптимизация поиска

### 1. Правильный выбор порога релевантности

```bash
# Для точного поиска
"level_of_relevance": 0.8

# Для широкого поиска
"level_of_relevance": 0.5

# Для включения всех результатов
"level_of_relevance": 0.0
```

### 2. Эффективная фильтрация

```bash
# Хорошо - фильтр по индексированным полям
"metadata_filter": {
  "category": {"$eq": "technical"},
  "language": {"$eq": "ru"}
}

# Плохо - сложные вычисления в фильтре
"metadata_filter": {
  "body": {"$regex": ".*pattern.*"}
}
```

### 3. Оптимальный размер лимита

```bash
# Для UI отображения
"limit": 10

# Для batch обработки
"limit": 100

# Для анализа
"limit": 1000
```

## 🔍 Примеры использования

### Поиск технической документации

```bash
curl -X POST http://localhost:8007/cmd \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "search",
    "params": {
      "search_str": "API документация",
      "metadata_filter": {
        "category": {"$eq": "documentation"},
        "type": {"$eq": "DocBlock"}
      },
      "limit": 10,
      "level_of_relevance": 0.7
    },
    "id": 1
  }'
```

### Поиск по временному периоду

```bash
curl -X POST http://localhost:8007/cmd \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "search",
    "params": {
      "search_str": "новые технологии",
      "metadata_filter": {
        "year": {"$gte": 2023},
        "category": {"$eq": "technology"}
      },
      "limit": 20
    },
    "id": 1
  }'
```

### Поиск по качеству контента

```bash
curl -X POST http://localhost:8007/cmd \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "search",
    "params": {
      "search_str": "лучшие практики",
      "metadata_filter": {
        "quality_score": {"$gte": 0.9},
        "status": {"$eq": "active"}
      },
      "limit": 5,
      "level_of_relevance": 0.8
    },
    "id": 1
  }'
```

## ⚠️ Обработка ошибок

### Типичные ошибки

```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32001,
    "message": "No search method specified",
    "data": {
      "error_code": "validation_error",
      "details": {
        "required_methods": ["search_str", "embedding", "metadata_filter"]
      }
    }
  },
  "id": 1
}
```

### Коды ошибок

| Код | Описание | Решение |
|-----|----------|---------|
| `validation_error` | Неверные параметры | Проверьте формат запроса |
| `search_error` | Ошибка поиска | Проверьте доступность сервисов |
| `reindex_error` | Ошибка переиндексации | Проверьте сервис эмбеддингов |

## 📈 Мониторинг производительности

### Метрики поиска

```bash
# Проверка времени ответа
time curl -X POST http://localhost:8007/cmd \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "search",
    "params": {
      "search_str": "test query",
      "limit": 10
    },
    "id": 1
  }'
```

### Анализ результатов

```python
import json
import requests

def analyze_search_performance(search_str, limit=10):
    response = requests.post(
        "http://localhost:8007/cmd",
        json={
            "jsonrpc": "2.0",
            "method": "search",
            "params": {
                "search_str": search_str,
                "limit": limit
            },
            "id": 1
        }
    )
    
    result = response.json()
    
    if "result" in result:
        data = result["result"]["data"]
        print(f"Найдено: {data['total_found']} результатов")
        print(f"Время ответа: {response.elapsed.total_seconds():.3f}с")
        
        for chunk in data["chunks"]:
            print(f"- {chunk['similarity']:.3f}: {chunk['body'][:50]}...")
    
    return result
```

## 🔗 Связанные разделы

- [HOWTO: Поиск по векторам](vector-search.md)
- [HOWTO: Фильтрация метаданных](metadata-filtering.md)
- [Справочник команд](../reference/command-schemas.md)
- [API Reference](../developer/api-reference.md)

---

*Следующий HOWTO: [Поиск по векторам](vector-search.md)* 