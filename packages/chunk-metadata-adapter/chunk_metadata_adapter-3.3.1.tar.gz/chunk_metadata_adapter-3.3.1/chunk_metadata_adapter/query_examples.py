"""
Базовые примеры типизированных запросов с ChunkQuery.

Этот файл демонстрирует основные паттерны запросов:
- Запросы на равенство
- Сравнения (>, <, >=, <=)
- Диапазоны [min,max]
- IN операции
- Валидация запросов

Используются только реальные поля из схемы SemanticChunk.
Рекомендуется использовать ChunkQuery.from_dict_with_validation() для безопасного создания запросов.
"""

from chunk_metadata_adapter.chunk_query import ChunkQuery
from chunk_metadata_adapter.data_types import ChunkType, ChunkStatus, ChunkRole, LanguageEnum, BlockType


def example_equality_queries():
    """Запросы на точное совпадение."""
    print("=== Запросы на равенство ===")
    
    # Поиск по типу чанка
    query_data = {"type": ChunkType.DOC_BLOCK.value}
    query, errors = ChunkQuery.from_dict_with_validation(query_data)
    assert errors is None
    print(f"✅ Поиск DOC_BLOCK: {query.type}")
    
    # Поиск по языку
    query_data = {"language": LanguageEnum.PYTHON.value}
    query, errors = ChunkQuery.from_dict_with_validation(query_data)
    assert errors is None
    print(f"✅ Поиск Python: {query.language}")
    
    # Поиск по статусу
    query_data = {"status": ChunkStatus.RELIABLE.value}
    query, errors = ChunkQuery.from_dict_with_validation(query_data)
    assert errors is None
    print(f"✅ Надежные чанки: {query.status}")
    
    # Поиск публичных чанков
    query_data = {"is_public": True}
    query, errors = ChunkQuery.from_dict_with_validation(query_data)
    assert errors is None
    print(f"✅ Публичные чанки: {query.is_public}")
    
    # Поиск по проекту
    query_data = {"project": "MyProject"}
    query, errors = ChunkQuery.from_dict_with_validation(query_data)
    assert errors is None
    print(f"✅ Проект: {query.project}")
    
    return query


def example_comparison_queries():
    """Запросы сравнения с операторами."""
    print("\n=== Запросы сравнения ===")
    
    # Высокое качество
    query_data = {"quality_score": ">=0.8"}
    query, errors = ChunkQuery.from_dict_with_validation(query_data)
    assert errors is None
    print(f"✅ Высокое качество (>=0.8): {query.quality_score}")
    
    # Высокое покрытие
    query_data = {"coverage": ">=0.9"}
    query, errors = ChunkQuery.from_dict_with_validation(query_data)
    assert errors is None
    print(f"✅ Высокое покрытие (>=0.9): {query.coverage}")
    
    # Недавние годы
    query_data = {"year": ">=2023"}
    query, errors = ChunkQuery.from_dict_with_validation(query_data)
    assert errors is None
    print(f"✅ Недавние (2023+): {query.year}")
    
    # Маленькие чанки по позиции
    query_data = {"end": "<1000"}
    query, errors = ChunkQuery.from_dict_with_validation(query_data)
    assert errors is None
    print(f"✅ Маленькие (<1000): {query.end}")
    
    # Много принятых отзывов
    query_data = {"feedback_accepted": ">5"}
    query, errors = ChunkQuery.from_dict_with_validation(query_data)
    assert errors is None
    print(f"✅ Популярные (>5 принятых): {query.feedback_accepted}")
    
    return query


def example_range_queries():
    """Диапазонные запросы."""
    print("\n=== Диапазонные запросы ===")
    
    # Оптимальное качество
    query_data = {"quality_score": "[0.7,0.95]"}
    query, errors = ChunkQuery.from_dict_with_validation(query_data)
    assert errors is None
    print(f"✅ Оптимальное качество [0.7-0.95]: {query.quality_score}")
    
    # Средние по размеру
    query_data = {"start": "[100,500]", "end": "[600,2000]"}
    query, errors = ChunkQuery.from_dict_with_validation(query_data)
    assert errors is None
    print(f"✅ Средние чанки: start={query.start}, end={query.end}")
    
    # Умеренная связность
    query_data = {"cohesion": "[0.4,0.8]"}
    query, errors = ChunkQuery.from_dict_with_validation(query_data)
    assert errors is None
    print(f"✅ Умеренная связность [0.4-0.8]: {query.cohesion}")
    
    # Диапазон отзывов
    query_data = {"feedback_accepted": "[1,10]"}
    query, errors = ChunkQuery.from_dict_with_validation(query_data)
    assert errors is None
    print(f"✅ Интерактивные [1-10 принятых]: {query.feedback_accepted}")
    
    return query


