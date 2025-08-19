"""
AST Parameterization Demo for Query Caching.

This example demonstrates how to use AST parameterization for efficient
query caching, allowing reuse of compiled query structures with different
parameter values.

Key features demonstrated:
- Converting concrete AST to parameterized template
- Caching parameterized templates for reuse
- Instantiating templates with different parameter values
- Performance benefits of template caching
- Cache statistics and management

Usage:
    python -m chunk_metadata_adapter.examples.ast_parameterization_demo

Author: Development Team
Created: 2024-01-20
"""

import time
from chunk_metadata_adapter.ast import (
    FieldCondition, LogicalOperator, TypedValue,
    ASTParameterizer, ASTInstantiator, QueryCache
)
from chunk_metadata_adapter.filter_parser import FilterParser


def demo_basic_parameterization():
    """Demonstrate basic AST parameterization."""
    print("=== Basic AST Parameterization ===")
    
    # Create a simple AST
    condition1 = FieldCondition("age", ">", TypedValue("int", 18))
    condition2 = FieldCondition("status", "=", TypedValue("str", "active"))
    ast = LogicalOperator("AND", [condition1, condition2])
    
    print(f"Original AST: {ast}")
    
    # Parameterize the AST
    parameterizer = ASTParameterizer()
    template = parameterizer.parameterize(ast)
    
    print(f"Parameterized template hash: {template.template_hash}")
    print(f"Number of parameters: {template.get_parameter_count()}")
    print(f"Parameter types: {template.get_parameter_types()}")
    print(f"Parameterized AST: {template.ast}")
    
    # Instantiate with different values
    instantiator = ASTInstantiator()
    
    # First instantiation
    params1 = {"param_0": 25, "param_1": "verified"}
    ast1 = instantiator.instantiate(template, params1)
    print(f"Instantiated AST 1: {ast1}")
    
    # Second instantiation with different values
    params2 = {"param_0": 30, "param_1": "pending"}
    ast2 = instantiator.instantiate(template, params2)
    print(f"Instantiated AST 2: {ast2}")
    
    print()


def demo_query_caching():
    """Demonstrate query caching with parameterization."""
    print("=== Query Caching with Parameterization ===")
    
    # Create cache
    cache = QueryCache(max_size=100)
    
    # Sample queries with similar structure but different values
    queries = [
        "age > 18 AND status = 'active'",
        "age > 25 AND status = 'verified'", 
        "age > 30 AND status = 'pending'",
        "age > 21 AND status = 'active'",
        "age > 35 AND status = 'verified'"
    ]
    
    parser = FilterParser()
    parameterizer = ASTParameterizer()
    instantiator = ASTInstantiator()
    
    print("Processing queries with caching:")
    
    for i, query in enumerate(queries, 1):
        print(f"\nQuery {i}: {query}")
        
        # Parse query
        ast = parser.parse(query)
        
        # Get or create template from cache
        start_time = time.time()
        template = cache.get_or_create(ast, parameterizer)
        cache_time = time.time() - start_time
        
        print(f"  Template hash: {template.template_hash}")
        print(f"  Cache time: {cache_time:.6f}s")
        print(f"  Parameters: {template.get_parameter_types()}")
        
        # Extract actual values from original query for demonstration
        if "age > 18" in query:
            age_value = 18
        elif "age > 25" in query:
            age_value = 25
        elif "age > 30" in query:
            age_value = 30
        elif "age > 21" in query:
            age_value = 21
        else:
            age_value = 35
            
        if "status = 'active'" in query:
            status_value = "active"
        elif "status = 'verified'" in query:
            status_value = "verified"
        else:
            status_value = "pending"
        
        # Instantiate with extracted values
        params = {"param_0": age_value, "param_1": status_value}
        instantiated_ast = instantiator.instantiate(template, params)
        print(f"  Instantiated: {instantiated_ast}")
    
    # Show cache statistics
    stats = cache.get_stats()
    print(f"\nCache Statistics:")
    print(f"  Hits: {stats['hits']}")
    print(f"  Misses: {stats['misses']}")
    print(f"  Evictions: {stats['evictions']}")
    print(f"  Cache size: {stats['size']}/{stats['max_size']}")
    print(f"  Hit rate: {stats['hits'] / (stats['hits'] + stats['misses']) * 100:.1f}%")
    
    print()


