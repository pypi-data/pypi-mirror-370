"""
Бизнес-сценарии использования типизированных запросов.

Этот файл демонстрирует реальные бизнес-кейсы:
- Управление контентом (CMS)
- Аналитика и отчетность
- Контроль качества
- Архивирование и очистка
- Поиск и рекомендации

Все примеры используют реальные поля из схемы SemanticChunk.
"""

from chunk_metadata_adapter.chunk_query import ChunkQuery
from chunk_metadata_adapter.data_types import ChunkType, ChunkStatus, LanguageEnum, ChunkRole


def example_content_management_queries():
    """Запросы для системы управления контентом."""
    print("=== Управление контентом (CMS) ===")
    
    # 1. Редакторская очередь - контент для человеческого обзора
    editorial_data = {
        "status": ChunkStatus.CLEANED.value,  # Одиночный статус
        "quality_score": "[0.6,0.85]",  # Нужна человеческая проверка
        "is_public": False,  # Еще не опубликовано
        "category": "article"  # Одиночная категория
    }
    editorial_query, errors = ChunkQuery.from_dict_with_validation(editorial_data)
    assert errors is None
    print(f"✅ Редакторская очередь: статус={editorial_query.status}, качество={editorial_query.quality_score}")
    
    # 2. Готовый к публикации контент
    publish_ready_data = {
        "status": ChunkStatus.RELIABLE.value,
        "quality_score": ">=0.9",
        "coverage": ">=0.85",
        "is_public": False,  # Готов к публикации
        "feedback_rejected": "<=1"  # Минимум негативных отзывов
    }
    publish_query, errors = ChunkQuery.from_dict_with_validation(publish_ready_data)
    assert errors is None
    print(f"✅ Готов к публикации: качество={publish_query.quality_score}, покрытие={publish_query.coverage}")
    
    # 3. Популярный опубликованный контент
    popular_published_data = {
        "is_public": True,
        "feedback_accepted": ">=10",
        "used_in_generation": True,
        "quality_score": ">=0.8",
        "status": ChunkStatus.RELIABLE.value
    }
    popular_query, errors = ChunkQuery.from_dict_with_validation(popular_published_data)
    assert errors is None
    print(f"✅ Популярный контент: отзывы={popular_query.feedback_accepted}, используется={popular_query.used_in_generation}")
    
    # 4. Контент, требующий обновления
    needs_update_data = {
        "year": "<2022",  # Старый контент
        "quality_score": "[0.5,0.8]",  # Средне-низкое качество
        "feedback_rejected": ">2",  # Есть критика
        "category": "tutorial"  # Одиночная категория
    }
    update_query, errors = ChunkQuery.from_dict_with_validation(needs_update_data)
    assert errors is None
    print(f"✅ Требует обновления: год={update_query.year}, отклонения={update_query.feedback_rejected}")
    
    return [editorial_query, publish_query, popular_query, update_query]


def example_quality_control_queries():
    """Запросы для контроля качества контента."""
    print("\n=== Контроль качества ===")
    
    # 1. Высококачественный контент для анализа лучших практик
    high_quality_data = {
        "quality_score": ">=0.95",
        "coverage": ">=0.9",
        "cohesion": ">=0.8",
        "feedback_accepted": ">=5",
        "feedback_rejected": "<=1"
    }
    high_quality_query, errors = ChunkQuery.from_dict_with_validation(high_quality_data)
    assert errors is None
    print(f"✅ Высокое качество: quality={high_quality_query.quality_score}, cohesion={high_quality_query.cohesion}")
    
    # 2. Проблемный контент, требующий исправления
    problematic_data = {
        "quality_score": "<0.5",
        "feedback_rejected": ">3",
        "status": ChunkStatus.RAW.value,  # Одиночный статус
        "used_in_generation": False  # Не используется
    }
    problematic_query, errors = ChunkQuery.from_dict_with_validation(problematic_data)
    assert errors is None
    print(f"✅ Проблемный контент: качество={problematic_query.quality_score}, отклонения={problematic_query.feedback_rejected}")
    
    # 3. Контент с плохими границами (нужна пересегментация)
    bad_boundaries_data = {
        "boundary_prev": "<0.4",
        "boundary_next": "<0.4",
        "cohesion": "<0.6",
        "type": ChunkType.DOC_BLOCK.value  # Одиночный тип
    }
    boundaries_query, errors = ChunkQuery.from_dict_with_validation(bad_boundaries_data)
    assert errors is None
    print(f"✅ Плохие границы: prev={boundaries_query.boundary_prev}, next={boundaries_query.boundary_next}")
    
    # 4. Недооцененный контент (хорошее качество, но мало используется)
    undervalued_data = {
        "quality_score": ">=0.8",
        "coverage": ">=0.7",
        "used_in_generation": False,
        "feedback_accepted": "<=2",
        "is_public": True
    }
    undervalued_query, errors = ChunkQuery.from_dict_with_validation(undervalued_data)
    assert errors is None
    print(f"✅ Недооцененный: качество={undervalued_query.quality_score}, используется={undervalued_query.used_in_generation}")
    
    return [high_quality_query, problematic_query, boundaries_query, undervalued_query]


