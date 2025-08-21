# Архитектура Vector Store

## 🏗️ Общая архитектура

Vector Store построен на принципах микросервисной архитектуры с четким разделением ответственности:

```
┌─────────────────────────────────────────────────────────────────┐
│                    JSON-RPC API Layer                          │
│                    (Port 8007)                                 │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Command Layer                               │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐            │
│  │chunk_create │ │   search    │ │chunk_delete │            │
│  └─────────────┘ └─────────────┘ └─────────────┘            │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Service Layer                               │
│  ┌─────────────────────┐ ┌─────────────────────┐              │
│  │ VectorStoreService  │ │ MaintenanceService  │              │
│  └─────────────────────┘ └─────────────────────┘              │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Core Layer                                  │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐            │
│  │FAISS Service│ │Redis Service│ │Embedding    │            │
│  │             │ │             │ │Service      │            │
│  └─────────────┘ └─────────────┘ └─────────────┘            │
└─────────────────────────────────────────────────────────────────┘
```

## 📦 Компоненты системы

### 1. API Layer (JSON-RPC 2.0)

**Ответственность**: Обработка HTTP запросов, валидация JSON-RPC, маршрутизация команд

**Компоненты**:
- `server.py` - Основной сервер FastAPI
- `mcp_proxy_adapter` - JSON-RPC фреймворк
- Middleware для стандартизации ответов

**Особенности**:
- JSON-RPC 2.0 протокол
- Автоматическая валидация запросов
- Стандартизированные ответы
- Поддержка batch операций

### 2. Command Layer

**Ответственность**: Бизнес-логика команд, валидация параметров, обработка результатов

**Структура**:
```
vector_store/commands/
├── base.py                    # Базовый класс команд
├── result_classes.py          # Классы результатов
├── command_validator.py       # Валидация команд
├── index/                     # Команды индексации
│   ├── create_record.py       # Создание записей
│   ├── delete.py              # Удаление записей
│   ├── hard_delete.py         # Жесткое удаление
│   ├── deferred_cleanup.py    # Отложенная очистка
│   └── ...
└── search/                    # Команды поиска
    └── search_records.py      # Универсальный поиск
```

**Базовый класс команд**:
```python
class BaseVectorStoreCommand(Command):
    def __init__(self, vector_store_service: VectorStoreService):
        self.vector_store_service = vector_store_service
        self.performance_monitor = PerformanceMonitor()
    
    async def execute(self, **params):
        # Общая логика выполнения
        pass
```

### 3. Service Layer

**Ответственность**: Оркестрация операций, управление зависимостями

**Основные сервисы**:

#### VectorStoreService
```python
class VectorStoreService:
    def __init__(self, redis_client, faiss_service, embedding_service):
        self.redis_crud = RedisMetadataCRUDService(redis_client)
        self.redis_filter = RedisMetadataFilterService(redis_client)
        self.faiss_service = faiss_service
        self.embedding_service = embedding_service
```

**Методы**:
- `upsert_chunk()` - Создание/обновление чанков
- `search()` - Универсальный поиск
- `delete_chunk()` - Удаление чанков
- `get_chunk()` - Получение чанков

#### VectorStoreMaintenanceService
```python
class VectorStoreMaintenanceService:
    def __init__(self, redis_client, faiss_service):
        self.redis_client = redis_client
        self.faiss_service = faiss_service
```

**Методы**:
- `cleanup_orphans()` - Очистка сиротских записей
- `reindex_missing()` - Переиндексация
- `find_duplicates()` - Поиск дубликатов

### 4. Core Layer

#### FAISS Service
**Ответственность**: Векторные операции, индексация, поиск по сходству

```python
class FaissIndexService:
    def __init__(self, vector_size=384):
        self.index = faiss.IndexFlatL2(vector_size)
        self.vector_size = vector_size
    
    async def add_vectors(self, vectors):
        # Добавление векторов в индекс
        pass
    
    async def search_vector(self, query_vector, k):
        # Поиск по вектору
        pass
```

**Возможности**:
- Индексация 384-мерных векторов
- Поиск по косинусному сходству
- Batch операции
- Сохранение/загрузка индекса

#### Redis Service
**Ответственность**: Хранение метаданных, кэширование, фильтрация

```python
class RedisMetadataCRUDService:
    def __init__(self, redis_client):
        self.redis = redis_client
    
    async def save_metadata(self, uuid, metadata):
        # Сохранение метаданных
        pass
    
    async def get_metadata(self, uuid):
        # Получение метаданных
        pass
```

**Возможности**:
- CRUD операции с метаданными
- Атомарные операции
- Поддержка TTL
- Транзакции

#### Embedding Service
**Ответственность**: Векторизация текста

```python
class EmbeddingService:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
    
    async def embed_text(self, text):
        # Векторизация текста
        pass
```

**Возможности**:
- Поддержка различных моделей
- Batch векторизация
- Кэширование результатов
- Асинхронная обработка

## 🔄 Потоки данных

### 1. Создание чанка

