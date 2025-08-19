"""
BM25 and Hybrid Search Usage Examples.

This module provides comprehensive examples of how to use BM25 and hybrid search
functionality in the ChunkMetadataAdapter package.

Examples cover:
- Basic BM25 search
- Hybrid search with different strategies
- Advanced configuration
- Real-world scenarios
- Performance optimization

Author: Development Team
Created: 2024-01-20
"""

from chunk_metadata_adapter import (
    ChunkQuery, SemanticChunk, SearchResult, ChunkQueryResponse,
    HybridStrategy, HybridSearchConfig, HybridSearchHelper, HybridSearchValidator
)


def example_basic_bm25_search():
    """
    Basic BM25 search example.
    
    This example demonstrates how to perform a simple BM25 search
    with default parameters.
    """
    print("=== Basic BM25 Search Example ===")
    
    # Create a simple BM25 search query
    query = ChunkQuery(
        search_query="python machine learning",
        search_fields=["title", "body", "summary"],
        min_score=0.5,
        max_results=20
    )
    
    # Validate the query
    validation = query.validate_bm25_parameters()
    print(f"Query valid: {validation.is_valid}")
    if validation.warnings:
        print(f"Warnings: {validation.warnings}")
    
    # Check if BM25 search is available
    print(f"Has BM25 search: {query.has_bm25_search()}")
    
    # Get search parameters
    search_params = query.get_search_params()
    print(f"Search parameters: {search_params}")
    
    # Create API request
    api_request = query.to_api_request()
    print(f"API request keys: {list(api_request.keys())}")
    
    print()


def example_hybrid_search_basic():
    """
    Basic hybrid search example.
    
    This example demonstrates how to perform hybrid search
    combining BM25 and semantic search.
    """
    print("=== Basic Hybrid Search Example ===")
    
    # Create a hybrid search query
    query = ChunkQuery(
        search_query="artificial intelligence algorithms",
        search_fields=["title", "body", "summary"],
        hybrid_search=True,
        bm25_weight=0.6,
        semantic_weight=0.4,
        min_score=0.6,
        max_results=50
    )
    
    # Validate the query
    validation = query.validate_bm25_parameters()
    print(f"Query valid: {validation.is_valid}")
    
    # Create API request
    api_request = query.to_api_request()
    print(f"Hybrid search: {api_request['hybrid_search']}")
    print(f"BM25 weight: {api_request['bm25_weight']}")
    print(f"Semantic weight: {api_request['semantic_weight']}")
    
    print()


def example_hybrid_search_strategies():
    """
    Hybrid search with different strategies example.
    
    This example demonstrates how to use different hybrid search
    strategies for various use cases.
    """
    print("=== Hybrid Search Strategies Example ===")
    
    # Sample scores for demonstration
    bm25_scores = [0.8, 0.6, 0.9, 0.4, 0.7]
    semantic_scores = [0.7, 0.5, 0.8, 0.6, 0.9]
    
    print("Original scores:")
    print(f"BM25: {bm25_scores}")
    print(f"Semantic: {semantic_scores}")
    print()
    
    # Strategy 1: Weighted Sum (default)
    config_weighted = HybridSearchConfig(
        bm25_weight=0.6,
        semantic_weight=0.4,
        strategy=HybridStrategy.WEIGHTED_SUM
    )
    
    hybrid_scores = HybridSearchHelper.calculate_hybrid_scores(
        bm25_scores, semantic_scores, config_weighted
    )
    print(f"Weighted Sum: {[round(s, 3) for s in hybrid_scores]}")
    
    # Strategy 2: CombSUM
    config_combsum = HybridSearchConfig(
        strategy=HybridStrategy.COMB_SUM,
        normalize_scores=False
    )
    
    hybrid_scores = HybridSearchHelper.calculate_hybrid_scores(
        bm25_scores, semantic_scores, config_combsum
    )
    print(f"CombSUM: {[round(s, 3) for s in hybrid_scores]}")
    
    # Strategy 3: CombMNZ
    config_combmnz = HybridSearchConfig(
        strategy=HybridStrategy.COMB_MNZ,
        normalize_scores=False
    )
    
    hybrid_scores = HybridSearchHelper.calculate_hybrid_scores(
        bm25_scores, semantic_scores, config_combmnz
    )
    print(f"CombMNZ: {[round(s, 3) for s in hybrid_scores]}")
    
    # Strategy 4: Reciprocal Rank
    bm25_ranks = [1, 3, 2, 5, 4]
    semantic_ranks = [2, 1, 4, 3, 5]
    
    hybrid_scores = HybridSearchHelper.reciprocal_rank(
        bm25_ranks, semantic_ranks, 0.6, 0.4
    )
    print(f"Reciprocal Rank: {[round(s, 6) for s in hybrid_scores]}")
    
    print()


