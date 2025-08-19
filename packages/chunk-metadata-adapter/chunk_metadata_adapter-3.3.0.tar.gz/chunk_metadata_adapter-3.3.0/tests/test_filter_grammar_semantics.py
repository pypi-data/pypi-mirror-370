"""
Tests for filter grammar semantic validation.
"""
from chunk_metadata_adapter.filter_grammar import FilterGrammarValidator

class TestFilterGrammarSemantics:
    def test_semantic_warnings(self):
        validator = FilterGrammarValidator()
        # Test mixing like and regex operators
        warnings = validator.validate_semantics("title like 'Python' AND author ~ 'John'")
        assert any("like" in warning.lower() and "regex" in warning.lower() for warning in warnings)
        # Test unmatched parentheses
        warnings = validator.validate_semantics("(age > 18 AND status = 'active'")
        assert any("parentheses" in warning.lower() for warning in warnings)
        # Test null comparison
        warnings = validator.validate_semantics("summary = null")
        assert any("null" in warning.lower() for warning in warnings)

    def test_no_semantic_warnings_for_valid_queries(self):
        validator = FilterGrammarValidator()
        valid_queries = [
            "age > 18 AND status = 'active'",
            "type = 'DocBlock' OR type = 'CodeBlock'",
            "quality_score >= 0.8"
        ]
        for query in valid_queries:
            warnings = validator.validate_semantics(query)
            assert len(warnings) == 0, f"Unexpected warnings for valid query: {query}" 