```
Client Request
    │
    ▼
JSON-RPC API
    │
    ▼
ChunkCreateCommand
    │
    ▼
VectorStoreService.upsert_chunk()
    │
    ├─► EmbeddingService.embed_text()
    ├─► FAISS Service.add_vectors()
    └─► Redis Service.save_metadata()
    │
    ▼
Response
```

### 2. Поиск

```
Client Request
    │
    ▼
JSON-RPC API
    │
    ▼
SearchCommand
    │
    ▼
VectorStoreService.search()
    │
    ├─► EmbeddingService.embed_text() (если search_str)
    ├─► FAISS Service.search_vector()
    └─► Redis Service.filter_metadata()
    │
    ▼
Response
```

### 3. Удаление

```
Client Request
    │
    ▼
JSON-RPC API
    │
    ▼
ChunkDeleteCommand
    │
    ▼
VectorStoreService.delete_chunk()
    │
    ├─► Redis Service.mark_deleted()
    └─► (Optional) FAISS Service.remove_vectors()
    │
    ▼
Response
```

## 🗄️ Модели данных

### Chunk Metadata
```json
{
    "uuid": "123e4567-e89b-12d3-a456-426614174000",
    "body": "Текст чанка",
    "text": "Дополнительный текст",
    "language": "ru",
    "type": "DocBlock",
    "category": "technical",
    "tags": ["ai", "ml"],
    "source_id": "doc_123",
    "summary": "Краткое описание",
    "quality_score": 0.95,
    "created_at": "2024-12-19T10:00:00Z",
    "updated_at": "2024-12-19T10:00:00Z",
    "deleted_at": null,
    "vector_id": 12345
}
```

### Search Query
```json
{
    "search_str": "машинное обучение",
    "embedding": [0.1, 0.2, ...],
    "metadata_filter": {
        "category": {"$eq": "technical"},
        "language": {"$in": ["ru", "en"]}
    },
    "limit": 10,
    "level_of_relevance": 0.7,
    "offset": 0
}
```

### Search Result
```json
{
    "chunks": [
        {
            "uuid": "123e4567-e89b-12d3-a456-426614174000",
            "body": "Найденный текст",
            "similarity": 0.85,
            "metadata": {...}
        }
    ],
    "total_found": 1,
    "search_params": {...}
}
```

## 🔧 Конфигурация

### Основные параметры
```json
{
    "vector_store": {
        "redis_url": "redis://localhost:6380",
        "vector_size": 384,
        "faiss_index_path": "./data/faiss_index"
    },
    "embedding": {
        "embedding_url": "http://localhost:8001/cmd",
        "model_name": "all-MiniLM-L6-v2"
    },
    "api": {
        "host": "0.0.0.0",
        "port": 8007
    }
}
```

### Переменные окружения
- `VECTOR_STORE_REDIS_URL` - URL Redis
- `VECTOR_STORE_FAISS_PATH` - Путь к FAISS индексу
- `VECTOR_STORE_EMBEDDING_URL` - URL сервиса эмбеддингов
- `VECTOR_STORE_LOG_LEVEL` - Уровень логирования

## 🚀 Производительность

### Оптимизации
1. **Batch операции** - группировка запросов
2. **Кэширование** - Redis для метаданных
3. **Асинхронность** - asyncio для I/O операций
4. **Индексация** - FAISS для быстрого поиска
5. **Сжатие** - оптимизация хранения векторов

### Метрики
- **Latency**: < 100ms для поиска
- **Throughput**: > 1000 запросов/сек
- **Memory**: ~100MB на 1M векторов
- **Storage**: ~1.5GB на 1M векторов

## 🔒 Безопасность

### Аутентификация
- Поддержка JWT токенов
- API ключи
- OAuth 2.0 (планируется)

### Авторизация
- Role-based access control
- Resource-level permissions
- Audit logging

### Валидация
- JSON Schema валидация
- SQL injection protection
- Rate limiting

## 🧪 Тестирование

### Структура тестов
```
tests/
├── conftest.py                    # Фикстуры
├── test_commands/                 # Тесты команд
│   ├── test_create_record.py
│   ├── test_search.py
│   └── test_delete.py
├── test_services/                 # Тесты сервисов
│   ├── test_vector_store_service.py
│   └── test_faiss_service.py
└── integration/                   # Интеграционные тесты
    └── test_full_workflow.py
```

### Покрытие кода
- Минимум 90% покрытия
- Unit тесты для всех компонентов
- Integration тесты для workflows
- Performance тесты

## 📈 Мониторинг

### Метрики
- **Системные**: CPU, Memory, Disk
- **Приложения**: Request rate, Latency, Error rate
- **Бизнес**: Chunks created, Searches performed

### Логирование
- Structured logging (JSON)
- Log levels: DEBUG, INFO, WARNING, ERROR
- Log rotation и compression

### Алерты
- High latency alerts
- Error rate thresholds
- Resource usage alerts

---

*Следующий раздел: [API Reference](api-reference.md)* 