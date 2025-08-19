"""
API Integration Examples for BM25 and Hybrid Search.

This module demonstrates how to use the API integration features
for BM25 and hybrid search with ChunkQuery.

Examples include:
- Forming API requests with BM25 parameters
- Handling search responses
- Error handling and validation
- Real-world usage scenarios

Author: Development Team
Created: 2024-01-20
"""

import json
from datetime import datetime
from chunk_metadata_adapter import (
    ChunkQuery, SearchResult, ChunkQueryResponse, SearchResponseBuilder,
    SemanticChunk, ChunkType, LanguageEnum
)


def example_basic_api_request():
    """
    Example: Basic API request formation with BM25 parameters.
    
    This example shows how to create a basic API request
    with BM25 search parameters.
    """
    print("=== Basic API Request with BM25 ===")
    
    # Create query with BM25 parameters
    query = ChunkQuery(
        type="DocBlock",
        search_query="machine learning algorithms",
        search_fields=["body", "text", "title"],
        bm25_k1=1.2,
        bm25_b=0.75,
        hybrid_search=True,
        bm25_weight=0.4,
        semantic_weight=0.6,
        min_score=0.5,
        max_results=50
    )
    
    # Form API request
    request = query.to_api_request()
    
    print("API Request:")
    print(json.dumps(request, indent=2))
    
    # Check if BM25 search is configured
    print(f"\nHas BM25 search: {query.has_bm25_search()}")
    
    # Get search parameters
    search_params = query.get_search_params()
    print(f"Search parameters: {len(search_params)} parameters")
    
    return request


def example_api_request_with_filter():
    """
    Example: API request with filter expression and BM25.
    
    This example shows how to combine filter expressions
    with BM25 search parameters.
    """
    print("\n=== API Request with Filter Expression ===")
    
    # Create query with filter expression and BM25
    query = ChunkQuery(
        filter_expr="type = 'DocBlock' AND quality_score >= 0.8 AND year >= 2020",
        search_query="neural networks",
        search_fields=["body", "text"],
        hybrid_search=True,
        bm25_weight=0.3,
        semantic_weight=0.7,
        min_score=0.6
    )
    
    # Form API request
    request = query.to_api_request()
    
    print("API Request with Filter:")
    print(json.dumps(request, indent=2))
    
    # Validate BM25 parameters
    validation = query.validate_bm25_parameters()
    print(f"\nBM25 Validation - Valid: {validation.is_valid}")
    if validation.warnings:
        print(f"Warnings: {validation.warnings}")
    
    return request


def example_response_handling():
    """
    Example: Handling search responses from server.
    
    This example demonstrates how to parse and work with
    search responses containing BM25 scores.
    """
    print("\n=== Response Handling ===")
    
    # Simulate server response
    chunk_data = {
        "uuid": "550e8400-e29b-41d4-a716-446655440000",
        "type": "DocBlock",
        "body": "Introduction to machine learning algorithms and neural networks.",
        "text": "Introduction to machine learning algorithms and neural networks.",
        "language": "en",
        "year": 2023,
        "quality_score": 0.9
    }
    
    response_data = {
        "status": "success",
        "data": {
            "results": [
                {
                    "chunk_id": "550e8400-e29b-41d4-a716-446655440000",
                    "chunk": chunk_data,
                    "bm25_score": 0.85,
                    "semantic_score": 0.92,
                    "hybrid_score": 0.89,
                    "rank": 1,
                    "matched_fields": ["body", "text"],
                    "highlights": {
                        "body": ["machine learning algorithms", "neural networks"]
                    }
                },
                {
                    "chunk_id": "550e8400-e29b-41d4-a716-446655440001",
                    "chunk": {
                        "uuid": "550e8400-e29b-41d4-a716-446655440001",
                        "type": "DocBlock",
                        "body": "Deep learning techniques for image recognition.",
                        "text": "Deep learning techniques for image recognition.",
                        "language": "en",
                        "year": 2023,
                        "quality_score": 0.8
                    },
                    "bm25_score": 0.72,
                    "semantic_score": 0.88,
                    "hybrid_score": 0.81,
                    "rank": 2,
                    "matched_fields": ["body"]
                }
            ],
            "metadata": {
                "query_type": "hybrid",
                "index_version": "1.0",
                "total_documents": 10000
            },
            "total_results": 2,
            "search_time": 0.045,
            "query_time": 0.012
        }
    }
    
    # Parse response
    response = ChunkQueryResponse(response_data)
    
    print("Response Status:", response.is_success)
    print("Total Results:", response.total_results)
    print("Search Time:", response.search_time)
    print("Query Time:", response.query_time)
    
    # Get results
    results = response.get_results()
    print(f"\nFound {len(results)} results:")
    
    for i, result in enumerate(results, 1):
        print(f"\nResult {i}:")
        print(f"  Chunk ID: {result.chunk_id}")
        print(f"  BM25 Score: {result.bm25_score}")
        print(f"  Semantic Score: {result.semantic_score}")
        print(f"  Hybrid Score: {result.hybrid_score}")
        print(f"  Rank: {result.rank}")
        print(f"  Matched Fields: {result.matched_fields}")
        if result.highlights:
            print(f"  Highlights: {result.highlights}")
    
    # Get statistics
    stats = response.get_statistics()
    print(f"\nStatistics:")
    if 'min_score' in stats:
        print(f"  Min Score: {stats['min_score']}")
        print(f"  Max Score: {stats['max_score']}")
        print(f"  Avg Score: {stats['avg_score']}")
        print(f"  Score Distribution: {stats['score_distribution']}")
    else:
        print(f"  No score statistics available")
    
    # Get top results
    if response.results:
        top_results = response.get_top_results(n=1)
        print(f"\nTop Result: {top_results[0].chunk_id} (Score: {top_results[0].primary_score})")
    else:
        print(f"\nNo results available")
    
    return response


