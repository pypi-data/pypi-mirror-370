"""
Tests for AST nodes and basic structure.

This module provides comprehensive tests for the AST node classes,
including TypedValue, FieldCondition, LogicalOperator, and ParenExpression.
Tests cover validation, creation, and basic functionality.

Author: Development Team
Created: 2024-01-15
Updated: 2024-01-20
"""

import pytest
from datetime import datetime
from typing import Any
from chunk_metadata_adapter.ast import (
    TypedValue,
    FieldCondition,
    LogicalOperator,
    ParenExpression,
    ASTNode,
    ASTVisitor
)


class TestTypedValue:
    """Tests for TypedValue class."""
    
    def test_creation_with_valid_data(self):
        """Test creating TypedValue with valid data."""
        # Test different types
        int_val = TypedValue("int", 42)
        assert int_val.type == "int"
        assert int_val.value == 42
        
        str_val = TypedValue("str", "hello")
        assert str_val.type == "str"
        assert str_val.value == "hello"
        
        float_val = TypedValue("float", 3.14)
        assert float_val.type == "float"
        assert float_val.value == 3.14
        
        bool_val = TypedValue("bool", True)
        assert bool_val.type == "bool"
        assert bool_val.value == True
        
        null_val = TypedValue("null", None)
        assert null_val.type == "null"
        assert null_val.value is None
    
    def test_creation_with_invalid_type(self):
        """Test creating TypedValue with invalid type."""
        with pytest.raises(ValueError, match="Int type requires int value"):
            TypedValue("int", "not an int")
        
        with pytest.raises(ValueError, match="Str type requires string value"):
            TypedValue("str", 42)
        
        with pytest.raises(ValueError, match="Bool type requires bool value"):
            TypedValue("bool", "not a bool")
    
    def test_null_type_validation(self):
        """Test null type validation."""
        # Valid null
        null_val = TypedValue("null", None)
        assert null_val.type == "null"
        assert null_val.value is None
        
        # Invalid null with non-None value
        with pytest.raises(ValueError, match="Null type must have None value"):
            TypedValue("null", 42)
        
        # Invalid non-null with None value
        with pytest.raises(ValueError, match="Type int cannot have None value"):
            TypedValue("int", None)
    
    def test_value_constraints(self):
        """Test value-specific constraints."""
        # String too long
        with pytest.raises(ValueError, match="String value too long"):
            TypedValue("str", "x" * 10001)
        
        # List too large
        with pytest.raises(ValueError, match="List value too large"):
            TypedValue("list", list(range(1001)))
        
        # Dict too large
        with pytest.raises(ValueError, match="Dict value too large"):
            TypedValue("dict", {str(i): i for i in range(101)})
    
    def test_string_representation(self):
        """Test string representation of TypedValue."""
        assert str(TypedValue("int", 42)) == "42"
        assert str(TypedValue("str", "hello")) == '"hello"'
        assert str(TypedValue("null", None)) == "null"
        assert str(TypedValue("bool", True)) == "True"
    
    def test_repr_representation(self):
        """Test detailed string representation."""
        val = TypedValue("int", 42)
        assert "TypedValue" in repr(val)
        assert "type='int'" in repr(val)
        assert "value=42" in repr(val)


