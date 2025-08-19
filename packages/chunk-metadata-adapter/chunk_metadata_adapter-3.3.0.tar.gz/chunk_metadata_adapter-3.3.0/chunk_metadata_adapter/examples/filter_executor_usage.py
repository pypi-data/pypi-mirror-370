"""
Example usage of FilterExecutor.

This example demonstrates how to use the FilterExecutor class to evaluate
filter expressions against different types of data.

Author: Development Team
Created: 2024-01-20
Updated: 2024-01-20
"""

from chunk_metadata_adapter.filter_executor import FilterExecutor
from chunk_metadata_adapter.ast import (
    FieldCondition, LogicalOperator, ParenExpression, TypedValue,
    ASTNodeFactory
)


def basic_usage_example():
    """Basic usage example with simple conditions."""
    print("=== Basic Usage Example ===")
    
    # Create executor
    executor = FilterExecutor()
    
    # Simple field condition
    condition = FieldCondition("age", ">", TypedValue("int", 18))
    
    # Test data
    data1 = {"age": 25, "name": "John"}
    data2 = {"age": 15, "name": "Jane"}
    
    # Execute filter
    result1 = executor.execute(condition, data1)
    result2 = executor.execute(condition, data2)
    
    print(f"Data: {data1} -> Result: {result1}")  # True
    print(f"Data: {data2} -> Result: {result2}")  # False
    print()


def logical_operations_example():
    """Example with logical operations (AND, OR, NOT)."""
    print("=== Logical Operations Example ===")
    
    executor = FilterExecutor()
    
    # Create conditions
    age_condition = FieldCondition("age", ">=", TypedValue("int", 18))
    status_condition = FieldCondition("status", "=", TypedValue("str", "active"))
    vip_condition = FieldCondition("vip", "=", TypedValue("bool", True))
    
    # AND operation
    and_condition = LogicalOperator("AND", [age_condition, status_condition])
    
    # OR operation
    or_condition = LogicalOperator("OR", [age_condition, vip_condition])
    
    # Test data
    data1 = {"age": 25, "status": "active", "vip": False}
    data2 = {"age": 15, "status": "inactive", "vip": True}
    data3 = {"age": 15, "status": "inactive", "vip": False}
    
    # Execute AND filter
    print("AND condition (age >= 18 AND status = 'active'):")
    print(f"Data: {data1} -> Result: {executor.execute(and_condition, data1)}")  # True
    print(f"Data: {data2} -> Result: {executor.execute(and_condition, data2)}")  # False
    print(f"Data: {data3} -> Result: {executor.execute(and_condition, data3)}")  # False
    
    # Execute OR filter
    print("\nOR condition (age >= 18 OR vip = true):")
    print(f"Data: {data1} -> Result: {executor.execute(or_condition, data1)}")  # True
    print(f"Data: {data2} -> Result: {executor.execute(or_condition, data2)}")  # True
    print(f"Data: {data3} -> Result: {executor.execute(or_condition, data3)}")  # False
    print()


def nested_fields_example():
    """Example with nested field access."""
    print("=== Nested Fields Example ===")
    
    executor = FilterExecutor()
    
    # Nested field condition
    condition = FieldCondition("user.profile.age", ">", TypedValue("int", 18))
    
    # Test data with nested structure
    data1 = {
        "user": {
            "profile": {
                "age": 25,
                "name": "John"
            }
        }
    }
    
    data2 = {
        "user": {
            "profile": {
                "age": 15,
                "name": "Jane"
            }
        }
    }
    
    data3 = {
        "user": {
            "age": 25  # Missing profile level
        }
    }
    
    # Execute filter
    print("Nested field condition (user.profile.age > 18):")
    print(f"Data: {data1} -> Result: {executor.execute(condition, data1)}")  # True
    print(f"Data: {data2} -> Result: {executor.execute(condition, data2)}")  # False
    print(f"Data: {data3} -> Result: {executor.execute(condition, data3)}")  # False
    print()


