"""
Tests for filter grammar error handling.
"""
import pytest
from chunk_metadata_adapter.filter_grammar import FilterGrammarValidator

class TestFilterGrammarErrors:
    def test_syntax_errors(self):
        validator = FilterGrammarValidator()
        invalid_queries = [
            "age >>>> 18",  # Invalid operator
            "(age > 18",    # Unclosed parentheses
            "title = 'unclosed",  # Unclosed quotes
            "age > AND status = 'active'",  # Invalid syntax
            "field..nested = 'value'",  # Invalid field name
            "field name = 'value'",  # Invalid field name with space
            "field-name = 'value'",  # Invalid field name with dash
            "123field = 'value'",  # Invalid field name starting with number
            "field = 'value' AND"  # Incomplete expression
        ]
        for query in invalid_queries:
            assert not validator.validate_syntax(query), f"Should reject invalid query: {query}"

    def test_error_details(self):
        validator = FilterGrammarValidator()
        query = "age >>>> 18"
        errors = validator.get_errors(query)
        assert errors['syntax_valid'] == False
        assert 'error_type' in errors
        assert 'error_message' in errors
        assert 'error_position' in errors

    def test_empty_query_validation(self):
        validator = FilterGrammarValidator()
        # Теперь метод возвращает False вместо исключения
        assert not validator.validate_syntax("")
        assert not validator.validate_syntax("   ")

    def test_query_length_validation(self):
        validator = FilterGrammarValidator(max_query_length=10)
        short_query = "age > 5"
        long_query = "age > 5 AND status = 'active' AND type = 'DocBlock'"
        assert validator.validate_syntax(short_query)
        # Теперь метод возвращает False вместо исключения
        assert not validator.validate_syntax(long_query) 