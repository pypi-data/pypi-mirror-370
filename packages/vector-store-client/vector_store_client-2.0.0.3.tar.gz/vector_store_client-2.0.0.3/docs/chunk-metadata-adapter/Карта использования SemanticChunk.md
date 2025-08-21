# Карта использования SemanticChunk и паспортов сервисов

## 1. Использование метаданных SemanticChunk

| Сервис                | Читает (поля / группы)                                    | Записывает / обновляет                                                      | Назначение                                                                        |                              |
| --------------------- | --------------------------------------------------------- | --------------------------------------------------------------------------- | --------------------------------------------------------------------------------- | ---------------------------- |
| **Gateway**           | `uuid`, `type`, `role`, `body`, `created_at`              | —                                                                           | Формирует первичный пользовательский `SemanticChunk` и проксирует запросы моделей |                              |
| **MCP‑Proxy**         | `uuid`, `type`, `role`, `body`, `block_meta.tool`, `tags` | `status`, `metrics.used_in_generation`, `links(parent)`                     | Валидирует и проксирует вызовы инструментов; логирует как `ToolCommand`           |                              |
| **Logger**            | —                                                         | Полный `SemanticChunk (type=Log)` + `status`, `metrics.*`                   | Централизованная трассировка запросов                                             |                              |
| **SVOChunker**        | `body`, `language`, `tags`                                | Создаёт дочерние чанки: `type=DocBlock`, `ordinal`, `text`, `boundary_next` | Семантическое разбиение текста                                                    |                              |
| **SentenceChunker**   | `body`, `language`                                        | `type=DocBlock`, `ordinal`, `text`                                          | Разбиение по предложениям/разметке                                                |                              |
| **SmartChunker**      | `List[SemanticChunk]`                                     | `links`, `chunking_version`, `metrics.coverage`                             | Комбинированный пайплайн, масштабирует чанкеры                                    |                              |
| **Embedding**         | \`body                                                    | text`, `language`, `type\`                                                  | `embedding`, `metrics.boundary_prev/next`                                         | Генерация эмбеддингов        |
| **EmbeddingPipeline** | `embedding` отсутствует                                   | `embedding`                                                                 | Балансировщик запросов к Embedding‑нодам                                          |                              |
| **ChunkWriter**       | Полный `SemanticChunk`                                    | — (конвертирует в flat перед записью)                                       | Пишет в несколько VectorStore                                                     |                              |
| **VectorStore**       | `uuid`, `embedding`, плоские индексационные поля          | —                                                                           | FAISS + Redis, гибридный поиск                                                    |                              |
| **ChunkRetriever**    | `embedding`, `ChunkQuery`                                 | —                                                                           | Параллельный поиск и агрегация                                                    |                              |
| **DocStore**          | `body`, `source_path`, `block_meta.*`                     | `type=DocBlock`, `category="docs"`, `tags=["docs"]`                         | Хранение/поиск документации                                                       |                              |
| **SemanticCodeBase**  | `block_meta.ast_signature`, `language`, …                 | `type=CodeBlock`, `block_meta` (repo, path, lines)                          | Семантическая база кода                                                           |                              |
| **RAG**               | `embedding`, `quality_score`, \`body                      | text`, `links\`                                                             | `metrics.used_as_context`, `metrics.matches`                                      | Retrieve‑and‑Generate ответы |
| **MDManager**         | Все логи (`type in {Log, ToolCommand}`) + чанки           | `metrics.quality_score`, `metrics.reliability`, `status`, `tags`            | Оценка качества, надёжности, сортировка                                           |                              |

---

## 2. Паспорт сервисов (ключевые поля конфигурации)

| Сервис                | Конфигурационные поля                                      |
| --------------------- | ---------------------------------------------------------- |
| **Gateway**           | `MODEL_ENDPOINT`, `RATE_LIMIT`, `TRACE_HEADER`             |
| **MCP‑Proxy**         | `CMD_SCAN_DIR`, `REDIS_DSN`, `LOG_LEVEL`, `JWT_PUBLIC_KEY` |
| **Logger**            | `CLICKHOUSE_DSN`, `BUFFER_SIZE`, `OTEL_EXPORTER_URL`       |
| **SVOChunker**        | `LANG_DETECT_MODEL`, `MAX_LEN`, `QUEUE_LIMIT`              |
| **SentenceChunker**   | `MARKDOWN`, `SPLIT_REGEX`                                  |
| **SmartChunker**      | `STEPS` (YAML list), `HPA_THRESHOLD`                       |
| **Embedding**         | `MODEL_NAME`, `DEVICE`, `BATCH_SIZE`                       |
| **EmbeddingPipeline** | `BACKENDS[]`, `RETRY`, `TIMEOUT`                           |
| **VectorStore**       | `REDIS_URI`, `FAISS_INDEX_PATH`, `NPROBES`                 |
| **ChunkWriter**       | `SHARDS[]`, `QUORUM`, `RETRY_POLICY`                       |
| **ChunkRetriever**    | `TARGET_STORES[]`, `AGG_MODE`                              |
| **DocStore**          | `DOC_PATHS[]`, `PARSER`, `LANG_DEFAULT`                    |
| **SemanticCodeBase**  | `REPOS[]`, `LANGS[]`, `MAX_FILE_SIZE`                      |
| **RAG**               | `RETRIEVER_TOP_K`, `RERANKER`, `SYSTEM_PROMPT`             |
| **MDManager**         | `QUALITY_RULES.yaml`, `CRON_SCHEDULE`, `ALERT_THRESHOLD`   |