class TestFieldCondition:
    """Tests for FieldCondition class."""
    
    def test_creation_with_valid_data(self):
        """Test creating FieldCondition with valid data."""
        condition = FieldCondition("age", ">", TypedValue("int", 18))
        assert condition.field == "age"
        assert condition.operator == ">"
        assert condition.value.type == "int"
        assert condition.value.value == 18
        assert condition.node_type == "field_condition"
        assert condition.is_leaf == True
    
    def test_creation_with_nested_field(self):
        """Test creating FieldCondition with nested field."""
        condition = FieldCondition("user.profile.age", ">=", TypedValue("int", 21))
        assert condition.field == "user.profile.age"
        assert condition.operator == ">="
        assert condition.value.value == 21
    
    def test_invalid_field_name(self):
        """Test validation of invalid field names."""
        with pytest.raises(ValueError, match="Field name cannot be empty"):
            FieldCondition("", ">", TypedValue("int", 18))
        
        with pytest.raises(ValueError, match="Invalid field name"):
            FieldCondition("123field", ">", TypedValue("int", 18))
        
        with pytest.raises(ValueError, match="Invalid field name"):
            FieldCondition("field..name", ">", TypedValue("int", 18))
    
    def test_invalid_operator(self):
        """Test validation of invalid operators."""
        with pytest.raises(ValueError, match="Operator cannot be empty"):
            FieldCondition("age", "", TypedValue("int", 18))
        
        with pytest.raises(ValueError, match="Invalid operator"):
            FieldCondition("age", "invalid_op", TypedValue("int", 18))
    
    def test_valid_operators(self):
        """Test all valid operators."""
        valid_operators = [
            "=", "!=", ">", ">=", "<", "<=",
            "like", "~", "!~",
            "in", "not_in", "intersects",
            "contains_key", "contains_value"
        ]
        
        for operator in valid_operators:
            condition = FieldCondition("field", operator, TypedValue("str", "value"))
            assert condition.operator == operator
    
    def test_string_representation(self):
        """Test string representation of FieldCondition."""
        condition = FieldCondition("age", ">", TypedValue("int", 18))
        assert str(condition) == "age > 18"
        
        condition = FieldCondition("name", "=", TypedValue("str", "John"))
        assert str(condition) == 'name = "John"'
    
    def test_evaluate_not_implemented(self):
        """Test that evaluate raises NotImplementedError."""
        condition = FieldCondition("age", ">", TypedValue("int", 18))
        with pytest.raises(NotImplementedError, match="Evaluation implemented in FilterExecutor"):
            condition.evaluate({})


class TestLogicalOperator:
    """Tests for LogicalOperator class."""
    
    def test_creation_with_and_operator(self):
        """Test creating LogicalOperator with AND operator."""
        left = FieldCondition("age", ">", TypedValue("int", 18))
        right = FieldCondition("status", "=", TypedValue("str", "active"))
        
        op = LogicalOperator("AND", [left, right])
        assert op.operator == "AND"
        assert len(op.children) == 2
        assert op.node_type == "logical_operator"
        assert op.is_leaf == False
    
    def test_creation_with_or_operator(self):
        """Test creating LogicalOperator with OR operator."""
        left = FieldCondition("type", "=", TypedValue("str", "DocBlock"))
        right = FieldCondition("type", "=", TypedValue("str", "CodeBlock"))
        
        op = LogicalOperator("OR", [left, right])
        assert op.operator == "OR"
        assert len(op.children) == 2
    
    def test_creation_with_not_operator(self):
        """Test creating LogicalOperator with NOT operator."""
        child = FieldCondition("is_deleted", "=", TypedValue("bool", True))
        
        op = LogicalOperator("NOT", [child])
        assert op.operator == "NOT"
        assert len(op.children) == 1
    
    def test_invalid_operator(self):
        """Test validation of invalid operators."""
        child = FieldCondition("age", ">", TypedValue("int", 18))
        
        with pytest.raises(ValueError, match="Invalid logical operator"):
            LogicalOperator("INVALID", [child])
    
    def test_invalid_children_count(self):
        """Test validation of children count."""
        child = FieldCondition("age", ">", TypedValue("int", 18))
        
        # NOT with wrong number of children
        with pytest.raises(ValueError, match="NOT operator must have exactly one child"):
            LogicalOperator("NOT", [child, child])
        
        # AND with insufficient children
        with pytest.raises(ValueError, match="AND operator must have at least two children"):
            LogicalOperator("AND", [child])
    
    def test_string_representation(self):
        """Test string representation of LogicalOperator."""
        left = FieldCondition("age", ">", TypedValue("int", 18))
        right = FieldCondition("status", "=", TypedValue("str", "active"))
        
        and_op = LogicalOperator("AND", [left, right])
        assert str(and_op) == "(age > 18) AND (status = \"active\")"
        
        not_op = LogicalOperator("NOT", [left])
        assert str(not_op) == "NOT (age > 18)"
    
    def test_depth_calculation(self):
        """Test depth calculation for LogicalOperator."""
        leaf = FieldCondition("age", ">", TypedValue("int", 18))
        op = LogicalOperator("AND", [leaf, leaf])
        
        assert leaf.depth == 0
        assert op.depth == 1


