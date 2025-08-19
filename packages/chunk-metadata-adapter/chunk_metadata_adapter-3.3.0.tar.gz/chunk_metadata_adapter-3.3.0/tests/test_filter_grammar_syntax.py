"""
Tests for filter grammar syntax validation.
"""
import pytest
from lark import Lark
from chunk_metadata_adapter.filter_grammar import FILTER_GRAMMAR, FilterGrammarValidator

class TestFilterGrammarSyntax:
    def test_grammar_creation(self):
        parser = Lark(FILTER_GRAMMAR, start='start', parser='lalr')
        assert parser is not None
        assert hasattr(parser, 'parse')

    def test_simple_numeric_comparisons(self):
        validator = FilterGrammarValidator()
        examples = [
            "age > 18",
            "quality_score >= 0.8",
            "feedback_accepted != 0",
            "year = 2024",
            "start <= 100",
            "end < 1000"
        ]
        for example in examples:
            assert validator.validate_syntax(example), f"Failed to parse: {example}"

    def test_simple_string_comparisons(self):
        validator = FilterGrammarValidator()
        examples = [
            "title = 'Python Tutorial'",
            "description like 'AI'",
            "author ~ 'John.*Doe'",
            "status != 'inactive'",
            "type = 'DocBlock'"
        ]
        for example in examples:
            assert validator.validate_syntax(example), f"Failed to parse: {example}"

    def test_boolean_values(self):
        validator = FilterGrammarValidator()
        examples = [
            "is_public = true",
            "used_in_generation != false",
            "is_deleted = True",
            "is_archived = FALSE"
        ]
        for example in examples:
            assert validator.validate_syntax(example), f"Failed to parse: {example}"

    def test_null_values(self):
        validator = FilterGrammarValidator()
        examples = [
            "summary = null",
            "year != NULL",
            "block_meta = None"
        ]
        for example in examples:
            assert validator.validate_syntax(example), f"Failed to parse: {example}"

    def test_logical_operators(self):
        validator = FilterGrammarValidator()
        examples = [
            "age > 18 AND status = 'active'",
            "type = 'DocBlock' OR type = 'CodeBlock'",
            "NOT is_deleted = true",
            "age > 18 AND status = 'active' OR vip = true"
        ]
        for example in examples:
            assert validator.validate_syntax(example), f"Failed to parse: {example}"

    def test_parentheses_precedence(self):
        validator = FilterGrammarValidator()
        examples = [
            "(age > 18 OR vip = true) AND status = 'active'",
            "NOT (is_deleted = true OR is_archived = true)",
            "((type = 'DocBlock' AND quality_score >= 0.8) OR (type = 'CodeBlock' AND language = 'python'))"
        ]
        for example in examples:
            assert validator.validate_syntax(example), f"Failed to parse: {example}"

    def test_nested_fields(self):
        validator = FilterGrammarValidator()
        examples = [
            "user.profile.name = 'John'",
            "block_meta.version = '1.0'",
            "metrics.quality.score > 0.8",
            "deeply.nested.field.name = 'value'"
        ]
        for example in examples:
            assert validator.validate_syntax(example), f"Failed to parse: {example}"

    def test_list_operations(self):
        validator = FilterGrammarValidator()
        examples = [
            "tags intersects ['ai', 'ml']",
            "categories intersects ['tutorial', 'guide']",
            "tags = ['python', 'ai', 'tutorial']"
        ]
        for example in examples:
            assert validator.validate_syntax(example), f"Failed to parse: {example}"

    def test_dict_operations(self):
        validator = FilterGrammarValidator()
        examples = [
            "block_meta contains_key 'version'",
            "metadata contains_value 'John'",
            "block_meta = {'version': '1.0', 'author': 'John'}"
        ]
        for example in examples:
            assert validator.validate_syntax(example), f"Failed to parse: {example}"

    def test_date_comparisons(self):
        validator = FilterGrammarValidator()
        examples = [
            "created_at > '2024-01-01'",
            "updated_at >= '2024-01-01T12:00:00Z'",
            "published_at < '2024-12-31'"
        ]
        for example in examples:
            assert validator.validate_syntax(example), f"Failed to parse: {example}" 