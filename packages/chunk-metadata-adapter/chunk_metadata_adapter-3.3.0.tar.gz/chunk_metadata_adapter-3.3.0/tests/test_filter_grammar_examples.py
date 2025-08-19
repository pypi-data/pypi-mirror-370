"""
Tests for filter grammar examples.
"""
from chunk_metadata_adapter.filter_grammar import FilterGrammarValidator, FilterGrammarExamples
from chunk_metadata_adapter.filter_parser import FilterParser

class TestFilterGrammarExamples:
    def setup_method(self):
        """Setup parser for tests."""
        self.parser = FilterParser()
    
    def test_simple_examples_are_valid(self):
        validator = FilterGrammarValidator()
        examples = FilterGrammarExamples.get_simple_examples()
        for example in examples:
            assert validator.validate_syntax(example), f"Invalid simple example: {example}"

    def test_complex_examples_are_valid(self):
        validator = FilterGrammarValidator()
        examples = FilterGrammarExamples.get_complex_examples()
        for example in examples:
            assert validator.validate_syntax(example), f"Invalid complex example: {example}"

    def test_list_examples_are_valid(self):
        validator = FilterGrammarValidator()
        examples = FilterGrammarExamples.get_list_examples()
        for example in examples:
            assert validator.validate_syntax(example), f"Invalid list example: {example}"

    def test_dict_examples_are_valid(self):
        """Test that dictionary examples are valid."""
        examples = FilterGrammarExamples.get_dict_examples()
        
        for example in examples:
            ast = self.parser.parse(example)
            assert ast is not None, f"Failed to parse: {example}"
    
    def test_total_chunks_metadata_examples(self):
        """Test total_chunks_in_source metadata examples."""
        examples = [
            "block_meta.total_chunks_in_source = 5",
            "block_meta.is_last_chunk = true",
            "block_meta.is_first_chunk = true",
            "block_meta.chunk_percentage > 50",
            "ordinal = 0 AND block_meta.is_first_chunk = true",
            "block_meta.total_chunks_in_source >= 10 AND block_meta.is_last_chunk = true"
        ]
        
        for example in examples:
            ast = self.parser.parse(example)
            assert ast is not None, f"Failed to parse: {example}"

    def test_date_examples_are_valid(self):
        validator = FilterGrammarValidator()
        examples = FilterGrammarExamples.get_date_examples()
        for example in examples:
            assert validator.validate_syntax(example), f"Invalid date example: {example}"

    def test_business_examples_are_valid(self):
        """Test that business examples are valid."""
        examples = [
            "type = 'DocBlock' AND quality_score >= 0.8",
            "tags intersects ['ai', 'ml'] AND year >= 2020",
            "block_meta.total_chunks_in_source = 5",
            "block_meta.is_last_chunk = true",
            "ordinal = 0 AND block_meta.is_first_chunk = true",
            "block_meta.chunk_percentage > 50"
        ]
        
        for example in examples:
            ast = self.parser.parse(example)
            assert ast is not None

    def test_invalid_examples_are_rejected(self):
        validator = FilterGrammarValidator()
        examples = FilterGrammarExamples.get_invalid_examples()
        for example in examples:
            assert not validator.validate_syntax(example), f"Should reject invalid example: {example}" 