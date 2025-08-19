"""
Test Lark compatibility and basic functionality.

This module tests the compatibility of Lark parser with our filter expression
requirements and ensures it can handle the complex grammar needed for
AST and Lark integration.
"""

import pytest
from lark import Lark, Transformer


def test_lark_basic_parsing():
    """Test basic Lark parsing functionality."""
    grammar = """
    start: NUMBER
    NUMBER: /\\d+/
    """
    
    parser = Lark(grammar, start='start')
    tree = parser.parse("123")
    assert tree is not None


    def test_lark_transformer():
        """Test Lark transformer functionality."""
        grammar = """
        start: NUMBER
        NUMBER: /\\d+/
        """
        
        class NumberTransformer(Transformer):
            def NUMBER(self, token):
                return int(token)
        
        parser = Lark(grammar, start='start', parser='lalr', transformer=NumberTransformer())
        result = parser.parse("123")
        assert result == 123


    def test_lark_complex_grammar():
        """Test Lark with complex grammar for filter expressions."""
        grammar = """
        ?start: or_expr
        ?or_expr: and_expr (OR and_expr)*
        ?and_expr: condition (AND condition)*
        ?condition: field_expr | paren_expr | not_expr
        ?paren_expr: "(" or_expr ")"
        ?not_expr: NOT condition
        ?field_expr: field_name operator value
        ?field_name: CNAME ("." CNAME)*
        ?operator: "=" | "!=" | ">" | ">=" | "<" | "<="
        ?value: NUMBER | STRING
        AND: "AND" | "and"
        OR: "OR" | "or"
        NOT: "NOT" | "not"
        CNAME: /[a-zA-Z_][a-zA-Z0-9_]*/
        NUMBER: /\\d+/
        STRING: /"[^"]*"/
        %import common.WS
        %ignore WS
        """
        
        parser = Lark(grammar, start='start', parser='lalr')
        
        # Test simple expression
        tree = parser.parse("age > 18")
        assert tree is not None
        
        # Test logical expression
        tree = parser.parse("age > 18 AND status = \"active\"")
        assert tree is not None


    def test_lark_nested_fields():
        """Test Lark parsing of nested field expressions."""
        grammar = """
        ?start: field_expr
        ?field_expr: field_name operator value
        ?field_name: CNAME ("." CNAME)*
        ?operator: "=" | "!=" | ">" | ">=" | "<" | "<="
        ?value: NUMBER | STRING
        CNAME: /[a-zA-Z_][a-zA-Z0-9_]*/
        NUMBER: /\\d+/
        STRING: /"[^"]*"/
        %import common.WS
        %ignore WS
        """
        
        parser = Lark(grammar, start='start', parser='lalr')
        
        # Test nested field
        tree = parser.parse('block_meta.version = "1.0"')
        assert tree is not None
        
        # Test deeply nested field
        tree = parser.parse('metrics.quality.score > 0.8')
        assert tree is not None


def test_lark_error_handling():
    """Test Lark error handling for invalid expressions."""
    grammar = """
    start: field_expr
    field_expr: field_name operator value
    field_name: CNAME
    operator: "=" | "!=" | ">" | ">=" | "<" | "<="
    value: NUMBER | STRING
    CNAME: /[a-zA-Z_][a-zA-Z0-9_]*/
    NUMBER: /\\d+/
    STRING: /"[^"]*"/
    %import common.WS
    %ignore WS
    """
    
    parser = Lark(grammar, start='start')
    
    # Test valid expression
    tree = parser.parse("age = 18")
    assert tree is not None
    
    # Test invalid expression should raise exception
    with pytest.raises(Exception):
        parser.parse("invalid expression")


    def test_lark_performance():
        """Test Lark performance for typical filter expressions."""
        grammar = """
        ?start: or_expr
        ?or_expr: and_expr (OR and_expr)*
        ?and_expr: condition (AND condition)*
        ?condition: field_expr | paren_expr | not_expr
        ?paren_expr: "(" or_expr ")"
        ?not_expr: NOT condition
        ?field_expr: field_name operator value
        ?field_name: CNAME ("." CNAME)*
        ?operator: "=" | "!=" | ">" | ">=" | "<" | "<=" | "in" | "not_in" | "like" | "~" | "!~" | "intersects"
        ?value: NUMBER | STRING | array | dict | date | null
        ?array: "[" value ("," value)* "]"
        ?dict: "{" pair ("," pair)* "}"
        ?pair: CNAME ":" value
        ?date: DATE_ISO
        ?null: "null" | "NULL"
        AND: "AND" | "and"
        OR: "OR" | "or"
        NOT: "NOT" | "not"
        CNAME: /[a-zA-Z_][a-zA-Z0-9_]*/
        NUMBER: /-?\\d+(\\.\\d+)?/
        STRING: /"[^"]*"/
        DATE_ISO: /"\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(\\.\\d+)?Z?"/
        %import common.WS
        %ignore WS
        """
        
        parser = Lark(grammar, start='start', parser='lalr')
        
        # Test complex expression
        complex_query = """
            (type = "DocBlock" OR type = "CodeBlock") AND
            quality_score >= 0.8 AND
            (tags intersects ["ai", "ml"] OR tags intersects ["python", "data"]) AND
            year >= 2020 AND
            NOT is_deleted
        """
        
        import time
        start_time = time.time()
        tree = parser.parse(complex_query)
        end_time = time.time()
        
        assert tree is not None
        assert (end_time - start_time) < 0.001  # Should parse in less than 1ms 