"""
Examples of BM25 search functionality in ChunkQuery.

This module demonstrates how to use the new BM25 search fields
added to ChunkQuery for full-text search capabilities.

Examples include:
- Basic BM25 search
- Hybrid search (BM25 + semantic)
- Search with metadata filters
- Parameter tuning
- Result ranking

Author: Development Team
Created: 2024-01-20
"""

from chunk_metadata_adapter import ChunkQuery, SemanticChunk
from chunk_metadata_adapter.data_types import ChunkType, LanguageEnum


def basic_bm25_search_example():
    """
    Basic BM25 search example.
    
    This example shows how to perform a simple full-text search
    using BM25 algorithm on chunk content.
    """
    print("=== Basic BM25 Search Example ===")
    
    # Create a query with BM25 search
    query = ChunkQuery(
        search_query="python machine learning",
        search_fields=["body", "text", "summary", "title"],
        bm25_k1=1.2,  # Term frequency saturation
        bm25_b=0.75,  # Length normalization
        max_results=50
    )
    
    print(f"Search query: {query.search_query}")
    print(f"Search fields: {query.search_fields}")
    print(f"BM25 k1: {query.bm25_k1}")
    print(f"BM25 b: {query.bm25_b}")
    print(f"Max results: {query.max_results}")
    
    # Validate the query
    validation = query.validate_bm25_parameters()
    print(f"Valid: {validation.is_valid}")
    if validation.warnings:
        print(f"Warnings: {validation.warnings}")
    
    # Convert to flat dict for transmission
    flat_query = query.to_flat_dict()
    print(f"Flat query: {flat_query}")
    
    print()


def hybrid_search_example():
    """
    Hybrid search example combining BM25 and semantic search.
    
    This example shows how to combine BM25 full-text search
    with semantic vector search for better results.
    """
    print("=== Hybrid Search Example ===")
    
    # Create a hybrid search query
    query = ChunkQuery(
        search_query="artificial intelligence neural networks",
        search_fields=["body", "text", "summary"],
        hybrid_search=True,
        bm25_weight=0.3,      # 30% weight for BM25
        semantic_weight=0.7,  # 70% weight for semantic search
        bm25_k1=1.5,          # Higher k1 for more term frequency importance
        bm25_b=0.8,           # Higher b for more length normalization
        min_score=0.6,        # Minimum relevance score
        max_results=100
    )
    
    print(f"Search query: {query.search_query}")
    print(f"Hybrid search: {query.hybrid_search}")
    print(f"BM25 weight: {query.bm25_weight}")
    print(f"Semantic weight: {query.semantic_weight}")
    print(f"Min score: {query.min_score}")
    
    # Validate hybrid search parameters
    validation = query.validate_bm25_parameters()
    print(f"Valid: {validation.is_valid}")
    if validation.warnings:
        print(f"Warnings: {validation.warnings}")
    
    print()


def bm25_with_metadata_filters_example():
    """
    BM25 search combined with metadata filters.
    
    This example shows how to combine full-text search
    with existing metadata filtering capabilities.
    """
    print("=== BM25 with Metadata Filters Example ===")
    
    # BM25 search with metadata filters
    query = ChunkQuery(
        # BM25 search parameters
        search_query="data science analytics",
        search_fields=["body", "text", "summary", "title"],
        bm25_k1=1.2,
        bm25_b=0.75,
        
        # Metadata filters
        type=ChunkType.DOC_BLOCK,
        language=LanguageEnum.EN,
        quality_score=">=0.8",
        year=">=2020",
        is_public=True,
        
        # Result parameters
        max_results=25,
        min_score=0.5
    )
    
    print(f"Search query: {query.search_query}")
    print(f"Type filter: {query.type}")
    print(f"Language filter: {query.language}")
    print(f"Quality score filter: {query.quality_score}")
    print(f"Year filter: {query.year}")
    print(f"Public filter: {query.is_public}")
    
    # Validate the query
    validation = query.validate_bm25_parameters()
    print(f"Valid: {validation.is_valid}")
    
    print()


def complex_filter_expression_with_bm25_example():
    """
    Complex AST filter expression combined with BM25 search.
    
    This example shows how to use complex logical expressions
    together with BM25 search.
    """
    print("=== Complex Filter Expression with BM25 Example ===")
    
    # Complex filter with BM25 search
    query = ChunkQuery(
        # BM25 search
        search_query="machine learning algorithms",
        search_fields=["body", "text", "summary"],
        hybrid_search=True,
        bm25_weight=0.4,
        semantic_weight=0.6,
        
        # Complex filter expression
        filter_expr="""
            (type = 'DocBlock' OR type = 'CodeBlock') AND
            quality_score >= 0.7 AND
            (tags intersects ['ai', 'ml'] OR tags intersects ['python', 'data']) AND
            year >= 2020 AND
            NOT is_deleted AND
            (is_public = true OR user_role = 'admin')
        """,
        
        # Result parameters
        max_results=50,
        min_score=0.4
    )
    
    print(f"Search query: {query.search_query}")
    print(f"Filter expression: {query.filter_expr}")
    print(f"Hybrid search: {query.hybrid_search}")
    
    # Validate both filter expression and BM25 parameters
    filter_validation = query.validate()
    bm25_validation = query.validate_bm25_parameters()
    
    print(f"Filter valid: {filter_validation.is_valid}")
    print(f"BM25 valid: {bm25_validation.is_valid}")
    
    if filter_validation.errors:
        print(f"Filter errors: {filter_validation.errors}")
    if bm25_validation.errors:
        print(f"BM25 errors: {bm25_validation.errors}")
    
    print()