def example_in_queries():
    """IN запросы для множественного выбора (только для не-enum полей)."""
    print("\n=== IN запросы ===")
    
    # Годы (работает - не enum)
    query_data = {"year": "in:2022,2023,2024"}
    query, errors = ChunkQuery.from_dict_with_validation(query_data)
    if errors:
        print(f"❌ Ошибка годов: {errors}")
        return None
    assert errors is None
    print(f"✅ Несколько годов: {query.year}")
    
    # Диапазоны позиций (работает - не enum)
    query_data = {"start": "in:100,200,300"}
    query, errors = ChunkQuery.from_dict_with_validation(query_data)
    if errors:
        print(f"❌ Ошибка позиций: {errors}")
        return None
    assert errors is None
    print(f"✅ Позиции: {query.start}")
    
    # Категории (работает - строковое поле, не enum)
    query_data = {"category": "in:documentation,tutorial,reference"}
    query, errors = ChunkQuery.from_dict_with_validation(query_data)
    if errors:
        print(f"❌ Ошибка категорий: {errors}")
        return None
    assert errors is None
    print(f"✅ Категории: {query.category}")
    
    # Источники (работает - строковое поле, не enum)
    query_data = {"source": "in:user,external,import"}
    query, errors = ChunkQuery.from_dict_with_validation(query_data)
    if errors:
        print(f"❌ Ошибка источников: {errors}")
        return None
    assert errors is None
    print(f"✅ Источники: {query.source}")
    
    # Проекты (работает - строковое поле, не enum)
    query_data = {"project": "in:ProjectA,ProjectB,ProjectC"}
    query, errors = ChunkQuery.from_dict_with_validation(query_data)
    if errors:
        print(f"❌ Ошибка проектов: {errors}")
        return None
    assert errors is None
    print(f"✅ Проекты: {query.project}")
    
    print("ℹ️  Примечание: IN запросы работают только для не-enum полей")
    print("   Для enum полей (type, status, language, role, block_type) используйте одиночные значения")
    
    return query


def example_enum_queries():
    """Примеры запросов с enum полями (одиночные значения)."""
    print("\n=== Запросы с enum полями ===")
    
    # Конкретный тип
    query_data = {"type": ChunkType.DOC_BLOCK.value}
    query, errors = ChunkQuery.from_dict_with_validation(query_data)
    assert errors is None
    print(f"✅ Тип документа: {query.type}")
    
    # Конкретный статус
    query_data = {"status": ChunkStatus.RELIABLE.value}
    query, errors = ChunkQuery.from_dict_with_validation(query_data)
    assert errors is None
    print(f"✅ Надежный статус: {query.status}")
    
    # Конкретный язык
    query_data = {"language": LanguageEnum.PYTHON.value}
    query, errors = ChunkQuery.from_dict_with_validation(query_data)
    assert errors is None
    print(f"✅ Python код: {query.language}")
    
    # Конкретная роль
    query_data = {"role": ChunkRole.DEVELOPER.value}
    query, errors = ChunkQuery.from_dict_with_validation(query_data)
    assert errors is None
    print(f"✅ Роль разработчика: {query.role}")
    
    # Тип блока
    query_data = {"block_type": BlockType.PARAGRAPH.value}
    query, errors = ChunkQuery.from_dict_with_validation(query_data)
    assert errors is None
    print(f"✅ Тип блока: {query.block_type}")
    
    print("ℹ️  Для поиска по нескольким enum значениям используйте отдельные запросы")
    
    return query


def example_validation_errors():
    """Примеры валидации и обработки ошибок."""
    print("\n=== Валидация запросов ===")
    
    # Валидный запрос
    valid_data = {"type": ChunkType.DOC_BLOCK.value, "quality_score": ">=0.8"}
    query, errors = ChunkQuery.from_dict_with_validation(valid_data)
    assert errors is None
    print(f"✅ Валидный запрос: {query.type}")
    
    # Неверный UUID
    invalid_data = {"uuid": "not-a-uuid", "type": ChunkType.DOC_BLOCK.value}
    query, errors = ChunkQuery.from_dict_with_validation(invalid_data)
    assert query is None
    print(f"❌ Ошибка UUID: {errors['fields']['uuid'][0]}")
    
    # Неверное значение enum
    invalid_data = {"type": "InvalidType"}
    query, errors = ChunkQuery.from_dict_with_validation(invalid_data)
    assert query is None
    print(f"❌ Ошибка enum: {errors['fields']['type'][0]}")
    
    # Неверный тип данных
    invalid_data = {"start": [1, 2, 3]}  # Должно быть int или str
    query, errors = ChunkQuery.from_dict_with_validation(invalid_data)
    assert query is None
    print(f"❌ Ошибка типа: {errors['fields']['start'][0]}")
    
    return errors