def example_analytics_and_reporting_queries():
    """Запросы для аналитики и отчетности."""
    print("\n=== Аналитика и отчетность ===")
    
    # 1. Отчет по производительности контента
    performance_report_data = {
        "used_in_generation": True,
        "quality_score": ">=0.7",
        "feedback_accepted": ">0",
        "year": ">=2023",
        "is_public": True
    }
    performance_query, errors = ChunkQuery.from_dict_with_validation(performance_report_data)
    assert errors is None
    print(f"✅ Отчет производительности: активный контент с вовлеченностью")
    
    # 2. Анализ распределения по языкам программирования (отдельные запросы)
    programming_languages = ["python", "javascript", "typescript", "java", "cpp"]
    language_queries = []
    
    for lang in programming_languages:
        lang_data = {
            "language": lang,
            "type": ChunkType.CODE_BLOCK.value,  # Одиночный тип
            "status": ChunkStatus.RELIABLE.value  # Одиночный статус
        }
        lang_query, errors = ChunkQuery.from_dict_with_validation(lang_data)
        if errors is None:
            language_queries.append((lang_query, lang))
            print(f"✅ Язык {lang}: тип={lang_query.type}")
    
    # 3. Метрики вовлеченности по категориям
    categories = ["documentation", "tutorial", "reference", "example"]
    engagement_queries = []
    
    for category in categories:
        engagement_data = {
            "category": category,
            "feedback_accepted": ">0",
            "used_in_generation": True,
            "quality_score": ">=0.7"
        }
        eng_query, errors = ChunkQuery.from_dict_with_validation(engagement_data)
        if errors is None:
            engagement_queries.append((eng_query, category))
            print(f"✅ Вовлеченность {category}: отзывы={eng_query.feedback_accepted}")
    
    # 4. Анализ жизненного цикла контента (отдельные запросы)
    lifecycle_stages = [
        (ChunkStatus.RAW.value, "Сырой"),
        (ChunkStatus.CLEANED.value, "Очищенный"),
        (ChunkStatus.VERIFIED.value, "Проверенный"),
        (ChunkStatus.VALIDATED.value, "Валидированный"),
        (ChunkStatus.RELIABLE.value, "Надежный")
    ]
    
    lifecycle_queries = []
    for status_value, description in lifecycle_stages:
        lifecycle_data = {"status": status_value}
        lc_query, errors = ChunkQuery.from_dict_with_validation(lifecycle_data)
        if errors is None:
            lifecycle_queries.append((lc_query, description))
            print(f"✅ Этап жизненного цикла '{description}': {lc_query.status}")
    
    return {
        "performance": performance_query,
        "languages": language_queries,
        "engagement": engagement_queries,
        "lifecycle": lifecycle_queries
    }


