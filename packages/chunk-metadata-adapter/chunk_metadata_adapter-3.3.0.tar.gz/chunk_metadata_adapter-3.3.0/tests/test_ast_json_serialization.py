"""
Tests for AST JSON serialization functionality.

This module tests the JSON serialization and deserialization of AST nodes,
including TypedValue, FieldCondition, LogicalOperator, and ParenExpression.

Test coverage:
- TypedValue serialization/deserialization
- FieldCondition serialization/deserialization
- LogicalOperator serialization/deserialization
- ParenExpression serialization/deserialization
- Complex AST serialization/deserialization
- Error handling for invalid JSON

Author: Development Team
Created: 2024-01-20
"""

import pytest
import json
from datetime import datetime
from chunk_metadata_adapter.ast import (
    TypedValue, FieldCondition, LogicalOperator, ParenExpression,
    ast_to_json, ast_from_json, ast_to_json_string, ast_from_json_string
)


class TestTypedValueSerialization:
    """Tests for TypedValue JSON serialization."""
    
    def test_int_value_serialization(self):
        """Test serialization of integer TypedValue."""
        value = TypedValue("int", 42)
        json_data = value.to_json()
        
        assert json_data["type"] == "int"
        assert json_data["value"] == 42
        
        # Test deserialization
        reconstructed = TypedValue.from_json(json_data)
        assert reconstructed.type == "int"
        assert reconstructed.value == 42
    
    def test_string_value_serialization(self):
        """Test serialization of string TypedValue."""
        value = TypedValue("str", "hello")
        json_data = value.to_json()
        
        assert json_data["type"] == "str"
        assert json_data["value"] == "hello"
        
        # Test deserialization
        reconstructed = TypedValue.from_json(json_data)
        assert reconstructed.type == "str"
        assert reconstructed.value == "hello"
    
    def test_float_value_serialization(self):
        """Test serialization of float TypedValue."""
        value = TypedValue("float", 3.14)
        json_data = value.to_json()
        
        assert json_data["type"] == "float"
        assert json_data["value"] == 3.14
        
        # Test deserialization
        reconstructed = TypedValue.from_json(json_data)
        assert reconstructed.type == "float"
        assert reconstructed.value == 3.14
    
    def test_list_value_serialization(self):
        """Test serialization of list TypedValue."""
        value = TypedValue("list", [1, 2, 3])
        json_data = value.to_json()
        
        assert json_data["type"] == "list"
        assert json_data["value"] == [1, 2, 3]
        
        # Test deserialization
        reconstructed = TypedValue.from_json(json_data)
        assert reconstructed.type == "list"
        assert reconstructed.value == [1, 2, 3]
    
    def test_dict_value_serialization(self):
        """Test serialization of dict TypedValue."""
        value = TypedValue("dict", {"key": "value"})
        json_data = value.to_json()
        
        assert json_data["type"] == "dict"
        assert json_data["value"] == {"key": "value"}
        
        # Test deserialization
        reconstructed = TypedValue.from_json(json_data)
        assert reconstructed.type == "dict"
        assert reconstructed.value == {"key": "value"}
    
    def test_date_value_serialization(self):
        """Test serialization of date TypedValue."""
        dt = datetime(2024, 1, 15, 12, 30, 45)
        value = TypedValue("date", dt)
        json_data = value.to_json()
        
        assert json_data["type"] == "date"
        assert json_data["value"] == dt.isoformat()
        
        # Test deserialization
        reconstructed = TypedValue.from_json(json_data)
        assert reconstructed.type == "date"
        assert isinstance(reconstructed.value, datetime)
        assert reconstructed.value == dt
    
    def test_null_value_serialization(self):
        """Test serialization of null TypedValue."""
        value = TypedValue("null", None)
        json_data = value.to_json()
        
        assert json_data["type"] == "null"
        assert json_data["value"] is None
        
        # Test deserialization
        reconstructed = TypedValue.from_json(json_data)
        assert reconstructed.type == "null"
        assert reconstructed.value is None
    
    def test_bool_value_serialization(self):
        """Test serialization of boolean TypedValue."""
        value = TypedValue("bool", True)
        json_data = value.to_json()
        
        assert json_data["type"] == "bool"
        assert json_data["value"] is True
        
        # Test deserialization
        reconstructed = TypedValue.from_json(json_data)
        assert reconstructed.type == "bool"
        assert reconstructed.value is True
    
    def test_invalid_json_data(self):
        """Test error handling for invalid JSON data."""
        with pytest.raises(ValueError, match="Data must be a dictionary"):
            TypedValue.from_json("not a dict")
        
        with pytest.raises(ValueError, match="Data must contain 'type' and 'value' fields"):
            TypedValue.from_json({"type": "int"})  # Missing value
        
        with pytest.raises(ValueError, match="Data must contain 'type' and 'value' fields"):
            TypedValue.from_json({"value": 42})  # Missing type