class TestParenExpression:
    """Tests for ParenExpression class."""
    
    def test_creation_with_valid_expression(self):
        """Test creating ParenExpression with valid expression."""
        inner = FieldCondition("age", ">", TypedValue("int", 18))
        paren = ParenExpression(inner)
        
        assert paren.expression == inner
        assert paren.node_type == "paren_expression"
        assert len(paren.children) == 1
        assert paren.children[0] == inner
    
    def test_invalid_expression(self):
        """Test validation of invalid expressions."""
        with pytest.raises(ValueError, match="Expression cannot be None"):
            ParenExpression(None)
        
        with pytest.raises(ValueError, match="Expression must be an ASTNode"):
            ParenExpression("not a node")
    
    def test_string_representation(self):
        """Test string representation of ParenExpression."""
        inner = FieldCondition("age", ">", TypedValue("int", 18))
        paren = ParenExpression(inner)
        
        assert str(paren) == "(age > 18)"
    
    def test_evaluate_delegation(self):
        """Test that evaluate delegates to inner expression."""
        inner = FieldCondition("age", ">", TypedValue("int", 18))
        paren = ParenExpression(inner)
        
        # Both should raise the same NotImplementedError
        with pytest.raises(NotImplementedError):
            paren.evaluate({})
        
        with pytest.raises(NotImplementedError):
            inner.evaluate({})


class TestASTVisitor:
    """Tests for ASTVisitor class."""
    
    def test_visitor_interface(self):
        """Test that ASTVisitor is abstract."""
        with pytest.raises(TypeError):
            ASTVisitor()
    
    def test_visitor_methods_exist(self):
        """Test that visitor methods exist."""
        # Create a concrete visitor for testing
        class TestVisitor(ASTVisitor):
            def visit_field_condition(self, node: FieldCondition) -> Any:
                return "field_visited"
            
            def visit_logical_operator(self, node: LogicalOperator) -> Any:
                return "logical_visited"
            
            def visit_paren_expression(self, node: ParenExpression) -> Any:
                return "paren_visited"
        
        visitor = TestVisitor()
        assert hasattr(visitor, 'visit_field_condition')
        assert hasattr(visitor, 'visit_logical_operator')
        assert hasattr(visitor, 'visit_paren_expression')


class TestASTNodeIntegration:
    """Integration tests for AST nodes."""
    
    def test_complex_expression_creation(self):
        """Test creating a complex expression with multiple node types."""
        # Create: (age > 18 AND status = 'active') OR (type = 'DocBlock')
        
        # Left side: age > 18 AND status = 'active'
        age_condition = FieldCondition("age", ">", TypedValue("int", 18))
        status_condition = FieldCondition("status", "=", TypedValue("str", "active"))
        left_and = LogicalOperator("AND", [age_condition, status_condition])
        left_paren = ParenExpression(left_and)
        
        # Right side: type = 'DocBlock'
        type_condition = FieldCondition("type", "=", TypedValue("str", "DocBlock"))
        
        # Root: OR
        root_or = LogicalOperator("OR", [left_paren, type_condition])
        
        # Verify structure
        assert root_or.operator == "OR"
        assert len(root_or.children) == 2
        assert isinstance(root_or.children[0], ParenExpression)
        assert isinstance(root_or.children[1], FieldCondition)
        
        # Verify depth
        assert root_or.depth == 3  # OR -> Paren -> AND -> FieldCondition
    
    def test_real_world_semantic_chunk_fields(self):
        """Test AST nodes with real SemanticChunk field names."""
        # Test various field types from SemanticChunk
        conditions = [
            FieldCondition("type", "=", TypedValue("str", "DocBlock")),
            FieldCondition("quality_score", ">=", TypedValue("float", 0.8)),
            FieldCondition("year", ">=", TypedValue("int", 2020)),
            FieldCondition("is_public", "=", TypedValue("bool", True)),
            FieldCondition("tags", "intersects", TypedValue("list", ["ai", "ml"])),
            FieldCondition("block_meta.version", "=", TypedValue("str", "1.0")),
        ]
        
        for condition in conditions:
            assert condition.field is not None
            assert condition.operator is not None
            assert condition.value is not None
            assert condition.node_type == "field_condition"
    
    def test_nested_field_access(self):
        """Test nested field access patterns."""
        nested_fields = [
            "block_meta.version",
            "block_meta.author",
            "metrics.quality_score",
            "metrics.feedback.accepted",
        ]
        
        for field in nested_fields:
            condition = FieldCondition(field, "=", TypedValue("str", "test"))
            assert condition.field == field
            assert condition._is_valid_field_name(field) 