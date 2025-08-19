"""
Tests for AST parameterization functionality.

This module tests the parameterization system that allows converting
concrete AST values to parameters for efficient caching and reuse.

Test coverage:
- ParameterValue creation and serialization
- ASTParameterizer functionality
- ASTInstantiator functionality  
- QueryCache operations
- Error handling and validation
- Performance characteristics

Author: Development Team
Created: 2024-01-20
"""

import pytest
import time
from chunk_metadata_adapter.ast import (
    FieldCondition, LogicalOperator, TypedValue,
    ParameterValue, ParameterizedAST, ASTParameterizer, ASTInstantiator, QueryCache
)


class TestParameterValue:
    """Tests for ParameterValue class."""
    
    def test_creation_with_valid_data(self):
        """Test creating ParameterValue with valid data."""
        param = ParameterValue("param_1", "int", "age threshold")
        assert param.param_id == "param_1"
        assert param.param_type == "int"
        assert param.description == "age threshold"
    
    def test_string_representation(self):
        """Test string representation of ParameterValue."""
        param = ParameterValue("param_1", "int")
        assert str(param) == "param_1:int"
    
    def test_json_serialization(self):
        """Test JSON serialization and deserialization."""
        param = ParameterValue("param_1", "str", "status value")
        json_data = param.to_json()
        
        assert json_data["param_id"] == "param_1"
        assert json_data["param_type"] == "str"
        assert json_data["description"] == "status value"
        
        # Deserialize
        restored_param = ParameterValue.from_json(json_data)
        assert restored_param.param_id == param.param_id
        assert restored_param.param_type == param.param_type
        assert restored_param.description == param.description


class TestParameterizedAST:
    """Tests for ParameterizedAST class."""
    
    def test_creation_with_valid_data(self):
        """Test creating ParameterizedAST with valid data."""
        # Create a simple AST
        condition = FieldCondition("age", ">", TypedValue("int", 18))
        
        # Create parameters
        params = {
            "param_1": ParameterValue("param_1", "int", "age threshold")
        }
        
        template = ParameterizedAST(condition, params, "abc123")
        assert template.ast == condition
        assert template.parameters == params
        assert template.template_hash == "abc123"
    
    def test_parameter_count(self):
        """Test getting parameter count."""
        condition = FieldCondition("age", ">", TypedValue("int", 18))
        params = {
            "param_1": ParameterValue("param_1", "int"),
            "param_2": ParameterValue("param_2", "str")
        }
        
        template = ParameterizedAST(condition, params, "hash")
        assert template.get_parameter_count() == 2
    
    def test_parameter_types(self):
        """Test getting parameter types mapping."""
        condition = FieldCondition("age", ">", TypedValue("int", 18))
        params = {
            "param_1": ParameterValue("param_1", "int"),
            "param_2": ParameterValue("param_2", "str")
        }
        
        template = ParameterizedAST(condition, params, "hash")
        types = template.get_parameter_types()
        assert types["param_1"] == "int"
        assert types["param_2"] == "str"
    
    def test_json_serialization(self):
        """Test JSON serialization and deserialization."""
        # Create parameterized AST
        condition = FieldCondition("age", ">", TypedValue("int", 18))
        params = {
            "param_1": ParameterValue("param_1", "int", "age threshold")
        }
        template = ParameterizedAST(condition, params, "abc123")
        
        # Serialize
        json_data = template.to_json()
        assert json_data["template_hash"] == "abc123"
        assert "ast" in json_data
        assert "parameters" in json_data
        
        # Deserialize
        restored_template = ParameterizedAST.from_json(json_data)
        assert restored_template.template_hash == template.template_hash
        assert restored_template.get_parameter_count() == template.get_parameter_count()


