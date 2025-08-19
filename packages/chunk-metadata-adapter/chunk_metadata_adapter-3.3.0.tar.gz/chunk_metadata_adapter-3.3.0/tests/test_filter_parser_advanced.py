"""
Advanced unit tests for FilterParser.

This module tests advanced functionality of FilterParser including
error handling, validation, and edge cases.

Author: Development Team
Created: 2024-06-13
Updated: 2024-06-13
"""
import pytest
from unittest.mock import Mock, patch
from lark import Token, Tree
from chunk_metadata_adapter.filter_parser import FilterParser, FilterParseError, FilterTransformer
from chunk_metadata_adapter.ast import FieldCondition, LogicalOperator, ParenExpression, TypedValue

class TestFilterParserAdvanced:
    """
    Advanced tests for FilterParser.
    """
    def setup_method(self):
        self.parser = FilterParser()

    def test_parse_filter_parser_methods(self):
        """
        Test FilterParser specific methods.
        """
        # Test initialization with custom max_query_length
        parser = FilterParser(max_query_length=5000)
        assert parser.max_query_length == 5000
        
        # Test _get_parser method
        parser_instance = FilterParser._get_parser()
        assert parser_instance is not None
        
        # Test _validate_query method
        parser = FilterParser()
        
        # Test empty query validation
        with pytest.raises(FilterParseError):
            parser._validate_query("")
        
        # Test whitespace-only query validation
        with pytest.raises(FilterParseError):
            parser._validate_query("   ")
        
        # Test query too long validation
        long_query = "a" * 10001
        with pytest.raises(FilterParseError):
            parser._validate_query(long_query)
        
        # Test valid query validation
        parser._validate_query("age > 18")  # Should not raise

    def test_parse_error_handling_with_position(self):
        """
        Test error handling with position information.
        """
        # Test LarkError with position
        with patch('chunk_metadata_adapter.filter_parser.Lark') as mock_lark:
            mock_parser = Mock()
            mock_parser.parse.side_effect = Exception("Parse error")
            mock_lark.return_value = mock_parser
            
            parser = FilterParser()
            with pytest.raises(FilterParseError) as exc_info:
                parser.parse("invalid query")
            
            assert "Parse error" in str(exc_info.value)

    def test_parse_filter_parse_error_initialization(self):
        """
        Test FilterParseError initialization.
        """
        error = FilterParseError("Test error", "test query", 42)
        assert error.message == "Test error"
        assert error.query == "test query"
        assert error.position == 42
        
        # Test without position
        error = FilterParseError("Test error", "test query")
        assert error.position is None

    def test_parse_or_expr_with_tokens(self):
        """
        Test or_expr method with token filtering.
        """
        transformer = FilterTransformer()
        
        # Test with OR tokens
        or_token = Token("OR", "OR")
        expr1 = TypedValue("int", 1)
        expr2 = TypedValue("int", 2)
        
        result = transformer.or_expr([expr1, or_token, expr2])
        assert isinstance(result, LogicalOperator)
        assert result.operator == "OR"
        assert len(result.children) == 2
        assert result.children[0] == expr1
        assert result.children[1] == expr2
        
        # Test with single expression
        result = transformer.or_expr([expr1])
        assert result == expr1

    def test_parse_and_expr_with_tokens(self):
        """
        Test and_expr method with token filtering.
        """
        transformer = FilterTransformer()
        
        # Test with AND tokens
        and_token = Token("AND", "AND")
        expr1 = TypedValue("int", 1)
        expr2 = TypedValue("int", 2)
        
        result = transformer.and_expr([expr1, and_token, expr2])
        assert isinstance(result, LogicalOperator)
        assert result.operator == "AND"
        assert len(result.children) == 2
        assert result.children[0] == expr1
        assert result.children[1] == expr2
        
        # Test with single expression
        result = transformer.and_expr([expr1])
        assert result == expr1

    def test_parse_xor_expr_with_tokens(self):
        """
        Test xor_expr method with token filtering.
        """
        transformer = FilterTransformer()
        
        # Test with XOR tokens
        xor_token = Token("XOR", "XOR")
        expr1 = TypedValue("int", 1)
        expr2 = TypedValue("int", 2)
        
        result = transformer.xor_expr([expr1, xor_token, expr2])
        assert isinstance(result, LogicalOperator)
        assert result.operator == "XOR"
        assert len(result.children) == 2
        assert result.children[0] == expr1
        assert result.children[1] == expr2
        
        # Test with single expression
        result = transformer.xor_expr([expr1])
        assert result == expr1

    def test_parse_comparison_with_tuple_value(self):
        """
        Test comparison method with tuple value from pair.
        """
        transformer = FilterTransformer()
        
        # Test with tuple value (from pair)
        field_name = "meta"
        operator = "="
        tuple_value = ("key", TypedValue("str", "value"))
        
        result = transformer.comparison([field_name, operator, tuple_value])
        assert isinstance(result, FieldCondition)
        assert result.field == field_name
        assert result.operator == operator
        assert result.value.type == "dict"
        assert result.value.value == {"key": "value"}

    def test_parse_comparison_with_normal_value(self):
        """
        Test comparison method with normal value.
        """
        transformer = FilterTransformer()
        
        # Test with normal value
        field_name = "age"
        operator = ">"
        value = TypedValue("int", 18)
        
        result = transformer.comparison([field_name, operator, value])
        assert isinstance(result, FieldCondition)
        assert result.field == field_name
        assert result.operator == operator
        assert result.value == value

    def test_parse_not_field_with_tokens(self):
        """
        Test not_field method with NOT token.
        """
        transformer = FilterTransformer()
        
        # Test with NOT token
        not_token = Token("NOT", "NOT")
        field_name = "is_deleted"
        
        result = transformer.not_field([not_token, field_name])
        assert isinstance(result, FieldCondition)
        assert result.field == field_name
        assert result.operator == "="
        assert result.value.type == "bool"
        assert result.value.value == False

    def test_parse_intersects_with_three_args(self):
        """
        Test intersects method with three arguments.
        """
        transformer = FilterTransformer()
        
        field = "tags"
        operator = "intersects"
        value = TypedValue("list", ["ai", "ml"])
        
        result = transformer.intersects([field, operator, value])
        assert isinstance(result, FieldCondition)
        assert result.field == field
        assert result.operator == "intersects"
        assert result.value == value

    def test_parse_intersects_with_two_args(self):
        """
        Test intersects method with two arguments.
        """
        transformer = FilterTransformer()
        
        field = "tags"
        value = TypedValue("list", ["ai", "ml"])
        
        result = transformer.intersects([field, value])
        assert isinstance(result, FieldCondition)
        assert result.field == field
        assert result.operator == "intersects"
        assert result.value == value

    def test_parse_paren_expr(self):
        """
        Test paren_expr method.
        """
        transformer = FilterTransformer()
        
        # Создаем FieldCondition как ASTNode
        inner_expr = FieldCondition("field", "=", TypedValue("int", 42))
        result = transformer.paren_expr([inner_expr])
        
        assert isinstance(result, ParenExpression)
        assert result.expression == inner_expr

    def test_parse_field_name_with_multiple_parts(self):
        """
        Test field_name method with multiple parts.
        """
        transformer = FilterTransformer()
        
        parts = ["user", "profile", "name"]
        result = transformer.field_name(parts)
        assert result == "user.profile.name"

    def test_parse_field_name_with_single_part(self):
        """
        Test field_name method with single part.
        """
        transformer = FilterTransformer()
        
        parts = ["age"]
        result = transformer.field_name(parts)
        assert result == "age"

    def test_parse_array_value_with_typed_values(self):
        """
        Test array_value method with TypedValue objects.
        """
        transformer = FilterTransformer()
        
        values = [TypedValue("str", "a"), TypedValue("str", "b")]
        result = transformer.array_value(values)
        
        assert isinstance(result, TypedValue)
        assert result.type == "list"
        assert result.value == ["a", "b"]

    def test_parse_array_value_with_strings(self):
        """
        Test array_value method with string values.
        """
        transformer = FilterTransformer()
        
        values = ["'a'", "'b'"]
        result = transformer.array_value(values)
        
        assert isinstance(result, TypedValue)
        assert result.type == "list"
        assert result.value == ["a", "b"]

    def test_parse_dict_value(self):
        """
        Test dict_value method.
        """
        transformer = FilterTransformer()
        
        pairs = [("key1", "value1"), ("key2", "value2")]
        result = transformer.dict_value(pairs)
        
        assert isinstance(result, TypedValue)
        assert result.type == "dict"
        assert result.value == {"key1": "value1", "key2": "value2"}

    def test_parse_pair_with_typed_value(self):
        """
        Test pair method with TypedValue.
        """
        transformer = FilterTransformer()
        
        key = "version"
        value = TypedValue("str", "1.0")
        result = transformer.pair([key, value])
        
        assert isinstance(result, tuple)
        assert result[0] == "version"
        assert result[1] == "1.0"

    def test_parse_pair_with_normal_value(self):
        """
        Test pair method with normal value.
        """
        transformer = FilterTransformer()
        
        key = "version"
        value = "1.0"
        result = transformer.pair([key, value])
        
        assert isinstance(result, tuple)
        assert result[0] == "version"
        assert result[1] == "1.0"

    def test_parse_date_value_with_quoted_date(self):
        """
        Test date_value method with quoted date.
        """
        transformer = FilterTransformer()
        
        date_token = Token("DATE", '"2024-01-01T00:00:00Z"')
        result = transformer.date_value([date_token])
        
        assert isinstance(result, TypedValue)
        assert result.type == "date"

    def test_parse_primitive_value(self):
        """
        Test primitive_value method.
        """
        transformer = FilterTransformer()
        
        value = TypedValue("str", "test")
        result = transformer.primitive_value([value])
        assert result == value

    def test_parse_value(self):
        """
        Test value method.
        """
        transformer = FilterTransformer()
        
        value = TypedValue("int", 42)
        result = transformer.value([value])
        assert result == value

    def test_parse_default_with_string_operators(self):
        """
        Test __default__ method with string operators.
        """
        transformer = FilterTransformer()
        
        # Test with string AND
        result = transformer.__default__("and", ["expr1", "AND", "expr2"], None)
        assert isinstance(result, LogicalOperator)
        assert result.operator == "AND"
        
        # Test with string OR
        result = transformer.__default__("or", ["expr1", "OR", "expr2"], None)
        assert isinstance(result, LogicalOperator)
        assert result.operator == "OR"
        
        # Test with string NOT
        result = transformer.__default__("not", ["NOT", "expr1"], None)
        assert isinstance(result, LogicalOperator)
        assert result.operator == "NOT"

    def test_parse_default_with_array_construction(self):
        """
        Test __default__ method with array construction.
        """
        transformer = FilterTransformer()
        
        # Test array with TypedValue
        result = transformer.__default__("array", [TypedValue("str", "a"), TypedValue("str", "b")], None)
        assert isinstance(result, TypedValue)
        assert result.type == "list"
        assert result.value == ["a", "b"]
        
        # Test array with strings
        result = transformer.__default__("array", ["'a'", "'b'"], None)
        assert isinstance(result, TypedValue)
        assert result.type == "list"
        assert result.value == ["a", "b"]

    def test_parse_default_with_dict_construction(self):
        """
        Test __default__ method with dict construction.
        """
        transformer = FilterTransformer()
        
        # Test dict with pairs
        pair1 = ("key1", TypedValue("str", "value1"))
        pair2 = ("key2", TypedValue("str", "value2"))
        result = transformer.__default__("dict", [pair1, pair2], None)
        
        assert isinstance(result, TypedValue)
        assert result.type == "dict"
        assert result.value == {"key1": "value1", "key2": "value2"}

    def test_parse_default_with_pair_construction(self):
        """
        Test __default__ method with pair construction.
        """
        transformer = FilterTransformer()
        
        # Test pair with TypedValue
        result = transformer.__default__("pair", ["key", TypedValue("str", "value")], None)
        assert isinstance(result, tuple)
        assert result[0] == "key"
        assert result[1] == "value"
        
        # Test pair with normal value
        result = transformer.__default__("pair", ["key", "value"], None)
        assert isinstance(result, tuple)
        assert result[0] == "key"
        assert result[1] == "value"

    def test_parse_default_fallback(self):
        """
        Test __default__ method fallback behavior.
        """
        transformer = FilterTransformer()
        
        # Test with unknown data type
        result = transformer.__default__("unknown", ["value"], None)
        assert result == "value"
        
        # Test with empty children
        result = transformer.__default__("unknown", [], None)
        assert result == "unknown" 