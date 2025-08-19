"""
Tests for compatibility with existing ChunkQuery/SemanticChunk fields and operators.
"""
from chunk_metadata_adapter.filter_grammar import FilterGrammarValidator

class TestFilterGrammarCompatibility:
    def test_existing_chunkquery_operators(self):
        validator = FilterGrammarValidator()
        existing_operators = [
            "quality_score >= 0.8",
            "year <= 2024",
            "start > 100",
            "end < 1000",
            "type = 'DocBlock'",
            "status != 'inactive'"
        ]
        for query in existing_operators:
            assert validator.validate_syntax(query), f"Failed to parse existing operator: {query}"

    def test_existing_field_names(self):
        validator = FilterGrammarValidator()
        existing_fields = [
            "uuid = 'test'",
            "source_id = 'test'",
            "project = 'test'",
            "type = 'DocBlock'",
            "language = 'en'",
            "body = 'test'",
            "text = 'test'",
            "summary = 'test'",
            "ordinal = 1",
            "sha256 = 'test'",
            "created_at = '2024-01-01'",
            "status = 'active'",
            "source_path = 'test'",
            "quality_score >= 0.8",
            "coverage >= 0.8",
            "cohesion >= 0.8",
            "boundary_prev >= 0.8",
            "boundary_next >= 0.8",
            "used_in_generation = true",
            "feedback_accepted >= 5",
            "feedback_rejected >= 0",
            "start > 100",
            "end < 1000",
            "category = 'science'",
            "title = 'test'",
            "year >= 2020",
            "is_public = true",
            "source = 'user'",
            "block_type = 'paragraph'",
            "chunking_version = '1.0'",
            "metrics = 'test'",
            "block_id = 'test'",
            "embedding = 'test'",
            "block_index = 1",
            "source_lines_start = 1",
            "source_lines_end = 10",
            "tags = ['test']",
            "links = ['test']",
            "block_meta = {'test': 'value'}",
            "tags_flat = 'test'",
            "link_related = 'test'",
            "link_parent = 'test'"
        ]
        passed = 0
        for query in existing_fields:
            if validator.validate_syntax(query):
                passed += 1
        success_rate = passed / len(existing_fields)
        assert success_rate >= 0.9, f"Too many fields not supported: {passed}/{len(existing_fields)}" 