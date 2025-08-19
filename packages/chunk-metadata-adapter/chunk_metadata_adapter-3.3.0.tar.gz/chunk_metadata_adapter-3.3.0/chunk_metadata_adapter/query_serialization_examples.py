"""
Примеры сериализации и продвинутых техник работы с запросами.

Этот файл демонстрирует:
- Сериализация запросов для Redis и API
- Динамическое построение запросов
- Паттерны оптимизации
- Обработка ошибок
- Композиция запросов

Используются только реальные поля из схемы SemanticChunk.
"""

from typing import List, Dict, Any, Optional, Tuple
from chunk_metadata_adapter.chunk_query import ChunkQuery
from chunk_metadata_adapter.data_types import ChunkType, ChunkStatus, LanguageEnum


def example_query_serialization():
    """Сериализация запросов для хранения и API."""
    print("=== Сериализация запросов ===")
    
    # Создаем комплексный запрос
    original_data = {
        "type": ChunkType.CODE_BLOCK.value,
        "language": LanguageEnum.PYTHON.value,
        "quality_score": ">=0.8",
        "year": ">=2020",
        "status": ChunkStatus.RELIABLE.value,  # Одиночное значение enum
        "is_public": True,
        "category": "tutorial"
    }
    original_query, errors = ChunkQuery.from_dict_with_validation(original_data)
    assert errors is None
    
    # 1. Сериализация в плоский словарь (для Redis/БД)
    flat_dict = original_query.to_flat_dict(for_redis=True)
    print(f"✅ Плоская сериализация: {len(flat_dict)} полей")
    print(f"   type={flat_dict.get('type')}, quality_score={flat_dict.get('quality_score')}")
    
    # 2. Восстановление из плоского словаря
    restored_from_flat = ChunkQuery.from_flat_dict(flat_dict)
    print(f"✅ Восстановлено из плоского: type={restored_from_flat.type}")
    
    # 3. Сериализация в JSON (для API)
    json_dict = original_query.to_json_dict()
    print(f"✅ JSON сериализация: {len(json_dict)} полей")
    print(f"   type={json_dict.get('type')}, is_public={json_dict.get('is_public')}")
    
    # 4. Восстановление из JSON
    restored_from_json = ChunkQuery.from_json_dict(json_dict)
    print(f"✅ Восстановлено из JSON: language={restored_from_json.language}")
    
    # 5. Проверка эквивалентности
    assert original_query.type == restored_from_flat.type == restored_from_json.type
    print(f"✅ Все методы сериализации сохраняют данные")
    
    return {
        "original": original_query,
        "flat_dict": flat_dict,
        "json_dict": json_dict
    }


def example_dynamic_query_building():
    """Динамическое построение запросов."""
    print("\n=== Динамическое построение запросов ===")
    
    def build_content_filter(
        min_quality: Optional[float] = None,
        languages: Optional[List[str]] = None,
        chunk_types: Optional[List[str]] = None,
        statuses: Optional[List[str]] = None,
        public_only: bool = False,
        recent_only: bool = False,
        category: Optional[str] = None
    ) -> Tuple[Optional[ChunkQuery], Optional[dict]]:
        """Построение фильтра контента на основе критериев."""
        query_data = {}
        
        if min_quality is not None:
            query_data["quality_score"] = f">={min_quality}"
        
        # Для enum полей берем только первое значение из списка
        if languages and len(languages) > 0:
            query_data["language"] = languages[0]  # Только одно значение
        
        if chunk_types and len(chunk_types) > 0:
            query_data["type"] = chunk_types[0]  # Только одно значение
            
        if statuses and len(statuses) > 0:
            query_data["status"] = statuses[0]  # Только одно значение
        
        if public_only:
            query_data["is_public"] = True
        
        if recent_only:
            query_data["year"] = ">=2023"
            
        if category:
            query_data["category"] = category
        
        return ChunkQuery.from_dict_with_validation(query_data)
    
        # 1. Базовый фильтр контента
    basic_filter, errors = build_content_filter(min_quality=0.8, public_only=True)
    assert basic_filter is not None
    print(f"✅ Базовый фильтр: качество>={basic_filter.quality_score}")

    # 2. Фильтр программного контента
    prog_filter, errors = build_content_filter(
        min_quality=0.7,
        languages=["Python"],  # Только один язык за раз для enum
        chunk_types=[ChunkType.CODE_BLOCK.value],  # Только один тип за раз
        recent_only=True
    )
    assert prog_filter is not None
    print(f"✅ Программный фильтр: языки={prog_filter.language}")
    
    # 3. Фильтр документации
    doc_filter, errors = build_content_filter(
        min_quality=0.85,
        chunk_types=[ChunkType.DOC_BLOCK.value],
        statuses=[ChunkStatus.RELIABLE.value],  # Только один статус за раз
        public_only=True,
        category="documentation"
    )
    assert doc_filter is not None
    print(f"✅ Фильтр документации: тип={doc_filter.type}, категория={doc_filter.category}")
    
    return [basic_filter, prog_filter, doc_filter]


