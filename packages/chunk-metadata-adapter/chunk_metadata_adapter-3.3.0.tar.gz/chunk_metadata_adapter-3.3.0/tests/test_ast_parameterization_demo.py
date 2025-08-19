"""
Tests for ast_parameterization_demo.py to achieve 90%+ coverage.

This module tests the AST parameterization demo functionality.

Author: Development Team
Created: 2024-01-20
Updated: 2024-01-20
"""

import pytest
import time
from unittest.mock import patch, Mock
from io import StringIO
from chunk_metadata_adapter.examples.ast_parameterization_demo import (
    demo_basic_parameterization,
    demo_query_caching,
    demo_complex_queries,
    demo_performance_comparison,
    demo_error_handling,
    main
)
from chunk_metadata_adapter.ast import (
    FieldCondition, LogicalOperator, TypedValue,
    ASTParameterizer, ASTInstantiator, QueryCache
)
from chunk_metadata_adapter.filter_parser import FilterParser


class TestASTParameterizationDemo:
    """Tests for AST parameterization demo."""
    
    def test_demo_basic_parameterization(self):
        """Test basic parameterization demo."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            demo_basic_parameterization()
            output = fake_out.getvalue()
            
            assert "=== Basic AST Parameterization ===" in output
            assert "Original AST:" in output
            assert "Parameterized template hash:" in output
            assert "Number of parameters:" in output
            assert "Parameter types:" in output
            assert "Parameterized AST:" in output
            assert "Instantiated AST 1:" in output
            assert "Instantiated AST 2:" in output
    
    def test_demo_query_caching(self):
        """Test query caching demo."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            demo_query_caching()
            output = fake_out.getvalue()
            
            assert "Query Caching with Parameterization" in output
            assert "Processing queries with caching:" in output
            assert "Query 1:" in output
            assert "Query 2:" in output
            assert "Template hash:" in output
            assert "Cache time:" in output
    
    def test_demo_complex_queries(self):
        """Test complex queries demo."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            demo_complex_queries()
            output = fake_out.getvalue()
            
            assert "Complex Query Parameterization" in output
            assert "Complex query:" in output
            assert "Template hash:" in output
            assert "Number of parameters:" in output
            assert "Parameter types:" in output
            assert "Scenario:" in output
    
    def test_demo_performance_comparison(self):
        """Test performance comparison demo."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            demo_performance_comparison()
            output = fake_out.getvalue()
            
            assert "Performance Comparison" in output
            assert "Testing without caching:" in output
            assert "Testing with caching:" in output
            assert "Performance improvement:" in output
            assert "Hit rate:" in output
    
    def test_demo_error_handling(self):
        """Test error handling demo."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            demo_error_handling()
            output = fake_out.getvalue()
            
            assert "Error Handling" in output
            assert "Testing parameter validation:" in output
            assert "Correctly caught" in output
    
    def test_main_function(self):
        """Test main function execution."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            main()
            output = fake_out.getvalue()
            
            assert "AST Parameterization Demo" in output
            assert "Basic AST Parameterization" in output
            assert "Query Caching with Parameterization" in output
            assert "Complex Query Parameterization" in output
            assert "Performance Comparison" in output
            assert "Error Handling" in output
            assert "completed successfully" in output
    
    def test_actual_parameterization_functionality(self):
        """Test actual parameterization functionality used in demo."""
        # Test basic parameterization
        condition1 = FieldCondition("age", ">", TypedValue("int", 18))
        condition2 = FieldCondition("status", "=", TypedValue("str", "active"))
        ast = LogicalOperator("AND", [condition1, condition2])
        
        parameterizer = ASTParameterizer()
        template = parameterizer.parameterize(ast)
        
        assert template.template_hash is not None
        assert template.get_parameter_count() == 2
        param_types = template.get_parameter_types()
        assert "int" in param_types.values() or "int" in list(param_types.values())
        assert "str" in param_types.values() or "str" in list(param_types.values())
        
        # Test instantiation
        instantiator = ASTInstantiator()
        params1 = {"param_0": 25, "param_1": "verified"}
        ast1 = instantiator.instantiate(template, params1)
        
        assert isinstance(ast1, LogicalOperator)
        assert ast1.operator == "AND"
        assert len(ast1.children) == 2
        assert ast1.children[0].value.value == 25
        assert ast1.children[1].value.value == "verified"
    
    def test_query_caching_functionality(self):
        """Test query caching functionality."""
        cache = QueryCache(max_size=100)
        parser = FilterParser()
        parameterizer = ASTParameterizer()
        
        # Test cache operations
        query1 = "age > 18 AND status = 'active'"
        query2 = "age > 25 AND status = 'verified'"
        
        ast1 = parser.parse(query1)
        ast2 = parser.parse(query2)
        
        template1 = cache.get_or_create(ast1, parameterizer)
        template2 = cache.get_or_create(ast2, parameterizer)
        
        # Should have same template hash (same structure, different values)
        assert template1.template_hash == template2.template_hash
        
        # Test cache statistics
        stats = cache.get_stats()
        assert "hits" in stats
        assert "misses" in stats
        assert "size" in stats
        assert "max_size" in stats
    
    def test_complex_query_parameterization(self):
        """Test complex query parameterization."""
        complex_query = """
        (type = 'DocBlock' OR type = 'CodeBlock') AND
        quality_score >= 0.8 AND
        tags intersects ['ai', 'ml'] AND
        year >= 2020 AND
        NOT is_deleted
        """
        
        parser = FilterParser()
        parameterizer = ASTParameterizer()
        
        ast = parser.parse(complex_query)
        template = parameterizer.parameterize(ast)
        
        assert template.template_hash is not None
        assert template.get_parameter_count() > 0
        
        # Test instantiation with different values
        instantiator = ASTInstantiator()
        params = {
            "param_0": "DocBlock",
            "param_1": "CodeBlock", 
            "param_2": 0.9,
            "param_3": ["python", "data"],
            "param_4": 2021,
            "param_5": False
        }
        
        instantiated = instantiator.instantiate(template, params)
        assert isinstance(instantiated, LogicalOperator)
    
    def test_performance_comparison_functionality(self):
        """Test performance comparison functionality."""
        queries = [
            "age > 18 AND status = 'active'",
            "age > 25 AND status = 'verified'",
            "age > 30 AND status = 'pending'"
        ]
        
        parser = FilterParser()
        parameterizer = ASTParameterizer()
        cache = QueryCache(max_size=100)
        
        # Test without caching
        start_time = time.time()
        for query in queries:
            ast = parser.parse(query)
            parameterizer.parameterize(ast)
        without_cache_time = time.time() - start_time
        
        # Test with caching
        start_time = time.time()
        for query in queries:
            ast = parser.parse(query)
            cache.get_or_create(ast, parameterizer)
        with_cache_time = time.time() - start_time
        
        # Caching should be faster (or at least not slower)
        assert with_cache_time <= without_cache_time * 1.5  # Allow some variance
    
    def test_error_handling_functionality(self):
        """Test error handling functionality."""
        # Create a template
        condition = FieldCondition("age", ">", TypedValue("int", 18))
        parameterizer = ASTParameterizer()
        template = parameterizer.parameterize(condition)
        instantiator = ASTInstantiator()
        
        # Test missing parameter
        with pytest.raises(ValueError):
            instantiator.instantiate(template, {})
        
        # Test extra parameter
        with pytest.raises(ValueError):
            instantiator.instantiate(template, {"param_0": 25, "extra_param": "value"})
        
        # Test wrong type parameter
        with pytest.raises(ValueError):
            instantiator.instantiate(template, {"param_0": "not an int"})
    
    def test_cache_eviction(self):
        """Test cache eviction functionality."""
        cache = QueryCache(max_size=2)
        parser = FilterParser()
        parameterizer = ASTParameterizer()
        
        # Add more items than cache size with different structures
        queries = [
            "age > 18",
            "status = 'active'", 
            "vip = true"
        ]
        
        for query in queries:
            ast = parser.parse(query)
            cache.get_or_create(ast, parameterizer)
        
        # Cache should have evicted oldest items
        stats = cache.get_stats()
        assert "hits" in stats
        assert "misses" in stats
        assert "evictions" in stats
        assert stats["size"] == 2  # Should be at max size
        assert stats["evictions"] >= 1  # Should have evicted at least one item
    
    def test_template_hash_consistency(self):
        """Test that template hash is consistent for similar structures."""
        parser = FilterParser()
        parameterizer = ASTParameterizer()
        
        # Similar queries should have same template hash
        query1 = "age > 18 AND status = 'active'"
        query2 = "age > 25 AND status = 'verified'"
        
        ast1 = parser.parse(query1)
        ast2 = parser.parse(query2)
        
        template1 = parameterizer.parameterize(ast1)
        template2 = parameterizer.parameterize(ast2)
        
        # Should have same template hash (same structure, different values)
        assert template1.template_hash == template2.template_hash 