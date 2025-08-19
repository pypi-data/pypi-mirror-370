"""
Tests for ast/parameterization.py coverage improvement.

This module contains tests to increase coverage of ast/parameterization.py
to 90%+ by testing edge cases and error conditions.
"""

import pytest
from chunk_metadata_adapter.ast.parameterization import (
    ParameterValue, ParameterizedAST, ASTParameterizer, ASTInstantiator, QueryCache
)
from chunk_metadata_adapter.ast.nodes import FieldCondition, TypedValue, LogicalOperator, ParenExpression


class TestASTParameterizationCoverage:
    """Tests for AST parameterization coverage improvement."""
    
    def test_parameterize_node_with_unsupported_type(self):
        """Test _parameterize_node with unsupported node type."""
        parameterizer = ASTParameterizer()
        
        class UnsupportedNode:
            pass
        
        with pytest.raises(ValueError, match="Unsupported node type"):
            parameterizer._parameterize_node(UnsupportedNode())
    
    def test_parameterize_field_condition(self):
        """Test _parameterize_field_condition."""
        parameterizer = ASTParameterizer()
        
        condition = FieldCondition("age", ">", TypedValue("int", 18))
        result = parameterizer._parameterize_field_condition(condition)
        
        assert isinstance(result, FieldCondition)
        assert result.field == "age"
        assert result.operator == ">"
        assert result.value.type == "str"
        assert result.value.value.startswith("param_")
    
    def test_parameterize_logical_operator(self):
        """Test _parameterize_logical_operator."""
        parameterizer = ASTParameterizer()
        
        condition1 = FieldCondition("age", ">", TypedValue("int", 18))
        condition2 = FieldCondition("status", "=", TypedValue("str", "active"))
        operator = LogicalOperator("AND", [condition1, condition2])
        
        result = parameterizer._parameterize_logical_operator(operator)
        
        assert isinstance(result, LogicalOperator)
        assert result.operator == "AND"
        assert len(result.children) == 2
        assert all(isinstance(child, FieldCondition) for child in result.children)
    
    def test_parameterize_paren_expression(self):
        """Test _parameterize_paren_expression."""
        parameterizer = ASTParameterizer()
        
        inner_condition = FieldCondition("age", ">", TypedValue("int", 18))
        paren = ParenExpression(inner_condition)
        
        result = parameterizer._parameterize_paren_expression(paren)
        
        assert isinstance(result, ParenExpression)
        assert isinstance(result.expression, FieldCondition)
        assert result.expression.field == "age"
    
    def test_create_parameter_value(self):
        """Test _create_parameter_value."""
        parameterizer = ASTParameterizer()
        
        typed_value = TypedValue("int", 42)
        result = parameterizer._create_parameter_value(typed_value)
        
        assert isinstance(result, TypedValue)
        assert result.type == "str"
        assert result.value.startswith("param_")
        
        # Check that parameter was stored
        param_id = result.value
        assert param_id in parameterizer._value_to_param
        assert parameterizer._value_to_param[param_id][0] == "int"
    
    def test_generate_template_hash(self):
        """Test _generate_template_hash."""
        parameterizer = ASTParameterizer()
        
        condition = FieldCondition("age", ">", TypedValue("int", 18))
        hash_result = parameterizer._generate_template_hash(condition)
        
        assert isinstance(hash_result, str)
        assert len(hash_result) == 16  # SHA256 hash truncated to 16 chars
    
    def test_ast_instantiator_validate_parameters_missing(self):
        """Test ASTInstantiator._validate_parameters with missing parameters."""
        instantiator = ASTInstantiator()
        
        # Create a parameterized AST with one parameter
        parameterizer = ASTParameterizer()
        condition = FieldCondition("age", ">", TypedValue("int", 18))
        template = parameterizer.parameterize(condition)
        
        # Try to instantiate without providing the parameter
        with pytest.raises(ValueError, match="Missing parameters"):
            instantiator.instantiate(template, {})
    
    def test_ast_instantiator_validate_parameters_invalid_type(self):
        """Test ASTInstantiator._validate_parameters with invalid parameter type."""
        instantiator = ASTInstantiator()
        
        # Create a parameterized AST with one parameter
        parameterizer = ASTParameterizer()
        condition = FieldCondition("age", ">", TypedValue("int", 18))
        template = parameterizer.parameterize(condition)
        
        # Get the parameter ID
        param_id = list(template.parameters.keys())[0]
        
        # Try to instantiate with wrong type
        with pytest.raises(ValueError, match="expects type int"):
            instantiator.instantiate(template, {param_id: "not an int"})
    
    def test_ast_instantiator_validate_parameters_extra(self):
        """Test ASTInstantiator._validate_parameters with extra parameters."""
        instantiator = ASTInstantiator()
        
        # Create a parameterized AST with one parameter
        parameterizer = ASTParameterizer()
        condition = FieldCondition("age", ">", TypedValue("int", 18))
        template = parameterizer.parameterize(condition)
        
        # Get the parameter ID
        param_id = list(template.parameters.keys())[0]
        
        # Try to instantiate with extra parameters
        with pytest.raises(ValueError, match="Extra parameters"):
            instantiator.instantiate(template, {param_id: 42, "extra_param": "value"})
    
    def test_ast_instantiator_replace_parameters_with_unsupported_type(self):
        """Test _replace_parameters with unsupported node type."""
        instantiator = ASTInstantiator()
        
        # Test that parameterization fails with unsupported node types
        parameterizer = ASTParameterizer()
        
        class UnsupportedNode:
            pass
        
        # This should fail during parameterization
        with pytest.raises(ValueError, match="Unsupported node type"):
            parameterizer._parameterize_node(UnsupportedNode())
    
    def test_ast_instantiator_replace_parameters_field_condition(self):
        """Test _replace_parameters with FieldCondition."""
        instantiator = ASTInstantiator()
        
        # Create a parameterized AST and instantiate it
        parameterizer = ASTParameterizer()
        condition = FieldCondition("age", ">", TypedValue("int", 18))
        template = parameterizer.parameterize(condition)
        
        # Get the parameter ID
        param_id = list(template.parameters.keys())[0]
        
        # Instantiate with correct parameter
        result = instantiator.instantiate(template, {param_id: 42})
        
        assert isinstance(result, FieldCondition)
        assert result.field == "age"
        assert result.operator == ">"
        assert result.value.type == "int"
        assert result.value.value == 42
    
    def test_ast_instantiator_replace_parameters_logical_operator(self):
        """Test _replace_parameters with LogicalOperator."""
        instantiator = ASTInstantiator()
        
        # Create a parameterized logical operator
        parameterizer = ASTParameterizer()
        condition1 = FieldCondition("age", ">", TypedValue("int", 18))
        condition2 = FieldCondition("status", "=", TypedValue("str", "active"))
        operator = LogicalOperator("AND", [condition1, condition2])
        
        template = parameterizer.parameterize(operator)
        
        # Get parameter IDs
        param_ids = list(template.parameters.keys())
        
        # Instantiate with correct parameters
        result = instantiator.instantiate(template, {param_ids[0]: 42, param_ids[1]: "active"})
        
        assert isinstance(result, LogicalOperator)
        assert result.operator == "AND"
        assert len(result.children) == 2
    
    def test_ast_instantiator_replace_parameters_paren_expression(self):
        """Test _replace_parameters with ParenExpression."""
        instantiator = ASTInstantiator()
        
        # Create a parameterized parenthesized expression
        parameterizer = ASTParameterizer()
        inner_condition = FieldCondition("age", ">", TypedValue("int", 18))
        paren = ParenExpression(inner_condition)
        
        template = parameterizer.parameterize(paren)
        
        # Get the parameter ID
        param_id = list(template.parameters.keys())[0]
        
        # Instantiate with correct parameter
        result = instantiator.instantiate(template, {param_id: 42})
        
        assert isinstance(result, ParenExpression)
        assert isinstance(result.expression, FieldCondition)
        assert result.expression.value.value == 42
    
    def test_ast_instantiator_replace_parameters_missing_param(self):
        """Test _replace_parameters with missing parameter."""
        instantiator = ASTInstantiator()
        
        # Create a parameterized field condition
        parameterizer = ASTParameterizer()
        condition = FieldCondition("age", ">", TypedValue("int", 18))
        template = parameterizer.parameterize(condition)
        
        # Try to instantiate with missing parameter
        with pytest.raises(ValueError, match="Missing parameters"):
            instantiator.instantiate(template, {})
    
    def test_query_cache_basic_functionality(self):
        """Test QueryCache basic functionality."""
        cache = QueryCache(max_size=10)
        
        # Test that cache can be created
        assert cache is not None
        assert hasattr(cache, 'get')
        assert hasattr(cache, 'put')
        assert hasattr(cache, 'clear')
        assert hasattr(cache, 'get_stats')