def list_operations_example():
    """Example with list operations."""
    print("=== List Operations Example ===")
    
    executor = FilterExecutor()
    
    # List operations
    in_condition = FieldCondition("tag", "in", TypedValue("list", ["python", "ai", "ml"]))
    intersects_condition = FieldCondition("tags", "intersects", TypedValue("list", ["python", "ai"]))
    
    # Test data
    data1 = {"tag": "python", "tags": ["python", "data-science"]}
    data2 = {"tag": "java", "tags": ["java", "backend"]}
    data3 = {"tag": "ai", "tags": ["ai", "ml", "python"]}
    
    # Execute in filter
    print("IN condition (tag in ['python', 'ai', 'ml']):")
    print(f"Data: {data1} -> Result: {executor.execute(in_condition, data1)}")  # True
    print(f"Data: {data2} -> Result: {executor.execute(in_condition, data2)}")  # False
    print(f"Data: {data3} -> Result: {executor.execute(in_condition, data3)}")  # True
    
    # Execute intersects filter
    print("\nINTERSECTS condition (tags intersects ['python', 'ai']):")
    print(f"Data: {data1} -> Result: {executor.execute(intersects_condition, data1)}")  # True
    print(f"Data: {data2} -> Result: {executor.execute(intersects_condition, data2)}")  # False
    print(f"Data: {data3} -> Result: {executor.execute(intersects_condition, data3)}")  # True
    print()


def string_operations_example():
    """Example with string operations including regex."""
    print("=== String Operations Example ===")
    
    executor = FilterExecutor()
    
    # String operations
    like_condition = FieldCondition("email", "like", TypedValue("str", r".*@.*\.com"))
    regex_condition = FieldCondition("text", "~", TypedValue("str", r"hello.*world"))
    
    # Test data
    data1 = {"email": "test@example.com", "text": "hello beautiful world"}
    data2 = {"email": "invalid-email", "text": "goodbye world"}
    data3 = {"email": "user@domain.org", "text": "hello python world"}
    
    # Execute like filter
    print("LIKE condition (email like '.*@.*\\.com'):")
    print(f"Data: {data1} -> Result: {executor.execute(like_condition, data1)}")  # True
    print(f"Data: {data2} -> Result: {executor.execute(like_condition, data2)}")  # False
    print(f"Data: {data3} -> Result: {executor.execute(like_condition, data3)}")  # False
    
    # Execute regex filter
    print("\nREGEX condition (text ~ 'hello.*world'):")
    print(f"Data: {data1} -> Result: {executor.execute(regex_condition, data1)}")  # True
    print(f"Data: {data2} -> Result: {executor.execute(regex_condition, data2)}")  # False
    print(f"Data: {data3} -> Result: {executor.execute(regex_condition, data3)}")  # True
    print()


def complex_expression_example():
    """Example with complex logical expressions."""
    print("=== Complex Expression Example ===")
    
    executor = FilterExecutor()
    
    # Create complex expression: (age >= 18 AND status = 'active') OR (vip = true AND tags intersects ['premium'])
    age_condition = FieldCondition("age", ">=", TypedValue("int", 18))
    status_condition = FieldCondition("status", "=", TypedValue("str", "active"))
    vip_condition = FieldCondition("vip", "=", TypedValue("bool", True))
    tags_condition = FieldCondition("tags", "intersects", TypedValue("list", ["premium"]))
    
    # Build complex expression
    and_group1 = LogicalOperator("AND", [age_condition, status_condition])
    and_group2 = LogicalOperator("AND", [vip_condition, tags_condition])
    complex_condition = LogicalOperator("OR", [and_group1, and_group2])
    
    # Test data
    data1 = {"age": 25, "status": "active", "vip": False, "tags": ["basic"]}
    data2 = {"age": 15, "status": "inactive", "vip": True, "tags": ["premium"]}
    data3 = {"age": 15, "status": "inactive", "vip": False, "tags": ["basic"]}
    
    # Execute complex filter
    print("Complex condition: (age >= 18 AND status = 'active') OR (vip = true AND tags intersects ['premium'])")
    print(f"Data: {data1} -> Result: {executor.execute(complex_condition, data1)}")  # True (first group)
    print(f"Data: {data2} -> Result: {executor.execute(complex_condition, data2)}")  # True (second group)
    print(f"Data: {data3} -> Result: {executor.execute(complex_condition, data3)}")  # False (neither group)
    print()


