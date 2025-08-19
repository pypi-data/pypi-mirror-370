"""
Metrics Demo for chunk_metadata_adapter.

This example demonstrates all available metrics and statistics
that can be exported to Prometheus for monitoring.

Available metrics:
- Cache statistics (hits, misses, evictions, hit rates)
- Performance metrics (execution times, throughput)
- Complexity metrics (AST depth, condition counts)
- Error metrics (validation errors, execution errors)
- Resource usage metrics (memory, cache sizes)
- Business metrics (field usage, operator usage)

Usage:
    python -m chunk_metadata_adapter.examples.metrics_demo

Author: Development Team
Created: 2024-01-20
"""

import time
import json
from typing import Dict, Any, List

from chunk_metadata_adapter import (
    ChunkQuery, SemanticChunk, ChunkType, ChunkStatus, LanguageEnum
)
from chunk_metadata_adapter.ast import (
    FieldCondition, LogicalOperator, TypedValue,
    ASTParameterizer, ASTInstantiator, QueryCache
)
from chunk_metadata_adapter.filter_parser import FilterParser
from chunk_metadata_adapter.filter_executor import FilterExecutor
from chunk_metadata_adapter.query_validator import QueryValidator
from chunk_metadata_adapter.ast_optimizer import ASTOptimizer
from chunk_metadata_adapter.performance_analyzer import PerformanceAnalyzer
from chunk_metadata_adapter.complexity_analyzer import analyze_complexity


def demo_cache_metrics():
    """Demonstrate cache-related metrics."""
    print("=== Cache Metrics Demo ===")
    
    # QueryCache metrics
    print("\n1. QueryCache (AST Parameterization) Metrics:")
    cache = QueryCache(max_size=100)
    
    # Create some queries to populate cache
    queries = [
        "age > 18 AND status = 'active'",
        "age > 25 AND status = 'verified'",
        "age > 30 AND status = 'pending'",
        "age > 18 AND status = 'active'",  # Duplicate for cache hit
        "age > 25 AND status = 'verified'"  # Duplicate for cache hit
    ]
    
    parser = FilterParser()
    parameterizer = ASTParameterizer()
    
    for query in queries:
        ast = parser.parse(query)
        cache.get_or_create(ast, parameterizer)
    
    cache_stats = cache.get_stats()
    print(f"  Cache hits: {cache_stats['hits']}")
    print(f"  Cache misses: {cache_stats['misses']}")
    print(f"  Cache evictions: {cache_stats['evictions']}")
    print(f"  Cache size: {cache_stats['size']}")
    print(f"  Cache max size: {cache_stats['max_size']}")
    print(f"  Hit rate: {cache_stats['hits'] / (cache_stats['hits'] + cache_stats['misses']) * 100:.1f}%")
    
    # FilterExecutor cache metrics
    print("\n2. FilterExecutor Cache Metrics:")
    executor = FilterExecutor()
    
    # Execute some filters to populate cache
    condition = FieldCondition("deeply.nested.field", "=", TypedValue("str", "value"))
    data = {"deeply": {"nested": {"field": "value"}}}
    
    for _ in range(5):
        executor.execute(condition, data)
    
    executor_stats = executor.get_cache_stats()
    print(f"  Field cache size: {executor_stats['field_cache_size']}")
    print(f"  Comparison cache size: {executor_stats['comparison_cache_size']}")
    
    # ChunkQuery cache metrics
    print("\n3. ChunkQuery Cache Metrics:")
    query = ChunkQuery(filter_expr="type = 'DocBlock' AND quality_score >= 0.8")
    
    # Get AST to initialize cache
    ast = query.get_ast()
    
    query_stats = query.get_cache_stats()
    print(f"  AST cached: {query_stats['ast_cached']}")
    print(f"  Validation cached: {query_stats['validation_cached']}")
    print(f"  Parser initialized: {query_stats['parser_initialized']}")
    print(f"  Executor initialized: {query_stats['executor_initialized']}")
    print(f"  Validator initialized: {query_stats['validator_initialized']}")
    print(f"  Optimizer initialized: {query_stats['optimizer_initialized']}")