def example_advanced_configuration():
    """
    Advanced configuration example.
    
    This example demonstrates advanced configuration options
    for BM25 and hybrid search.
    """
    print("=== Advanced Configuration Example ===")
    
    # Advanced BM25 configuration
    query = ChunkQuery(
        search_query="deep learning neural networks",
        search_fields=["title", "body", "summary"],
        bm25_k1=1.5,  # Custom k1 parameter
        bm25_b=0.8,   # Custom b parameter
        hybrid_search=True,
        bm25_weight=0.7,
        semantic_weight=0.3,
        min_score=0.7,
        max_results=100
    )
    
    # Validate with custom parameters
    validation = query.validate_bm25_parameters()
    print(f"Advanced query valid: {validation.is_valid}")
    
    # Custom hybrid search configuration
    config = HybridSearchConfig(
        bm25_weight=0.7,
        semantic_weight=0.3,
        strategy=HybridStrategy.WEIGHTED_SUM,
        normalize_scores=True,
        min_score_threshold=0.1,
        max_score_threshold=0.9
    )
    
    print(f"Custom config: {config}")
    
    # Validate configuration
    is_valid = HybridSearchValidator.validate_config(config)
    print(f"Config valid: {is_valid}")
    
    print()


def example_real_world_scenarios():
    """
    Real-world scenarios example.
    
    This example demonstrates practical use cases for BM25
    and hybrid search in real applications.
    """
    print("=== Real-World Scenarios Example ===")
    
    # Scenario 1: Content Discovery
    print("Scenario 1: Content Discovery")
    content_query = ChunkQuery(
        search_query="machine learning algorithms",
        search_fields=["title", "body", "summary"],
        hybrid_search=True,
        bm25_weight=0.6,
        semantic_weight=0.4,
        min_score=0.5,
        max_results=20
    )
    print(f"Content query valid: {content_query.validate_bm25_parameters().is_valid}")
    
    # Scenario 2: Code Search
    print("\nScenario 2: Code Search")
    code_query = ChunkQuery(
        search_query="def train_model",
        search_fields=["body"],  # Only search in code body
        hybrid_search=False,     # BM25 only for code
        min_score=0.8,
        max_results=10
    )
    print(f"Code query valid: {code_query.validate_bm25_parameters().is_valid}")
    
    # Scenario 3: Academic Research
    print("\nScenario 3: Academic Research")
    research_query = ChunkQuery(
        search_query="artificial intelligence applications",
        search_fields=["title", "body", "summary"],
        hybrid_search=True,
        bm25_weight=0.4,  # More weight on semantic similarity
        semantic_weight=0.6,
        filter_expr="type = 'DocBlock' AND quality_score >= 0.8",
        min_score=0.6,
        max_results=50
    )
    print(f"Research query valid: {research_query.validate_bm25_parameters().is_valid}")
    
    print()