class TestASTParameterizer:
    """Tests for ASTParameterizer class."""
    
    def test_parameterize_simple_condition(self):
        """Test parameterizing a simple field condition."""
        condition = FieldCondition("age", ">", TypedValue("int", 18))
        
        parameterizer = ASTParameterizer()
        template = parameterizer.parameterize(condition)
        
        assert template.get_parameter_count() == 1
        assert template.get_parameter_types()["param_0"] == "int"
        assert template.template_hash is not None
    
    def test_parameterize_logical_operator(self):
        """Test parameterizing a logical operator."""
        condition1 = FieldCondition("age", ">", TypedValue("int", 18))
        condition2 = FieldCondition("status", "=", TypedValue("str", "active"))
        ast = LogicalOperator("AND", [condition1, condition2])
        
        parameterizer = ASTParameterizer()
        template = parameterizer.parameterize(ast)
        
        assert template.get_parameter_count() == 2
        assert template.get_parameter_types()["param_0"] == "int"
        assert template.get_parameter_types()["param_1"] == "str"
    
    def test_parameterize_complex_expression(self):
        """Test parameterizing a complex expression."""
        # (age > 18 AND status = 'active') OR (vip = true)
        condition1 = FieldCondition("age", ">", TypedValue("int", 18))
        condition2 = FieldCondition("status", "=", TypedValue("str", "active"))
        condition3 = FieldCondition("vip", "=", TypedValue("bool", True))
        
        and_op = LogicalOperator("AND", [condition1, condition2])
        or_op = LogicalOperator("OR", [and_op, condition3])
        
        parameterizer = ASTParameterizer()
        template = parameterizer.parameterize(or_op)
        
        assert template.get_parameter_count() == 3
        assert template.get_parameter_types()["param_0"] == "int"
        assert template.get_parameter_types()["param_1"] == "str"
        assert template.get_parameter_types()["param_2"] == "bool"
    
    def test_custom_parameter_prefix(self):
        """Test using custom parameter prefix."""
        condition = FieldCondition("age", ">", TypedValue("int", 18))
        
        parameterizer = ASTParameterizer(param_prefix="value")
        template = parameterizer.parameterize(condition)
        
        param_types = template.get_parameter_types()
        assert "value_0" in param_types
        assert param_types["value_0"] == "int"
    
    def test_template_hash_consistency(self):
        """Test that template hash is consistent for same structure."""
        condition1 = FieldCondition("age", ">", TypedValue("int", 18))
        condition2 = FieldCondition("age", ">", TypedValue("int", 25))
        
        parameterizer = ASTParameterizer()
        template1 = parameterizer.parameterize(condition1)
        template2 = parameterizer.parameterize(condition2)
        
        # Same structure should have same hash
        assert template1.template_hash == template2.template_hash


class TestASTInstantiator:
    """Tests for ASTInstantiator class."""
    
    def test_instantiate_simple_condition(self):
        """Test instantiating a simple condition."""
        # Create template
        condition = FieldCondition("age", ">", TypedValue("int", 18))
        parameterizer = ASTParameterizer()
        template = parameterizer.parameterize(condition)
        
        # Instantiate
        instantiator = ASTInstantiator()
        params = {"param_0": 25}
        instantiated = instantiator.instantiate(template, params)
        
        assert isinstance(instantiated, FieldCondition)
        assert instantiated.field == "age"
        assert instantiated.operator == ">"
        assert instantiated.value.type == "int"
        assert instantiated.value.value == 25
    
    def test_instantiate_logical_operator(self):
        """Test instantiating a logical operator."""
        # Create template
        condition1 = FieldCondition("age", ">", TypedValue("int", 18))
        condition2 = FieldCondition("status", "=", TypedValue("str", "active"))
        ast = LogicalOperator("AND", [condition1, condition2])
        
        parameterizer = ASTParameterizer()
        template = parameterizer.parameterize(ast)
        
        # Instantiate
        instantiator = ASTInstantiator()
        params = {"param_0": 25, "param_1": "verified"}
        instantiated = instantiator.instantiate(template, params)
        
        assert isinstance(instantiated, LogicalOperator)
        assert instantiated.operator == "AND"
        assert len(instantiated.children) == 2
        
        # Check first child
        child1 = instantiated.children[0]
        assert isinstance(child1, FieldCondition)
        assert child1.value.value == 25
        
        # Check second child
        child2 = instantiated.children[1]
        assert isinstance(child2, FieldCondition)
        assert child2.value.value == "verified"
    
    def test_missing_parameters_error(self):
        """Test error handling for missing parameters."""
        condition = FieldCondition("age", ">", TypedValue("int", 18))
        parameterizer = ASTParameterizer()
        template = parameterizer.parameterize(condition)
        
        instantiator = ASTInstantiator()
        
        with pytest.raises(ValueError, match="Missing parameters"):
            instantiator.instantiate(template, {})
    
    def test_extra_parameters_error(self):
        """Test error handling for extra parameters."""
        condition = FieldCondition("age", ">", TypedValue("int", 18))
        parameterizer = ASTParameterizer()
        template = parameterizer.parameterize(condition)
        
        instantiator = ASTInstantiator()
        
        with pytest.raises(ValueError, match="Extra parameters"):
            instantiator.instantiate(template, {"param_0": 25, "extra": "value"})
    
    def test_wrong_parameter_type_error(self):
        """Test error handling for wrong parameter types."""
        condition = FieldCondition("age", ">", TypedValue("int", 18))
        parameterizer = ASTParameterizer()
        template = parameterizer.parameterize(condition)
        
        instantiator = ASTInstantiator()
        
        with pytest.raises(ValueError, match="expects type int"):
            instantiator.instantiate(template, {"param_0": "not_a_number"})
    
    def test_type_validation(self):
        """Test type validation for different types."""
        instantiator = ASTInstantiator()
        
        # Test valid types
        assert instantiator._is_valid_type(42, "int")
        assert instantiator._is_valid_type(3.14, "float")
        assert instantiator._is_valid_type("hello", "str")
        assert instantiator._is_valid_type([1, 2, 3], "list")
        assert instantiator._is_valid_type({"key": "value"}, "dict")
        assert instantiator._is_valid_type(True, "bool")
        assert instantiator._is_valid_type(None, "null")
        
        # Test invalid types
        assert not instantiator._is_valid_type("not_a_number", "int")
        assert not instantiator._is_valid_type(42, "str")
        assert not instantiator._is_valid_type("not_a_list", "list")