def example_optimization_patterns():
    """Паттерны оптимизации для больших датасетов."""
    print("\n=== Паттерны оптимизации ===")
    
    # 1. Приоритет индексированных полей (самые селективные первыми)
    indexed_data = {
        "project": "SpecificProject",  # Высокая селективность
        "type": ChunkType.DOC_BLOCK.value,  # Обычно индексируется
        "status": ChunkStatus.RELIABLE.value,  # Обычно индексируется
        "is_public": True  # Булев индекс
    }
    indexed_query, errors = ChunkQuery.from_dict_with_validation(indexed_data)
    assert errors is None
    print(f"✅ Приоритет индексов: project -> type -> status -> is_public")
    
    # 2. Оптимизация диапазонов (предпочитать диапазоны вместо множественных сравнений)
    range_data = {
        "quality_score": "[0.8,1.0]",  # Диапазон вместо >=0.8
        "year": "[2020,2024]",  # Диапазон вместо IN
        "start": "[100,1000]",  # Ограниченный диапазон
        "feedback_accepted": "[5,50]"  # Разумные границы
    }
    range_query, errors = ChunkQuery.from_dict_with_validation(range_data)
    assert errors is None
    print(f"✅ Оптимизация диапазонов: ограниченные диапазоны для лучшей производительности")
    
    # 3. Минимальный набор полей (только необходимые фильтры)
    minimal_data = {
        "type": ChunkType.CODE_BLOCK.value,
        "language": LanguageEnum.PYTHON.value,
        "quality_score": ">=0.8"
    }
    minimal_query, errors = ChunkQuery.from_dict_with_validation(minimal_data)
    assert errors is None
    print(f"✅ Минимальный набор: только критически важные фильтры")
    
    # 4. Пакетная обработка (для массовых операций)
    batch_data = {
        "status": ChunkStatus.RAW.value,  # Одиночное значение enum
        "quality_score": "<0.6",  # Четкая цель для улучшения
        "year": ">=2020"  # Разумное временное окно
    }
    batch_query, errors = ChunkQuery.from_dict_with_validation(batch_data)
    assert errors is None
    print(f"✅ Пакетная обработка: эффективные массовые операции")
    
    return [indexed_query, range_query, minimal_query, batch_query]


def example_error_handling_patterns():
    """Продвинутые паттерны обработки ошибок."""
    print("\n=== Продвинутая обработка ошибок ===")
    
    def safe_query_builder(query_data: dict) -> Tuple[Optional[ChunkQuery], List[str]]:
        """Безопасное построение запроса с детальной обработкой ошибок."""
        query, errors = ChunkQuery.from_dict_with_validation(query_data)
        
        if errors:
            error_messages = []
            for field, field_errors in errors.get('fields', {}).items():
                for error in field_errors:
                    error_messages.append(f"Поле '{field}': {error}")
            return None, error_messages
        
        return query, []
    
    def validate_and_sanitize_query(query_data: dict) -> Tuple[Optional[ChunkQuery], List[str], List[str]]:
        """Валидация с попыткой санитизации данных."""
        warnings = []
        sanitized_data = query_data.copy()
        
        # Попытка исправить распространенные ошибки
        if 'type' in sanitized_data and isinstance(sanitized_data['type'], str):
            # Попытка исправить регистр
            for chunk_type in ChunkType:
                if sanitized_data['type'].lower() == chunk_type.value.lower():
                    sanitized_data['type'] = chunk_type.value
                    warnings.append(f"Исправлен регистр для type: {query_data['type']} -> {chunk_type.value}")
                    break
        
        # Проверка диапазонов качества
        if 'quality_score' in sanitized_data:
            qs = sanitized_data['quality_score']
            if isinstance(qs, (int, float)):
                if qs > 1.0:
                    sanitized_data['quality_score'] = ">=0.8"
                    warnings.append(f"Качество {qs} > 1.0, заменено на '>=0.8'")
                elif qs < 0.0:
                    sanitized_data['quality_score'] = ">=0.0"
                    warnings.append(f"Качество {qs} < 0.0, заменено на '>=0.0'")
        
        query, errors = safe_query_builder(sanitized_data)
        return query, errors, warnings
    
    # 1. Успешный случай
    valid_data = {"type": ChunkType.DOC_BLOCK.value, "quality_score": ">=0.8"}
    query, error_msgs = safe_query_builder(valid_data)
    assert query is not None
    print(f"✅ Успешный запрос: {query.type}")
    
    # 2. Обработка ошибок с санитизацией
    fixable_data = {"type": "docblock", "quality_score": 1.5}  # Неправильный регистр и значение
    query, errors, warnings = validate_and_sanitize_query(fixable_data)
    if warnings:
        print(f"⚠️  Предупреждения: {'; '.join(warnings)}")
    if query:
        print(f"✅ Исправленный запрос: type={query.type}, quality={query.quality_score}")
    
    # 3. Обработка критических ошибок
    critical_errors_data = {
        "uuid": "bad-uuid",
        "type": "CompletelyWrongType",
        "start": {"invalid": "object"}
    }
    query, error_msgs = safe_query_builder(critical_errors_data)
    assert query is None
    print(f"❌ Критические ошибки ({len(error_msgs)}):")
    for msg in error_msgs[:3]:  # Показываем первые 3
        print(f"   - {msg}")
    
    return error_msgs


