# Справочник команд Vector Store

## AST поддержка

Vector Store поддерживает AST (Abstract Syntax Tree) фильтрацию для сложных запросов. AST позволяет создавать структурированные выражения с логическими операторами.

### Поддерживаемые операторы

- **Логические операторы**: `AND`, `OR`, `NOT`
- **Операторы сравнения**: `=`, `!=`, `>`, `>=`, `<`, `<=`
- **Операторы включения**: `IN`, `NOT_IN`

### Примеры AST фильтров

```json
{
    "operator": "AND",
    "left": {
        "field": "category",
        "operator": "=",
        "value": "technical"
    },
    "right": {
        "field": "language",
        "operator": "=",
        "value": "en"
    }
}
```

```json
{
    "operator": "OR",
    "left": {
        "field": "type",
        "operator": "=",
        "value": "DocBlock"
    },
    "right": {
        "field": "type",
        "operator": "=",
        "value": "CodeBlock"
    }
}
```

```json
{
    "operator": "NOT",
    "operand": {
        "field": "category",
        "operator": "=",
        "value": "test"
    }
}
```

### Параметр ast_filter

Команды `search`, `chunk_delete`, `count` поддерживают параметр `ast_filter` для AST-фильтрации:

```json
{
    "ast_filter": {
        "operator": "AND",
        "left": {"field": "category", "operator": "=", "value": "technical"},
        "right": {"field": "language", "operator": "=", "value": "en"}
    }
}
```

## Общий формат JSON-RPC запросов

Все команды используют JSON-RPC 2.0 формат:

```json
{
    "jsonrpc": "2.0",
    "method": "command_name",
    "params": {
        // параметры команды
    },
    "id": 1
}
```

## Общий формат ответов

### Успешный ответ
```json
{
    "jsonrpc": "2.0",
    "result": {
        "success": true,
        "data": {
            // данные результата
        }
    },
    "id": 1
}
```

### Ответ с ошибкой
```json
{
    "jsonrpc": "2.0",
    "error": {
        "code": -32001,
        "message": "Описание ошибки",
        "data": {
            "error_code": "validation_error",
            "details": {}
        }
    },
    "id": 1
}
```

---

## 1. chunk_create - Создание чанков

### Описание
Создает один или несколько текстовых чанков с автоматической векторизацией.

### Параметры
```json
{
    "chunks": [
        {
            "body": "Текст чанка (обязательно)",
            "text": "Дополнительный текст (опционально)",
            "type": "DocBlock",
            "language": "en",
            "category": "technical",
            "title": "Заголовок чанка",
            "tags": ["tag1", "tag2"]
        }
    ]
}
```

### Схема параметров
```json
{
    "type": "object",
    "properties": {
        "chunks": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "body": {
                        "type": "string",
                        "description": "Original chunk text (required)",
                        "minLength": 1,
                        "maxLength": 10000
                    },
                    "text": {
                        "type": "string",
                        "description": "Normalized text for search (optional, defaults to body)",
                        "minLength": 0,
                        "maxLength": 10000
                    },
                    "type": {
                        "type": "string",
                        "description": "Chunk type",
                        "enum": ["Draft", "DocBlock", "CodeBlock", "Message", "Section", "Other"]
                    },
                    "language": {
                        "type": "string",
                        "description": "Language code"
                    },
                    "category": {
                        "type": "string",
                        "description": "Business category",
                        "maxLength": 64
                    },
                    "title": {
                        "type": "string",
                        "description": "Title or short name",
                        "maxLength": 256
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of tags for classification"
                    }
                },
                "required": ["body"],
                "additionalProperties": true
            },
            "description": "Array of chunk metadata objects for creation",
            "minItems": 1
        }
    },
    "required": ["chunks"],
    "additionalProperties": false
}
```

### Пример запроса
```json
{
    "jsonrpc": "2.0",
    "method": "chunk_create",
    "params": {
        "chunks": [
            {
                "body": "Vector Store - это высокопроизводительный сервис для хранения и поиска векторных эмбеддингов.",
                "text": "Vector Store service description",
                "type": "DocBlock",
                "category": "technical",
                "tags": ["vector", "search", "ai"]
            }
        ]
    },
    "id": 1
}
```