def demo_performance_metrics():
    """Demonstrate performance-related metrics."""
    print("\n=== Performance Metrics Demo ===")
    
    # Query parsing performance
    print("\n1. Query Parsing Performance:")
    parser = FilterParser()
    
    queries = [
        "age > 18",
        "type = 'DocBlock' AND quality_score >= 0.8",
        "(type = 'DocBlock' OR type = 'CodeBlock') AND quality_score >= 0.7 AND tags intersects ['ai', 'ml']"
    ]
    
    parse_times = []
    for query in queries:
        start_time = time.time()
        ast = parser.parse(query)
        parse_time = time.time() - start_time
        parse_times.append(parse_time)
        print(f"  Query: '{query[:30]}...' -> {parse_time:.6f}s")
    
    avg_parse_time = sum(parse_times) / len(parse_times)
    print(f"  Average parse time: {avg_parse_time:.6f}s")
    
    # Filter execution performance
    print("\n2. Filter Execution Performance:")
    executor = FilterExecutor()
    
    # Create test data
    test_data = {
        "type": "DocBlock",
        "quality_score": 0.85,
        "tags": ["ai", "python", "machine-learning"],
        "year": 2023,
        "is_public": True
    }
    
    # Test different filter complexities
    filters = [
        FieldCondition("type", "=", TypedValue("str", "DocBlock")),
        LogicalOperator("AND", [
            FieldCondition("type", "=", TypedValue("str", "DocBlock")),
            FieldCondition("quality_score", ">=", TypedValue("float", 0.8))
        ]),
        LogicalOperator("AND", [
            FieldCondition("type", "=", TypedValue("str", "DocBlock")),
            FieldCondition("quality_score", ">=", TypedValue("float", 0.8)),
            FieldCondition("tags", "intersects", TypedValue("list", ["ai", "ml"]))
        ])
    ]
    
    execution_times = []
    for i, filter_ast in enumerate(filters, 1):
        start_time = time.time()
        result = executor.execute(filter_ast, test_data)
        exec_time = time.time() - start_time
        execution_times.append(exec_time)
        print(f"  Filter {i} complexity: {exec_time:.6f}s -> Result: {result}")
    
    avg_exec_time = sum(execution_times) / len(execution_times)
    print(f"  Average execution time: {avg_exec_time:.6f}s")


def demo_complexity_metrics():
    """Demonstrate complexity-related metrics."""
    print("\n=== Complexity Metrics Demo ===")
    
    # AST complexity analysis
    print("\n1. AST Complexity Analysis:")
    
    complex_queries = [
        "age > 18",
        "type = 'DocBlock' AND quality_score >= 0.8",
        "(type = 'DocBlock' OR type = 'CodeBlock') AND quality_score >= 0.7",
        "(type = 'DocBlock' AND quality_score >= 0.8) OR (type = 'CodeBlock' AND language = 'python')"
    ]
    
    parser = FilterParser()
    
    for i, query in enumerate(complex_queries, 1):
        ast = parser.parse(query)
        complexity = analyze_complexity(ast)
        
        print(f"  Query {i}:")
        print(f"    Max depth: {complexity.get('max_depth', 0)}")
        print(f"    Total conditions: {complexity.get('total_conditions', 0)}")
        print(f"    Operator distribution: {complexity.get('operator_distribution', {})}")
        print(f"    Field distribution: {complexity.get('field_distribution', {})}")
    
    # Performance analysis
    print("\n2. Performance Analysis:")
    analyzer = PerformanceAnalyzer()
    
    for i, query in enumerate(complex_queries, 1):
        ast = parser.parse(query)
        analysis = analyzer.analyze(query, ast)
        
        print(f"  Query {i} analysis:")
        print(f"    Estimated complexity: {analysis['details']['estimated_complexity']}")
        print(f"    Warnings: {len(analysis['warnings'])}")
        print(f"    Potential issues: {len(analysis['details']['potential_issues'])}")
        print(f"    Optimization suggestions: {len(analysis['details']['optimization_suggestions'])}")