def example_query_composition():
    """Композиция и комбинирование запросов."""
    print("\n=== Композиция запросов ===")
    
    class QueryBuilder:
        """Билдер для пошагового создания запросов."""
        
        def __init__(self):
            self.data = {}
        
        def with_type(self, chunk_type: ChunkType):
            self.data["type"] = chunk_type.value
            return self
        
        def with_language(self, language: LanguageEnum):
            self.data["language"] = language.value
            return self
        
        def with_min_quality(self, min_quality: float):
            self.data["quality_score"] = f">={min_quality}"
            return self
        
        def with_status(self, status: ChunkStatus):
            """Добавляет одиночный статус (enum поддерживает только равенство)."""
            self.data["status"] = status.value
            return self
        
        def public_only(self):
            self.data["is_public"] = True
            return self
        
        def recent_only(self, year: int = 2023):
            self.data["year"] = f">={year}"
            return self
        
        def with_category(self, category: str):
            self.data["category"] = category
            return self
        
        def build(self) -> Tuple[Optional[ChunkQuery], Optional[dict]]:
            return ChunkQuery.from_dict_with_validation(self.data)
    
    # 1. Пошаговое создание запроса для качественной документации
    quality_docs_query, errors = (QueryBuilder()
                                  .with_type(ChunkType.DOC_BLOCK)
                                  .with_language(LanguageEnum.PYTHON)
                                  .with_min_quality(0.8)
                                  .with_status(ChunkStatus.RELIABLE)
                                  .public_only()
                                  .with_category("documentation")
                                  .build())
    
    assert errors is None
    print(f"✅ Качественная документация: {quality_docs_query.type}, {quality_docs_query.language}")
    
    # 2. Запрос для анализа кода
    code_analysis_query, errors = (QueryBuilder()
                                   .with_type(ChunkType.CODE_BLOCK)
                                   .with_language(LanguageEnum.PYTHON)
                                   .with_min_quality(0.6)
                                   .with_status(ChunkStatus.VERIFIED)  # Только один статус
                                   .recent_only(2022)
                                   .build())
    
    assert errors is None
    print(f"✅ Анализ кода: статусы={code_analysis_query.status}, год={code_analysis_query.year}")
    
    # 3. Запрос для контента, требующего внимания
    attention_needed_query, errors = (QueryBuilder()
                                      .with_min_quality(0.4)  # Низкое качество
                                      .with_status(ChunkStatus.RAW)  # Только один статус
                                      .build())
    
    assert errors is None
    # Добавляем дополнительные условия вручную
    attention_needed_query.feedback_rejected = ">0"  # Есть отклонения
    attention_needed_query.used_in_generation = False  # Не используется
    
    print(f"✅ Требует внимания: качество={attention_needed_query.quality_score}")
    
    return [quality_docs_query, code_analysis_query, attention_needed_query]


if __name__ == "__main__":
    print("🚀 ПРОДВИНУТЫЕ ТЕХНИКИ РАБОТЫ С ЗАПРОСАМИ")
    print("=" * 55)
    
    example_query_serialization()
    example_dynamic_query_building()
    example_optimization_patterns()
    example_error_handling_patterns()
    example_query_composition()
    
    print("\n" + "=" * 55)
    print("✅ Все продвинутые примеры выполнены успешно!")
    print("📚 См. также query_examples.py для базовых примеров") 