class TestFieldConditionSerialization:
    """Tests for FieldCondition JSON serialization."""
    
    def test_simple_field_condition_serialization(self):
        """Test serialization of simple FieldCondition."""
        condition = FieldCondition("age", ">", TypedValue("int", 18))
        json_data = condition.to_json()
        
        assert json_data["node_type"] == "field_condition"
        assert json_data["field"] == "age"
        assert json_data["operator"] == ">"
        assert json_data["value"]["type"] == "int"
        assert json_data["value"]["value"] == 18
        
        # Test deserialization
        reconstructed = FieldCondition.from_json(json_data)
        assert reconstructed.field == "age"
        assert reconstructed.operator == ">"
        assert reconstructed.value.type == "int"
        assert reconstructed.value.value == 18
    
    def test_nested_field_condition_serialization(self):
        """Test serialization of FieldCondition with nested field."""
        condition = FieldCondition("user.profile.name", "=", TypedValue("str", "John"))
        json_data = condition.to_json()
        
        assert json_data["field"] == "user.profile.name"
        assert json_data["operator"] == "="
        assert json_data["value"]["value"] == "John"
        
        # Test deserialization
        reconstructed = FieldCondition.from_json(json_data)
        assert reconstructed.field == "user.profile.name"
        assert reconstructed.operator == "="
        assert reconstructed.value.value == "John"
    
    def test_invalid_field_condition_json(self):
        """Test error handling for invalid FieldCondition JSON."""
        with pytest.raises(ValueError, match="Data must be a dictionary"):
            FieldCondition.from_json("not a dict")
        
        with pytest.raises(ValueError, match="Data must contain 'node_type' field"):
            FieldCondition.from_json({"field": "age"})
        
        with pytest.raises(ValueError, match="Expected node_type 'field_condition'"):
            FieldCondition.from_json({
                "node_type": "logical_operator",
                "field": "age",
                "operator": ">",
                "value": {"type": "int", "value": 18}
            })


class TestLogicalOperatorSerialization:
    """Tests for LogicalOperator JSON serialization."""
    
    def test_and_operator_serialization(self):
        """Test serialization of AND LogicalOperator."""
        condition1 = FieldCondition("age", ">", TypedValue("int", 18))
        condition2 = FieldCondition("status", "=", TypedValue("str", "active"))
        operator = LogicalOperator("AND", [condition1, condition2])
        
        json_data = operator.to_json()
        
        assert json_data["node_type"] == "logical_operator"
        assert json_data["operator"] == "AND"
        assert len(json_data["children"]) == 2
        assert json_data["children"][0]["node_type"] == "field_condition"
        assert json_data["children"][1]["node_type"] == "field_condition"
        
        # Test deserialization
        reconstructed = LogicalOperator.from_json(json_data)
        assert reconstructed.operator == "AND"
        assert len(reconstructed.children) == 2
        assert isinstance(reconstructed.children[0], FieldCondition)
        assert isinstance(reconstructed.children[1], FieldCondition)
    
    def test_or_operator_serialization(self):
        """Test serialization of OR LogicalOperator."""
        condition1 = FieldCondition("type", "=", TypedValue("str", "user"))
        condition2 = FieldCondition("type", "=", TypedValue("str", "admin"))
        operator = LogicalOperator("OR", [condition1, condition2])
        
        json_data = operator.to_json()
        
        assert json_data["operator"] == "OR"
        assert len(json_data["children"]) == 2
        
        # Test deserialization
        reconstructed = LogicalOperator.from_json(json_data)
        assert reconstructed.operator == "OR"
        assert len(reconstructed.children) == 2
    
    def test_not_operator_serialization(self):
        """Test serialization of NOT LogicalOperator."""
        condition = FieldCondition("deleted", "=", TypedValue("bool", True))
        operator = LogicalOperator("NOT", [condition])
        
        json_data = operator.to_json()
        
        assert json_data["operator"] == "NOT"
        assert len(json_data["children"]) == 1
        
        # Test deserialization
        reconstructed = LogicalOperator.from_json(json_data)
        assert reconstructed.operator == "NOT"
        assert len(reconstructed.children) == 1
    
    def test_invalid_logical_operator_json(self):
        """Test error handling for invalid LogicalOperator JSON."""
        with pytest.raises(ValueError, match="Expected node_type 'logical_operator'"):
            LogicalOperator.from_json({
                "node_type": "field_condition",
                "operator": "AND",
                "children": []
            })
        
        with pytest.raises(ValueError, match="Children must be a list"):
            LogicalOperator.from_json({
                "node_type": "logical_operator",
                "operator": "AND",
                "children": "not a list"
            })


class TestParenExpressionSerialization:
    """Tests for ParenExpression JSON serialization."""
    
    def test_paren_expression_serialization(self):
        """Test serialization of ParenExpression."""
        condition = FieldCondition("age", ">", TypedValue("int", 18))
        paren = ParenExpression(condition)
        
        json_data = paren.to_json()
        
        assert json_data["node_type"] == "paren_expression"
        assert json_data["expression"]["node_type"] == "field_condition"
        
        # Test deserialization
        reconstructed = ParenExpression.from_json(json_data)
        assert isinstance(reconstructed.expression, FieldCondition)
        assert reconstructed.expression.field == "age"
    
    def test_invalid_paren_expression_json(self):
        """Test error handling for invalid ParenExpression JSON."""
        with pytest.raises(ValueError, match="Expected node_type 'paren_expression'"):
            ParenExpression.from_json({
                "node_type": "field_condition",
                "expression": {"node_type": "field_condition"}
            })


