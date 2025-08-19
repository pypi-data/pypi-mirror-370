"""
Example demonstrating BM25 tokens integration in SemanticChunk.

This example shows how to use the new bm25_tokens field in SemanticChunk,
which works exactly like the existing tokens field but is specifically
for BM25 search operations.
"""

from chunk_metadata_adapter.semantic_chunk import SemanticChunk, ChunkMetrics
from chunk_metadata_adapter.data_types import ChunkType, LanguageEnum


def demonstrate_bm25_tokens_usage():
    """
    Demonstrate various ways to use bm25_tokens in SemanticChunk.
    """
    print("=== BM25 Tokens Integration Example ===\n")
    
    # Example 1: Creating SemanticChunk with bm25_tokens in metrics
    print("1. Creating SemanticChunk with bm25_tokens in metrics:")
    chunk1 = SemanticChunk(
        type=ChunkType.DOC_BLOCK,
        body="This is a test document about machine learning and artificial intelligence.",
        metrics=ChunkMetrics(
            tokens=["this", "is", "a", "test", "document", "about", "machine", "learning"],
            bm25_tokens=["test", "document", "machine", "learning", "artificial", "intelligence"]
        )
    )
    print(f"   Tokens: {chunk1.metrics.tokens}")
    print(f"   BM25 Tokens: {chunk1.metrics.bm25_tokens}")
    print()
    
    # Example 2: Creating SemanticChunk with bm25_tokens from top level
    print("2. Creating SemanticChunk with bm25_tokens from top level:")
    chunk2, errors = SemanticChunk.validate_and_fill({
        "type": "DocBlock",
        "body": "Python programming language examples and tutorials.",
        "bm25_tokens": ["python", "programming", "examples", "tutorials"]
    })
    
    if errors is None:
        print(f"   BM25 Tokens: {chunk2.metrics.bm25_tokens}")
        print(f"   Tokens: {chunk2.metrics.tokens}")
    else:
        print(f"   Errors: {errors}")
    print()
    
    # Example 3: Round trip through flat dictionary (Redis simulation)
    print("3. Round trip through flat dictionary (Redis simulation):")
    original_chunk = SemanticChunk(
        type=ChunkType.DOC_BLOCK,
        body="Data science and analytics content.",
        metrics=ChunkMetrics(
            tokens=["data", "science", "content"],
            bm25_tokens=["data", "science", "analytics", "content", "machine", "learning"]
        )
    )
    
    # Convert to flat dict (simulating Redis storage)
    flat_dict = original_chunk.to_flat_dict(for_redis=True)
    print(f"   Flat dict keys: {list(flat_dict.keys())}")
    
    # Convert back from flat dict
    restored_chunk = SemanticChunk.from_flat_dict(flat_dict, from_redis=True)
    print(f"   Restored tokens: {restored_chunk.metrics.tokens}")
    print(f"   Restored BM25 tokens: {restored_chunk.metrics.bm25_tokens}")
    print()
    
    # Example 4: Priority handling (metrics over top level)
    print("4. Priority handling (metrics over top level):")
    chunk4, errors = SemanticChunk.validate_and_fill({
        "type": "DocBlock",
        "body": "Web development and frontend technologies.",
        "bm25_tokens": ["web", "development"],  # Top level
        "metrics": {
            "bm25_tokens": ["web", "development", "frontend", "technologies"]  # Metrics level
        }
    })
    
    if errors is None:
        print(f"   BM25 Tokens (should be from metrics): {chunk4.metrics.bm25_tokens}")
    else:
        print(f"   Errors: {errors}")
    print()
    
    # Example 5: Handling None values
    print("5. Handling None values:")
    chunk5, errors = SemanticChunk.validate_and_fill({
        "type": "DocBlock",
        "body": "Content without BM25 tokens.",
        "bm25_tokens": None
    })
    
    if errors is None:
        print(f"   BM25 Tokens (should be None): {chunk5.metrics.bm25_tokens}")
    else:
        print(f"   Errors: {errors}")
    print()
    
    # Example 6: Mixed data types conversion
    print("6. Mixed data types conversion:")
    chunk6, errors = SemanticChunk.validate_and_fill({
        "type": "DocBlock",
        "body": "Content with mixed token types.",
        "bm25_tokens": [123, "string", 45.67, True, "final"]
    })
    
    if errors is None:
        print(f"   BM25 Tokens (converted to strings): {chunk6.metrics.bm25_tokens}")
    else:
        print(f"   Errors: {errors}")
    print()
    
    print("=== Example completed successfully! ===")


if __name__ == "__main__":
    demonstrate_bm25_tokens_usage()
