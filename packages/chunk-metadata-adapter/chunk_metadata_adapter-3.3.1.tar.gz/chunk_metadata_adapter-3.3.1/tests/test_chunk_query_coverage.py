"""
Tests for chunk_query.py module coverage.

This module tests the chunk_query.py module to achieve 90%+ coverage
by testing all methods, edge cases, and functionality.
"""

import pytest
from unittest.mock import patch, MagicMock
from pydantic import ValidationError
from chunk_metadata_adapter import ChunkQuery, SemanticChunk
from chunk_metadata_adapter.data_types import ChunkType, ChunkRole, ChunkStatus, LanguageEnum, BlockType


class TestChunkQueryCoverage:
    """Tests for ChunkQuery coverage."""
    
    def test_all_field_validators(self):
        """Test all field validators in ChunkQuery."""
        # Test UUID field validators
        valid_uuids = [
            "550e8400-e29b-41d4-a716-446655440000"
        ]
        
        for uuid_str in valid_uuids:
            query = ChunkQuery(uuid=uuid_str)
            assert query.uuid == uuid_str
        
        # Test invalid UUID
        with pytest.raises(ValidationError):
            ChunkQuery(uuid="invalid-uuid")
        
        # Test type field validator
        query = ChunkQuery(type="DocBlock")
        assert query.type == ChunkType.DOC_BLOCK
        
        with pytest.raises(ValidationError):
            ChunkQuery(type="InvalidType")
        
        # Test role field validator
        query = ChunkQuery(role="user")
        assert query.role == ChunkRole.USER
        
        with pytest.raises(ValidationError):
            ChunkQuery(role="InvalidRole")
        
        # Test status field validator
        query = ChunkQuery(status="new")
        assert query.status == ChunkStatus.NEW
        
        with pytest.raises(ValidationError):
            ChunkQuery(status="InvalidStatus")
        
        # Test language field validator
        query = ChunkQuery(language="en")
        assert query.language == LanguageEnum.EN
        
        with pytest.raises(ValidationError):
            ChunkQuery(language="invalid")
        
        # Test block_type field validator
        query = ChunkQuery(block_type="paragraph")
        assert query.block_type == BlockType.PARAGRAPH
        
        with pytest.raises(ValidationError):
            ChunkQuery(block_type="InvalidBlockType")
    
    def test_search_fields_validator(self):
        """Test search_fields validator."""
        # Test valid search fields
        valid_fields = ["body", "text", "summary", "title"]
        query = ChunkQuery(search_fields=valid_fields)
        assert query.search_fields == valid_fields
        
        # Test invalid search fields - should raise ValueError as validation is strict
        with pytest.raises(ValueError):
            ChunkQuery(search_fields=["invalid_field"])
        
        # Test duplicate fields - duplicates are allowed, just test that it works
        query_dup = ChunkQuery(search_fields=["body", "body"])
        assert query_dup.search_fields == ["body", "body"]
        
        # Test None value
        query = ChunkQuery(search_fields=None)
        assert query.search_fields is None
    
    def test_get_ast_with_cache(self):
        """Test get_ast method with caching."""
        query = ChunkQuery(filter_expr="type = 'DocBlock'")
        
        # First call - should parse
        ast1 = query.get_ast()
        assert ast1 is not None
        
        # Second call - should use cache
        ast2 = query.get_ast()
        assert ast2 is ast1
        
        # Test with no filter expression
        query_no_filter = ChunkQuery(type="DocBlock")
        ast_none = query_no_filter.get_ast()
        assert ast_none is None
    
    def test_get_ast_error_handling(self):
        """Test get_ast error handling."""
        # Test with invalid filter expression
        query = ChunkQuery(filter_expr="invalid expression")
        
        with pytest.raises(Exception):
            query.get_ast()
    
    def test_matches_with_filter_expression(self):
        """Test matches method with filter expression."""
        query = ChunkQuery(filter_expr="type = 'DocBlock'")
        
        # Test with SemanticChunk
        chunk = SemanticChunk(type=ChunkType.DOC_BLOCK, body="test content")
        result = query.matches(chunk)
        assert result == True
        
        # Test with dict
        chunk_dict = {"type": "DocBlock"}
        result = query.matches(chunk_dict)
        assert result == True
        
        # Test with object
        class MockChunk:
            def __init__(self):
                self.type = "DocBlock"
        
        mock_chunk = MockChunk()
        result = query.matches(mock_chunk)
        assert result == True
    
    def test_matches_with_simple_fields(self):
        """Test matches method with simple field filters."""
        query = ChunkQuery(type="DocBlock", quality_score=">=0.8")
        
        # Test matching chunk
        chunk = SemanticChunk(type=ChunkType.DOC_BLOCK, quality_score=0.9, body="test content")
        result = query.matches(chunk)
        assert result == True
        
        # Test non-matching chunk
        chunk = SemanticChunk(type=ChunkType.DOC_BLOCK, quality_score=0.7, body="test content")
        result = query.matches(chunk)
        assert result == False
    
    def test_matches_field_value_operators(self):
        """Test _matches_field_value with different operators."""
        query = ChunkQuery()
        
        # Test numeric operators (using fields from the numeric list)
        assert query._matches_field_value(0.9, ">=0.8", "quality_score") == True
        assert query._matches_field_value(0.7, ">=0.8", "quality_score") == False
        assert query._matches_field_value(0.9, "<=0.95", "quality_score") == True
        assert query._matches_field_value(0.97, "<=0.95", "quality_score") == False
        assert query._matches_field_value(0.9, ">0.8", "quality_score") == True
        assert query._matches_field_value(0.7, ">0.8", "quality_score") == False
        assert query._matches_field_value(0.9, "<0.95", "quality_score") == True
        assert query._matches_field_value(0.97, "<0.95", "quality_score") == False
        assert query._matches_field_value(0.9, "!=0.8", "quality_score") == True
        assert query._matches_field_value(0.8, "!=0.8", "quality_score") == False
        assert query._matches_field_value(0.9, "=0.9", "quality_score") == True
        assert query._matches_field_value(20, "=25", "age") == False
        
        # Test list operators
        assert query._matches_field_value(["ai", "ml"], "in:ai,python", "tags") == True
        assert query._matches_field_value(["python"], "in:ai,python", "tags") == True
        assert query._matches_field_value(["other"], "in:ai,python", "tags") == False
        
        # Test string operators
        assert query._matches_field_value("hello world", "like:hello", "text") == True
        assert query._matches_field_value("hello world", "like:bye", "text") == False
        
        # Test regex operators
        assert query._matches_field_value("hello123", "~[0-9]+", "text") == True
        assert query._matches_field_value("hello", "~[0-9]+", "text") == False
    
    def test_matches_list_field(self):
        """Test _matches_list_field method."""
        query = ChunkQuery()
        
        # Test with string input - should find intersection
        assert query._matches_list_field("ai,ml", "ai,python") == True  # 'ai' is common
        assert query._matches_list_field("ai,ml", "other,python") == False  # no intersection
        assert query._matches_list_field("other", "ai,python") == False
        
        # Test with list input
        assert query._matches_list_field(["ai", "ml"], ["ai", "python"]) == True
        assert query._matches_list_field(["ai", "ml"], ["other", "python"]) == False  # no intersection
        assert query._matches_list_field(["other"], ["ai", "python"]) == False
        
        # Test with None values
        assert query._matches_list_field(None, "ai,python") == False
        assert query._matches_list_field("ai,ml", None) == False
    
    def test_matches_boolean_field(self):
        """Test _matches_boolean_field method."""
        query = ChunkQuery()
        
        # Test boolean values
        assert query._matches_boolean_field(True, True) == True
        assert query._matches_boolean_field(False, False) == True
        assert query._matches_boolean_field(True, False) == False
        
        # Test string values
        assert query._matches_boolean_field("true", "true") == True
        assert query._matches_boolean_field("false", "false") == True
        assert query._matches_boolean_field("true", "false") == False
        
        # Test mixed types
        assert query._matches_boolean_field(True, "true") == True
        assert query._matches_boolean_field(False, "false") == True
        assert query._matches_boolean_field(True, "false") == False
    
    def test_matches_numeric_field(self):
        """Test _matches_numeric_field method."""
        query = ChunkQuery()
        
        # Test numeric values
        assert query._matches_numeric_field(42, 42) == True
        assert query._matches_numeric_field(42, 43) == False
        
        # Test string values
        assert query._matches_numeric_field("42", "42") == True
        assert query._matches_numeric_field("42", "43") == False
        
        # Test mixed types
        assert query._matches_numeric_field(42, "42") == True
        assert query._matches_numeric_field("42", 42) == True
        
        # Test float values
        assert query._matches_numeric_field(3.14, "3.14") == True
        assert query._matches_numeric_field("3.14", 3.14) == True
    
    def test_matches_numeric_operator(self):
        """Test _matches_numeric_operator method."""
        query = ChunkQuery()
        
        # Test comparison operators
        assert query._matches_numeric_operator(25, ">=", "18") == True
        assert query._matches_numeric_operator(15, ">=", "18") == False
        assert query._matches_numeric_operator(25, "<=", "30") == True
        assert query._matches_numeric_operator(35, "<=", "30") == False
        assert query._matches_numeric_operator(25, ">", "20") == True
        assert query._matches_numeric_operator(15, ">", "20") == False
        assert query._matches_numeric_operator(25, "<", "30") == True
        assert query._matches_numeric_operator(35, "<", "30") == False
        assert query._matches_numeric_operator(25, "!=", "20") == True
        assert query._matches_numeric_operator(20, "!=", "20") == False
        assert query._matches_numeric_operator(25, "=", "25") == True
        assert query._matches_numeric_operator(20, "=", "25") == False
        
        # Test invalid operator
        assert query._matches_numeric_operator(25, "invalid", "20") == False
        
        # Test invalid values
        assert query._matches_numeric_operator("invalid", ">", "20") == False
        assert query._matches_numeric_operator(25, ">", "invalid") == False
    
    def test_matches_list_operator(self):
        """Test _matches_list_operator method."""
        query = ChunkQuery()
        
        # Test 'in' operator
        assert query._matches_list_operator(["ai", "ml"], "in", "ai,python") == True
        assert query._matches_list_operator(["other"], "in", "ai,python") == False
        
        # Test 'not_in' operator
        assert query._matches_list_operator(["other"], "not_in", "ai,python") == True
        assert query._matches_list_operator(["ai"], "not_in", "ai,python") == False
        
        # Test invalid operator
        assert query._matches_list_operator(["ai"], "invalid", "ai,python") == False
    
    def test_compare_strings(self):
        """Test _compare_strings method."""
        query = ChunkQuery()
        
        # Test equality operators
        assert query._compare_strings("hello", "=", "hello") == True
        assert query._compare_strings("hello", "=", "world") == False
        assert query._compare_strings("hello", "!=", "world") == True
        assert query._compare_strings("hello", "!=", "hello") == False
        
        # Test like operator
        assert query._compare_strings("hello world", "like", "hello") == True
        assert query._compare_strings("hello world", "like", "bye") == False
        
        # Test regex operators
        assert query._compare_strings("hello123", "~", "[0-9]+") == True
        assert query._compare_strings("hello", "~", "[0-9]+") == False
        assert query._compare_strings("hello123", "!~", "[0-9]+") == False
        assert query._compare_strings("hello", "!~", "[0-9]+") == True
        
        # Test invalid regex
        assert query._compare_strings("hello", "~", "[invalid") == False
        assert query._compare_strings("hello", "!~", "[invalid") == True
        
        # Test invalid operator
        assert query._compare_strings("hello", "invalid", "world") == False
    
    def test_validate_bm25_parameters_edge_cases(self):
        """Test validate_bm25_parameters edge cases."""
        # Test with no search query but BM25 parameters
        query = ChunkQuery(bm25_k1=1.5, bm25_b=0.8)
        validation = query.validate_bm25_parameters()
        assert validation.is_valid == True
        assert len(validation.warnings) > 0
        
        # Test with hybrid search but missing weights
        query = ChunkQuery(search_query="test", hybrid_search=True)
        validation = query.validate_bm25_parameters()
        assert validation.is_valid == True  # Default weights are used
        # No warnings expected as default weights are valid
        
        # Test with weights not summing to 1.0
        query = ChunkQuery(
            search_query="test", 
            hybrid_search=True, 
            bm25_weight=0.3, 
            semantic_weight=0.3
        )
        validation = query.validate_bm25_parameters()
        assert validation.is_valid == True
        assert len(validation.warnings) > 0
        
        # Test with extreme weights
        query = ChunkQuery(
            search_query="test", 
            hybrid_search=True, 
            bm25_weight=0.05, 
            semantic_weight=0.95
        )
        validation = query.validate_bm25_parameters()
        assert validation.is_valid == True
        assert len(validation.warnings) > 0
        
        # Test with empty search fields
        query = ChunkQuery(search_query="test", search_fields=[])
        validation = query.validate_bm25_parameters()
        assert validation.is_valid == False
        assert len(validation.errors) > 0
        
        # Test with duplicate search fields
        query = ChunkQuery(search_query="test", search_fields=["body", "body"])
        validation = query.validate_bm25_parameters()
        assert validation.is_valid == False
        assert len(validation.errors) > 0
        
        # Test with high min_score and large max_results
        query = ChunkQuery(
            search_query="test", 
            min_score=0.95, 
            max_results=500
        )
        validation = query.validate_bm25_parameters()
        assert validation.is_valid == True
        assert len(validation.warnings) > 0
    
    def test_has_simple_fields(self):
        """Test _has_simple_fields method."""
        query = ChunkQuery()
        assert query._has_simple_fields() == False
        
        # Test with different fields
        fields_to_test = [
            ("type", "DocBlock"),
            ("role", "user"),
            ("status", "new"),
            ("language", "en"),
            ("block_type", "paragraph"),
            ("quality_score", 0.8),
            ("coverage", 0.7),
            ("cohesion", 0.6),
            ("boundary_prev", 0.5),
            ("boundary_next", 0.4),
            ("feedback_accepted", 5),
            ("feedback_rejected", 2),
            ("start", 100),
            ("end", 200),
            ("year", 2024),
            ("ordinal", 1),
            ("source_lines_start", 10),
            ("source_lines_end", 20),
            ("block_index", 5),
            ("is_deleted", False),
            ("is_public", True),
            ("used_in_generation", True),
            ("tags", ["ai", "ml"]),
            ("links", ["link1", "link2"]),
            ("block_meta", {"key": "value"}),
            ("tags_flat", "ai,ml"),
            ("link_related", "550e8400-e29b-41d4-a716-446655440000"),
            ("link_parent", "550e8400-e29b-41d4-a716-446655440000"),
            ("filter_expr", "type = 'DocBlock'")
        ]
        
        for field_name, field_value in fields_to_test:
            query = ChunkQuery(**{field_name: field_value})
            assert query._has_simple_fields() == True
    
    def test_get_search_params_edge_cases(self):
        """Test get_search_params edge cases."""
        # Test with None values
        query = ChunkQuery(search_query="test")
        params = query.get_search_params()
        assert "search_query" in params
        assert "search_fields" in params  # Uses default
        
        # Test with all parameters set
        query = ChunkQuery(
            search_query="test",
            search_fields=["body", "text"],
            bm25_k1=1.5,
            bm25_b=0.8,
            hybrid_search=True,
            bm25_weight=0.6,
            semantic_weight=0.4,
            min_score=0.5,
            max_results=50
        )
        params = query.get_search_params()
        assert len(params) >= 8  # At least 8 parameters
        assert params["search_query"] == "test"
        assert params["search_fields"] == ["body", "text"]
        assert params["bm25_k1"] == 1.5
        assert params["bm25_b"] == 0.8
        assert params["hybrid_search"] == True
        assert params["bm25_weight"] == 0.6
        assert params["semantic_weight"] == 0.4
        assert params["min_score"] == 0.5
        assert params["max_results"] == 50
    
    def test_to_api_request_edge_cases(self):
        """Test to_api_request edge cases."""
        # Test without BM25 search
        query = ChunkQuery(type="DocBlock")
        request = query.to_api_request()
        assert "type" in request
        assert "search_query" not in request
        assert request["api_version"] == "3.3.0"
        
        # Test with BM25 search but exclude search params
        query = ChunkQuery(
            type="DocBlock",
            search_query="test",
            hybrid_search=True
        )
        request = query.to_api_request(include_search_params=False)
        assert "type" in request
        assert "search_query" not in request
        assert "hybrid_search" not in request
        
        # Test with all fields
        query = ChunkQuery(
            type="DocBlock",
            quality_score=">=0.8",
            tags="in:ai,ml",
            year=">=2020",
            language="en",
            is_public=True,
            is_deleted=False,
            filter_expr="type = 'DocBlock'",
            search_query="test",
            hybrid_search=True
        )
        request = query.to_api_request()
        assert len(request) >= 10  # Multiple fields + metadata
        assert request["api_version"] == "3.3.0"
        assert request["request_type"] == "chunk_query"
        assert "timestamp" in request
    
    def test_to_flat_dict_and_from_flat_dict(self):
        """Test to_flat_dict and from_flat_dict methods."""
        query = ChunkQuery(
            type="DocBlock",
            quality_score=">=0.8",
            search_query="test"
        )
        
        # Test to_flat_dict
        flat_dict = query.to_flat_dict()
        assert isinstance(flat_dict, dict)
        assert "type" in flat_dict
        assert "quality_score" in flat_dict
        assert "search_query" in flat_dict
        
        # Test from_flat_dict
        restored_query = ChunkQuery.from_flat_dict(flat_dict)
        assert restored_query.type == query.type
        assert restored_query.quality_score == query.quality_score
        assert restored_query.search_query == query.search_query
    
    def test_from_dict_with_validation(self):
        """Test from_dict_with_validation method."""
        # Test valid data
        data = {"type": "DocBlock", "quality_score": ">=0.8"}
        query, errors = ChunkQuery.from_dict_with_validation(data)
        assert query is not None
        assert errors is None
        assert query.type == ChunkType.DOC_BLOCK
        assert query.quality_score == ">=0.8"
        
        # Test with filter expression
        data = {"filter_expr": "type = 'DocBlock'"}
        query, errors = ChunkQuery.from_dict_with_validation(data)
        assert query is not None
        assert errors is None
        
        # Test with invalid filter expression
        data = {"filter_expr": "invalid expression"}
        query, errors = ChunkQuery.from_dict_with_validation(data)
        assert query is None
        assert errors is not None
        
        # Test with invalid BM25 parameters
        data = {
            "search_query": "test",
            "hybrid_search": True,
            "bm25_weight": 0.3,
            "semantic_weight": 0.3  # Sum < 1.0
        }
        query, errors = ChunkQuery.from_dict_with_validation(data)
        assert query is not None  # Should still create query
        assert errors is None  # Warnings don't prevent creation
        
        # Test with Pydantic validation error
        data = {"type": "InvalidType"}
        query, errors = ChunkQuery.from_dict_with_validation(data)
        assert query is None
        assert errors is not None
        assert "fields" in errors
    
    def test_to_json_dict_and_from_json_dict(self):
        """Test to_json_dict and from_json_dict methods."""
        query = ChunkQuery(
            type="DocBlock",
            quality_score=">=0.8",
            search_query="test"
        )
        
        # Test to_json_dict
        json_dict = query.to_json_dict()
        assert isinstance(json_dict, dict)
        assert "type" in json_dict
        assert "quality_score" in json_dict
        assert "search_query" in json_dict
        
        # Test from_json_dict
        restored_query = ChunkQuery.from_json_dict(json_dict)
        assert restored_query.type == query.type
        assert restored_query.quality_score == query.quality_score
        assert restored_query.search_query == query.search_query
    
    def test_clear_cache(self):
        """Test clear_cache method."""
        query = ChunkQuery(filter_expr="type = 'DocBlock'")
        
        # Create some cached data
        ast1 = query.get_ast()
        validation1 = query.validate()
        
        # Clear cache
        query.clear_cache()
        
        # Get again - should recreate
        ast2 = query.get_ast()
        validation2 = query.validate()
        
        # Should be different objects (recreated)
        assert ast1 is not ast2
        assert validation1 is not validation2
    
    def test_get_cache_stats(self):
        """Test get_cache_stats method."""
        query = ChunkQuery(filter_expr="type = 'DocBlock'")
        
        # Get stats before any operations
        stats = query.get_cache_stats()
        assert isinstance(stats, dict)
        assert "ast_cached" in stats
        assert "validation_cached" in stats
        assert stats["ast_cached"] == False
        assert stats["validation_cached"] == False
        
        # Perform operations
        ast = query.get_ast()
        validation = query.validate()
        
        # Get stats after operations
        stats = query.get_cache_stats()
        assert stats["ast_cached"] == True
        assert stats["validation_cached"] == True
        assert stats["parser_initialized"] == True
        # Executor might not be initialized yet as it's lazy
        # assert stats["executor_initialized"] == True
        assert stats["validator_initialized"] == True
        assert stats["optimizer_initialized"] == True
    
    def test_component_management(self):
        """Test component management methods."""
        query = ChunkQuery()
        
        # Test _get_parser
        parser1 = query._get_parser()
        parser2 = query._get_parser()
        assert parser1 is parser2  # Should be cached
        
        # Test _get_executor
        executor1 = query._get_executor()
        executor2 = query._get_executor()
        assert executor1 is executor2  # Should be cached
        
        # Test _get_validator
        validator1 = query._get_validator()
        validator2 = query._get_validator()
        assert validator1 is validator2  # Should be cached
        
        # Test _get_optimizer
        optimizer1 = query._get_optimizer()
        optimizer2 = query._get_optimizer()
        assert optimizer1 is optimizer2  # Should be cached
    
    def test_matches_simple_fields(self):
        """Test _matches_simple_fields method."""
        query = ChunkQuery(type="DocBlock", quality_score=0.8)
        
        # Test matching chunk - type should be enum, not string
        chunk_dict = {"type": ChunkType.DOC_BLOCK, "quality_score": 0.8}
        assert query._matches_simple_fields(chunk_dict) == True
        
        # Test non-matching chunk
        chunk_dict = {"type": ChunkType.DOC_BLOCK, "quality_score": 0.7}
        assert query._matches_simple_fields(chunk_dict) == False
        
        # Test with missing field
        chunk_dict = {"type": ChunkType.DOC_BLOCK}
        assert query._matches_simple_fields(chunk_dict) == False
        
        # Test with None values in query
        query_none = ChunkQuery(type="DocBlock", quality_score=None)
        chunk_dict = {"type": "DocBlock", "quality_score": 0.9}
        assert query_none._matches_simple_fields(chunk_dict) == True 