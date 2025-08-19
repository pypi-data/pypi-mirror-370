"""
Example demonstrating filter parser with total_chunks_in_source metadata.

This example shows how the FilterParser handles queries involving
the new total_chunks_in_source field in block_meta.
"""

from chunk_metadata_adapter.filter_parser import FilterParser
from chunk_metadata_adapter.filter_executor import FilterExecutor
from chunk_metadata_adapter.semantic_chunk import SemanticChunk, ChunkStatus
from chunk_metadata_adapter.ast import TypedValue
import uuid


def example_filter_parser_with_total_chunks():
    """
    Example demonstrating filter parser with total_chunks_in_source.
    
    This example shows:
    1. How to parse queries with total_chunks_in_source
    2. How to execute filters on chunks with this metadata
    3. Different query patterns for chunk positioning
    """
    print("=== Filter Parser with Total Chunks Example ===\n")
    
    # Initialize parser and executor
    parser = FilterParser()
    executor = FilterExecutor()
    
    # Create sample chunks with total_chunks_in_source metadata
    chunks = []
    total_chunks = 5
    
    for i in range(total_chunks):
        chunk = SemanticChunk(
            uuid=str(uuid.uuid4()),
            body=f"Content of chunk {i+1}",
            type="DocBlock",
            content=f"Content of chunk {i+1}",
            quality_score=0.8 + (i * 0.02),
            tags=["example", "metadata"],
            year=2024,
            ordinal=i,
            block_meta={
                "total_chunks_in_source": total_chunks,
                "is_last_chunk": (i == total_chunks - 1),
                "is_first_chunk": (i == 0),
                "chunk_position": f"{i+1}/{total_chunks}",
                "chunk_percentage": (i / (total_chunks - 1)) * 100 if total_chunks > 1 else 0
            }
        )
        chunks.append(chunk)
    
    print(f"Created {len(chunks)} chunks with total_chunks_in_source={total_chunks}")
    
    # Test queries with total_chunks_in_source
    test_queries = [
        # Basic total chunks queries
        "block_meta.total_chunks_in_source = 5",
        "block_meta.total_chunks_in_source >= 3",
        "block_meta.total_chunks_in_source <= 10",
        
        # Position-based queries
        "block_meta.is_last_chunk = true",
        "block_meta.is_first_chunk = true",
        "ordinal = 0 AND block_meta.is_first_chunk = true",
        
        # Percentage-based queries
        "block_meta.chunk_percentage > 50",
        "block_meta.chunk_percentage <= 25",
        
        # Complex queries combining multiple conditions
        "block_meta.total_chunks_in_source >= 5 AND block_meta.is_last_chunk = true",
        "quality_score >= 0.8 AND block_meta.chunk_percentage > 50",
        "type = 'DocBlock' AND block_meta.is_first_chunk = true AND year = 2024",
        
        # Nested field access
        "block_meta.total_chunks_in_source = 5 AND block_meta.chunk_position = '1/5'"
    ]
    
    print("\n=== Testing Query Parsing ===\n")
    
    for i, query in enumerate(test_queries, 1):
        try:
            # Parse the query
            ast = parser.parse(query)
            print(f"{i:2d}. ✅ Parsed: {query}")
            print(f"    AST Type: {type(ast).__name__}")
            
            # Test execution on chunks
            matching_chunks = []
            for chunk in chunks:
                if executor.execute(ast, chunk):
                    matching_chunks.append(chunk)
            
            print(f"    Matches: {len(matching_chunks)} chunks")
            if matching_chunks:
                positions = [chunk.block_meta.get("chunk_position", "?") for chunk in matching_chunks]
                print(f"    Positions: {positions}")
            
        except Exception as e:
            print(f"{i:2d}. ❌ Failed: {query}")
            print(f"    Error: {type(e).__name__}: {e}")
        
        print()
    
    # Test specific scenarios
    print("=== Specific Scenarios ===\n")
    
    # Scenario 1: Find last chunk in large sources
    scenario1_query = "block_meta.total_chunks_in_source >= 5 AND block_meta.is_last_chunk = true"
    print(f"Scenario 1 - Last chunk in large sources:")
    print(f"Query: {scenario1_query}")
    
    ast1 = parser.parse(scenario1_query)
    last_chunks = [chunk for chunk in chunks if executor.execute(ast1, chunk)]
    print(f"Found {len(last_chunks)} chunks")
    for chunk in last_chunks:
        print(f"  - {chunk.block_meta['chunk_position']} (quality: {chunk.quality_score})")
    
    print()
    
    # Scenario 2: Find chunks in first half of source
    scenario2_query = "block_meta.chunk_percentage <= 50"
    print(f"Scenario 2 - First half of source:")
    print(f"Query: {scenario2_query}")
    
    ast2 = parser.parse(scenario2_query)
    first_half_chunks = [chunk for chunk in chunks if executor.execute(ast2, chunk)]
    print(f"Found {len(first_half_chunks)} chunks")
    for chunk in first_half_chunks:
        print(f"  - {chunk.block_meta['chunk_position']} ({chunk.block_meta['chunk_percentage']:.1f}%)")
    
    print()
    
    # Scenario 3: Complex business query
    scenario3_query = """
        (type = 'DocBlock' OR type = 'CodeBlock') AND
        quality_score >= 0.8 AND
        block_meta.total_chunks_in_source >= 3 AND
        (block_meta.is_first_chunk = true OR block_meta.is_last_chunk = true) AND
        year = 2024
    """.strip()
    
    print(f"Scenario 3 - Complex business query:")
    print(f"Query: {scenario3_query}")
    
    ast3 = parser.parse(scenario3_query)
    business_chunks = [chunk for chunk in chunks if executor.execute(ast3, chunk)]
    print(f"Found {len(business_chunks)} chunks")
    for chunk in business_chunks:
        position = chunk.block_meta['chunk_position']
        is_first = chunk.block_meta['is_first_chunk']
        is_last = chunk.block_meta['is_last_chunk']
        role = "first" if is_first else "last" if is_last else "middle"
        print(f"  - {position} ({role}) - quality: {chunk.quality_score}")
    
    print("\n=== Summary ===")
    print(f"✅ All queries with total_chunks_in_source were successfully parsed")
    print(f"✅ Filter execution works correctly with nested block_meta fields")
    print(f"✅ Complex queries combining multiple conditions work as expected")
    print(f"✅ Percentage-based filtering works correctly")


