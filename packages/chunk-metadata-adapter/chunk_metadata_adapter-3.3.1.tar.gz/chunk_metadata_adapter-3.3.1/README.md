# Chunk Metadata Adapter

Библиотека для создания, управления и преобразования метаданных для чанков контента в различных системах, включая RAG-пайплайны, обработку документов и наборы данных для машинного обучения.

## Возможности

- Создание структурированных метаданных для чанков контента
- Поддержка разных форматов метаданных (плоский и структурированный)
- Отслеживание происхождения и жизненного цикла данных
- Сохранение информации о качестве и использовании чанков
- Поддержка расширенных метрик качества: coverage, cohesion, boundary_prev, boundary_next
- **BM25 полнотекстовый поиск** по содержимому чанков
- **Гибридный поиск** (BM25 + семантический) с настраиваемыми весами
- **Сложные фильтры** с логическими выражениями (AND/OR/NOT)
- **Валидация и безопасность** для всех типов запросов

## Жизненный цикл данных

Библиотека поддерживает следующие этапы жизненного цикла данных:

1. **RAW (Сырые данные)** - данные в исходном виде, сразу после загрузки в систему
2. **CLEANED (Очищенные)** - данные прошли предварительную очистку от шума, ошибок и опечаток
3. **VERIFIED (Проверенные)** - данные проверены на соответствие правилам и стандартам
4. **VALIDATED (Валидированные)** - данные прошли валидацию с учетом контекста и перекрестных ссылок
5. **RELIABLE (Надежные)** - данные признаны надежными и готовы к использованию в критических системах

