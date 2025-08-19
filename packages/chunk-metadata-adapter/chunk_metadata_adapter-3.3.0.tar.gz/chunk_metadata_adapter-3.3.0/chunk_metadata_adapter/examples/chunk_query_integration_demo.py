"""
Demonstration of ChunkQuery integration with AST filtering system.

This example shows how to use the enhanced ChunkQuery with both simple
field filtering and complex AST-based filtering capabilities.

Features demonstrated:
- Simple field filtering (legacy compatibility)
- Complex AST-based filtering with logical expressions
- Filter validation and security checks
- Performance optimization and caching
- Integration with SemanticChunk objects
- Real-world filtering scenarios

Author: Development Team
Created: 2024-01-20
"""

from chunk_metadata_adapter import (
    ChunkQuery, SemanticChunk, ChunkType, ChunkStatus, LanguageEnum
)
from chunk_metadata_adapter.ast import ASTNode, LogicalOperator, FieldCondition


def demo_simple_field_filtering():
    """Demonstrate simple field-based filtering."""
    print("=== Simple Field Filtering Demo ===")
    
    # Create sample chunk data
    chunk_data = {
        "type": "DocBlock",
        "quality_score": 0.85,
        "tags": ["ai", "python", "machine-learning"],
        "year": 2023,
        "is_public": True,
        "is_deleted": False,
        "language": "en",
        "title": "Python Machine Learning Guide"
    }
    
    # Simple exact match
    query1 = ChunkQuery(type="DocBlock")
    matches1 = query1.matches(chunk_data)
    print(f"Query: type='DocBlock' -> Matches: {matches1}")
    
    # Numeric comparison
    query2 = ChunkQuery(quality_score=">=0.8")
    matches2 = query2.matches(chunk_data)
    print(f"Query: quality_score>='0.8' -> Matches: {matches2}")
    
    # List field matching
    query3 = ChunkQuery(tags=["ai", "ml"])
    matches3 = query3.matches(chunk_data)
    print(f"Query: tags=['ai', 'ml'] -> Matches: {matches3}")
    
    # Boolean field
    query4 = ChunkQuery(is_public=True)
    matches4 = query4.matches(chunk_data)
    print(f"Query: is_public=True -> Matches: {matches4}")
    
    # Non-matching query
    query5 = ChunkQuery(type="CodeBlock")
    matches5 = query5.matches(chunk_data)
    print(f"Query: type='CodeBlock' -> Matches: {matches5}")
    
    print()


def demo_ast_based_filtering():
    """Demonstrate AST-based complex filtering."""
    print("=== AST-Based Filtering Demo ===")
    
    # Create sample chunk data
    chunk_data = {
        "type": "DocBlock",
        "quality_score": 0.85,
        "tags": ["ai", "python", "machine-learning"],
        "year": 2023,
        "is_public": True,
        "is_deleted": False,
        "language": "en",
        "title": "Python Machine Learning Guide",
        "feedback_accepted": 5,
        "used_in_generation": True
    }
    
    # Simple AND condition
    query1 = ChunkQuery(filter_expr="type = 'DocBlock' AND quality_score >= 0.8")
    matches1 = query1.matches(chunk_data)
    print(f"Query: type='DocBlock' AND quality_score>=0.8 -> Matches: {matches1}")
    
    # OR condition
    query2 = ChunkQuery(filter_expr="type = 'DocBlock' OR type = 'CodeBlock'")
    matches2 = query2.matches(chunk_data)
    print(f"Query: type='DocBlock' OR type='CodeBlock' -> Matches: {matches2}")
    
    # Complex logical expression
    query3 = ChunkQuery(filter_expr="""
        (type = 'DocBlock' OR type = 'CodeBlock') AND
        quality_score >= 0.7 AND
        tags intersects ['ai', 'ml'] AND
        year >= 2020 AND
        NOT is_deleted
    """)
    matches3 = query3.matches(chunk_data)
    print(f"Query: Complex expression -> Matches: {matches3}")
    
    # String pattern matching
    query4 = ChunkQuery(filter_expr="title like 'Python' AND language = 'en'")
    matches4 = query4.matches(chunk_data)
    print(f"Query: title like 'Python' AND language='en' -> Matches: {matches4}")
    
    # Nested conditions with parentheses
    query5 = ChunkQuery(filter_expr="""
        (quality_score >= 0.8 OR feedback_accepted >= 5) AND
        (is_public = true OR used_in_generation = true) AND
        NOT is_deleted
    """)
    matches5 = query5.matches(chunk_data)
    print(f"Query: Nested conditions -> Matches: {matches5}")
    
    print()


def demo_filter_validation():
    """Demonstrate filter validation and security checks."""
    print("=== Filter Validation Demo ===")
    
    # Valid filter
    query1 = ChunkQuery(filter_expr="type = 'DocBlock' AND quality_score >= 0.8")
    validation1 = query1.validate()
    print(f"Valid filter: {validation1.is_valid}")
    print(f"Errors: {validation1.errors}")
    print(f"Warnings: {validation1.warnings}")
    
    # Invalid filter (syntax error)
    query2 = ChunkQuery(filter_expr="type = 'DocBlock' AND")
    validation2 = query2.validate()
    print(f"\nInvalid filter: {validation2.is_valid}")
    print(f"Errors: {validation2.errors}")
    
    # Potentially dangerous filter
    query3 = ChunkQuery(filter_expr="__import__('os').system('rm -rf /')")
    validation3 = query3.validate()
    print(f"\nDangerous filter: {validation3.is_valid}")
    print(f"Errors: {validation3.errors}")
    
    print()


