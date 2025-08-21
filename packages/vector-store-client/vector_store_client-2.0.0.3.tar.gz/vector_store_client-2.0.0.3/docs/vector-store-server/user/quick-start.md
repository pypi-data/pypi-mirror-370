# Быстрый старт - Vector Store

## 🚀 Запуск сервера

### 1. Активация виртуальной среды
```bash
source .venv/bin/activate
```

### 2. Запуск сервера
```bash
python server.py --config=config/config-host.json
```

Сервер запустится на `http://localhost:8007`

### 3. Проверка состояния
```bash
curl http://localhost:8007/health
```

## 📝 Первые шаги

### 1. Создание чанков

Создайте первый текстовый чанк:

```bash
curl -X POST http://localhost:8007/cmd \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "chunk_create",
    "params": {
      "chunks": [
        {
          "body": "Vector Store - это высокопроизводительный сервис для хранения и поиска векторных эмбеддингов.",
          "text": "Vector Store service description",
          "language": "ru",
          "category": "technical",
          "tags": ["vector", "search", "ai"]
        }
      ]
    },
    "id": 1
  }'
```

### 2. Поиск по тексту

Найдите созданный чанк:

```bash
curl -X POST http://localhost:8007/cmd \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "search",
    "params": {
      "search_str": "vector store",
      "limit": 5
    },
    "id": 1
  }'
```

### 3. Фильтрация по метаданным

Найдите чанки по категории:

```bash
curl -X POST http://localhost:8007/cmd \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "search",
    "params": {
      "metadata_filter": {
        "category": {"$eq": "technical"}
      },
      "limit": 10
    },
    "id": 1
  }'
```

## 🔍 Основные операции

### Создание множественных чанков

```bash
curl -X POST http://localhost:8007/cmd \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "chunk_create",
    "params": {
      "chunks": [
        {
          "body": "Первый чанк о машинном обучении",
          "category": "ai",
          "tags": ["ml", "ai"]
        },
        {
          "body": "Второй чанк о нейронных сетях",
          "category": "ai",
          "tags": ["neural", "deep-learning"]
        }
      ]
    },
    "id": 1
  }'
```

### Гибридный поиск

Комбинируйте текстовый поиск с фильтрацией:

```bash
curl -X POST http://localhost:8007/cmd \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "search",
    "params": {
      "search_str": "машинное обучение",
      "metadata_filter": {
        "category": {"$eq": "ai"},
        "language": {"$eq": "ru"}
      },
      "limit": 5,
      "level_of_relevance": 0.7
    },
    "id": 1
  }'
```

### Удаление записей

Удалите записи по фильтру:

```bash
curl -X POST http://localhost:8007/cmd \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "chunk_delete",
    "params": {
      "metadata_filter": {
        "category": {"$eq": "test"}
      }
    },
    "id": 1
  }'
```

## 📊 Мониторинг

### Проверка состояния системы

```bash
curl -X POST http://localhost:8007/cmd \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "health",
    "params": {},
    "id": 1
  }'
```

### Получение справки

```bash
curl -X POST http://localhost:8007/cmd \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "help",
    "params": {},
    "id": 1
  }'
```

## 🛠️ Полезные команды

### Очистка данных

```bash
# Очистка soft-deleted записей
curl -X POST http://localhost:8007/cmd \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "chunk_deferred_cleanup",
    "params": {},
    "id": 1
  }'

# Очистка сиротских записей FAISS
curl -X POST http://localhost:8007/cmd \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "clean_faiss_orphans",
    "params": {},
    "id": 1
  }'
```

### Поиск дубликатов

```bash
curl -X POST http://localhost:8007/cmd \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "find_duplicate_uuids",
    "params": {
      "metadata_filter": {
        "category": {"$eq": "technical"}
      }
    },
    "id": 1
  }'
```

## 📋 Чеклист быстрого старта

- [ ] Сервер запущен на порту 8007
- [ ] Health check возвращает `{"status": "ok"}`
- [ ] Создан первый чанк
- [ ] Поиск по тексту работает
- [ ] Фильтрация по метаданным работает
- [ ] Удаление записей работает

## 🔗 Следующие шаги

1. **Изучите [Основные операции](basic-operations.md)** для глубокого понимания
2. **Изучите [Поиск и фильтрация](search-and-filtering.md)** для продвинутых возможностей
3. **Изучите [Управление данными](data-management.md)** для администрирования
4. **Изучите [Мониторинг](monitoring.md)** для отслеживания состояния

## 🆘 Получение помощи

- **Документация**: Этот раздел
- **API Reference**: [Справочник команд](../reference/command-schemas.md)
- **Health Check**: `http://localhost:8007/health`
- **OpenAPI**: `http://localhost:8007/docs`

---

*Следующий шаг: [Установка и настройка](installation.md)* 