### Пример успешного ответа
```json
{
    "jsonrpc": "2.0",
    "result": {
        "success": true,
        "data": {
            "created_count": 1,
            "chunks": [
                {
                    "uuid": "123e4567-e89b-12d3-a456-426614174000",
                    "status": "created"
                }
            ]
        }
    },
    "id": 1
}
```

### Коды ошибок
- `invalid_params` - Неверные параметры (chunks не массив, пустой массив)
- `validation_error` - Ошибка валидации чанка (отсутствует body, неверный тип)
- `creation_error` - Ошибка создания (ошибка сервиса, векторизации)
- `embedding_error` - Ошибка генерации эмбеддинга (ошибка сервиса эмбеддингов)

---

## 2. search - Поиск

### Описание
Универсальная команда поиска, поддерживающая семантический поиск, поиск по векторам и фильтрацию метаданных.

### Параметры
```json
{
    "search_str": "текст для поиска (опционально)",
    "embedding": [0.1, 0.2, 0.3, ...], // 384-мерный вектор (опционально)
    "metadata_filter": {
        "category": {"$eq": "technical"},
        "language": {"$in": ["en", "ru"]},
        "year": {"$gte": 2020, "$lte": 2024}
    },
    "limit": 10,
    "level_of_relevance": 0.7,
    "offset": 0
}
```

### Схема параметров
```json
{
    "type": "object",
    "properties": {
        "search_str": {
            "type": "string",
            "description": "Semantic search string that will be converted to 384-dimensional embedding vector"
        },
        "embedding": {
            "type": "array",
            "items": {"type": "number"},
            "minItems": 384,
            "maxItems": 384,
            "description": "Precomputed 384-dim embedding vector for direct similarity search"
        },
        "metadata_filter": {
            "type": "object",
            "description": "Metadata filter for filtering results",
            "additionalProperties": true
        },
        "ast_filter": {
            "type": "object",
            "description": "AST-based filter expression for advanced filtering",
            "additionalProperties": true
        },
        "limit": {
            "type": "integer",
            "minimum": 1,
            "maximum": 1000,
            "default": 10,
            "description": "Maximum number of results to return"
        },
        "level_of_relevance": {
            "type": "number",
            "minimum": 0.0,
            "maximum": 1.0,
            "default": 0.0,
            "description": "Minimum similarity threshold"
        },
        "offset": {
            "type": "integer",
            "minimum": 0,
            "default": 0,
            "description": "Number of results to skip for pagination"
        }
    },
    "required": [],
    "additionalProperties": false
}
```

### Пример запроса
```json
{
    "jsonrpc": "2.0",
    "method": "search",
    "params": {
        "search_str": "vector store performance",
        "metadata_filter": {
            "category": {"$eq": "technical"},
            "language": {"$eq": "en"}
        },
        "ast_filter": {
            "operator": "AND",
            "left": {"field": "category", "operator": "=", "value": "technical"},
            "right": {"field": "language", "operator": "=", "value": "en"}
        },
        "limit": 5,
        "level_of_relevance": 0.8
    },
    "id": 1
}
```

### Пример успешного ответа
```json
{
    "jsonrpc": "2.0",
    "result": {
        "success": true,
        "data": {
            "chunks": [
                {
                    "uuid": "123e4567-e89b-12d3-a456-426614174000",
                    "body": "Vector Store обеспечивает высокую производительность...",
                    "text": "Vector Store обеспечивает высокую производительность...",
                    "similarity": 0.85,
                    "metadata": {
                        "category": "technical",
                        "language": "en",
                        "tags": ["performance", "vector"]
                    }
                }
            ],
            "total_found": 1,
            "search_params": {
                "search_str": "vector store performance",
                "limit": 5,
                "level_of_relevance": 0.8
            }
        }
    },
    "id": 1
}
```

### Коды ошибок
- `invalid_params` - Неверные параметры (неверный формат embedding)
- `validation_error` - Ошибка валидации (не указан метод поиска)
- `search_error` - Ошибка поиска (ошибка сервиса)
- `embedding_error` - Ошибка генерации эмбеддинга (ошибка сервиса эмбеддингов)

---

## 3. count - Подсчет записей

### Описание
Подсчитывает количество записей с опциональной фильтрацией по метаданным.