def example_response_builder():
    """
    Example: Building search responses for testing.
    
    This example shows how to use SearchResponseBuilder
    to create test responses.
    """
    print("\n=== Response Builder ===")
    
    # Create test chunks
    chunk1 = SemanticChunk(
        uuid="550e8400-e29b-41d4-a716-446655440003",
        type=ChunkType.DOC_BLOCK,
        body="Machine learning fundamentals and algorithms.",
        text="Machine learning fundamentals and algorithms.",
        language=LanguageEnum.EN,
        year=2023,
        quality_score=0.9
    )
    
    chunk2 = SemanticChunk(
        uuid="550e8400-e29b-41d4-a716-446655440004",
        type=ChunkType.DOC_BLOCK,
        body="Deep learning and neural network architectures.",
        text="Deep learning and neural network architectures.",
        language=LanguageEnum.EN,
        year=2023,
        quality_score=0.85
    )
    
    # Create search results
    result1 = SearchResult(
        chunk_id="550e8400-e29b-41d4-a716-446655440003",
        chunk=chunk1,
        bm25_score=0.88,
        semantic_score=0.92,
        hybrid_score=0.90,
        rank=1,
        matched_fields=["body", "text"],
        highlights={"body": ["machine learning", "algorithms"]}
    )
    
    result2 = SearchResult(
        chunk_id="550e8400-e29b-41d4-a716-446655440004",
        chunk=chunk2,
        bm25_score=0.75,
        semantic_score=0.89,
        hybrid_score=0.83,
        rank=2,
        matched_fields=["body"]
    )
    
    # Build response
    builder = SearchResponseBuilder()
    response = (builder
                .add_result(result1)
                .add_result(result2)
                .set_metadata({
                    "query_type": "hybrid",
                    "index_version": "1.0",
                    "test_mode": True
                })
                .set_timing(0.05, 0.01)
                .build())
    
    print("Built Response:")
    print(f"  Status: {response.is_success}")
    print(f"  Results: {len(response.results)}")
    print(f"  Search Time: {response.search_time}")
    print(f"  Metadata: {response.metadata}")
    
    # Convert to JSON
    json_response = response.to_json()
    print(f"\nJSON Response (first 200 chars):")
    print(json_response[:200] + "...")
    
    return response


def example_error_handling():
    """
    Example: Error handling in API responses.
    
    This example demonstrates how to handle various
    error scenarios in API responses.
    """
    print("\n=== Error Handling ===")
    
    # Test invalid response structure
    try:
        invalid_response = {
            "status": "success"
            # Missing 'data' field
        }
        response = ChunkQueryResponse(invalid_response)
    except ValueError as e:
        print(f"Validation Error: {e}")
    
    # Test error response
    error_response_data = {
        "status": "error",
        "error": "Invalid search query: empty or too short"
    }
    
    response = ChunkQueryResponse(error_response_data)
    print(f"Error Response - Success: {response.is_success}")
    print(f"Error Message: {response.error_message}")
    
    # Test invalid JSON
    try:
        response = ChunkQueryResponse.from_json("invalid json string")
    except ValueError as e:
        print(f"JSON Parse Error: {e}")
    
    # Test score threshold validation
    try:
        chunk = SemanticChunk(
            uuid="test",
            type=ChunkType.DOC_BLOCK,
            text="Test content"
        )
        
        if response.is_success:
            # This would fail if response was successful
            high_threshold_results = response.get_results_by_score_threshold(1.5)
    except ValueError as e:
        print(f"Threshold Validation Error: {e}")
    
    return response