def demo_complex_queries():
    """Demonstrate parameterization with complex queries."""
    print("=== Complex Query Parameterization ===")
    
    # Complex query with multiple conditions
    complex_query = """
        (age > 18 AND status = 'active') OR 
        (vip = true AND quality_score >= 0.8) AND 
        NOT is_deleted
    """
    
    parser = FilterParser()
    parameterizer = ASTParameterizer()
    
    # Parse and parameterize
    ast = parser.parse(complex_query)
    template = parameterizer.parameterize(ast)
    
    print(f"Complex query: {complex_query.strip()}")
    print(f"Template hash: {template.template_hash}")
    print(f"Number of parameters: {template.get_parameter_count()}")
    print(f"Parameter types: {template.get_parameter_types()}")
    
    # Instantiate with different scenarios
    instantiator = ASTInstantiator()
    
    scenarios = [
        {
            "name": "Regular user",
            "params": {"param_0": 25, "param_1": "active", "param_2": True, "param_3": 0.9, "param_4": False}
        },
        {
            "name": "VIP user", 
            "params": {"param_0": 35, "param_1": "pending", "param_2": True, "param_3": 0.95, "param_4": False}
        },
        {
            "name": "Deleted user",
            "params": {"param_0": 20, "param_1": "active", "param_2": False, "param_3": 0.7, "param_4": True}
        }
    ]
    
    for scenario in scenarios:
        print(f"\nScenario: {scenario['name']}")
        instantiated_ast = instantiator.instantiate(template, scenario['params'])
        print(f"  Instantiated AST: {instantiated_ast}")
    
    print()


def demo_performance_comparison():
    """Compare performance with and without caching."""
    print("=== Performance Comparison ===")
    
    # Create similar queries
    base_query = "age > {age} AND status = '{status}' AND quality_score >= {score}"
    age_values = [18, 25, 30, 35, 40, 45, 50, 55, 60]
    status_values = ["active", "verified", "pending", "suspended"]
    score_values = [0.5, 0.6, 0.7, 0.8, 0.9]
    
    parser = FilterParser()
    cache = QueryCache(max_size=1000)
    parameterizer = ASTParameterizer()
    instantiator = ASTInstantiator()
    
    # Test without caching
    print("Testing without caching:")
    start_time = time.time()
    
    for age in age_values[:5]:  # Test with first 5 age values
        for status in status_values[:3]:  # Test with first 3 status values
            for score in score_values[:3]:  # Test with first 3 score values
                query = base_query.format(age=age, status=status, score=score)
                ast = parser.parse(query)
    
    no_cache_time = time.time() - start_time
    print(f"  Time without caching: {no_cache_time:.6f}s")
    
    # Test with caching
    print("Testing with caching:")
    start_time = time.time()
    
    for age in age_values[:5]:
        for status in status_values[:3]:
            for score in score_values[:3]:
                query = base_query.format(age=age, status=status, score=score)
                ast = parser.parse(query)
                template = cache.get_or_create(ast, parameterizer)
                params = {"param_0": age, "param_1": status, "param_2": score}
                instantiated_ast = instantiator.instantiate(template, params)
    
    cache_time = time.time() - start_time
    print(f"  Time with caching: {cache_time:.6f}s")
    
    # Calculate improvement
    improvement = (no_cache_time - cache_time) / no_cache_time * 100
    print(f"  Performance improvement: {improvement:.1f}%")
    
    # Show cache statistics
    stats = cache.get_stats()
    print(f"  Cache hits: {stats['hits']}")
    print(f"  Cache misses: {stats['misses']}")
    print(f"  Hit rate: {stats['hits'] / (stats['hits'] + stats['misses']) * 100:.1f}%")
    
    print()


def demo_error_handling():
    """Demonstrate error handling in parameterization."""
    print("=== Error Handling ===")
    
    # Create a template
    condition = FieldCondition("age", ">", TypedValue("int", 18))
    template = ASTParameterizer().parameterize(condition)
    instantiator = ASTInstantiator()
    
    print("Testing parameter validation:")
    
    # Test missing parameter
    try:
        instantiator.instantiate(template, {})
        print("  ❌ Should have raised error for missing parameter")
    except ValueError as e:
        print(f"  ✅ Correctly caught missing parameter: {e}")
    
    # Test wrong parameter type
    try:
        instantiator.instantiate(template, {"param_0": "not_a_number"})
        print("  ❌ Should have raised error for wrong type")
    except ValueError as e:
        print(f"  ✅ Correctly caught wrong type: {e}")
    
    # Test extra parameter
    try:
        instantiator.instantiate(template, {"param_0": 25, "extra_param": "value"})
        print("  ❌ Should have raised error for extra parameter")
    except ValueError as e:
        print(f"  ✅ Correctly caught extra parameter: {e}")
    
    # Test valid instantiation
    try:
        result = instantiator.instantiate(template, {"param_0": 25})
        print(f"  ✅ Valid instantiation: {result}")
    except Exception as e:
        print(f"  ❌ Unexpected error: {e}")
    
    print()


def main():
    """Run all parameterization demos."""
    print("AST Parameterization Demo")
    print("=" * 50)
    
    demo_basic_parameterization()
    demo_query_caching()
    demo_complex_queries()
    demo_performance_comparison()
    demo_error_handling()
    
    print("Demo completed successfully!")


if __name__ == "__main__":
    main() 