def example_complex_query():
    """Комплексный запрос с несколькими условиями."""
    print("\n=== Комплексный запрос ===")
    
    query_data = {
        "type": ChunkType.DOC_BLOCK.value,
        "language": LanguageEnum.PYTHON.value,
        "quality_score": ">=0.8",
        "status": ChunkStatus.RELIABLE.value,  # Одиночное значение enum
        "is_public": True,
        "year": ">=2023",
        "category": "tutorial",
        "used_in_generation": True
    }
    query, errors = ChunkQuery.from_dict_with_validation(query_data)
    if errors:
        print(f"❌ Ошибка комплексного запроса: {errors}")
        return None
    assert errors is None
    
    print(f"✅ Комплексный запрос:")
    print(f"   - Тип: {query.type}")
    print(f"   - Язык: {query.language}")
    print(f"   - Качество: {query.quality_score}")
    print(f"   - Статус: {query.status}")
    print(f"   - Публичный: {query.is_public}")
    print(f"   - Год: {query.year}")
    print(f"   - Категория: {query.category}")
    print(f"   - Используется: {query.used_in_generation}")
    
    return query


def example_real_world_scenarios():
    """Реальные сценарии использования запросов."""
    print("\n=== Реальные сценарии ===")
    
    # 1. Поиск качественной документации Python
    python_docs_data = {
        "type": ChunkType.DOC_BLOCK.value,
        "language": LanguageEnum.PYTHON.value,
        "quality_score": ">=0.8",
        "status": ChunkStatus.RELIABLE.value,
        "category": "documentation"
    }
    query, errors = ChunkQuery.from_dict_with_validation(python_docs_data)
    assert errors is None
    print(f"✅ Качественная Python документация")
    
    # 2. Код, требующий проверки (только один тип за раз)
    code_review_data = {
        "type": ChunkType.CODE_BLOCK.value,  # Только один тип
        "quality_score": "<0.6",
        "status": ChunkStatus.RAW.value,  # Только один статус
        "feedback_rejected": ">0"
    }
    query, errors = ChunkQuery.from_dict_with_validation(code_review_data)
    assert errors is None
    print(f"✅ Код для проверки: низкое качество + отклонения")
    
    # 3. Популярный контент для анализа
    popular_content_data = {
        "feedback_accepted": ">=10",
        "used_in_generation": True,
        "quality_score": ">=0.7",
        "is_public": True
    }
    query, errors = ChunkQuery.from_dict_with_validation(popular_content_data)
    assert errors is None
    print(f"✅ Популярный контент: много принятых отзывов")
    
    # 4. Контент для архивирования
    archive_candidates_data = {
        "year": "<2020",
        "used_in_generation": False,
        "feedback_accepted": "<=2",
        "quality_score": "<0.5"
    }
    query, errors = ChunkQuery.from_dict_with_validation(archive_candidates_data)
    assert errors is None
    print(f"✅ Кандидаты для архива: старый + неиспользуемый")
    
    # 5. Контент с хорошими границами
    well_structured_data = {
        "boundary_prev": ">=0.7",
        "boundary_next": ">=0.7",
        "cohesion": ">=0.8",
        "quality_score": ">=0.8"
    }
    query, errors = ChunkQuery.from_dict_with_validation(well_structured_data)
    assert errors is None
    print(f"✅ Хорошо структурированный контент")
    
    print("ℹ️  Примечание: Для поиска по нескольким enum значениям")
    print("   создавайте отдельные запросы для каждого значения")
    
    return [query]


if __name__ == "__main__":
    print("🔍 БАЗОВЫЕ ПРИМЕРЫ ТИПИЗИРОВАННЫХ ЗАПРОСОВ")
    print("=" * 50)
    
    example_equality_queries()
    example_comparison_queries()
    example_range_queries()
    example_in_queries()
    example_enum_queries()
    example_validation_errors()
    example_complex_query()
    example_real_world_scenarios()
    
    print("\n" + "=" * 50)
    print("✅ Все базовые примеры выполнены успешно!")
    print("📝 Использованы только реальные поля из схемы SemanticChunk") 