def bm25_parameter_tuning_example():
    """
    BM25 parameter tuning examples.
    
    This example shows different BM25 parameter configurations
    for different use cases.
    """
    print("=== BM25 Parameter Tuning Examples ===")
    
    # Example 1: Standard BM25 (good for general search)
    standard_query = ChunkQuery(
        search_query="python programming",
        bm25_k1=1.2,
        bm25_b=0.75
    )
    print("Standard BM25:")
    print(f"  k1={standard_query.bm25_k1}, b={standard_query.bm25_b}")
    
    # Example 2: High precision (good for technical documents)
    precision_query = ChunkQuery(
        search_query="machine learning algorithms",
        bm25_k1=0.8,   # Lower k1 for less term frequency saturation
        bm25_b=0.9     # Higher b for more length normalization
    )
    print("High precision BM25:")
    print(f"  k1={precision_query.bm25_k1}, b={precision_query.bm25_b}")
    
    # Example 3: High recall (good for broad searches)
    recall_query = ChunkQuery(
        search_query="artificial intelligence",
        bm25_k1=2.0,   # Higher k1 for more term frequency importance
        bm25_b=0.5     # Lower b for less length normalization
    )
    print("High recall BM25:")
    print(f"  k1={recall_query.bm25_k1}, b={recall_query.bm25_b}")
    
    print()


def search_field_selection_example():
    """
    Search field selection examples.
    
    This example shows how to choose different search fields
    for different types of content.
    """
    print("=== Search Field Selection Examples ===")
    
    # Example 1: Search in all fields
    all_fields_query = ChunkQuery(
        search_query="data analysis",
        search_fields=["body", "text", "summary", "title"]
    )
    print("All fields search:")
    print(f"  Fields: {all_fields_query.search_fields}")
    
    # Example 2: Search only in content (body and text)
    content_query = ChunkQuery(
        search_query="python code examples",
        search_fields=["body", "text"]
    )
    print("Content-only search:")
    print(f"  Fields: {content_query.search_fields}")
    
    # Example 3: Search only in metadata (summary and title)
    metadata_query = ChunkQuery(
        search_query="machine learning",
        search_fields=["summary", "title"]
    )
    print("Metadata-only search:")
    print(f"  Fields: {metadata_query.search_fields}")
    
    print()


def result_ranking_example():
    """
    Result ranking and scoring examples.
    
    This example shows how to configure result ranking
    and scoring thresholds.
    """
    print("=== Result Ranking Examples ===")
    
    # Example 1: High quality results only
    high_quality_query = ChunkQuery(
        search_query="deep learning",
        min_score=0.8,      # High minimum score
        max_results=10      # Few results, high quality
    )
    print("High quality results:")
    print(f"  Min score: {high_quality_query.min_score}")
    print(f"  Max results: {high_quality_query.max_results}")
    
    # Example 2: Broad search with many results
    broad_query = ChunkQuery(
        search_query="artificial intelligence",
        min_score=0.3,      # Lower minimum score
        max_results=200     # Many results
    )
    print("Broad search:")
    print(f"  Min score: {broad_query.min_score}")
    print(f"  Max results: {broad_query.max_results}")
    
    # Example 3: Balanced approach
    balanced_query = ChunkQuery(
        search_query="data science",
        min_score=0.5,      # Medium minimum score
        max_results=50      # Moderate number of results
    )
    print("Balanced approach:")
    print(f"  Min score: {balanced_query.min_score}")
    print(f"  Max results: {balanced_query.max_results}")
    
    print()


def validation_examples():
    """
    Validation examples for BM25 parameters.
    
    This example shows how to validate BM25 search parameters
    and handle validation errors.
    """
    print("=== Validation Examples ===")
    
    # Example 1: Valid configuration
    valid_query = ChunkQuery(
        search_query="python programming",
        search_fields=["body", "text"],
        hybrid_search=True,
        bm25_weight=0.4,
        semantic_weight=0.6
    )
    
    validation = valid_query.validate_bm25_parameters()
    print("Valid configuration:")
    print(f"  Valid: {validation.is_valid}")
    print(f"  Errors: {validation.errors}")
    print(f"  Warnings: {validation.warnings}")
    
    # Example 2: Invalid configuration (weights don't sum to 1.0)
    invalid_query = ChunkQuery(
        search_query="machine learning",
        hybrid_search=True,
        bm25_weight=0.3,
        semantic_weight=0.3  # Sum = 0.6, should be 1.0
    )
    
    validation = invalid_query.validate_bm25_parameters()
    print("Invalid configuration (weights don't sum to 1.0):")
    print(f"  Valid: {validation.is_valid}")
    print(f"  Errors: {validation.errors}")
    print(f"  Warnings: {validation.warnings}")
    
    # Example 3: Empty search fields
    empty_fields_query = ChunkQuery(
        search_query="test query",
        search_fields=[]
    )
    
    validation = empty_fields_query.validate_bm25_parameters()
    print("Empty search fields:")
    print(f"  Valid: {validation.is_valid}")
    print(f"  Errors: {validation.errors}")
    
    print()


def main():
    """Run all BM25 search examples."""
    print("BM25 Search Examples for ChunkQuery")
    print("=" * 50)
    print()
    
    basic_bm25_search_example()
    hybrid_search_example()
    bm25_with_metadata_filters_example()
    complex_filter_expression_with_bm25_example()
    bm25_parameter_tuning_example()
    search_field_selection_example()
    result_ranking_example()
    validation_examples()
    
    print("All examples completed!")


if __name__ == "__main__":
    main()
