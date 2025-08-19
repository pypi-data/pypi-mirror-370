"""
Integration tests for filter grammar with other components.
"""
from lark import Lark
from chunk_metadata_adapter.filter_grammar import FILTER_GRAMMAR, FilterGrammarValidator, FilterGrammarExamples

class TestFilterGrammarIntegration:
    def test_grammar_with_lark_parser(self):
        parser = Lark(FILTER_GRAMMAR, start='start', parser='lalr')
        validator = FilterGrammarValidator()
        test_queries = [
            "age > 18",
            "type = 'DocBlock' AND quality_score >= 0.8",
            "NOT is_deleted = true"
        ]
        for query in test_queries:
            parser.parse(query)
            assert validator.validate_syntax(query)

    def test_grammar_with_examples(self):
        validator = FilterGrammarValidator()
        all_examples = (
            FilterGrammarExamples.get_simple_examples() +
            FilterGrammarExamples.get_complex_examples() +
            FilterGrammarExamples.get_list_examples() +
            FilterGrammarExamples.get_dict_examples() +
            FilterGrammarExamples.get_date_examples()
        )
        for example in all_examples:
            assert validator.validate_syntax(example), f"Failed to parse example: {example}"

    def test_grammar_error_recovery(self):
        validator = FilterGrammarValidator()
        assert not validator.validate_syntax("invalid query")
        assert validator.validate_syntax("age > 18")
        valid_queries = ["age > 18", "status = 'active'", "type = 'DocBlock'"]
        for query in valid_queries:
            assert validator.validate_syntax(query) 