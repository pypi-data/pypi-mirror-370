"""
Transformer unit tests for FilterParser.

This module tests the FilterTransformer class and its methods for converting
Lark parse trees to AST nodes.

Author: Development Team
Created: 2024-06-13
Updated: 2024-06-13
"""
import pytest
from unittest.mock import Mock, patch
from lark import Token, Tree
from chunk_metadata_adapter.filter_parser import FilterTransformer
from chunk_metadata_adapter.ast import FieldCondition, LogicalOperator, ParenExpression, TypedValue

class TestFilterTransformer:
    """
    Tests for FilterTransformer class.
    """
    def setup_method(self):
        self.transformer = FilterTransformer()

    def test_parse_comparison_invalid_args(self):
        """
        Test parsing comparison with invalid arguments.
        """
        with pytest.raises(ValueError):
            self.transformer.comparison(["field", "operator"])  # Missing value

    def test_parse_not_field_invalid_args(self):
        """
        Test parsing NOT field with invalid arguments.
        """
        with pytest.raises(ValueError):
            self.transformer.not_field(["NOT"])  # Missing field name

    def test_parse_intersects_invalid_args(self):
        """
        Test parsing intersects with invalid arguments.
        """
        result = self.transformer.intersects(["field"])  # Single argument
        assert result == "field"

    def test_parse_field_name_multiple_parts(self):
        """
        Test parsing field name with multiple parts.
        """
        result = self.transformer.field_name(["user", "profile", "name"])
        assert result == "user.profile.name"

    def test_parse_operator_fallbacks(self):
        """
        Test parsing operators with fallback values.
        """
        # Test comparison_op fallback
        result = self.transformer.comparison_op([])
        assert result == "="
        
        # Test inclusion_op fallback
        result = self.transformer.inclusion_op([])
        assert result == "in"
        
        # Test string_op fallback
        result = self.transformer.string_op([])
        assert result == "like"
        
        # Test dict_op fallback
        result = self.transformer.dict_op([])
        assert result == "contains_key"

    def test_parse_date_string_detection(self):
        """
        Test date string detection in transformer.
        """
        # Test with quoted date
        assert self.transformer._is_date_string('"2024-01-01T00:00:00Z"')
        assert self.transformer._is_date_string("'2024-01-01'")
        
        # Test with unquoted date
        assert self.transformer._is_date_string("2024-01-01T00:00:00Z")
        
        # Test with non-date string
        assert not self.transformer._is_date_string("'not a date'")

    def test_parse_date_parsing(self):
        """
        Test date parsing in transformer.
        """
        # Test ISO format with Z
        result = self.transformer._parse_date('"2024-01-01T00:00:00Z"')
        assert "2024-01-01T00:00:00" in result
        
        # Test ISO format without Z
        result = self.transformer._parse_date("'2024-01-01T12:30:45'")
        assert "2024-01-01T12:30:45" in result
        
        # Test date with space separator
        result = self.transformer._parse_date("'2024-01-01 12:30:45'")
        assert "2024-01-01T12:30:45" in result
        
        # Test date with milliseconds
        result = self.transformer._parse_date("'2024-01-01 12:30:45.123'")
        assert "2024-01-01T12:30:45.123" in result
        
        # Test date only
        result = self.transformer._parse_date("'2024-01-01'")
        assert "2024-01-01T00:00:00" in result
        
        # Test invalid date (should return original string)
        result = self.transformer._parse_date("'invalid date'")
        assert result == "invalid date"

    def test_parse_default_transformer_methods(self):
        """
        Test __default__ transformer method with various data types.
        """
        # Test logical operators
        result = self.transformer.__default__("or", [Token("OR", "OR"), "expr1", "expr2"], None)
        assert isinstance(result, LogicalOperator)
        assert result.operator == "OR"
        
        result = self.transformer.__default__("and", [Token("AND", "AND"), "expr1", "expr2"], None)
        assert isinstance(result, LogicalOperator)
        assert result.operator == "AND"
        
        result = self.transformer.__default__("not", [Token("NOT", "NOT"), "expr1"], None)
        assert isinstance(result, LogicalOperator)
        assert result.operator == "NOT"
        
        # Test comparison operators
        assert self.transformer.__default__(">", [], None) == ">"
        assert self.transformer.__default__("<", [], None) == "<"
        assert self.transformer.__default__(">=", [], None) == ">="
        assert self.transformer.__default__("<=", [], None) == "<="
        assert self.transformer.__default__("=", [], None) == "="
        assert self.transformer.__default__("!=", [], None) == "!="
        
        # Test inclusion operators
        assert self.transformer.__default__("in", [], None) == "in"
        assert self.transformer.__default__("not_in", [], None) == "not_in"
        assert self.transformer.__default__("intersects", [], None) == "intersects"
        
        # Test string operators
        assert self.transformer.__default__("like", [], None) == "like"
        assert self.transformer.__default__("~", [], None) == "~"
        assert self.transformer.__default__("!~", [], None) == "!~"
        
        # Test dict operators
        assert self.transformer.__default__("contains_key", [], None) == "contains_key"
        assert self.transformer.__default__("contains_value", [], None) == "contains_value"
        
        # Test special constructions
        result = self.transformer.__default__("in_array", ["field", "in", TypedValue("list", [])], None)
        assert isinstance(result, FieldCondition)
        assert result.operator == "in"
        
        # Test intersects with empty children (returns string)
        result = self.transformer.__default__("intersects", [], None)
        assert result == "intersects"
        
        # Test intersects with 3 arguments
        result = self.transformer.__default__("intersects", ["field", "intersects", TypedValue("list", [])], None)
        assert isinstance(result, FieldCondition)
        assert result.operator == "intersects"
        
        # Test intersects with 1 argument (should return the argument)
        result = self.transformer.__default__("intersects", ["field"], None)
        assert result == "field"
        
        # Test intersects with 2 arguments where second is not TypedValue (should return first)
        result = self.transformer.__default__("intersects", ["field", "value"], None)
        assert result == "field"
        
        # Test array construction
        result = self.transformer.__default__("array", [TypedValue("str", "a"), TypedValue("str", "b")], None)
        assert isinstance(result, TypedValue)
        assert result.type == "list"
        assert result.value == ["a", "b"]
        
        # Test dict construction
        result = self.transformer.__default__("dict", [("key", TypedValue("str", "value"))], None)
        assert isinstance(result, TypedValue)
        assert result.type == "dict"
        
        # Test pair construction
        result = self.transformer.__default__("pair", ["key", TypedValue("str", "value")], None)
        assert isinstance(result, tuple)
        assert result[0] == "key"
        assert result[1] == "value"

    def test_parse_token_methods(self):
        """
        Test token transformation methods.
        """
        # Test comparison operator tokens
        assert self.transformer.EQUAL(Token("EQUAL", "=")) == "="
        assert self.transformer.NOTEQUAL(Token("NOTEQUAL", "!=")) == "!="
        assert self.transformer.MORETHAN(Token("MORETHAN", ">")) == ">"
        assert self.transformer.MOREEQUAL(Token("MOREEQUAL", ">=")) == ">="
        assert self.transformer.LESSTHAN(Token("LESSTHAN", "<")) == "<"
        assert self.transformer.LESSEQUAL(Token("LESSEQUAL", "<=")) == "<="
        
        # Test string operator tokens
        assert self.transformer.LIKE(Token("LIKE", "like")) == "like"
        assert self.transformer.TILDE(Token("TILDE", "~")) == "~"
        assert self.transformer.NOT_TILDE(Token("NOT_TILDE", "!~")) == "!~"
        
        # Test inclusion operator tokens
        assert self.transformer.IN(Token("IN", "in")) == "in"
        assert self.transformer.NOT_IN(Token("NOT_IN", "not_in")) == "not_in"
        assert self.transformer.INTERSECTS(Token("INTERSECTS", "intersects")) == "intersects"
        
        # Test dict operator tokens
        assert self.transformer.CONTAINS_KEY(Token("CONTAINS_KEY", "contains_key")) == "contains_key"
        assert self.transformer.CONTAINS_VALUE(Token("CONTAINS_VALUE", "contains_value")) == "contains_value"
        
        # Test logical operator tokens
        assert self.transformer.NOT(Token("NOT", "NOT")) == "NOT"
        assert self.transformer.AND(Token("AND", "AND")) == "AND"
        assert self.transformer.OR(Token("OR", "OR")) == "OR"
        assert self.transformer.XOR(Token("XOR", "XOR")) == "XOR"

    def test_parse_value_methods(self):
        """
        Test value transformation methods.
        """
        # Test number method
        result = self.transformer.number([Token("NUMBER", "42")])
        assert isinstance(result, TypedValue)
        assert result.type == "int"
        assert result.value == 42
        
        result = self.transformer.number([Token("NUMBER", "3.14")])
        assert result.type == "float"
        assert result.value == 3.14
        
        # Test string method
        result = self.transformer.string([Token("STRING", '"hello"')])
        assert result.type == "str"
        assert result.value == "hello"
        
        result = self.transformer.string([Token("STRING", "'world'")])
        assert result.type == "str"
        assert result.value == "world"
        
        # Test boolean method
        result = self.transformer.boolean([Token("BOOLEAN", "true")])
        assert result.type == "bool"
        assert result.value == True
        
        result = self.transformer.boolean([Token("BOOLEAN", "false")])
        assert result.type == "bool"
        assert result.value == False
        
        # Test null_value method
        result = self.transformer.null_value([Token("NULL", "null")])
        assert result.type == "null"
        assert result.value is None
        
        # Test array_value method
        result = self.transformer.array_value([TypedValue("str", "a"), TypedValue("str", "b")])
        assert result.type == "list"
        assert result.value == ["a", "b"]
        
        # Test dict_value method
        result = self.transformer.dict_value([("key", "value")])
        assert result.type == "dict"
        assert result.value == {"key": "value"}
        
        # Test pair method
        result = self.transformer.pair(["key", TypedValue("str", "value")])
        assert isinstance(result, tuple)
        assert result[0] == "key"
        assert result[1] == "value"
        
        # Test date_value method
        result = self.transformer.date_value([Token("DATE", '"2024-01-01T00:00:00Z"')])
        assert result.type == "date"
        
        # Test primitive_value method
        value = TypedValue("str", "test")
        result = self.transformer.primitive_value([value])
        assert result == value
        
        # Test value method
        value = TypedValue("int", 42)
        result = self.transformer.value([value])
        assert result == value

    def test_parse_literal_tokens(self):
        """
        Test literal token transformation methods.
        """
        # Test boolean literals
        result = self.transformer.TRUE(Token("TRUE", "true"))
        assert result.type == "bool"
        assert result.value == True
        
        result = self.transformer.FALSE(Token("FALSE", "false"))
        assert result.type == "bool"
        assert result.value == False
        
        # Test null literal
        result = self.transformer.NULL(Token("NULL", "null"))
        assert result.type == "null"
        assert result.value is None
        
        # Test integer literal
        result = self.transformer.INT(Token("INT", "42"))
        assert result.type == "int"
        assert result.value == 42
        
        # Test float literal
        result = self.transformer.FLOAT(Token("FLOAT", "3.14"))
        assert result.type == "float"
        assert result.value == 3.14
        
        # Test string literals
        result = self.transformer.STRING(Token("STRING", '"hello"'))
        assert result.type == "str"
        assert result.value == "hello"
        
        # Test string with date detection
        result = self.transformer.STRING(Token("STRING", '"2024-01-01T00:00:00Z"'))
        assert result.type == "date"
        
        # Test raw string literals
        result = self.transformer.RAW_STRING(Token("RAW_STRING", "'world'"))
        assert result.type == "str"
        assert result.value == "world"
        
        # Test raw string with date detection
        result = self.transformer.RAW_STRING(Token("RAW_STRING", "'2024-01-01'"))
        assert result.type == "date"
        
        # Test date ISO literal
        result = self.transformer.DATE_ISO(Token("DATE_ISO", '"2024-01-01T00:00:00Z"'))
        assert result.type == "date"
        
        # Test CNAME literal
        result = self.transformer.CNAME(Token("CNAME", "field_name"))
        assert result == "field_name"
        
        # Test NUMBER literal
        result = self.transformer.NUMBER(Token("NUMBER", "42"))
        assert result.type == "int"
        assert result.value == 42
        
        result = self.transformer.NUMBER(Token("NUMBER", "3.14"))
        assert result.type == "float"
        assert result.value == 3.14

    def test_parse_comparator_method(self):
        """
        Test comparator method.
        """
        # Test with operator
        result = self.transformer.comparator(["="])
        assert result == "="
        
        # Test fallback
        result = self.transformer.comparator([])
        assert result == "="

    def test_parse_complex_date_formats(self):
        """
        Test parsing complex date formats.
        """
        # Test various date formats
        date_formats = [
            "2024-01-01T00:00:00Z",
            "2024-01-01T12:30:45",
            "2024-01-01",
            "2024-01-01 12:30:45",
            "2024-01-01 12:30:45.123"
        ]
        
        for date_str in date_formats:
            result = self.transformer._parse_date(date_str)
            assert "2024-01-01" in result

    def test_parse_edge_case_transformations(self):
        """
        Test edge case transformations.
        """
        # Test not_expr with single argument
        result = self.transformer.not_expr([TypedValue("bool", True)])
        assert result == TypedValue("bool", True)
        
        # Test not_expr with NOT token
        not_token = Token("NOT", "NOT")
        result = self.transformer.not_expr([not_token, TypedValue("bool", True)])
        assert isinstance(result, LogicalOperator)
        assert result.operator == "NOT"
        
        # Test not_expr with other first argument
        result = self.transformer.not_expr([TypedValue("bool", True), TypedValue("bool", False)])
        assert result == TypedValue("bool", True) 