class TestComplexASTSerialization:
    """Tests for complex AST serialization."""
    
    def test_complex_ast_serialization(self):
        """Test serialization of complex AST with multiple node types."""
        # Create complex AST: (age > 18 AND status = 'active') OR (vip = true)
        age_condition = FieldCondition("age", ">", TypedValue("int", 18))
        status_condition = FieldCondition("status", "=", TypedValue("str", "active"))
        vip_condition = FieldCondition("vip", "=", TypedValue("bool", True))
        
        and_operator = LogicalOperator("AND", [age_condition, status_condition])
        paren_expression = ParenExpression(and_operator)
        or_operator = LogicalOperator("OR", [paren_expression, vip_condition])
        
        # Test serialization
        json_data = or_operator.to_json()
        
        assert json_data["node_type"] == "logical_operator"
        assert json_data["operator"] == "OR"
        assert len(json_data["children"]) == 2
        
        # First child should be paren_expression
        assert json_data["children"][0]["node_type"] == "paren_expression"
        assert json_data["children"][0]["expression"]["node_type"] == "logical_operator"
        assert json_data["children"][0]["expression"]["operator"] == "AND"
        
        # Second child should be field_condition
        assert json_data["children"][1]["node_type"] == "field_condition"
        assert json_data["children"][1]["field"] == "vip"
        
        # Test deserialization
        reconstructed = LogicalOperator.from_json(json_data)
        assert reconstructed.operator == "OR"
        assert len(reconstructed.children) == 2
        
        # Verify structure
        assert isinstance(reconstructed.children[0], ParenExpression)
        assert isinstance(reconstructed.children[0].expression, LogicalOperator)
        assert reconstructed.children[0].expression.operator == "AND"
        assert isinstance(reconstructed.children[1], FieldCondition)
        assert reconstructed.children[1].field == "vip"


class TestUtilityFunctions:
    """Tests for utility serialization functions."""
    
    def test_ast_to_json(self):
        """Test ast_to_json utility function."""
        condition = FieldCondition("age", ">", TypedValue("int", 18))
        json_data = ast_to_json(condition)
        
        assert json_data["node_type"] == "field_condition"
        assert json_data["field"] == "age"
    
    def test_ast_from_json(self):
        """Test ast_from_json utility function."""
        json_data = {
            "node_type": "field_condition",
            "field": "age",
            "operator": ">",
            "value": {"type": "int", "value": 18}
        }
        
        ast = ast_from_json(json_data)
        assert isinstance(ast, FieldCondition)
        assert ast.field == "age"
    
    def test_ast_to_json_string(self):
        """Test ast_to_json_string utility function."""
        condition = FieldCondition("age", ">", TypedValue("int", 18))
        json_str = ast_to_json_string(condition, indent=2)
        
        # Should be valid JSON
        data = json.loads(json_str)
        assert data["node_type"] == "field_condition"
        assert data["field"] == "age"
    
    def test_ast_from_json_string(self):
        """Test ast_from_json_string utility function."""
        json_str = '{"node_type": "field_condition", "field": "age", "operator": ">", "value": {"type": "int", "value": 18}}'
        
        ast = ast_from_json_string(json_str)
        assert isinstance(ast, FieldCondition)
        assert ast.field == "age"
    
    def test_round_trip_serialization(self):
        """Test round-trip serialization (AST -> JSON -> AST)."""
        # Create complex AST
        condition1 = FieldCondition("age", ">", TypedValue("int", 18))
        condition2 = FieldCondition("status", "=", TypedValue("str", "active"))
        operator = LogicalOperator("AND", [condition1, condition2])
        
        # Round trip
        json_data = ast_to_json(operator)
        reconstructed = ast_from_json(json_data)
        
        # Verify structure is preserved
        assert isinstance(reconstructed, LogicalOperator)
        assert reconstructed.operator == "AND"
        assert len(reconstructed.children) == 2
        assert isinstance(reconstructed.children[0], FieldCondition)
        assert isinstance(reconstructed.children[1], FieldCondition)
        assert reconstructed.children[0].field == "age"
        assert reconstructed.children[1].field == "status"
    
    def test_round_trip_string_serialization(self):
        """Test round-trip string serialization (AST -> JSON string -> AST)."""
        condition = FieldCondition("age", ">", TypedValue("int", 18))
        
        # Round trip
        json_str = ast_to_json_string(condition)
        reconstructed = ast_from_json_string(json_str)
        
        # Verify structure is preserved
        assert isinstance(reconstructed, FieldCondition)
        assert reconstructed.field == "age"
        assert reconstructed.operator == ">"
        assert reconstructed.value.type == "int"
        assert reconstructed.value.value == 18 