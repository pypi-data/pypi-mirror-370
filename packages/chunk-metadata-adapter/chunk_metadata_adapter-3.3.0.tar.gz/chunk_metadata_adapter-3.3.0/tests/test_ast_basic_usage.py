"""
Tests for ast_basic_usage.py to achieve 90%+ coverage.

This module tests the basic AST usage example functionality.

Author: Development Team
Created: 2024-01-20
Updated: 2024-01-20
"""

import pytest
from unittest.mock import patch
from io import StringIO
from chunk_metadata_adapter.examples.ast_basic_usage import main
from chunk_metadata_adapter.ast import (
    TypedValue,
    FieldCondition,
    LogicalOperator,
    ParenExpression
)


class TestASTBasicUsage:
    """Tests for AST basic usage example."""
    
    def test_main_function_execution(self):
        """Test that main function executes without errors."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            main()
            output = fake_out.getvalue()
            
            # Check that output contains expected content
            assert "=== AST Basic Usage Example ===" in output
            assert "Creating simple field conditions:" in output
            assert "Creating logical operators:" in output
            assert "Creating complex expression:" in output
            assert "Nested field access:" in output
            assert "Different value types:" in output
            assert "Validation examples:" in output
            assert "=== Example completed successfully! ===" in output
    
    def test_field_condition_creation(self):
        """Test field condition creation."""
        age_condition = FieldCondition("age", ">", TypedValue("int", 18))
        assert age_condition.field == "age"
        assert age_condition.operator == ">"
        assert age_condition.value.type == "int"
        assert age_condition.value.value == 18
    
    def test_logical_operator_creation(self):
        """Test logical operator creation."""
        age_condition = FieldCondition("age", ">", TypedValue("int", 18))
        status_condition = FieldCondition("status", "=", TypedValue("str", "active"))
        and_condition = LogicalOperator("AND", [age_condition, status_condition])
        
        assert and_condition.operator == "AND"
        assert len(and_condition.children) == 2
        assert and_condition.children[0] == age_condition
        assert and_condition.children[1] == status_condition
    
    def test_paren_expression_creation(self):
        """Test parenthesized expression creation."""
        age_condition = FieldCondition("age", ">", TypedValue("int", 18))
        status_condition = FieldCondition("status", "=", TypedValue("str", "active"))
        and_condition = LogicalOperator("AND", [age_condition, status_condition])
        paren_expr = ParenExpression(and_condition)
        
        assert paren_expr.expression == and_condition
    
    def test_complex_expression_creation(self):
        """Test complex expression creation."""
        age_condition = FieldCondition("age", ">", TypedValue("int", 18))
        status_condition = FieldCondition("status", "=", TypedValue("str", "active"))
        and_condition = LogicalOperator("AND", [age_condition, status_condition])
        left_paren = ParenExpression(and_condition)
        type_condition = FieldCondition("type", "=", TypedValue("str", "DocBlock"))
        complex_expr = LogicalOperator("OR", [left_paren, type_condition])
        
        assert complex_expr.operator == "OR"
        assert len(complex_expr.children) == 2
        assert isinstance(complex_expr.children[0], ParenExpression)
        assert complex_expr.children[1] == type_condition
        assert complex_expr.depth > 0
        assert not complex_expr.is_leaf
    
    def test_nested_field_access(self):
        """Test nested field access."""
        nested_condition = FieldCondition("block_meta.version", "=", TypedValue("str", "1.0"))
        assert nested_condition.field == "block_meta.version"
        assert nested_condition.value.type == "str"
        assert nested_condition.value.value == "1.0"
    
    def test_different_value_types(self):
        """Test different value types."""
        float_condition = FieldCondition("quality_score", ">=", TypedValue("float", 0.8))
        bool_condition = FieldCondition("is_public", "=", TypedValue("bool", True))
        list_condition = FieldCondition("tags", "intersects", TypedValue("list", ["ai", "ml"]))
        null_condition = FieldCondition("deleted_at", "=", TypedValue("null", None))
        
        assert float_condition.value.type == "float"
        assert float_condition.value.value == 0.8
        assert bool_condition.value.type == "bool"
        assert bool_condition.value.value is True
        assert list_condition.value.type == "list"
        assert list_condition.value.value == ["ai", "ml"]
        assert null_condition.value.type == "null"
        assert null_condition.value.value is None
    
    def test_validation_examples(self):
        """Test validation examples."""
        # Test invalid field name
        with pytest.raises(ValueError):
            FieldCondition("123field", ">", TypedValue("int", 18))
        
        # Test invalid operator
        with pytest.raises(ValueError):
            FieldCondition("age", "invalid_op", TypedValue("int", 18))
        
        # Test invalid type
        with pytest.raises(ValueError):
            TypedValue("int", "not an int")
    
    def test_typed_value_creation(self):
        """Test TypedValue creation."""
        int_value = TypedValue("int", 42)
        str_value = TypedValue("str", "hello")
        float_value = TypedValue("float", 3.14)
        bool_value = TypedValue("bool", True)
        list_value = TypedValue("list", [1, 2, 3])
        null_value = TypedValue("null", None)
        
        assert int_value.type == "int"
        assert int_value.value == 42
        assert str_value.type == "str"
        assert str_value.value == "hello"
        assert float_value.type == "float"
        assert float_value.value == 3.14
        assert bool_value.type == "bool"
        assert bool_value.value is True
        assert list_value.type == "list"
        assert list_value.value == [1, 2, 3]
        assert null_value.type == "null"
        assert null_value.value is None
    
    def test_ast_node_properties(self):
        """Test AST node properties."""
        age_condition = FieldCondition("age", ">", TypedValue("int", 18))
        status_condition = FieldCondition("status", "=", TypedValue("str", "active"))
        and_condition = LogicalOperator("AND", [age_condition, status_condition])
        
        # Test depth calculation
        assert age_condition.depth == 0
        assert and_condition.depth == 1
        
        # Test is_leaf property
        assert age_condition.is_leaf
        assert not and_condition.is_leaf
        
        # Test node_type
        assert age_condition.node_type == "field_condition"
        assert and_condition.node_type == "logical_operator" 