def example_search_and_discovery_queries():
    """Запросы для поиска и обнаружения контента."""
    print("\n=== Поиск и обнаружение ===")
    
    # 1. Поиск качественной документации по Python
    python_docs_data = {
        "type": ChunkType.DOC_BLOCK.value,
        "language": LanguageEnum.PYTHON.value,
        "quality_score": ">=0.8",
        "status": ChunkStatus.RELIABLE.value,
        "category": "documentation",  # Одиночная категория
        "is_public": True
    }
    python_docs_query, errors = ChunkQuery.from_dict_with_validation(python_docs_data)
    assert errors is None
    print(f"✅ Python документация: тип={python_docs_query.type}, язык={python_docs_query.language}")
    
    # 2. Поиск примеров кода для изучения
    code_examples_data = {
        "type": ChunkType.CODE_BLOCK.value,  # Одиночный тип
        "quality_score": ">=0.7",
        "feedback_accepted": ">=3",  # Проверенные сообществом
        "category": "example",  # Одиночная категория
        "is_public": True,
        "used_in_generation": True  # Полезные для генерации
    }
    examples_query, errors = ChunkQuery.from_dict_with_validation(code_examples_data)
    assert errors is None
    print(f"✅ Примеры кода: типы={examples_query.type}, отзывы={examples_query.feedback_accepted}")
    
    # 3. Обнаружение скрытых жемчужин (высокое качество, мало известны)
    hidden_gems_data = {
        "quality_score": ">=0.85",
        "coverage": ">=0.8",
        "feedback_accepted": "[1,5]",  # Мало, но положительные отзывы
        "used_in_generation": False,  # Недоиспользуется
        "is_public": True,
        "status": ChunkStatus.RELIABLE.value
    }
    gems_query, errors = ChunkQuery.from_dict_with_validation(hidden_gems_data)
    assert errors is None
    print(f"✅ Скрытые жемчужины: качество={gems_query.quality_score}, используется={gems_query.used_in_generation}")
    
    # 4. Поиск контента для конкретной роли
    developer_content_data = {
        "role": ChunkRole.DEVELOPER.value,
        "type": ChunkType.CODE_BLOCK.value,  # Одиночный тип
        "language": LanguageEnum.PYTHON.value,  # Одиночный язык
        "quality_score": ">=0.7",
        "category": "tutorial"  # Одиночная категория
    }
    dev_query, errors = ChunkQuery.from_dict_with_validation(developer_content_data)
    assert errors is None
    print(f"✅ Контент для разработчиков: роль={dev_query.role}, язык={dev_query.language}")
    
    return [python_docs_query, examples_query, gems_query, dev_query]


def example_maintenance_and_cleanup_queries():
    """Запросы для обслуживания и очистки данных."""
    print("\n=== Обслуживание и очистка ===")
    
    # 1. Кандидаты для архивирования
    archive_candidates_data = {
        "year": "<2020",  # Старый контент
        "used_in_generation": False,  # Не используется
        "feedback_accepted": "<=2",  # Низкая вовлеченность
        "quality_score": "<0.6",  # Низкое качество
        "is_public": False  # Не публичный
    }
    archive_query, errors = ChunkQuery.from_dict_with_validation(archive_candidates_data)
    assert errors is None
    print(f"✅ Кандидаты для архива: год={archive_query.year}, качество={archive_query.quality_score}")
    
    # 2. Дублированный или избыточный контент
    duplicate_candidates_data = {
        "quality_score": "[0.3,0.7]",  # Среднее качество
        "cohesion": "<0.5",  # Плохая связность
        "boundary_prev": ">0.8",  # Слишком похож на предыдущий
        "boundary_next": ">0.8",  # Слишком похож на следующий
        "used_in_generation": False
    }
    duplicate_query, errors = ChunkQuery.from_dict_with_validation(duplicate_candidates_data)
    assert errors is None
    print(f"✅ Возможные дубли: связность={duplicate_query.cohesion}, границы={duplicate_query.boundary_prev}")
    
    # 3. Контент, требующий миграции статуса
    status_migration_data = {
        "status": ChunkStatus.RAW.value,  # Одиночный статус
        "quality_score": ">=0.8",  # Хорошее качество
        "feedback_rejected": "<=1",  # Мало отклонений
        "year": ">=2023"  # Недавний
    }
    migration_query, errors = ChunkQuery.from_dict_with_validation(status_migration_data)
    assert errors is None
    print(f"✅ Готов к повышению статуса: текущий={migration_query.status}, качество={migration_query.quality_score}")
    
    # 4. Контент с устаревшими метаданными
    outdated_metadata_data = {
        "chunking_version": "",  # Пустая версия чанкинга
        "source_path": "",  # Пустой путь к источнику
        "category": "",  # Пустая категория
        "quality_score": ">=0.5"  # Но приемлемое качество
    }
    outdated_query, errors = ChunkQuery.from_dict_with_validation(outdated_metadata_data)
    assert errors is None
    print(f"✅ Устаревшие метаданные: версия='{outdated_query.chunking_version}', путь='{outdated_query.source_path}'")
    
    return [archive_query, duplicate_query, migration_query, outdated_query]


if __name__ == "__main__":
    print("💼 БИЗНЕС-СЦЕНАРИИ ТИПИЗИРОВАННЫХ ЗАПРОСОВ")
    print("=" * 55)
    
    example_content_management_queries()
    example_quality_control_queries()
    example_analytics_and_reporting_queries()
    example_search_and_discovery_queries()
    example_maintenance_and_cleanup_queries()
    
    print("\n" + "=" * 55)
    print("✅ Все бизнес-сценарии выполнены успешно!")
    print("🎯 Примеры готовы для использования в реальных системах") 