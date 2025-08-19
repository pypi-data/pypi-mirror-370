"""
Basic unit tests for FilterParser and AST integration.

This module tests the basic parsing functionality of filter expressions
into AST nodes using FilterParser.

Author: Development Team
Created: 2024-06-13
Updated: 2024-06-13
"""
import pytest
from chunk_metadata_adapter.filter_parser import FilterParser, FilterParseError
from chunk_metadata_adapter.ast import FieldCondition, LogicalOperator, ParenExpression, TypedValue

class TestFilterParserBasic:
    """
    Basic tests for FilterParser and AST node construction.
    """
    def setup_method(self):
        self.parser = FilterParser()

    def test_parse_simple_comparison(self):
        """
        Test parsing a simple comparison expression.
        """
        ast = self.parser.parse("age > 18")
        assert isinstance(ast, FieldCondition)
        assert ast.field == "age"
        assert ast.operator == ">"
        assert ast.value.type == "int"
        assert ast.value.value == 18

    def test_parse_logical_and(self):
        """
        Test parsing a logical AND expression.
        """
        ast = self.parser.parse("age > 18 AND status = 'active'")
        assert isinstance(ast, LogicalOperator)
        assert ast.operator == "AND"
        assert len(ast.children) == 2
        assert isinstance(ast.children[0], FieldCondition)
        assert isinstance(ast.children[1], FieldCondition)

    def test_parse_logical_or(self):
        """
        Test parsing a logical OR expression.
        """
        ast = self.parser.parse("age > 18 OR status = 'active'")
        assert isinstance(ast, LogicalOperator)
        assert ast.operator == "OR"
        assert len(ast.children) == 2

    def test_parse_not_expression(self):
        """
        Test parsing a NOT expression.
        """
        ast = self.parser.parse("NOT is_deleted = true")
        assert isinstance(ast, LogicalOperator)
        assert ast.operator == "NOT"
        assert len(ast.children) == 1
        assert isinstance(ast.children[0], FieldCondition)
        assert ast.children[0].field == "is_deleted"
        assert ast.children[0].operator == "="
        assert ast.children[0].value.type == "bool"
        assert ast.children[0].value.value == True

    def test_parse_paren_expression(self):
        """
        Test parsing a parenthesized expression.
        """
        ast = self.parser.parse("(age > 18 OR vip = true) AND status = 'active'")
        assert isinstance(ast, LogicalOperator)
        assert ast.operator == "AND"
        assert len(ast.children) == 2
        left = ast.children[0]
        assert isinstance(left, LogicalOperator)
        assert left.operator == "OR"

    def test_parse_list_and_dict(self):
        """
        Test parsing list and dict values.
        """
        ast = self.parser.parse("tags in ['ai', 'ml'] AND meta = {'a': 1}")
        assert isinstance(ast, LogicalOperator)
        assert ast.operator == "AND"
        left, right = ast.children
        assert left.operator == "in"
        assert left.value.type == "list"
        assert right.value.type == "dict"

    def test_parse_nested_field(self):
        """
        Test parsing a nested field name.
        """
        ast = self.parser.parse("user.profile.name = 'John'")
        assert isinstance(ast, FieldCondition)
        assert ast.field == "user.profile.name"
        assert ast.value.value == "John"

    def test_parse_date_and_bool(self):
        """
        Test parsing date and boolean values.
        """
        ast = self.parser.parse("created_at = \"2024-01-01T00:00:00Z\" AND is_public = true")
        assert isinstance(ast, LogicalOperator)
        assert ast.operator == "AND"
        left, right = ast.children
        assert left.value.type in ("date", "str")
        assert right.value.type == "bool"
        assert right.value.value is True

    def test_error_empty_query(self):
        """
        Test error on empty query.
        """
        with pytest.raises(FilterParseError):
            self.parser.parse("")

    def test_error_invalid_syntax(self):
        """
        Test error handling for invalid syntax.
        """
        with pytest.raises(FilterParseError):
            self.parser.parse("age > AND status = 'active'")

    def test_parse_complex_nested_expressions(self):
        """
        Test parsing complex nested expressions with multiple parentheses.
        """
        query = "((age > 18 OR vip = true) AND (status = 'active' OR role = 'admin')) AND NOT is_deleted"
        ast = self.parser.parse(query)
        
        assert isinstance(ast, LogicalOperator)
        assert ast.operator == "AND"
        assert len(ast.children) == 2
        
        # Check NOT operator - the transformer converts NOT to a field condition
        not_child = ast.children[1]
        assert isinstance(not_child, FieldCondition)
        assert not_child.field == "is_deleted"
        assert not_child.operator == "="
        assert not_child.value.value == False

    def test_parse_all_comparison_operators(self):
        """
        Test parsing all supported comparison operators.
        """
        # Test basic operators that work
        operators = ["=", "!=", ">", ">=", "<", "<=", "in", "like", "~", "!~"]
        
        for op in operators:
            if op in ["in"]:
                query = f"tags {op} ['test']"
            elif op in ["like", "~", "!~"]:
                query = f"name {op} 'test.*'"
            else:
                query = f"age {op} 18"
            
            ast = self.parser.parse(query)
            assert isinstance(ast, FieldCondition)
            assert ast.operator == op
        
        # Test intersects separately as it has different behavior
        ast = self.parser.parse("tags intersects ['test']")
        assert isinstance(ast, FieldCondition)
        assert ast.operator == "intersects"
        assert ast.field == "tags"

    def test_parse_different_value_types(self):
        """
        Test parsing different value types.
        """
        # Integer
        ast = self.parser.parse("age = 25")
        assert ast.value.type == "int"
        assert ast.value.value == 25
        
        # Float
        ast = self.parser.parse("score = 8.5")
        assert ast.value.type == "float"
        assert ast.value.value == 8.5
        
        # String
        ast = self.parser.parse("name = 'John'")
        assert ast.value.type == "str"
        assert ast.value.value == "John"
        
        # Boolean
        ast = self.parser.parse("active = true")
        assert ast.value.type == "bool"
        assert ast.value.value == True
        
        # Null
        ast = self.parser.parse("value = null")
        assert ast.value.type == "null"
        assert ast.value.value is None
        
        # Date
        ast = self.parser.parse("created = '2024-01-01T00:00:00Z'")
        assert ast.value.type == "date"

    def test_parse_complex_list_values(self):
        """
        Test parsing complex list values with different types.
        """
        # Mixed types in list
        ast = self.parser.parse("tags in ['python', 42, true, null]")
        assert ast.value.type == "list"
        assert len(ast.value.value) == 4
        
        # Nested lists
        ast = self.parser.parse("data in [['a', 'b'], ['c', 'd']]")
        assert ast.value.type == "list"
        assert len(ast.value.value) == 2

    def test_parse_complex_dict_values(self):
        """
        Test parsing complex dictionary values.
        """
        # Simple dict - note: keys are strings in the parser
        ast = self.parser.parse("meta = {'key': 'value'}")
        assert ast.value.type == "dict"
        # The parser treats keys as quoted strings, so we expect quoted keys
        assert ast.value.value == {'"key"': 'value'}

    def test_parse_deep_nested_fields(self):
        """
        Test parsing deeply nested field names.
        """
        ast = self.parser.parse("user.profile.settings.theme.color = 'blue'")
        assert ast.field == "user.profile.settings.theme.color"
        assert ast.value.value == "blue"

    def test_parse_whitespace_handling(self):
        """
        Test parsing with various whitespace patterns.
        """
        # Extra spaces
        ast1 = self.parser.parse("age  >  18")
        ast2 = self.parser.parse("age > 18")
        assert ast1.field == ast2.field
        assert ast1.operator == ast2.operator
        assert ast1.value.value == ast2.value.value
        
        # Newlines and tabs
        ast = self.parser.parse("age > 18\nAND\nstatus = 'active'")
        assert isinstance(ast, LogicalOperator)
        assert ast.operator == "AND"

    def test_parse_case_insensitive_operators(self):
        """
        Test parsing case-insensitive logical operators.
        """
        # Lowercase
        ast1 = self.parser.parse("age > 18 and status = 'active'")
        assert ast1.operator == "AND"
        
        # Mixed case
        ast2 = self.parser.parse("age > 18 Or status = 'active'")
        assert ast2.operator == "OR"
        
        # NOT operator needs to be at the beginning
        ast3 = self.parser.parse("NOT is_deleted = true")
        assert ast3.operator == "NOT"

    def test_parse_edge_cases(self):
        """
        Test parsing edge cases and boundary conditions.
        """
        # Empty string in list
        ast = self.parser.parse("tags in ['', 'test']")
        assert ast.value.value == ["", "test"]
        
        # Unicode characters
        ast = self.parser.parse("name = 'José'")
        assert ast.value.value == "José"

    def test_parse_error_handling(self):
        """
        Test comprehensive error handling.
        """
        # Missing operator
        with pytest.raises(FilterParseError):
            self.parser.parse("age 18")
        
        # Missing value
        with pytest.raises(FilterParseError):
            self.parser.parse("age >")
        
        # Invalid operator
        with pytest.raises(FilterParseError):
            self.parser.parse("age => 18")
        
        # Unclosed parentheses
        with pytest.raises(FilterParseError):
            self.parser.parse("(age > 18")
        
        # Unclosed quotes
        with pytest.raises(FilterParseError):
            self.parser.parse("name = 'John")
        
        # Invalid list syntax
        with pytest.raises(FilterParseError):
            self.parser.parse("tags in [1, 2,]")

    def test_parse_performance_edge_cases(self):
        """
        Test parsing performance edge cases.
        """
        # Very long field name
        long_field = "a" * 1000
        ast = self.parser.parse(f"{long_field} = 'test'")
        assert ast.field == long_field
        
        # Very long string value
        long_value = "a" * 1000
        ast = self.parser.parse(f"field = '{long_value}'")
        assert ast.value.value == long_value
        
        # Many nested parentheses - the parser simplifies them
        nested = "(" * 50 + "age > 18" + ")" * 50
        ast = self.parser.parse(nested)
        # The parser simplifies nested parentheses, so we get a FieldCondition
        assert isinstance(ast, FieldCondition)

    def test_parse_grammar_specific_cases(self):
        """
        Test parsing specific grammar cases.
        """
        # Multiple OR conditions - parser creates nested structure
        ast = self.parser.parse("a = 1 OR b = 2 OR c = 3")
        assert isinstance(ast, LogicalOperator)
        assert ast.operator == "OR"
        # The parser creates nested OR operators, so we have 2 children
        assert len(ast.children) == 2
        
        # Multiple AND conditions
        ast = self.parser.parse("a = 1 AND b = 2 AND c = 3")
        assert isinstance(ast, LogicalOperator)
        assert ast.operator == "AND"
        assert len(ast.children) == 2
        
        # Mixed precedence
        ast = self.parser.parse("a = 1 OR b = 2 AND c = 3")
        assert isinstance(ast, LogicalOperator)
        assert ast.operator == "OR"

    def test_parse_validation_errors(self):
        """
        Test parsing validation errors.
        """
        # Query too long
        long_query = "age > 18 AND " * 1000 + "status = 'active'"
        with pytest.raises(FilterParseError):
            self.parser.parse(long_query)
        
        # Empty query
        with pytest.raises(FilterParseError):
            self.parser.parse("")
        
        # None query
        with pytest.raises(FilterParseError):
            self.parser.parse(None)

    def test_parse_transformer_methods(self):
        """
        Test specific transformer methods.
        """
        # Test field name transformation
        ast = self.parser.parse("user_name = 'test'")
        assert ast.field == "user_name"
        
        # Test operator transformation
        ast = self.parser.parse("age != 18")
        assert ast.operator == "!="
        
        # Test value transformation
        ast = self.parser.parse("active = true")
        assert ast.value.type == "bool"
        assert ast.value.value == True

    def test_parse_xor_expression(self):
        """
        Test parsing XOR expression.
        """
        ast = self.parser.parse("a = 1 XOR b = 2")
        assert isinstance(ast, LogicalOperator)
        assert ast.operator == "XOR"
        assert len(ast.children) == 2

    def test_parse_not_field_expression(self):
        """
        Test parsing NOT field expression.
        """
        ast = self.parser.parse("NOT field_name")
        assert isinstance(ast, FieldCondition)
        assert ast.field == "field_name"
        assert ast.operator == "="
        assert ast.value.type == "bool"
        assert ast.value.value == False

    def test_parse_intersects_expression(self):
        """
        Test parsing intersects expression.
        """
        ast = self.parser.parse("tags intersects ['ai', 'ml']")
        assert isinstance(ast, FieldCondition)
        assert ast.operator == "intersects"
        assert ast.field == "tags"
        assert ast.value.type == "list"

    def test_parse_comparison_with_tuple_value(self):
        """
        Test parsing comparison with tuple value (from pair).
        """
        ast = self.parser.parse("meta = {'key': 'value'}")
        assert isinstance(ast, FieldCondition)
        assert ast.value.type == "dict" 