def semantic_chunk_example():
    """Example with SemanticChunk objects."""
    print("=== SemanticChunk Example ===")
    
    try:
        from chunk_metadata_adapter.semantic_chunk import SemanticChunk
        
        executor = FilterExecutor()
        
        # Create test chunks
        chunk1 = SemanticChunk(
            type="DocBlock",
            body="Python tutorial content",
            quality_score=0.8,
            tags=["python", "tutorial"],
            year=2024,
            is_public=True
        )
        
        chunk2 = SemanticChunk(
            type="CodeBlock",
            body="def hello(): print('world')",
            quality_score=0.6,
            tags=["python", "code"],
            year=2023,
            is_public=False
        )
        
        # Create filter for high-quality public Python content
        type_condition = FieldCondition("type", "=", TypedValue("str", "DocBlock"))
        quality_condition = FieldCondition("quality_score", ">=", TypedValue("float", 0.7))
        tags_condition = FieldCondition("tags", "intersects", TypedValue("list", ["python"]))
        public_condition = FieldCondition("is_public", "=", TypedValue("bool", True))
        
        filter_condition = LogicalOperator("AND", [
            type_condition, quality_condition, tags_condition, public_condition
        ])
        
        # Execute filter
        print("Filter: type = 'DocBlock' AND quality_score >= 0.7 AND tags intersects ['python'] AND is_public = true")
        print(f"Chunk 1: {chunk1.type}, quality={chunk1.quality_score}, tags={chunk1.tags}, public={chunk1.is_public}")
        print(f"Result: {executor.execute(filter_condition, chunk1)}")  # True
        
        print(f"Chunk 2: {chunk2.type}, quality={chunk2.quality_score}, tags={chunk2.tags}, public={chunk2.is_public}")
        print(f"Result: {executor.execute(filter_condition, chunk2)}")  # False
        print()
        
    except ImportError:
        print("SemanticChunk not available, skipping this example")
        print()


def performance_example():
    """Example demonstrating performance features."""
    print("=== Performance Example ===")
    
    executor = FilterExecutor()
    
    # Create a condition that will be executed multiple times
    condition = FieldCondition("deeply.nested.field", "=", TypedValue("str", "value"))
    
    # Create data with deep nesting
    data = {}
    current = data
    for i in range(10):
        current[f"level_{i}"] = {}
        current = current[f"level_{i}"]
    current["field"] = "value"
    
    # Execute multiple times to demonstrate caching
    print("Executing same condition multiple times to demonstrate caching:")
    
    # First execution
    result1 = executor.execute(condition, data)
    stats1 = executor.get_cache_stats()
    print(f"First execution: {result1}, Cache stats: {stats1}")
    
    # Second execution (should use cache)
    result2 = executor.execute(condition, data)
    stats2 = executor.get_cache_stats()
    print(f"Second execution: {result2}, Cache stats: {stats2}")
    
    # Clear cache
    executor.clear_cache()
    stats3 = executor.get_cache_stats()
    print(f"After clearing cache: {stats3}")
    print()


def main():
    """Run all examples."""
    print("FilterExecutor Usage Examples")
    print("=" * 50)
    print()
    
    basic_usage_example()
    logical_operations_example()
    nested_fields_example()
    list_operations_example()
    string_operations_example()
    complex_expression_example()
    semantic_chunk_example()
    performance_example()
    
    print("All examples completed successfully!")


if __name__ == "__main__":
    main() 