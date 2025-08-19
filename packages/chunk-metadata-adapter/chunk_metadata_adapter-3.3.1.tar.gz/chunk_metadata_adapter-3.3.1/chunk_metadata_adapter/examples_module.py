"""
Examples of how to use the Chunk Metadata Adapter.

This module contains practical examples for various use cases.

Recommended usage:
- Always create SemanticChunk objects via ChunkMetadataBuilder factory methods.
- For any transformation (flat <-> semantic <-> dict), use only public builder methods.
- Full recommended chain: dict (structured) -> build_semantic_chunk -> semantic_to_flat -> flat_to_semantic -> model_dump() (dict).
"""
import uuid

from chunk_metadata_adapter import (
    ChunkMetadataBuilder,
    SemanticChunk,
    ChunkType,
    ChunkRole,
    ChunkStatus,
    ChunkMetrics,
    FeedbackMetrics,
    BlockType,
    LanguageEnum,
)
from chunk_metadata_adapter.chunk_query import ChunkQuery


def example_basic_flat_metadata():
    """Example of creating basic flat metadata for a chunk."""
    # Create a builder instance for a specific project
    builder = ChunkMetadataBuilder(project="HelloWorld", unit_id="de93be12-3af5-4e6d-9ad2-c2a843c0bfb5")
    
    # Generate UUID for the source document
    source_id = "b7e23ec2-8b7a-4e6d-9ad2-c2a843c0bfb5"
    
    # Create metadata for a piece of code
    metadata = builder.build_flat_metadata(
        body="print('Hello, world!')",
        source_id=source_id,
        ordinal=0,
        type=ChunkType.CODE_BLOCK,
        language=LanguageEnum.PYTHON,
        source_path="src/hello.py",
        source_lines_start=10,
        source_lines_end=12,
        summary="Prints Hello, world!",
        tags=["example","hello"],
        role=ChunkRole.DEVELOPER
    )
    
    # Access the metadata
    print(f"Generated UUID: {metadata['uuid']}")
    print(f"SHA256: {metadata['sha256']}")
    print(f"Created at: {metadata['created_at']}")
    print(f"Is code: {metadata['is_code_chunk']}")  # Automatically computed as True
    
    return metadata


def example_structured_chunk():
    """Example of creating a structured SemanticChunk instance."""
    # Create a builder for a project with task
    builder = ChunkMetadataBuilder(
        project="DocumentationProject",
        unit_id="docs-generator"
    )
    
    # Generate a source document ID
    source_id = str(uuid.uuid4())
    
    # Create a structured chunk 
    chunk = builder.build_semantic_chunk(
        body="# Introduction\n\nThis is the documentation for the system.",
        text="# Introduction\n\nThis is the documentation for the system.",
        language=LanguageEnum.MARKDOWN,
        chunk_type=ChunkType.DOC_BLOCK,
        source_id=source_id,
        summary="Project introduction section",
        role=ChunkRole.DEVELOPER,
        source_path="docs/intro.md",
        source_lines=[1, 3],
        ordinal=0,
        task_id="DOC-123",
        subtask_id="DOC-123-A",
        tags=["introduction", "documentation", "overview"],
        links=[f"parent:{str(uuid.uuid4())}"],
        start=0,
        end=56,
        category="документация",
        title="Введение",
        year=2024,
        is_public=True,
        source="external"
    )
    
    # Access the data
    print(f"Chunk UUID: {chunk.uuid}")
    print(f"Content summary: {chunk.summary}")
    print(f"Links: {chunk.links}")
    
    return chunk


def example_conversion_between_formats():
    """Example of converting between structured and flat formats."""
    # Create a builder instance
    builder = ChunkMetadataBuilder(project="ConversionExample")
    
    # Start with a structured chunk
    structured_chunk = builder.build_semantic_chunk(
        body="This is a sample chunk for conversion demonstration.",
        text="This is a sample chunk for conversion demonstration.",
        language=LanguageEnum.EN,
        chunk_type=ChunkType.COMMENT,
        source_id=str(uuid.uuid4()),
        role=ChunkRole.REVIEWER,
        start=0,
        end=1
    )
    
    # Convert to flat dictionary
    flat_dict = builder.semantic_to_flat(structured_chunk)
    print(f"Flat representation has {len(flat_dict)} fields")
    
    # Convert back to structured format
    restored_chunk = builder.flat_to_semantic(flat_dict)
    print(f"Restored structured chunk: {restored_chunk.uuid}")
    
    # Verify they're equivalent
    assert restored_chunk.uuid == structured_chunk.uuid
    assert restored_chunk.text == structured_chunk.text
    assert restored_chunk.type == structured_chunk.type
    
    return {
        "original": structured_chunk,
        "flat": flat_dict,
        "restored": restored_chunk
    }