def example_performance_optimization():
    """
    Performance optimization example.
    
    This example demonstrates how to optimize performance
    for BM25 and hybrid search operations.
    """
    print("=== Performance Optimization Example ===")
    
    # Optimized query for performance
    optimized_query = ChunkQuery(
        search_query="python programming",
        search_fields=["title", "body"],  # Limit search fields
        hybrid_search=True,
        bm25_weight=0.5,
        semantic_weight=0.5,
        min_score=0.6,  # Higher threshold for fewer results
        max_results=20  # Limit results for faster processing
    )
    
    # Validate performance considerations
    validation = optimized_query.validate_bm25_parameters()
    print(f"Optimized query valid: {validation.is_valid}")
    
    # Performance tips
    print("\nPerformance Tips:")
    print("1. Limit search fields to essential ones")
    print("2. Use higher min_score to reduce result set")
    print("3. Set reasonable max_results limit")
    print("4. Use hybrid search only when needed")
    print("5. Cache frequently used queries")
    
    print()


def example_error_handling():
    """
    Error handling example.
    
    This example demonstrates how to handle errors and
    validate parameters properly.
    """
    print("=== Error Handling Example ===")
    
    # Example 1: Invalid weights
    try:
        query = ChunkQuery(
            search_query="test",
            hybrid_search=True,
            bm25_weight=0.6,
            semantic_weight=0.5  # Sum != 1.0
        )
        validation = query.validate_bm25_parameters()
        print(f"Query valid: {validation.is_valid}")
        if validation.warnings:
            print(f"Warnings: {validation.warnings}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 2: Invalid search fields
    try:
        query = ChunkQuery(
            search_query="test",
            search_fields=["invalid_field"]  # Invalid field
        )
        validation = query.validate_bm25_parameters()
        print(f"Query valid: {validation.is_valid}")
        if validation.errors:
            print(f"Errors: {validation.errors}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 3: Valid configuration
    try:
        config = HybridSearchConfig(
            bm25_weight=0.6,
            semantic_weight=0.4,
            strategy=HybridStrategy.WEIGHTED_SUM
        )
        is_valid = HybridSearchValidator.validate_config(config)
        print(f"Config valid: {is_valid}")
    except Exception as e:
        print(f"Error: {e}")
    
    print()


def example_serialization():
    """
    Serialization example.
    
    This example demonstrates how to serialize and deserialize
    queries with BM25 and hybrid search parameters.
    """
    print("=== Serialization Example ===")
    
    # Create a query with BM25 parameters
    original_query = ChunkQuery(
        search_query="python machine learning",
        search_fields=["title", "body"],
        hybrid_search=True,
        bm25_weight=0.6,
        semantic_weight=0.4,
        min_score=0.5,
        max_results=20
    )
    
    print("Original query:")
    print(f"Search query: {original_query.search_query}")
    print(f"Hybrid search: {original_query.hybrid_search}")
    print(f"BM25 weight: {original_query.bm25_weight}")
    
    # Serialize to flat dictionary
    flat_dict = original_query.to_flat_dict()
    print(f"\nSerialized keys: {list(flat_dict.keys())}")
    
    # Deserialize from flat dictionary
    restored_query = ChunkQuery.from_flat_dict(flat_dict)
    print(f"\nRestored query:")
    print(f"Search query: {restored_query.search_query}")
    print(f"Hybrid search: {restored_query.hybrid_search}")
    print(f"BM25 weight: {restored_query.bm25_weight}")
    
    # Verify they are the same
    assert original_query.search_query == restored_query.search_query
    assert original_query.hybrid_search == restored_query.hybrid_search
    assert original_query.bm25_weight == restored_query.bm25_weight
    print("\nSerialization successful!")
    
    print()


def run_all_examples():
    """
    Run all BM25 and hybrid search examples.
    
    This function executes all the example functions to demonstrate
    the complete functionality of BM25 and hybrid search.
    """
    print("BM25 and Hybrid Search Examples")
    print("=" * 50)
    print()
    
    example_basic_bm25_search()
    example_hybrid_search_basic()
    example_hybrid_search_strategies()
    example_advanced_configuration()
    example_real_world_scenarios()
    example_performance_optimization()
    example_error_handling()
    example_serialization()
    
    print("All examples completed successfully!")


if __name__ == "__main__":
    run_all_examples()