![Жизненный цикл данных](https://example.com/data_lifecycle.png)

### Преимущества учета жизненного цикла

- **Прозрачность происхождения** - отслеживание всех этапов обработки данных
- **Контроль качества** - возможность отфильтровать данные, не достигшие требуемых этапов обработки
- **Аудит процессов** - возможность анализировать и улучшать процессы очистки и валидации
- **Управление надежностью** - возможность использовать только проверенные данные для критических задач

## Установка

### Основные зависимости
```bash
pip install chunk-metadata-adapter
```

### Зависимости для разработки
```bash
pip install -e ".[dev]"
```

### Виртуальное окружение
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -e ".[dev]"
```

### Новые возможности фильтрации
После установки зависимостей доступны новые возможности:
- Сложные логические выражения (AND/OR/NOT)
- Расширенные строковые операции (LIKE, regex)
- Вложенные поля (block_meta.version)
- Оптимизация запросов
- Валидация безопасности

## Использование

### Создание метаданных для чанка в процессе жизненного цикла

```python
from chunk_metadata_adapter import ChunkMetadataBuilder, ChunkType, ChunkStatus
import uuid

# Создаем builder для проекта
builder = ChunkMetadataBuilder(project="MyProject")
source_id = str(uuid.uuid4())

# Шаг 1: Создание чанка с сырыми данными (RAW)
raw_chunk = builder.build_semantic_chunk(
    text="Данные пользователя: Иван Иванов, ivan@eample.com, Москва",
    language="text",
    type=ChunkType.DOC_BLOCK,
    source_id=source_id,
    status=ChunkStatus.RAW,  # Указываем статус RAW
    body="Данные пользователя: Иван Иванов, ivan@eample.com, Москва"  # raw
)

# Шаг 2: Очистка данных (исправление ошибок, опечаток)
cleaned_chunk = builder.build_semantic_chunk(
    text="Данные пользователя: Иван Иванов, ivan@example.com, Москва",  # Исправлена опечатка в email
    language="text",
    type=ChunkType.DOC_BLOCK,
    source_id=source_id,
    status=ChunkStatus.CLEANED,  # Данные очищены
    body="Данные пользователя: Иван Иванов, ivan@example.com, Москва"  # cleaned
)

# Шаг 3: Верификация данных (проверка по правилам)
verified_chunk = builder.build_semantic_chunk(
    text="Данные пользователя: Иван Иванов, ivan@example.com, Москва",
    language="text",
    type=ChunkType.DOC_BLOCK,
    source_id=source_id,
    status=ChunkStatus.VERIFIED,  # Данные проверены
    tags=["verified_email"],  # Метки верификации
    body="Данные пользователя: Иван Иванов, ivan@example.com, Москва"  # raw
)

# Шаг 4: Валидация данных (проверка относительно других данных)
validated_chunk = builder.build_semantic_chunk(
    text="Данные пользователя: Иван Иванов, ivan@example.com, Москва",
    language="text",
    type=ChunkType.DOC_BLOCK,
    source_id=source_id,
    status=ChunkStatus.VALIDATED,  # Данные валидированы
    links=[f"reference:{str(uuid.uuid4())}"],  # Связь с проверочным источником
    body="Данные пользователя: Иван Иванов, ivan@example.com, Москва"  # raw
)

# Шаг 5: Надежные данные (готовы к использованию)
reliable_chunk = builder.build_semantic_chunk(
    text="Данные пользователя: Иван Иванов, ivan@example.com, Москва",
    language="text",
    type=ChunkType.DOC_BLOCK,
    source_id=source_id,
    status=ChunkStatus.RELIABLE,  # Данные признаны надежными
    coverage=0.95,
    cohesion=0.8,
    boundary_prev=0.7,
    boundary_next=0.9,
    body="Данные пользователя: Иван Иванов, ivan@example.com, Москва"  # raw
)
```

### Фильтрация чанков по статусу жизненного цикла

```python
# Пример функции для фильтрации чанков по статусу
def filter_chunks_by_status(chunks, min_status):
    """
    Фильтрует чанки, оставляя только те, которые достигли определенного статуса
    или выше в жизненном цикле данных.
    
    Порядок статусов: 
    RAW < CLEANED < VERIFIED < VALIDATED < RELIABLE
    
    Args:
        chunks: список чанков для фильтрации
        min_status: минимальный требуемый статус (ChunkStatus)
        
    Returns:
        отфильтрованный список чанков
    """
    status_order = {
        ChunkStatus.RAW.value: 1,
        ChunkStatus.CLEANED.value: 2,
        ChunkStatus.VERIFIED.value: 3,
        ChunkStatus.VALIDATED.value: 4, 
        ChunkStatus.RELIABLE.value: 5
    }
    
    min_level = status_order.get(min_status.value, 0)
    
    return [
        chunk for chunk in chunks 
        if status_order.get(chunk.status.value, 0) >= min_level
    ]

# Пример использования
reliable_only = filter_chunks_by_status(all_chunks, ChunkStatus.RELIABLE)
```

## Best Practice: Рекомендованные сценарии использования

### 1. Создание чанка с расширенными метриками качества

```python
from chunk_metadata_adapter import ChunkMetadataBuilder, ChunkType, ChunkStatus
import uuid

builder = ChunkMetadataBuilder(project="MetricsDemo", unit_id="metrics-unit")
source_id = str(uuid.uuid4())
chunk = builder.build_semantic_chunk(
    text="Sample text for metrics.",
    language="text",
    type=ChunkType.DOC_BLOCK,
    source_id=source_id,
    status=ChunkStatus.RELIABLE,
    coverage=0.95,
    cohesion=0.8,
    boundary_prev=0.7,
    boundary_next=0.9,
    body="Sample text for metrics."  # raw
)
print(chunk.metrics)
```

### 2. Конвертация между flat и structured форматами

```python
from chunk_metadata_adapter import ChunkMetadataBuilder, ChunkType, ChunkRole
import uuid

builder = ChunkMetadataBuilder(project="ConversionExample")
structured_chunk = builder.build_semantic_chunk(
    text="This is a sample chunk for conversion demonstration.",
    language="text",
    type=ChunkType.COMMENT,
    source_id=str(uuid.uuid4()),
    role=ChunkRole.REVIEWER,
    body="This is a sample chunk for conversion demonstration."  # raw
)
flat_dict = builder.semantic_to_flat(structured_chunk)
restored_chunk = builder.flat_to_semantic(flat_dict)
assert restored_chunk.uuid == structured_chunk.uuid
```

### 3. Цепочка обработки документа с обновлением статусов и метрик

```python
from chunk_metadata_adapter import ChunkMetadataBuilder, ChunkType, ChunkStatus
import uuid

builder = ChunkMetadataBuilder(project="ChainExample", unit_id="processor")
source_id = str(uuid.uuid4())
chunks = []
for i, text in enumerate([
    "# Document Title",
    "## Section 1\n\nThis is the content of section 1.",
    "## Section 2\n\nThis is the content of section 2.",
    "## Conclusion\n\nFinal thoughts on the topic."
]):
    chunk = builder.build_semantic_chunk(
        text=text,
        language="markdown",
        type=ChunkType.DOC_BLOCK,
        source_id=source_id,
        ordinal=i,
        summary=f"Section {i}" if i > 0 else "Title",
        body=text  # raw
    )
    chunks.append(chunk)
# Устанавливаем связи и статусы
for i in range(1, len(chunks)):
    chunks[i].links.append(f"parent:{chunks[0].uuid}")
    chunks[i].status = ChunkStatus.INDEXED
# Обновляем метрики
for chunk in chunks:
    chunk.metrics.quality_score = 0.95
    chunk.metrics.used_in_generation = True
    chunk.metrics.matches = 3
    chunk.metrics.feedback.accepted = 2
```

### 4. Round-trip: flat -> structured -> flat

```python
from chunk_metadata_adapter import ChunkMetadataBuilder, ChunkType
import uuid

builder = ChunkMetadataBuilder(project="RoundTripDemo")
source_id = str(uuid.uuid4())
flat = builder.build_flat_metadata(
    text="Round-trip test chunk.",
    source_id=source_id,
    ordinal=1,
    type=ChunkType.DOC_BLOCK,
    language="text",
    body="Round-trip test chunk."  # raw
)
structured = builder.flat_to_semantic(flat)
flat2 = builder.semantic_to_flat(structured)
assert flat2["uuid"] == flat["uuid"]
```

## BM25 Full-Text Search

Библиотека поддерживает полнотекстовый поиск с использованием алгоритма BM25 и гибридный поиск, сочетающий BM25 с семантическим поиском.

### Basic BM25 Search

```python
from chunk_metadata_adapter import ChunkQuery

# Простой BM25 поиск
query = ChunkQuery(
    search_query="python machine learning",
    search_fields=["body", "text", "summary", "title"],
    bm25_k1=1.2,  # Term frequency saturation
    bm25_b=0.75,  # Length normalization
    max_results=50
)

# Валидация параметров
validation = query.validate_bm25_parameters()
print(f"Valid: {validation.is_valid}")
```

### Hybrid Search (BM25 + Semantic)

```python
# Гибридный поиск с настраиваемыми весами
query = ChunkQuery(
    search_query="artificial intelligence neural networks",
    search_fields=["body", "text", "summary"],
    hybrid_search=True,
    bm25_weight=0.3,      # 30% вес для BM25
    semantic_weight=0.7,  # 70% вес для семантического поиска
    bm25_k1=1.5,
    bm25_b=0.8,
    min_score=0.6,        # Минимальный порог релевантности
    max_results=100
)
```

### BM25 with Metadata Filters

```python
from chunk_metadata_adapter import ChunkQuery, ChunkType, LanguageEnum

# BM25 поиск с фильтрами метаданных
query = ChunkQuery(
    # BM25 параметры
    search_query="data science analytics",
    search_fields=["body", "text", "summary", "title"],
    bm25_k1=1.2,
    bm25_b=0.75,
    
    # Фильтры метаданных
    type=ChunkType.DOC_BLOCK,
    language=LanguageEnum.EN,
    quality_score=">=0.8",
    year=">=2020",
    is_public=True,
    
    # Параметры результатов
    max_results=25,
    min_score=0.5
)
```

### Complex Filter Expressions with BM25

```python
# Сложные фильтры с BM25 поиском
query = ChunkQuery(
    # BM25 поиск
    search_query="machine learning algorithms",
    search_fields=["body", "text", "summary"],
    hybrid_search=True,
    bm25_weight=0.4,
    semantic_weight=0.6,
    
    # Сложное выражение фильтра
    filter_expr="""
        (type = 'DocBlock' OR type = 'CodeBlock') AND
        quality_score >= 0.7 AND
        (tags intersects ['ai', 'ml'] OR tags intersects ['python', 'data']) AND
        year >= 2020 AND
        NOT is_deleted AND
        (is_public = true OR user_role = 'admin')
    """,
    
    max_results=50,
    min_score=0.4
)

# Валидация фильтра и BM25 параметров
filter_validation = query.validate()
bm25_validation = query.validate_bm25_parameters()
```

### BM25 Parameter Tuning

```python
# Стандартный BM25 (хорош для общего поиска)
standard_query = ChunkQuery(
    search_query="python programming",
    bm25_k1=1.2,
    bm25_b=0.75
)

# Высокая точность (хорошо для технических документов)
precision_query = ChunkQuery(
    search_query="machine learning algorithms",
    bm25_k1=0.8,   # Меньший k1 для меньшей насыщенности частоты терминов
    bm25_b=0.9     # Больший b для большей нормализации длины
)

# Высокий отзыв (хорошо для широких поисков)
recall_query = ChunkQuery(
    search_query="artificial intelligence",
    bm25_k1=2.0,   # Больший k1 для большей важности частоты терминов
    bm25_b=0.5     # Меньший b для меньшей нормализации длины
)
```

### BM25 Search Fields

Поддерживаемые поля для поиска:
- `body` - исходный текст чанка
- `text` - нормализованный текст для поиска
- `summary` - краткое описание чанка
- `title` - заголовок или название

### BM25 Parameters

| Параметр | Тип | Диапазон | По умолчанию | Описание |
|----------|-----|----------|--------------|----------|
| `bm25_k1` | float | [0.0, 3.0] | 1.2 | Насыщенность частоты терминов |
| `bm25_b` | float | [0.0, 1.0] | 0.75 | Нормализация длины документа |
| `bm25_weight` | float | [0.0, 1.0] | 0.5 | Вес BM25 в гибридном поиске |
| `semantic_weight` | float | [0.0, 1.0] | 0.5 | Вес семантического поиска |
| `min_score` | float | [0.0, 1.0] | 0.0 | Минимальный порог релевантности |
| `max_results` | int | [1, 1000] | 100 | Максимальное количество результатов |

## Business fields (Бизнес-поля)

Дополнительные поля для бизнес-логики:

| Поле      | Тип           | Описание                                                        |
|-----------|---------------|-----------------------------------------------------------------|
| category  | Optional[str] | Бизнес-категория записи (например, 'наука', 'программирование') |
| title     | Optional[str] | Заголовок или краткое название записи                           |
| year      | Optional[int] | Год, связанный с записью (например, публикации)                 |
| is_public | Optional[bool]| Публичность записи (True/False)                                 |
| source    | Optional[str] | Источник данных ('user', 'external', 'import')                  |

### Пример использования (структурная модель)

```python
from chunk_metadata_adapter import SemanticChunk
chunk = SemanticChunk(
    uuid="...",
    type="DocBlock",
    text="...",
    language="ru",
    sha256="...",
    start=0,
    end=10,
    category="наука",
    title="Краткое описание",
    year=2024,
    is_public=True,
    source="user",
    tags=["example", "science"]
)
```

### Пример использования (плоская модель)

```python
from chunk_metadata_adapter import FlatSemanticChunk
chunk = FlatSemanticChunk(
    uuid="...",
    type="DocBlock",
    text="...",
    language="ru",
    sha256="...",
    start=0,
    end=10,
    category="наука",
    title="Краткое описание",
    year=2024,
    is_public=True,
    source="user",
    tags="example,science"
)
```

## Примеры использования

Библиотека включает подробные примеры использования в папке `chunk_metadata_adapter/examples/`:

### AST и фильтрация
- **`ast_basic_usage.py`** - Базовое использование AST узлов
- **`ast_visitor_pattern_usage.py`** - Использование паттерна Visitor для AST
- **`ast_json_serialization_demo.py`** - Демонстрация JSON сериализации AST для клиент-серверного взаимодействия
- **`ast_parameterization_demo.py`** - Демонстрация параметризации AST для эффективного кеширования запросов
- **`filter_parser_total_chunks_example.py`** - Примеры парсинга фильтров
- **`filter_executor_usage.py`** - Использование исполнителя фильтров

### Интеграция с ChunkQuery
- **`chunk_query_integration_demo.py`** - Демонстрация интеграции с ChunkQuery

### Запуск примеров
```bash
# JSON сериализация AST
python -m chunk_metadata_adapter.examples.ast_json_serialization_demo

# Параметризация AST для кеширования
python -m chunk_metadata_adapter.examples.ast_parameterization_demo

# Базовое использование AST
python -m chunk_metadata_adapter.examples.ast_basic_usage

# Паттерн Visitor
python -m chunk_metadata_adapter.examples.ast_visitor_pattern_usage

# Парсинг фильтров
python -m chunk_metadata_adapter.examples.filter_parser_total_chunks_example

# Исполнитель фильтров
python -m chunk_metadata_adapter.examples.filter_executor_usage

# Интеграция с ChunkQuery
python -m chunk_metadata_adapter.examples.chunk_query_integration_demo
```

## Документация

Более подробную документацию можно найти в [директории docs](./docs).

## Лицензия

MIT 

## to_flat_dict: flat dict для Redis

Функция `to_flat_dict` (и метод модели) возвращает плоский словарь, полностью готовый для записи в Redis:
- Все значения — только str/int/float (bool → "true"/"false", None → "", Enum → str, list/dict → JSON, datetime → ISO8601).
- Вложенные структуры превращаются в плоские ключи (`a.b.c`).
- created_at всегда присутствует и автозаполняется, если не указан (только на верхнем уровне).
- Все ключи — строки.
- Параметр `for_redis` по умолчанию True (поведение для Redis). Если False — старое поведение (часть значений остаётся в исходном типе).
- Внутренний параметр `first_call` (True только при первом вызове) гарантирует, что created_at добавляется только на верхнем уровне.

**Пример:**
```python
flat = chunk.to_flat_dict()  # flat dict для Redis
# {'uuid': '...', 'is_public': 'false', 'embedding': '[0.1, 0.2]', 'block_meta.author': 'vasily', 'created_at': '2024-06-13T12:00:00+00:00', ...}
```

**Round-trip:**
- dict → to_flat_dict() → from_flat_dict() → dict — все типы и вложенность сохраняются, created_at только на верхнем уровне.

**Важно:**
- created_at — только на верхнем уровне, во вложенных dict (например, block_meta) отсутствует.
- Для seamless-интеграции с Redis не требуется ручная фильтрация или преобразование типов. 