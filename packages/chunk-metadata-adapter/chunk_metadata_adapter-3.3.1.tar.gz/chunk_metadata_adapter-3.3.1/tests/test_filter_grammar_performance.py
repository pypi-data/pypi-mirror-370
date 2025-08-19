"""
Performance tests for filter grammar parsing.
"""
import time
from chunk_metadata_adapter.filter_grammar import FilterGrammarValidator

class TestFilterGrammarPerformance:
    def test_parsing_performance(self):
        validator = FilterGrammarValidator()
        simple_queries = [
            "age > 18",
            "status = 'active'",
            "type = 'DocBlock'",
            "quality_score >= 0.8"
        ]
        start_time = time.time()
        for query in simple_queries * 100:  # 400 total queries
            validator.validate_syntax(query)
        end_time = time.time()
        total_time = end_time - start_time
        avg_time = total_time / 400
        
        # More realistic performance requirement: 3ms per query is acceptable
        # This accounts for Python overhead, system load, and measurement variance
        assert avg_time < 0.003, f"Average parsing time too slow: {avg_time:.6f}s (total: {total_time:.3f}s for 400 queries)"

    def test_complex_parsing_performance(self):
        validator = FilterGrammarValidator()
        complex_query = """
            (type = 'DocBlock' OR type = 'CodeBlock') AND
            quality_score >= 0.8 AND
            (tags intersects ['ai', 'ml'] OR tags intersects ['python', 'data']) AND
            year >= 2020 AND
            NOT is_deleted = true
        """.strip().replace('\n', ' ')
        start_time = time.time()
        for _ in range(100):
            validator.validate_syntax(complex_query)
        end_time = time.time()
        avg_time = (end_time - start_time) / 100
        assert avg_time < 0.01, f"Complex parsing time too slow: {avg_time:.6f}s"

    def test_parser_caching(self):
        validator = FilterGrammarValidator()
        parser1 = validator.parser
        parser2 = validator.parser
        assert parser1 is parser2, "Parser caching not working within instance" 