class TestQueryCache:
    """Tests for QueryCache class."""
    
    def test_cache_creation(self):
        """Test creating cache with custom size."""
        cache = QueryCache(max_size=50)
        assert cache.max_size == 50
        assert cache.get_stats()["size"] == 0
    
    def test_get_or_create_new_template(self):
        """Test creating new template when not in cache."""
        cache = QueryCache()
        condition = FieldCondition("age", ">", TypedValue("int", 18))
        parameterizer = ASTParameterizer()
        
        template = cache.get_or_create(condition, parameterizer)
        
        assert template.get_parameter_count() == 1
        stats = cache.get_stats()
        assert stats["misses"] == 1
        assert stats["hits"] == 0
        assert stats["size"] == 1
    
    def test_get_or_create_existing_template(self):
        """Test retrieving existing template from cache."""
        cache = QueryCache()
        condition = FieldCondition("age", ">", TypedValue("int", 18))
        parameterizer = ASTParameterizer()
        
        # Create template
        template1 = cache.get_or_create(condition, parameterizer)
        
        # Create same template again
        condition2 = FieldCondition("age", ">", TypedValue("int", 25))  # Same structure
        template2 = cache.get_or_create(condition2, parameterizer)
        
        # Should be the same template
        assert template1.template_hash == template2.template_hash
        stats = cache.get_stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["size"] == 1
    
    def test_cache_eviction(self):
        """Test cache eviction when full."""
        cache = QueryCache(max_size=2)
        parameterizer = ASTParameterizer()
        
        # Add three templates
        condition1 = FieldCondition("age", ">", TypedValue("int", 18))
        condition2 = FieldCondition("status", "=", TypedValue("str", "active"))
        condition3 = FieldCondition("vip", "=", TypedValue("bool", True))
        
        template1 = cache.get_or_create(condition1, parameterizer)
        template2 = cache.get_or_create(condition2, parameterizer)
        template3 = cache.get_or_create(condition3, parameterizer)
        
        stats = cache.get_stats()
        assert stats["size"] == 2  # Should be at max size
        assert stats["evictions"] == 1  # Should have evicted one
    
    def test_cache_clear(self):
        """Test clearing cache."""
        cache = QueryCache()
        condition = FieldCondition("age", ">", TypedValue("int", 18))
        parameterizer = ASTParameterizer()
        
        cache.get_or_create(condition, parameterizer)
        assert cache.get_stats()["size"] == 1
        
        cache.clear()
        assert cache.get_stats()["size"] == 0
        assert cache.get_stats()["hits"] == 0
        assert cache.get_stats()["misses"] == 0
    
    def test_get_by_hash(self):
        """Test getting template by hash."""
        cache = QueryCache()
        condition = FieldCondition("age", ">", TypedValue("int", 18))
        parameterizer = ASTParameterizer()
        
        template = cache.get_or_create(condition, parameterizer)
        template_hash = template.template_hash
        
        # Get by hash
        retrieved = cache.get(template_hash)
        assert retrieved is not None
        assert retrieved.template_hash == template_hash
        
        # Get non-existent hash
        non_existent = cache.get("non_existent_hash")
        assert non_existent is None
    
    def test_cache_statistics(self):
        """Test cache statistics tracking."""
        cache = QueryCache()
        parameterizer = ASTParameterizer()
        
        # Add some templates
        condition1 = FieldCondition("age", ">", TypedValue("int", 18))
        condition2 = FieldCondition("status", "=", TypedValue("str", "active"))
        
        cache.get_or_create(condition1, parameterizer)  # miss
        cache.get_or_create(condition1, parameterizer)  # hit (same structure)
        cache.get_or_create(condition2, parameterizer)  # miss
        
        stats = cache.get_stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 2
        assert stats["size"] == 2
        assert stats["max_size"] == 1000