### Параметры
```json
{
    "metadata_filter": {
        "category": {"$eq": "technical"},
        "language": {"$in": ["en", "ru"]}
    },
    "include_deleted": false
}
```

### Схема параметров
```json
{
    "type": "object",
    "properties": {
        "metadata_filter": {
            "type": "object",
            "description": "Metadata filter for counting",
            "additionalProperties": true
        },
        "ast_filter": {
            "type": "object",
            "description": "AST-based filter expression for advanced counting",
            "additionalProperties": true
        },
        "include_deleted": {
            "type": "boolean",
            "default": false,
            "description": "Whether to include records marked for deletion in the count"
        }
    },
    "required": [],
    "additionalProperties": false
}
```

### Пример запроса
```json
{
    "jsonrpc": "2.0",
    "method": "count",
    "params": {
        "metadata_filter": {
            "category": {"$eq": "technical"},
            "language": {"$eq": "en"}
        },
        "ast_filter": {
            "operator": "AND",
            "left": {"field": "category", "operator": "=", "value": "technical"},
            "right": {"field": "language", "operator": "=", "value": "en"}
        },
        "include_deleted": false
    },
    "id": 1
}
```

### Пример успешного ответа
```json
{
    "jsonrpc": "2.0",
    "result": {
        "success": true,
        "data": {
            "count": 150,
            "filter_applied": {
                "category": {"$eq": "technical"},
                "language": {"$eq": "en"}
            },
            "include_deleted": false
        }
    },
    "id": 1
}
```

### Коды ошибок
- `invalid_params` - Неверные параметры (неверный формат фильтра)
- `validation_error` - Ошибка валидации фильтра
- `count_error` - Ошибка подсчета (ошибка сервиса)

---

## 4. info - Информация о системе

### Описание
Возвращает подробную информацию о состоянии векторного хранилища.

### Параметры
```json
{}
```

### Схема параметров
```json
{
    "type": "object",
    "properties": {},
    "required": [],
    "additionalProperties": false
}
```

### Пример запроса
```json
{
    "jsonrpc": "2.0",
    "method": "info",
    "params": {},
    "id": 1
}
```

### Пример успешного ответа
```json
{
    "jsonrpc": "2.0",
    "result": {
        "success": true,
        "data": {
            "uuid_statistics": {
                "total_uuids": 1000,
                "active_uuids": 950,
                "deleted_uuids": 50,
                "deletion_rate": 0.05
            },
            "source_id_statistics": {
                "total_source_ids": 1000,
                "unique_source_ids": 25,
                "source_id_distribution": {"doc1": 40, "doc2": 35},
                "most_common_source_ids": [["doc1", 40], ["doc2", 35]]
            },
            "faiss_statistics": {
                "total_vectors": 950,
                "vector_size": 384,
                "index_type": "IndexFlatL2",
                "operations_since_save": 0,
                "last_save_time": "2024-01-15T10:30:00",
                "auto_save_enabled": true
            },
            "redis_statistics": {
                "total_vector_keys": 1000,
                "deleted_keys": 50,
                "estimated_memory_usage_bytes": 1048576,
                "redis_connection_healthy": true
            },
            "metadata_statistics": {
                "indexed_fields": ["category", "year", "source_id"],
                "index_statistics": {"size": 1000, "unique_values_count": 25},
                "has_index_manager": true
            },
            "search_statistics": {
                "total_records": 1000,
                "deleted_records": 50,
                "active_records": 950,
                "vector_size": 384
            },
            "system_info": {
                "vector_size": 384,
                "has_embedding_service": true,
                "has_crud_service": true,
                "has_filter_service": true,
                "has_maintenance_service": true
            },
            "cache_metrics": {
                "query_cache": {
                    "hits": 44,
                    "misses": 1,
                    "evictions": 0,
                    "size": 3,
                    "hit_rate": 97.8
                }
            },
            "performance_metrics": {
                "query_parsing": {
                    "average_parse_time_ms": 0.5,
                    "total_queries_parsed": 1000
                }
            },
            "complexity_metrics": {
                "ast_analysis": {
                    "average_max_depth": 3.2,
                    "average_total_conditions": 2.8
                }
            },
            "error_metrics": {
                "validation_errors": {
                    "total_queries": 1000,
                    "valid_queries": 950,
                    "invalid_queries": 50,
                    "error_rate": 5.0
                }
            }
        }
    },
    "id": 1
}
```