def example_chain_processing():
    """Example of a chain of processing for document chunks."""
    # Create a document with multiple chunks
    builder = ChunkMetadataBuilder(project="ChainExample", unit_id="processor")
    source_id = str(uuid.uuid4())
    
    # Create a sequence of chunks from a document
    chunks = []
    for i, text in enumerate([
        "# Document Title",
        "## Section 1\n\nThis is the content of section 1.",
        "## Section 2\n\nThis is the content of section 2.",
        "## Conclusion\n\nFinal thoughts on the topic."
    ]):
        chunk = builder.build_semantic_chunk(
            body=text,
            text=text,
            language=LanguageEnum.MARKDOWN,
            chunk_type=ChunkType.DOC_BLOCK,
            source_id=source_id,
            ordinal=i,
            summary=f"Section {i}" if i > 0 else "Title",
            start=0,
            end=1
        )
        chunks.append(chunk)
    
    # Create explicit links between chunks (parent-child relationships)
    for i in range(1, len(chunks)):
        # Add parent link to the title chunk
        chunks[i].links.append(f"parent:{chunks[0].uuid}")
        # Update status to show progress
        chunks[i].status = ChunkStatus.INDEXED
    
    # Add metadata about total chunks in source
    total_chunks = len(chunks)
    for i, chunk in enumerate(chunks):
        chunk.block_meta = {
            "total_chunks_in_source": total_chunks,
            "is_last_chunk": (i == total_chunks - 1),
            "chunk_position": f"{i + 1}/{total_chunks}",
            "source_info": {
                "total_sections": total_chunks - 1,  # excluding title
                "has_title": True
            }
        }
    
    # Simulate processing and updating metrics
    for chunk in chunks:
        # Update metrics based on some processing
        chunk.metrics.quality_score = 0.95
        chunk.metrics.used_in_generation = True
        chunk.metrics.matches = 3
        
        # Add feedback
        chunk.metrics.feedback.accepted = 2
        
    # Print the processed chain
    print(f"Processed {len(chunks)} chunks from source {source_id}")
    for i, chunk in enumerate(chunks):
        print(f"Chunk {i}: {chunk.summary} - Status: {chunk.status}")
    
    return chunks


def example_total_chunks_metadata():
    """
    Example demonstrating how to work with total_chunks_in_source metadata.
    
    This example shows how to:
    1. Add total_chunks_in_source to block_meta
    2. Query chunks based on their position in source
    3. Determine if a chunk is the last one in source
    """
    builder = ChunkMetadataBuilder(project="TotalChunksExample")
    
    # Create a source with multiple chunks
    source_id = str(uuid.uuid4())
    chunks = []
    
    # Create chunks for a document
    chunk_texts = [
        "Document Title",
        "Introduction to the topic.",
        "Main content section 1.",
        "Main content section 2.",
        "Conclusion and summary."
    ]
    
    total_chunks = len(chunk_texts)
    
    for i, text in enumerate(chunk_texts):
        chunk = builder.build_semantic_chunk(
            body=text,
            text=text,
            language=LanguageEnum.EN,
            chunk_type=ChunkType.DOC_BLOCK,
            source_id=source_id,
            ordinal=i,
            summary=f"Section {i}" if i > 0 else "Title",
            start=i * 100,
            end=(i + 1) * 100
        )
        
        # Add metadata about position in source
        chunk.block_meta = {
            "total_chunks_in_source": total_chunks,
            "is_last_chunk": (i == total_chunks - 1),
            "is_first_chunk": (i == 0),
            "chunk_position": f"{i + 1}/{total_chunks}",
            "chunk_percentage": round((i + 1) / total_chunks * 100, 1),
            "source_info": {
                "total_sections": total_chunks - 1,  # excluding title
                "has_title": True,
                "has_conclusion": True
            }
        }
        
        chunks.append(chunk)
    
    # Demonstrate querying based on total_chunks_in_source
    print(f"Created {len(chunks)} chunks from source {source_id}")
    
    # Find the last chunk
    last_chunk = next((chunk for chunk in chunks if chunk.block_meta.get("is_last_chunk")), None)
    if last_chunk:
        print(f"Last chunk: {last_chunk.summary} (position: {last_chunk.block_meta['chunk_position']})")
    
    # Find chunks that are more than 50% through the source
    mid_chunks = [chunk for chunk in chunks if chunk.block_meta.get("chunk_percentage", 0) > 50]
    print(f"Chunks past 50%: {len(mid_chunks)}")
    
    # Demonstrate filter queries
    print("\nExample filter queries:")
    print("- block_meta.total_chunks_in_source = 5")
    print("- block_meta.is_last_chunk = true")
    print("- block_meta.chunk_percentage > 50")
    print("- ordinal = 0 AND block_meta.is_first_chunk = true")
    
    return chunks