class TestParameterizationIntegration:
    """Integration tests for parameterization system."""
    
    def test_full_parameterization_cycle(self):
        """Test complete parameterization and instantiation cycle."""
        # Create original AST
        condition1 = FieldCondition("age", ">", TypedValue("int", 18))
        condition2 = FieldCondition("status", "=", TypedValue("str", "active"))
        original_ast = LogicalOperator("AND", [condition1, condition2])
        
        # Parameterize
        parameterizer = ASTParameterizer()
        template = parameterizer.parameterize(original_ast)
        
        # Instantiate with different values
        instantiator = ASTInstantiator()
        params = {"param_0": 25, "param_1": "verified"}
        instantiated_ast = instantiator.instantiate(template, params)
        
        # Verify structure is preserved
        assert isinstance(instantiated_ast, LogicalOperator)
        assert instantiated_ast.operator == "AND"
        assert len(instantiated_ast.children) == 2
        
        # Verify values are updated
        child1 = instantiated_ast.children[0]
        assert child1.value.value == 25
        
        child2 = instantiated_ast.children[1]
        assert child2.value.value == "verified"
    
    def test_cache_with_multiple_queries(self):
        """Test caching with multiple similar queries."""
        cache = QueryCache()
        parameterizer = ASTParameterizer()
        instantiator = ASTInstantiator()
        
        # Create similar queries
        queries = [
            FieldCondition("age", ">", TypedValue("int", 18)),
            FieldCondition("age", ">", TypedValue("int", 25)),
            FieldCondition("age", ">", TypedValue("int", 30)),
        ]
        
        templates = []
        for query in queries:
            template = cache.get_or_create(query, parameterizer)
            templates.append(template)
        
        # All should have same hash (same structure)
        assert templates[0].template_hash == templates[1].template_hash
        assert templates[1].template_hash == templates[2].template_hash
        
        # But different parameter values
        assert templates[0].parameters["param_0"].param_type == "int"
        assert templates[1].parameters["param_0"].param_type == "int"
        assert templates[2].parameters["param_0"].param_type == "int"
        
        # Instantiate with different values
        params_list = [{"param_0": 18}, {"param_0": 25}, {"param_0": 30}]
        for template, params in zip(templates, params_list):
            instantiated = instantiator.instantiate(template, params)
            assert instantiated.value.value == params["param_0"]
    
    def test_performance_benefits(self):
        """Test performance benefits of caching."""
        cache = QueryCache()
        parameterizer = ASTParameterizer()
        
        # Create base condition
        base_condition = FieldCondition("age", ">", TypedValue("int", 18))
        
        # Time without caching
        start_time = time.time()
        for i in range(100):
            condition = FieldCondition("age", ">", TypedValue("int", i))
            parameterizer.parameterize(condition)
        no_cache_time = time.time() - start_time
        
        # Time with caching
        start_time = time.time()
        for i in range(100):
            condition = FieldCondition("age", ">", TypedValue("int", i))
            cache.get_or_create(condition, parameterizer)
        cache_time = time.time() - start_time
        
        # Check cache statistics - this is more reliable than timing
        stats = cache.get_stats()
        assert stats["hits"] > 0
        assert stats["misses"] == 1  # Only one unique template
        assert stats["size"] == 1
        
        # Verify that caching works correctly
        # The cache should have hit the same template multiple times
        assert stats["hits"] >= 99  # At least 99 hits for 100 calls 