def demo_error_metrics():
    """Demonstrate error-related metrics."""
    print("\n=== Error Metrics Demo ===")
    
    # Validation errors
    print("\n1. Validation Error Metrics:")
    validator = QueryValidator()
    
    test_queries = [
        "type = 'DocBlock' AND quality_score >= 0.8",  # Valid
        "type = 'DocBlock' AND",  # Invalid - incomplete
        "__import__('os').system('rm -rf /')",  # Dangerous
        "age > 18 AND status = 'active' AND quality_score >= 0.8 AND tags intersects ['ai', 'ml'] AND year >= 2020 AND is_public = true AND NOT is_deleted AND feedback_accepted >= 5 AND used_in_generation = true AND language = 'en' AND title like 'Python' AND summary like 'machine learning' AND category = 'programming' AND source = 'github' AND block_type = 'code' AND chunking_version = '1.0' AND block_id = '123' AND embedding = [0.1, 0.2, 0.3] AND block_index = 1 AND source_lines_start = 10 AND source_lines_end = 20 AND tags_flat = 'ai,python,ml' AND link_related = '456' AND link_parent = '789' AND uuid = 'abc' AND source_id = 'def' AND project = 'test' AND task_id = 'ghi' AND subtask_id = 'jkl' AND unit_id = 'mno' AND role = 'content' AND body = 'test' AND text = 'test' AND summary = 'test' AND ordinal = 1 AND sha256 = 'hash' AND created_at = '2024-01-01' AND status = 'active' AND source_path = '/path' AND coverage = 0.9 AND cohesion = 0.8 AND boundary_prev = 0.7 AND boundary_next = 0.6 AND feedback_rejected = 0 AND start = 0 AND end = 100 AND category = 'test' AND title = 'test' AND year = 2024 AND source = 'test' AND block_type = 'code' AND chunking_version = '1.0' AND block_id = '123' AND block_index = 1 AND source_lines_start = 10 AND source_lines_end = 20 AND tags_flat = 'test' AND link_related = '456' AND link_parent = '789'"  # Very long
    ]
    
    validation_results = []
    for query in test_queries:
        result = validator.validate(query)
        validation_results.append(result)
        print(f"  Query: '{query[:50]}...' -> Valid: {result.is_valid}")
        if not result.is_valid:
            print(f"    Errors: {result.errors}")
    
    valid_count = sum(1 for r in validation_results if r.is_valid)
    invalid_count = len(validation_results) - valid_count
    print(f"  Total queries: {len(validation_results)}")
    print(f"  Valid queries: {valid_count}")
    print(f"  Invalid queries: {invalid_count}")
    print(f"  Error rate: {invalid_count / len(validation_results) * 100:.1f}%")


def demo_business_metrics():
    """Demonstrate business-related metrics."""
    print("\n=== Business Metrics Demo ===")
    
    # Field usage statistics
    print("\n1. Field Usage Statistics:")
    
    sample_queries = [
        "type = 'DocBlock'",
        "quality_score >= 0.8",
        "tags intersects ['ai', 'ml']",
        "year >= 2020",
        "is_public = true",
        "language = 'en'",
        "status = 'active'",
        "feedback_accepted >= 5",
        "used_in_generation = true",
        "title like 'Python'"
    ]
    
    field_usage = {}
    operator_usage = {}
    
    parser = FilterParser()
    
    for query in sample_queries:
        try:
            ast = parser.parse(query)
            # Extract field and operator usage from AST
            if hasattr(ast, 'field'):
                field = ast.field
                field_usage[field] = field_usage.get(field, 0) + 1
            if hasattr(ast, 'operator'):
                operator = ast.operator
                operator_usage[operator] = operator_usage.get(operator, 0) + 1
        except Exception:
            pass
    
    print("  Field usage:")
    for field, count in sorted(field_usage.items(), key=lambda x: x[1], reverse=True):
        print(f"    {field}: {count}")
    
    print("  Operator usage:")
    for operator, count in sorted(operator_usage.items(), key=lambda x: x[1], reverse=True):
        print(f"    {operator}: {count}")