def example_is_code_detection():
    """Example demonstrating automatic is_code field detection."""
    builder = ChunkMetadataBuilder(project="CodeDetectionExample")
    
    # Example 1: Python code - should be detected as code
    python_chunk = builder.build_semantic_chunk(
        body="def hello_world():\n    print('Hello, World!')\n    return True",
        language=LanguageEnum.PYTHON,
        chunk_type=ChunkType.CODE_BLOCK,
        source_id=str(uuid.uuid4()),
        start=0,
        end=1
    )
    
    # Example 2: JavaScript code with DOC_BLOCK type - still detected as code due to language
    js_chunk = builder.build_semantic_chunk(
        body="function greet(name) {\n    console.log(`Hello, ${name}!`);\n}",
        language=LanguageEnum.JAVASCRIPT,
        chunk_type=ChunkType.DOC_BLOCK,  # Type is not CODE_BLOCK
        source_id=str(uuid.uuid4()),
        start=0,
        end=1
    )
    
    # Example 3: English text - should not be detected as code
    text_chunk = builder.build_semantic_chunk(
        body="This is a regular text document explaining the functionality.",
        language=LanguageEnum.EN,
        chunk_type=ChunkType.DOC_BLOCK,
        source_id=str(uuid.uuid4()),
        start=0,
        end=1
    )
    
    # Example 4: CODE_BLOCK with natural language - still code due to type
    comment_chunk = builder.build_semantic_chunk(
        body="This is a comment explaining the algorithm in English",
        language=LanguageEnum.EN,
        chunk_type=ChunkType.CODE_BLOCK,  # Type forces it to be code
        source_id=str(uuid.uuid4()),
        start=0,
        end=1
    )
    
    # Example 5: 1C code - should be detected as code
    onec_chunk = builder.build_semantic_chunk(
        body="Процедура ВывестиСообщение()\n    Сообщить(\"Привет, мир!\");\nКонецПроцедуры",
        language=LanguageEnum.ONEC,
        chunk_type=ChunkType.DOC_BLOCK,
        source_id=str(uuid.uuid4()),
        start=0,
        end=1
    )
    
    examples = [
        ("Python code", python_chunk),
        ("JavaScript (DOC_BLOCK)", js_chunk),
        ("English text", text_chunk),
        ("Comment (CODE_BLOCK)", comment_chunk),
        ("1C code", onec_chunk)
    ]
    
    print("Code detection examples:")
    for name, chunk in examples:
        print(f"{name:20} | Type: {chunk.type:10} | Language: {chunk.language:12} | is_code: {chunk.is_code()}")
    
    # Demonstrate that method and field return the same value
    for name, chunk in examples:
        method_result = chunk.is_code()
        field_result = chunk.is_code_chunk
        assert method_result == field_result, f"Mismatch for {name}: method={method_result}, field={field_result}"
    
    print("\n✅ All examples show consistent is_code detection between method and field")
    
    return examples