### Коды ошибок
- `service_operation_error` - Ошибка сервиса (не удалось получить информацию)

---

## 5. chunk_delete - Удаление чанков

### Описание
Удаляет чанки по фильтру метаданных (soft delete).

### Параметры
```json
{
    "metadata_filter": {
        "uuid": {"$eq": "123e4567-e89b-12d3-a456-426614174000"},
        "category": {"$eq": "test"},
        "language": {"$in": ["en", "ru"]}
    }
}
```

### Схема параметров
```json
{
    "type": "object",
    "properties": {
        "metadata_filter": {
            "type": "object",
            "description": "Metadata filter for deletion",
            "additionalProperties": true
        },
        "ast_filter": {
            "type": "object",
            "description": "AST-based filter expression for advanced deletion",
            "additionalProperties": true
        }
    },
    "required": [],
    "additionalProperties": false
}
```

### Пример запроса
```json
{
    "jsonrpc": "2.0",
    "method": "chunk_delete",
    "params": {
        "metadata_filter": {
            "category": {"$eq": "test"},
            "language": {"$eq": "en"}
        },
        "ast_filter": {
            "operator": "AND",
            "left": {"field": "category", "operator": "=", "value": "test"},
            "right": {"field": "language", "operator": "=", "value": "en"}
        }
    },
    "id": 1
}
```

### Пример успешного ответа
```json
{
    "jsonrpc": "2.0",
    "result": {
        "success": true,
        "data": {
            "deleted_count": 3,
            "filter_applied": {
                "category": {"$eq": "test"},
                "language": {"$eq": "en"}
            }
        }
    },
    "id": 1
}
```

### Коды ошибок
- `invalid_params` - Неверные параметры
- `validation_error` - Ошибка валидации фильтра
- `deletion_error` - Ошибка удаления
- `safety_error` - Ошибка безопасности (попытка удалить все записи)

---

## 6. chunk_hard_delete - Жесткое удаление

### Описание
Физически удаляет чанки из системы (требует блокировки сервиса).

### Параметры
```json
{
    "uuids": [
        "123e4567-e89b-12d3-a456-426614174000",
        "456e7890-f12c-34d5-e678-901234567890"
    ]
}
```

### Схема параметров
```json
{
    "type": "object",
    "properties": {
        "uuids": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of UUIDs to hard delete",
            "minItems": 1
        }
    },
    "required": ["uuids"],
    "additionalProperties": false
}
```

### Пример запроса
```json
{
    "jsonrpc": "2.0",
    "method": "chunk_hard_delete",
    "params": {
        "uuids": [
            "123e4567-e89b-12d3-a456-426614174000",
            "456e7890-f12c-34d5-e678-901234567890"
        ]
    },
    "id": 1
}
```

### Пример успешного ответа
```json
{
    "jsonrpc": "2.0",
    "result": {
        "success": true,
        "data": {
            "deleted_count": 2,
            "deleted_uuids": [
                "123e4567-e89b-12d3-a456-426614174000",
                "456e7890-f12c-34d5-e678-901234567890"
            ]
        }
    },
    "id": 1
}
```

### Коды ошибок
- `service_locked` - Сервис заблокирован
- `invalid_uuids` - Неверный формат UUID
- `vector_manager_missing` - VectorIndexManager недоступен
- `lock_manager_missing` - ServiceLockManager недоступен
- `deletion_failed` - Ошибка удаления

---

## 7. chunk_deferred_cleanup - Отложенная очистка

### Описание
Физически удаляет все soft-deleted записи для освобождения места.

### Параметры
```json
{}
```

### Схема параметров
```json
{
    "type": "object",
    "properties": {},
    "required": [],
    "additionalProperties": false
}
```

### Пример запроса
```json
{
    "jsonrpc": "2.0",
    "method": "chunk_deferred_cleanup",
    "params": {},
    "id": 1
}
```

### Пример успешного ответа
```json
{
    "jsonrpc": "2.0",
    "result": {
        "success": true,
        "data": {
            "cleaned_count": 15,
            "message": "Successfully cleaned up 15 soft-deleted records"
        }
    },
    "id": 1
}
```

### Коды ошибок
- `vector_manager_missing` - VectorIndexManager недоступен
- `cleanup_failed` - Ошибка очистки
- `no_deleted_records` - Нет удаленных записей