def example_real_world_scenario():
    """
    Example: Real-world search scenario.
    
    This example demonstrates a complete workflow
    for a real-world search scenario.
    """
    print("\n=== Real-World Search Scenario ===")
    
    # 1. Create search query
    query = ChunkQuery(
        type="DocBlock",
        language="en",
        year=">=2020",
        quality_score=">=0.7",
        search_query="artificial intelligence and machine learning",
        search_fields=["body", "text", "title"],
        hybrid_search=True,
        bm25_weight=0.4,
        semantic_weight=0.6,
        min_score=0.6,
        max_results=20
    )
    
    print("Search Query Created:")
    print(f"  Type: {query.type}")
    print(f"  Language: {query.language}")
    print(f"  Search Query: {query.search_query}")
    print(f"  Hybrid Search: {query.hybrid_search}")
    
    # 2. Validate query
    validation = query.validate_bm25_parameters()
    print(f"\nQuery Validation:")
    print(f"  Valid: {validation.is_valid}")
    if validation.errors:
        print(f"  Errors: {validation.errors}")
    if validation.warnings:
        print(f"  Warnings: {validation.warnings}")
    
    # 3. Form API request
    request = query.to_api_request()
    print(f"\nAPI Request Size: {len(json.dumps(request))} characters")
    print(f"API Version: {request['api_version']}")
    
    # 4. Simulate server response
    response_data = {
        "status": "success",
        "data": {
            "results": [
                {
                    "chunk_id": "550e8400-e29b-41d4-a716-446655440002",
                    "chunk": {
                        "uuid": "550e8400-e29b-41d4-a716-446655440002",
                        "type": "DocBlock",
                        "body": "Introduction to artificial intelligence and machine learning concepts.",
                        "text": "Introduction to artificial intelligence and machine learning concepts.",
                        "language": "en",
                        "year": 2023,
                        "quality_score": 0.9
                    },
                    "bm25_score": 0.92,
                    "semantic_score": 0.95,
                    "hybrid_score": 0.94,
                    "rank": 1,
                    "matched_fields": ["body", "title"],
                    "highlights": {
                        "body": ["artificial intelligence", "machine learning"]
                    }
                }
            ],
            "metadata": {
                "query_type": "hybrid",
                "index_version": "1.0",
                "total_documents": 15000,
                "filtered_documents": 5000
            },
            "total_results": 1,
            "search_time": 0.078,
            "query_time": 0.015
        }
    }
    
    # 5. Parse and analyze response
    response = ChunkQueryResponse(response_data)
    
    print(f"\nSearch Results:")
    print(f"  Total Found: {response.total_results}")
    print(f"  Search Time: {response.search_time:.3f}s")
    print(f"  Query Time: {response.query_time:.3f}s")
    
    # 6. Process results
    results = response.get_results()
    for result in results:
        print(f"\n  Result: {result.chunk_id}")
        print(f"    Hybrid Score: {result.hybrid_score:.3f}")
        print(f"    BM25 Score: {result.bm25_score:.3f}")
        print(f"    Semantic Score: {result.semantic_score:.3f}")
        print(f"    Text: {result.chunk.text[:50]}...")
    
    # 7. Get statistics
    stats = response.get_statistics()
    print(f"\nPerformance Statistics:")
    if 'avg_score' in stats:
        print(f"  Average Score: {stats['avg_score']:.3f}")
        print(f"  Score Range: {stats['min_score']:.3f} - {stats['max_score']:.3f}")
        print(f"  High Quality Results: {stats['score_distribution']['high']}")
    else:
        print(f"  No score statistics available")
    
    return query, response


def main():
    """Run all API integration examples."""
    print("BM25 API Integration Examples")
    print("=" * 50)
    
    # Run examples
    example_basic_api_request()
    example_api_request_with_filter()
    example_response_handling()
    example_response_builder()
    example_error_handling()
    example_real_world_scenario()
    
    print("\n" + "=" * 50)
    print("All examples completed successfully!")


if __name__ == "__main__":
    main()