def example_data_lifecycle():
    """
    Example of data lifecycle processing from raw to reliable data.
    
    This example demonstrates the transition of data through the following stages:
    1. RAW - Initial ingestion of raw, unprocessed data
    2. CLEANED - Data that has been cleaned and preprocessed
    3. VERIFIED - Data verified against rules and standards
    4. VALIDATED - Data validated with cross-references and context
    5. RELIABLE - Reliable data ready for use in critical systems
    
    All transitions use only builder factory methods.
    """
    # Create a builder instance
    builder = ChunkMetadataBuilder(project="DataLifecycleDemo", unit_id="data-processor")
    source_id = str(uuid.uuid4())
    
    # Step 1: Create a chunk with RAW status - initial data ingestion
    raw_chunk = builder.build_semantic_chunk(
        body="Customer data: John Doe, jdoe@eample.com, 123-456-7890, New York",
        text="Customer data: John Doe, jdoe@eample.com, 123-456-7890, New York",
        language=LanguageEnum.EN,
        chunk_type=ChunkType.DOC_BLOCK,
        source_id=source_id,
        status=ChunkStatus.RAW,  # Mark as raw data
        summary="Customer contact information",
        tags=["customer", "contact", "personal"],
        start=0,
        end=1
    )
    print(f"RAW data created: {raw_chunk.uuid} (Status: {raw_chunk.status})")
    uuid_val = raw_chunk.uuid
    # Step 2: Clean the data (fix formatting, typos, etc.)
    cleaned_chunk = builder.build_semantic_chunk(
        chunk_uuid=uuid_val,
        body=raw_chunk.body,  # keep original raw
        text="Customer data: John Doe, jdoe@example.com, 123-456-7890, New York",  # cleaned
        language=raw_chunk.language,
        chunk_type=raw_chunk.type,
        source_id=raw_chunk.source_id,
        status=ChunkStatus.CLEANED,
        summary=raw_chunk.summary,
        tags=raw_chunk.tags,
        start=raw_chunk.start,
        end=raw_chunk.end
    )
    print(f"Data CLEANED: {cleaned_chunk.uuid} (Status: {cleaned_chunk.status})")
    # Step 3: Verify the data against rules (email format, phone number format)
    verified_tags = cleaned_chunk.tags + ["verified_email", "verified_phone"]
    verified_chunk = builder.build_semantic_chunk(
        chunk_uuid=uuid_val,
        body=cleaned_chunk.body,
        text=cleaned_chunk.text,
        language=cleaned_chunk.language,
        chunk_type=cleaned_chunk.type,
        source_id=cleaned_chunk.source_id,
        status=ChunkStatus.VERIFIED,
        summary=cleaned_chunk.summary,
        tags=verified_tags,
        start=cleaned_chunk.start,
        end=cleaned_chunk.end
    )
    print(f"Data VERIFIED: {verified_chunk.uuid} (Status: {verified_chunk.status})")
    # Step 4: Validate data with cross-references
    validated_tags = verified_chunk.tags + ["crm_validated"]
    validated_links = (verified_chunk.links or []) + [f"reference:{str(uuid.uuid4())}"]
    validated_chunk = builder.build_semantic_chunk(
        chunk_uuid=uuid_val,
        body=verified_chunk.body,
        text=verified_chunk.text,
        language=verified_chunk.language,
        chunk_type=verified_chunk.type,
        source_id=verified_chunk.source_id,
        status=ChunkStatus.VALIDATED,
        summary=verified_chunk.summary,
        tags=validated_tags,
        links=validated_links,
        start=verified_chunk.start,
        end=verified_chunk.end
    )
    print(f"Data VALIDATED: {validated_chunk.uuid} (Status: {validated_chunk.status})")
    # Step 5: Mark as reliable data, ready for use in critical systems
    reliable_chunk = builder.build_semantic_chunk(
        chunk_uuid=uuid_val,
        body=validated_chunk.body,
        text=validated_chunk.text,
        language=validated_chunk.language,
        chunk_type=validated_chunk.type,
        source_id=validated_chunk.source_id,
        status=ChunkStatus.RELIABLE,
        summary=validated_chunk.summary,
        tags=validated_chunk.tags,
        links=validated_chunk.links,
        start=validated_chunk.start,
        end=validated_chunk.end,
        coverage=0.98,  # High quality score (for demo)
        quality_score=0.98
    )
    print(f"Data marked as RELIABLE: {reliable_chunk.uuid} (Status: {reliable_chunk.status})")
    return {
        "raw": raw_chunk,
        "cleaned": cleaned_chunk,
        "verified": verified_chunk,
        "validated": validated_chunk,
        "reliable": reliable_chunk
    }


def example_metrics_extension():
    """Example of using extended metrics fields in chunk creation."""
    builder = ChunkMetadataBuilder(project="MetricsDemo", unit_id="metrics-unit")
    source_id = str(uuid.uuid4())
    chunk = builder.build_semantic_chunk(
        body="Sample text for metrics.",
        text="Sample text for metrics.",
        language=LanguageEnum.EN,
        chunk_type=ChunkType.DOC_BLOCK,
        source_id=source_id,
        status=ChunkStatus.RELIABLE,
        coverage=0.95,
        cohesion=0.8,
        boundary_prev=0.7,
        boundary_next=0.9,
        start=0,
        end=1
    )
    print(f"Chunk with extended metrics: {chunk.metrics}")
    return chunk


