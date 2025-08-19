"""
Tests for ast_json_serialization_demo.py to achieve 90%+ coverage.

This module tests the AST JSON serialization demo functionality.

Author: Development Team
Created: 2024-01-20
Updated: 2024-01-20
"""

import pytest
import json
from unittest.mock import patch
from io import StringIO
from datetime import datetime
from chunk_metadata_adapter.examples.ast_json_serialization_demo import (
    demo_basic_serialization,
    demo_complex_ast_serialization,
    demo_different_value_types,
    demo_round_trip_validation,
    demo_error_handling,
    demo_client_server_scenario,
    main
)
from chunk_metadata_adapter.ast import (
    TypedValue, FieldCondition, LogicalOperator, ParenExpression,
    ast_to_json, ast_from_json, ast_to_json_string, ast_from_json_string
)


class TestASTJSONSerializationDemo:
    """Tests for AST JSON serialization demo."""
    
    def test_demo_basic_serialization(self):
        """Test basic serialization demo."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            demo_basic_serialization()
            output = fake_out.getvalue()
            
            assert "=== Basic AST Node Serialization ===" in output
            assert "Serialized to JSON:" in output
            assert "Deserialized AST:" in output
            assert "Type:" in output
            assert "Field:" in output
            assert "Operator:" in output
            assert "Value:" in output
    
    def test_demo_complex_ast_serialization(self):
        """Test complex AST serialization demo."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            demo_complex_ast_serialization()
            output = fake_out.getvalue()
            
            assert "=== Complex AST Serialization ===" in output
            assert "Complex AST serialized to JSON string:" in output
            assert "Deserialized complex AST:" in output
            assert "Type:" in output
            assert "Operator:" in output
            assert "Number of children:" in output
    
    def test_demo_different_value_types(self):
        """Test different value types demo."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            demo_different_value_types()
            output = fake_out.getvalue()
            
            assert "=== Different Value Types Serialization ===" in output
            assert "Original:" in output
            assert "JSON:" in output
            assert "Reconstructed:" in output
    
    def test_demo_round_trip_validation(self):
        """Test round trip validation demo."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            demo_round_trip_validation()
            output = fake_out.getvalue()
            
            assert "Round-trip" in output
            assert "Original AST:" in output
            assert "Reconstructed AST:" in output
            assert "Round-trip successful:" in output
    
    def test_demo_error_handling(self):
        """Test error handling demo."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            demo_error_handling()
            output = fake_out.getvalue()
            
            assert "Error Handling" in output
            assert "Error:" in output
    
    def test_demo_client_server_scenario(self):
        """Test client server scenario demo."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            demo_client_server_scenario()
            output = fake_out.getvalue()
            
            assert "Client-Server" in output
            assert "Client:" in output
            assert "Server:" in output
            assert "JSON payload:" in output
            assert "successfully reconstructed" in output
    
    def test_main_function(self):
        """Test main function execution."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            main()
            output = fake_out.getvalue()
            
            assert "AST JSON Serialization Demo" in output
            assert "Basic AST Node Serialization" in output
            assert "Complex AST Serialization" in output
            assert "Different Value Types Serialization" in output
            assert "Round-trip" in output
            assert "Error Handling" in output
            assert "Client-Server" in output
            assert "completed successfully" in output
    
    def test_actual_serialization_functionality(self):
        """Test actual serialization functionality used in demo."""
        # Test basic serialization
        condition = FieldCondition("age", ">", TypedValue("int", 18))
        json_data = ast_to_json(condition)
        reconstructed = ast_from_json(json_data)
        
        assert isinstance(json_data, dict)
        assert json_data["node_type"] == "field_condition"
        assert json_data["field"] == "age"
        assert json_data["operator"] == ">"
        assert reconstructed.field == "age"
        assert reconstructed.operator == ">"
        assert reconstructed.value.type == "int"
        assert reconstructed.value.value == 18
        
        # Test complex serialization
        age_condition = FieldCondition("age", ">", TypedValue("int", 18))
        status_condition = FieldCondition("status", "=", TypedValue("str", "active"))
        and_operator = LogicalOperator("AND", [age_condition, status_condition])
        
        json_str = ast_to_json_string(and_operator, indent=2)
        reconstructed = ast_from_json_string(json_str)
        
        assert isinstance(json_str, str)
        assert "node_type" in json_str
        assert "logical_operator" in json_str
        assert reconstructed.operator == "AND"
        assert len(reconstructed.children) == 2
    
    def test_typed_value_serialization(self):
        """Test TypedValue serialization."""
        # Test different types
        int_value = TypedValue("int", 42)
        float_value = TypedValue("float", 3.14)
        str_value = TypedValue("str", "hello")
        bool_value = TypedValue("bool", True)
        null_value = TypedValue("null", None)
        list_value = TypedValue("list", [1, 2, 3])
        dict_value = TypedValue("dict", {"key": "value"})
        date_value = TypedValue("date", datetime(2024, 1, 15, 12, 30, 45))
        
        # Test serialization
        for value in [int_value, float_value, str_value, bool_value, null_value, 
                     list_value, dict_value, date_value]:
            json_data = value.to_json()
            reconstructed = TypedValue.from_json(json_data)
            
            assert json_data["type"] == value.type
            assert reconstructed.type == value.type
            assert reconstructed.value == value.value
    
    def test_error_handling_functionality(self):
        """Test error handling functionality."""
        # Test invalid JSON
        with pytest.raises(Exception):
            ast_from_json_string("invalid json")
        
        # Test missing required fields
        invalid_json = {"node_type": "field_condition"}
        with pytest.raises(Exception):
            ast_from_json(invalid_json)
        
        # Test invalid TypedValue JSON
        invalid_typed_json = {"type": "invalid_type"}
        with pytest.raises(Exception):
            TypedValue.from_json(invalid_typed_json)
    
    def test_round_trip_validation_functionality(self):
        """Test round trip validation functionality."""
        # Create complex AST
        age_condition = FieldCondition("age", ">", TypedValue("int", 18))
        status_condition = FieldCondition("status", "=", TypedValue("str", "active"))
        vip_condition = FieldCondition("vip", "=", TypedValue("bool", True))
        
        and_operator = LogicalOperator("AND", [age_condition, status_condition])
        paren_expression = ParenExpression(and_operator)
        or_operator = LogicalOperator("OR", [paren_expression, vip_condition])
        
        # Test round trip
        json_data = ast_to_json(or_operator)
        reconstructed = ast_from_json(json_data)
        
        # Validate structure
        assert reconstructed.operator == "OR"
        assert len(reconstructed.children) == 2
        assert isinstance(reconstructed.children[0], ParenExpression)
        assert isinstance(reconstructed.children[1], FieldCondition)
        
        # Validate nested structure
        paren_expr = reconstructed.children[0]
        assert isinstance(paren_expr.expression, LogicalOperator)
        assert paren_expr.expression.operator == "AND"
        assert len(paren_expr.expression.children) == 2 