def demo_ast_parsing_and_caching():
    """Demonstrate AST parsing and caching."""
    print("=== AST Parsing and Caching Demo ===")
    
    # Create query with complex expression
    query = ChunkQuery(filter_expr="""
        (type = 'DocBlock' OR type = 'CodeBlock') AND
        quality_score >= 0.7 AND
        tags intersects ['ai', 'ml'] AND
        year >= 2020 AND
        NOT is_deleted
    """)
    
    # Get AST (first time - parses)
    print("Getting AST (first time)...")
    ast1 = query.get_ast()
    print(f"AST type: {type(ast1).__name__}")
    print(f"AST operator: {ast1.operator if hasattr(ast1, 'operator') else 'N/A'}")
    
    # Get AST again (cached)
    print("\nGetting AST (second time - cached)...")
    ast2 = query.get_ast()
    print(f"AST type: {type(ast2).__name__}")
    print(f"Same AST object: {ast1 is ast2}")
    
    # Check cache stats
    stats = query.get_cache_stats()
    print(f"\nCache stats: {stats}")
    
    # Clear cache
    print("\nClearing cache...")
    query.clear_cache()
    ast3 = query.get_ast()
    print(f"New AST object: {ast1 is ast3}")
    
    print()


def demo_semantic_chunk_integration():
    """Demonstrate integration with SemanticChunk objects."""
    print("=== SemanticChunk Integration Demo ===")
    
    # Create SemanticChunk object
    chunk = SemanticChunk(
        uuid="ebc534d7-a682-4ff3-b370-acdda910422c",
        type=ChunkType.DOC_BLOCK,
        body="Sample content for testing",
        quality_score=0.85,
        tags=["ai", "python", "machine-learning"],
        year=2023,
        is_public=True,
        is_deleted=False,
        language=LanguageEnum.EN,
        title="Python Machine Learning Guide",
        category="programming"
    )
    
    # Simple field filtering with SemanticChunk
    query1 = ChunkQuery(type="DocBlock", quality_score=">=0.8")
    matches1 = query1.matches(chunk)
    print(f"Simple query with SemanticChunk: {matches1}")
    
    # AST-based filtering with SemanticChunk
    query2 = ChunkQuery(filter_expr="""
        type = 'DocBlock' AND
        quality_score >= 0.8 AND
        tags intersects ['ai', 'ml'] AND
        language = 'en'
    """)
    matches2 = query2.matches(chunk)
    print(f"AST query with SemanticChunk: {matches2}")
    
    print()


def demo_real_world_scenarios():
    """Demonstrate real-world filtering scenarios."""
    print("=== Real-World Scenarios Demo ===")
    
    # Sample chunks for different scenarios
    chunks = [
        {
            "type": "DocBlock",
            "quality_score": 0.9,
            "tags": ["documentation", "guide"],
            "year": 2023,
            "is_public": True,
            "is_deleted": False,
            "feedback_accepted": 10,
            "used_in_generation": True
        },
        {
            "type": "CodeBlock",
            "quality_score": 0.7,
            "tags": ["python", "ai"],
            "year": 2022,
            "is_public": False,
            "is_deleted": False,
            "feedback_accepted": 3,
            "used_in_generation": False
        },
        {
            "type": "DocBlock",
            "quality_score": 0.6,
            "tags": ["tutorial", "example"],
            "year": 2021,
            "is_public": True,
            "is_deleted": True,
            "feedback_accepted": 1,
            "used_in_generation": False
        }
    ]
    
    # Scenario 1: Content Management - Find high-quality public documentation
    print("Scenario 1: Content Management")
    query1 = ChunkQuery(filter_expr="""
        type = 'DocBlock' AND
        quality_score >= 0.8 AND
        is_public = true AND
        NOT is_deleted AND
        (tags intersects ['documentation', 'guide'] OR 
         tags intersects ['tutorial', 'example'])
    """)
    
    matches1 = [query1.matches(chunk) for chunk in chunks]
    print(f"High-quality public docs: {sum(matches1)} matches")
    
    # Scenario 2: Analytics - Find chunks used in generation with good feedback
    print("\nScenario 2: Analytics")
    query2 = ChunkQuery(filter_expr="""
        used_in_generation = true AND
        feedback_accepted >= 5 AND
        quality_score >= 0.7
    """)
    
    matches2 = [query2.matches(chunk) for chunk in chunks]
    print(f"Used in generation with good feedback: {sum(matches2)} matches")
    
    # Scenario 3: Search and Discovery - Find recent AI/ML content
    print("\nScenario 3: Search and Discovery")
    query3 = ChunkQuery(filter_expr="""
        (title like 'AI' OR title like 'ML' OR 
         tags intersects ['ai', 'ml', 'machine-learning']) AND
        year >= 2022 AND
        is_public = true AND
        NOT is_deleted
    """)
    
    matches3 = [query3.matches(chunk) for chunk in chunks]
    print(f"Recent AI/ML content: {sum(matches3)} matches")
    
    print()


def main():
    """Run all demonstrations."""
    print("ChunkQuery AST Integration Demo")
    print("=" * 50)
    
    demo_simple_field_filtering()
    demo_ast_based_filtering()
    demo_filter_validation()
    demo_ast_parsing_and_caching()
    demo_semantic_chunk_integration()
    demo_real_world_scenarios()
    
    print("Demo completed successfully!")


if __name__ == "__main__":
    main() 