def example_full_chain_structured_semantic_flat():
    """
    Example of the full recommended chain:
    structured_dict -> semantic (via builder) -> flat -> semantic -> dict
    """
    builder = ChunkMetadataBuilder(project="FullChainDemo")
    # Step 1: Structured dict (user input or external source)
    structured_dict = {
        "body": "Full chain example body.",
        "text": "Full chain example body.",
        "language": LanguageEnum.EN,
        "chunk_type": ChunkType.DOC_BLOCK,
        "summary": "Full chain summary",
        "tags": ["full", "chain", "test"],
        "start": 0,
        "end": 1
    }
    # Step 2: Structured dict -> semantic
    semantic_chunk = builder.build_semantic_chunk(**structured_dict)
    # Step 3: semantic -> flat
    flat_dict = builder.semantic_to_flat(semantic_chunk)
    # Step 4: flat -> semantic
    restored_semantic = builder.flat_to_semantic(flat_dict)
    # Step 5: semantic -> dict
    restored_dict = restored_semantic.model_dump()
    print("Full chain:")
    print("Structured dict:", structured_dict)
    print("Semantic chunk:", semantic_chunk)
    print("Flat dict:", flat_dict)
    print("Restored semantic:", restored_semantic)
    print("Restored dict:", restored_dict)
    # Check equivalence of key fields
    assert restored_semantic.body == structured_dict["body"]
    assert set(restored_semantic.tags) == set(structured_dict["tags"])
    assert restored_semantic.text == structured_dict["text"]
    assert restored_semantic.type == structured_dict["chunk_type"]
    return {
        "structured_dict": structured_dict,
        "semantic": semantic_chunk,
        "flat": flat_dict,
        "restored_semantic": restored_semantic,
        "restored_dict": restored_dict
    }


def example_filter_factory_method():
    """Пример создания фильтра через фабричный метод класса ChunkQuery."""
    # Корректный фильтр
    data = {
        "type": "DocBlock",
        "start": ">100",
        "year": "in:2022,2023",
        "language": "en"
    }
    filter_obj, errors = ChunkQuery.from_dict_with_validation(data)
    assert errors is None
    print(f"Filter created: {filter_obj}")
    # Некорректный фильтр (ошибка в поле)
    bad_data = {
        "type": "DocBlock",
        "start": [1,2,3],  # Ошибка: должен быть int или str
        "year": "in:2022,2023",
        "language": "en"
    }
    filter_obj2, errors2 = ChunkQuery.from_dict_with_validation(bad_data)
    assert filter_obj2 is None
    print(f"Validation errors: {errors2}")
    return filter_obj, errors, filter_obj2, errors2


def example_filter_usage():
    """Подробные примеры работы с фильтром ChunkQuery."""
    # 1. Фильтр по равенству
    data_eq = {"type": "DocBlock", "language": "en"}
    f1, err1 = ChunkQuery.from_dict_with_validation(data_eq)
    assert err1 is None
    print(f"Filter (equality): {f1}")

    # 2. Фильтр по диапазону и in
    data_cmp = {"start": ">=10", "end": "<100", "year": "in:2022,2023"}
    f2, err2 = ChunkQuery.from_dict_with_validation(data_cmp)
    assert err2 is None
    print(f"Filter (comparison/in): {f2}")

    # 3. Сериализация и восстановление
    flat = f2.to_flat_dict()
    print(f"Flat filter: {flat}")
    f2_restored = ChunkQuery.from_flat_dict(flat)
    print(f"Restored from flat: {f2_restored}")

    # 4. Ошибка валидации
    bad = {"start": [1,2,3]}  # start должен быть int или str
    f3, err3 = ChunkQuery.from_dict_with_validation(bad)
    assert f3 is None and err3 is not None
    print(f"Validation error: {err3}")

    # 5. Пример фильтрации списка чанков (упрощённо)
    chunks = [
        {"type": "DocBlock", "start": 15, "year": 2022},
        {"type": "CodeBlock", "start": 5, "year": 2023},
        {"type": "DocBlock", "start": 50, "year": 2023},
    ]
    # Фильтр: type=DocBlock, start>=10
    filter_data = {"type": "DocBlock", "start": ">=10"}
    f, _ = ChunkQuery.from_dict_with_validation(filter_data)
    def match(chunk, f):
        # Только для примера: поддержка >= для start и равенство type
        if f.type and chunk["type"] != f.type:
            return False
        if f.start and isinstance(f.start, str) and f.start.startswith(">="):
            try:
                val = int(f.start[2:])
                if chunk["start"] < val:
                    return False
            except Exception:
                return False
        return True
    filtered = [c for c in chunks if match(c, f)]
    print(f"Filtered chunks: {filtered}")
    return f1, f2, flat, f2_restored, err3, filtered


if __name__ == "__main__":
    print("Running examples...")
    example_basic_flat_metadata()
    example_structured_chunk()
    example_conversion_between_formats()
    example_chain_processing()
    example_total_chunks_metadata()
    example_data_lifecycle()
    example_metrics_extension()
    example_full_chain_structured_semantic_flat()
    example_filter_factory_method()
    example_filter_usage()
    print("All examples completed.") 