---

## 8. find_duplicate_uuids - Поиск дубликатов

### Описание
Находит все UUID с дублирующимися записями.

### Параметры
```json
{
    "metadata_filter": {
        "category": {"$eq": "technical"}
    }
}
```

### Схема параметров
```json
{
    "type": "object",
    "properties": {
        "metadata_filter": {
            "type": "object",
            "description": "Optional metadata filter to apply before finding duplicates",
            "additionalProperties": true
        }
    },
    "required": [],
    "additionalProperties": false
}
```

### Пример запроса
```json
{
    "jsonrpc": "2.0",
    "method": "find_duplicate_uuids",
    "params": {
        "metadata_filter": {
            "category": {"$eq": "technical"}
        }
    },
    "id": 1
}
```

### Пример успешного ответа
```json
{
    "jsonrpc": "2.0",
    "result": {
        "success": true,
        "data": {
            "duplicate_uuids": [
                {
                    "uuid": "duplicate-uuid-1",
                    "records": [
                        {"uuid": "duplicate-uuid-1", "text": "content 1"},
                        {"uuid": "duplicate-uuid-1", "text": "content 2"}
                    ]
                }
            ]
        }
    },
    "id": 1
}
```

### Коды ошибок
- `validation_error` - Ошибка валидации фильтра
- `scan_error` - Ошибка сканирования базы данных

---

## 9. clean_faiss_orphans - Очистка сиротских записей

### Описание
Удаляет записи из FAISS, которые отсутствуют в Redis.

### Параметры
```json
{}
```

### Схема параметров
```json
{
    "type": "object",
    "properties": {},
    "additionalProperties": false
}
```

### Пример запроса
```json
{
    "jsonrpc": "2.0",
    "method": "clean_faiss_orphans",
    "params": {},
    "id": 1
}
```

### Пример успешного ответа
```json
{
    "jsonrpc": "2.0",
    "result": {
        "success": true,
        "data": {
            "removed": 5
        }
    },
    "id": 1
}
```

### Коды ошибок
- `clean_error` - Внутренняя ошибка очистки

---

## 10. reindex_missing_embeddings - Переиндексация

### Описание
Пересоздает эмбеддинги для записей, у которых они отсутствуют.

### Параметры
```json
{}
```

### Схема параметров
```json
{
    "type": "object",
    "properties": {},
    "additionalProperties": false
}
```

### Пример запроса
```json
{
    "jsonrpc": "2.0",
    "method": "reindex_missing_embeddings",
    "params": {},
    "id": 1
}
```

### Пример успешного ответа
```json
{
    "jsonrpc": "2.0",
    "result": {
        "success": true,
        "data": {
            "updated": 10,
            "skipped": 5,
            "errors": 2,
            "errors_uuids": ["uuid1", "uuid2"]
        }
    },
    "id": 1
}
```

### Коды ошибок
- `reindex_error` - Внутренняя ошибка переиндексации

---

## 11. force_delete_by_uuids - Принудительное удаление

### Описание
Принудительно удаляет записи по UUID без проверок.

### Параметры
```json
{
    "uuids": [
        "123e4567-e89b-12d3-a456-426614174000",
        "456e7890-f12c-34d5-e678-901234567890"
    ]
}
```

### Схема параметров
```json
{
    "type": "object",
    "properties": {
        "uuids": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 1,
            "description": "List of UUIDs (any strings) to delete"
        }
    },
    "required": ["uuids"],
    "additionalProperties": false
}
```

### Пример запроса
```json
{
    "jsonrpc": "2.0",
    "method": "force_delete_by_uuids",
    "params": {
        "uuids": [
            "123e4567-e89b-12d3-a456-426614174000",
            "456e7890-f12c-34d5-e678-901234567890"
        ]
    },
    "id": 1
}
```

### Пример успешного ответа
```json
{
    "jsonrpc": "2.0",
    "result": {
        "success": true,
        "data": {
            "deleted": 5,
            "not_found": 2,
            "errors": 1,
            "errors_uuids": ["bad-uuid"]
        }
    },
    "id": 1
}
```

### Коды ошибок
- `force_delete_error` - Внутренняя ошибка удаления

---

## 12. health - Проверка состояния