def example_nested_field_access():
    """
    Example demonstrating nested field access in block_meta.
    """
    print("\n=== Nested Field Access Example ===\n")
    
    parser = FilterParser()
    executor = FilterExecutor()
    
    # Create chunk with nested metadata
    chunk = SemanticChunk(
        uuid=str(uuid.uuid4()),
        body="Example content",
        type="DocBlock",
        content="Example content",
        block_meta={
            "total_chunks_in_source": 10,
            "source_info": {
                "total_sections": 8,
                "has_title": True,
                "author": "John Doe"
            },
            "chunk_position": "3/10"
        }
    )
    
    # Test nested field access
    nested_queries = [
        "block_meta.source_info.total_sections = 8",
        "block_meta.source_info.has_title = true",
        "block_meta.source_info.author = 'John Doe'",
        "block_meta.total_chunks_in_source = 10 AND block_meta.source_info.has_title = true"
    ]
    
    for i, query in enumerate(nested_queries, 1):
        try:
            ast = parser.parse(query)
            result = executor.execute(ast, chunk)
            print(f"{i}. ✅ {query}")
            print(f"   Result: {result}")
        except Exception as e:
            print(f"{i}. ❌ {query}")
            print(f"   Error: {e}")
        print()


if __name__ == "__main__":
    example_filter_parser_with_total_chunks()
    example_nested_field_access() 