def demo_resource_metrics():
    """Demonstrate resource usage metrics."""
    print("\n=== Resource Metrics Demo ===")
    
    # Memory usage estimation
    print("\n1. Memory Usage Estimation:")
    
    # Create various caches and measure their sizes
    cache = QueryCache(max_size=1000)
    executor = FilterExecutor()
    
    # Populate caches
    queries = [
        "age > 18 AND status = 'active'",
        "type = 'DocBlock' AND quality_score >= 0.8",
        "tags intersects ['ai', 'ml'] AND year >= 2020"
    ]
    
    parser = FilterParser()
    parameterizer = ASTParameterizer()
    
    for query in queries:
        ast = parser.parse(query)
        cache.get_or_create(ast, parameterizer)
        
        # Execute to populate executor cache
        test_data = {"age": 25, "status": "active", "type": "DocBlock", "quality_score": 0.9}
        executor.execute(ast, test_data)
    
    # Get cache statistics
    cache_stats = cache.get_stats()
    executor_stats = executor.get_cache_stats()
    
    print(f"  QueryCache memory usage:")
    print(f"    Templates cached: {cache_stats['size']}")
    print(f"    Cache size: ~{cache_stats['size'] * 1024} bytes (estimated)")
    
    print(f"  FilterExecutor memory usage:")
    print(f"    Field cache entries: {executor_stats['field_cache_size']}")
    print(f"    Comparison cache entries: {executor_stats['comparison_cache_size']}")
    print(f"    Total cache entries: {executor_stats['field_cache_size'] + executor_stats['comparison_cache_size']}")


def generate_prometheus_metrics():
    """Generate Prometheus-style metrics."""
    print("\n=== Prometheus Metrics Format ===")
    
    # This would be the actual Prometheus metrics format
    metrics = {
        "cache_hits_total": {"component": "query_cache", "value": 44},
        "cache_misses_total": {"component": "query_cache", "value": 1},
        "cache_evictions_total": {"component": "query_cache", "value": 0},
        "cache_size": {"component": "query_cache", "value": 3},
        "cache_hit_rate": {"component": "query_cache", "value": 97.8},
        "field_cache_size": {"component": "filter_executor", "value": 15},
        "comparison_cache_size": {"component": "filter_executor", "value": 12},
        "ast_cached": {"component": "chunk_query", "value": 1},
        "validation_cached": {"component": "chunk_query", "value": 0},
        "parser_initialized": {"component": "chunk_query", "value": 1},
        "executor_initialized": {"component": "chunk_query", "value": 1},
        "validator_initialized": {"component": "chunk_query", "value": 1},
        "optimizer_initialized": {"component": "chunk_query", "value": 1}
    }
    
    print("Prometheus metrics format:")
    for metric_name, labels in metrics.items():
        value = labels.pop("value")
        label_str = ",".join([f'{k}="{v}"' for k, v in labels.items()])
        print(f"  {metric_name}{{{label_str}}} {value}")


def main():
    """Run all metrics demonstrations."""
    print("Metrics Demo for chunk_metadata_adapter")
    print("=" * 50)
    
    demo_cache_metrics()
    demo_performance_metrics()
    demo_complexity_metrics()
    demo_error_metrics()
    demo_business_metrics()
    demo_resource_metrics()
    generate_prometheus_metrics()
    
    print("\n" + "=" * 50)
    print("All metrics demonstrations completed!")
    print("\nThese metrics can be exported to Prometheus for monitoring:")
    print("- Cache performance and hit rates")
    print("- Query parsing and execution times")
    print("- AST complexity and optimization opportunities")
    print("- Error rates and validation statistics")
    print("- Business usage patterns")
    print("- Resource consumption")


if __name__ == "__main__":
    main() 