### Описание
Возвращает информацию о состоянии сервера.

### Параметры
```json
{}
```

### Пример запроса
```json
{
    "jsonrpc": "2.0",
    "method": "health",
    "params": {},
    "id": 1
}
```

### Пример успешного ответа
```json
{
    "jsonrpc": "2.0",
    "result": {
        "success": true,
        "data": {
            "status": "ok",
            "version": "3.1.6",
            "uptime": 141.99389,
            "components": {
                "system": {
                    "python_version": "3.12.3",
                    "platform": "Linux-6.8.0-64-generic-x86_64",
                    "cpu_count": 8
                },
                "process": {
                    "pid": 198272,
                    "memory_usage_mb": 91.921875,
                    "start_time": "2025-07-28T01:29:32.620000"
                },
                "commands": {
                    "registered_count": 12
                }
            }
        }
    },
    "id": 1
}
```

---

## 13. help - Справка

### Описание
Возвращает информацию о доступных командах.

### Параметры
```json
{
    "cmdname": "command_name" // опционально
}
```

### Пример запроса
```json
{
    "jsonrpc": "2.0",
    "method": "help",
    "params": {},
    "id": 1
}
```

### Пример успешного ответа
```json
{
    "jsonrpc": "2.0",
    "result": {
        "tool_info": {
            "name": "MCP-Proxy API Service",
            "description": "JSON-RPC API for microservice command execution",
            "version": "1.0.0"
        },
        "commands": {
            "chunk_create": {
                "summary": "Creates chunk records in vector store",
                "params_count": 4
            },
            "search": {
                "summary": "Unified search command",
                "params_count": 4
            }
        },
        "total": 12
    },
    "id": 1
}
```

---

## 14. config - Конфигурация

### Описание
Управляет конфигурацией сервиса.

### Параметры
```json
{
    "action": "get|set|reload",
    "config": {
        // параметры конфигурации
    }
}
```

### Пример запроса
```json
{
    "jsonrpc": "2.0",
    "method": "config",
    "params": {
        "action": "get"
    },
    "id": 1
}
```

### Пример успешного ответа
```json
{
    "jsonrpc": "2.0",
    "result": {
        "success": true,
        "data": {
            "config": {
                "vector_store": {
                    "redis_url": "redis://localhost:6380",
                    "vector_size": 384,
                    "faiss_index_path": "./data/faiss_index"
                },
                "embedding": {
                    "embedding_url": "http://localhost:8001/cmd",
                    "model_name": "all-MiniLM-L6-v2"
                }
            }
        }
    },
    "id": 1
}
```

---

## Операторы фильтрации метаданных

### Поддерживаемые операторы

| Оператор | Описание | Пример |
|----------|----------|---------|
| `$eq` | Равно | `{"category": {"$eq": "technical"}}` |
| `$ne` | Не равно | `{"language": {"$ne": "en"}}` |
| `$in` | В списке | `{"tags": {"$in": ["ai", "ml"]}}` |
| `$nin` | Не в списке | `{"status": {"$nin": ["deleted"]}}` |
| `$gt` | Больше | `{"year": {"$gt": 2020}}` |
| `$gte` | Больше или равно | `{"quality_score": {"$gte": 0.8}}` |
| `$lt` | Меньше | `{"tokens": {"$lt": 1000}}` |
| `$lte` | Меньше или равно | `{"coverage": {"$lte": 1.0}}` |
| `$range` | Диапазон | `{"year": {"$range": [2020, 2024]}}` |

### Примеры сложных фильтров

```json
{
    "metadata_filter": {
        "$and": [
            {"category": {"$eq": "technical"}},
            {"language": {"$in": ["en", "ru"]}},
            {"year": {"$gte": 2020}},
            {"quality_score": {"$gte": 0.8}}
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

---

## Общие коды ошибок

| Код | Описание | HTTP Status |
|-----|----------|-------------|
| -32001 | Validation Error | 400 |
| -32002 | Command Error | 500 |
| -32003 | Service Error | 503 |
| -32004 | Authentication Error | 401 |
| -32005 | Authorization Error | 403 |
| -32006 | Resource Not Found | 404 |
| -32007 | Conflict Error | 409 |
| -32008 | Rate Limit Exceeded | 429 |

---

*Последнее обновление: 2024-12-19* 