"""
Tests for API integration with BM25 parameters.

This module tests the integration of BM25 parameters with existing API
methods, including request formation, response handling, and compatibility.

Test coverage:
- API request formation with BM25 parameters
- Response parsing and validation
- Error handling
- Compatibility with existing API

Author: Development Team
Created: 2024-01-20
"""

import pytest
import json
from datetime import datetime
from chunk_metadata_adapter import (
    ChunkQuery, SearchResult, ChunkQueryResponse, SearchResponseBuilder,
    SemanticChunk, ChunkType, LanguageEnum
)


class TestChunkQueryAPIMethods:
    """Tests for ChunkQuery API methods with BM25 integration."""
    
    def test_has_bm25_search_with_query(self):
        """Test has_bm25_search() with search query."""
        query = ChunkQuery(search_query="python programming")
        assert query.has_bm25_search() is True
    
    def test_has_bm25_search_without_query(self):
        """Test has_bm25_search() without search query."""
        query = ChunkQuery(type="DocBlock")
        assert query.has_bm25_search() is False
    
    def test_has_bm25_search_empty_query(self):
        """Test has_bm25_search() with empty search query."""
        query = ChunkQuery(search_query="")
        assert query.has_bm25_search() is False
    
    def test_has_bm25_search_whitespace_query(self):
        """Test has_bm25_search() with whitespace-only query."""
        query = ChunkQuery(search_query="   ")
        assert query.has_bm25_search() is False
    
    def test_get_search_params_complete(self):
        """Test get_search_params() with all parameters."""
        query = ChunkQuery(
            search_query="machine learning",
            search_fields=["body", "text"],
            bm25_k1=1.5,
            bm25_b=0.8,
            hybrid_search=True,
            bm25_weight=0.3,
            semantic_weight=0.7,
            min_score=0.5,
            max_results=50
        )
        
        params = query.get_search_params()
        
        assert params["search_query"] == "machine learning"
        assert params["search_fields"] == ["body", "text"]
        assert params["bm25_k1"] == 1.5
        assert params["bm25_b"] == 0.8
        assert params["hybrid_search"] is True
        assert params["bm25_weight"] == 0.3
        assert params["semantic_weight"] == 0.7
        assert params["min_score"] == 0.5
        assert params["max_results"] == 50
    
    def test_get_search_params_partial(self):
        """Test get_search_params() with partial parameters."""
        query = ChunkQuery(
            search_query="python",
            bm25_k1=1.2
        )
        
        params = query.get_search_params()
        
        assert params["search_query"] == "python"
        assert params["bm25_k1"] == 1.2
        # Default values are included in params
        assert "bm25_b" in params
        assert "hybrid_search" in params
    
    def test_get_search_params_none_values(self):
        """Test get_search_params() with None values."""
        query = ChunkQuery(
            search_query="test",
            bm25_k1=None,
            bm25_b=None,
            hybrid_search=None
        )
        
        params = query.get_search_params()
        
        assert params["search_query"] == "test"
        assert "bm25_k1" not in params
        assert "bm25_b" not in params
        assert "hybrid_search" not in params
    
    def test_to_api_request_with_bm25(self):
        """Test to_api_request() with BM25 parameters."""
        query = ChunkQuery(
            type="DocBlock",
            search_query="artificial intelligence",
            search_fields=["body", "text"],
            hybrid_search=True,
            bm25_weight=0.4,
            semantic_weight=0.6
        )
        
        request = query.to_api_request()
        
        # Check existing fields
        assert request["type"] == "DocBlock"
        
        # Check BM25 fields
        assert request["search_query"] == "artificial intelligence"
        assert request["search_fields"] == ["body", "text"]
        assert request["hybrid_search"] is True
        assert request["bm25_weight"] == 0.4
        assert request["semantic_weight"] == 0.6
        
        # Check API metadata
        assert request["api_version"] == "3.3.0"
        assert request["request_type"] == "chunk_query"
        assert "timestamp" in request
    
    def test_to_api_request_without_bm25(self):
        """Test to_api_request() without BM25 parameters."""
        query = ChunkQuery(
            type="DocBlock",
            quality_score=">=0.8"
        )
        
        request = query.to_api_request()
        
        # Check existing fields
        assert request["type"] == "DocBlock"
        assert request["quality_score"] == ">=0.8"
        
        # Check that BM25 fields are not present
        assert "search_query" not in request
        assert "hybrid_search" not in request
        
        # Check API metadata
        assert request["api_version"] == "3.3.0"
        assert request["request_type"] == "chunk_query"
    
    def test_to_api_request_exclude_search_params(self):
        """Test to_api_request() with search params excluded."""
        query = ChunkQuery(
            type="DocBlock",
            search_query="python programming",
            hybrid_search=True
        )
        
        request = query.to_api_request(include_search_params=False)
        
        # Check existing fields
        assert request["type"] == "DocBlock"
        
        # Check that BM25 fields are excluded
        assert "search_query" not in request
        assert "hybrid_search" not in request
        
        # Check API metadata
        assert request["api_version"] == "3.3.0"
        assert request["request_type"] == "chunk_query"
    
    def test_to_api_request_with_filter_expression(self):
        """Test to_api_request() with filter expression."""
        query = ChunkQuery(
            filter_expr="type = 'DocBlock' AND quality_score >= 0.8",
            search_query="machine learning",
            hybrid_search=True
        )
        
        request = query.to_api_request()
        
        # Check filter expression
        assert request["filter_expr"] == "type = 'DocBlock' AND quality_score >= 0.8"
        
        # Check BM25 fields
        assert request["search_query"] == "machine learning"
        assert request["hybrid_search"] is True


class TestSearchResult:
    """Tests for SearchResult class."""
    
    def test_search_result_creation(self):
        """Test creating SearchResult with basic data."""
        chunk = SemanticChunk(
            uuid="550e8400-e29b-41d4-a716-446655440000",
            type=ChunkType.DOC_BLOCK,
            body="Test chunk content",
            text="Test chunk content"
        )
        
        result = SearchResult(
            chunk_id="test-uuid",
            chunk=chunk,
            bm25_score=0.85,
            rank=1
        )
        
        assert result.chunk_id == "test-uuid"
        assert result.chunk == chunk
        assert result.bm25_score == 0.85
        assert result.rank == 1
        assert result.primary_score == 0.85
    
    def test_search_result_hybrid_score(self):
        """Test SearchResult with hybrid score."""
        chunk = SemanticChunk(
            uuid="550e8400-e29b-41d4-a716-446655440000",
            type=ChunkType.DOC_BLOCK,
            body="Test chunk content",
            text="Test chunk content"
        )
        
        result = SearchResult(
            chunk_id="test-uuid",
            chunk=chunk,
            bm25_score=0.8,
            semantic_score=0.9,
            hybrid_score=0.85,
            rank=1
        )
        
        assert result.hybrid_score == 0.85
        assert result.primary_score == 0.85  # Should use hybrid_score
    
    def test_search_result_primary_score_fallback(self):
        """Test SearchResult primary score fallback."""
        chunk = SemanticChunk(
            uuid="550e8400-e29b-41d4-a716-446655440000",
            type=ChunkType.DOC_BLOCK,
            body="Test chunk content",
            text="Test chunk content"
        )
        
        # No hybrid_score, should fall back to bm25_score
        result = SearchResult(
            chunk_id="test-uuid",
            chunk=chunk,
            bm25_score=0.8,
            semantic_score=0.9,
            rank=1
        )
        
        assert result.primary_score == 0.8  # Should use bm25_score
    
    def test_search_result_validation_invalid_score(self):
        """Test SearchResult validation with invalid score."""
        chunk = SemanticChunk(
            uuid="550e8400-e29b-41d4-a716-446655440000",
            type=ChunkType.DOC_BLOCK,
            body="Test chunk content",
            text="Test chunk content"
        )
        
        with pytest.raises(ValueError, match="bm25_score must be between 0.0 and 1.0"):
            SearchResult(
                chunk_id="test-uuid",
                chunk=chunk,
                bm25_score=1.5  # Invalid score
            )
    
    def test_search_result_validation_negative_rank(self):
        """Test SearchResult validation with negative rank."""
        chunk = SemanticChunk(
            uuid="550e8400-e29b-41d4-a716-446655440000",
            type=ChunkType.DOC_BLOCK,
            body="Test chunk content",
            text="Test chunk content"
        )
        
        with pytest.raises(ValueError, match="Rank must be non-negative"):
            SearchResult(
                chunk_id="test-uuid",
                chunk=chunk,
                rank=-1  # Invalid rank
            )
    
    def test_search_result_to_dict(self):
        """Test SearchResult to_dict() method."""
        chunk = SemanticChunk(
            uuid="550e8400-e29b-41d4-a716-446655440000",
            type=ChunkType.DOC_BLOCK,
            body="Test chunk content",
            text="Test chunk content"
        )
        
        result = SearchResult(
            chunk_id="test-uuid",
            chunk=chunk,
            bm25_score=0.85,
            semantic_score=0.9,
            hybrid_score=0.87,
            rank=1,
            matched_fields=["body", "text"],
            highlights={"body": ["Test chunk content"]}
        )
        
        result_dict = result.to_dict()
        
        assert result_dict["chunk_id"] == "test-uuid"
        assert result_dict["bm25_score"] == 0.85
        assert result_dict["semantic_score"] == 0.9
        assert result_dict["hybrid_score"] == 0.87
        assert result_dict["rank"] == 1
        assert result_dict["matched_fields"] == ["body", "text"]
        assert result_dict["highlights"] == {"body": ["Test chunk content"]}
        assert "chunk" in result_dict
    
    def test_search_result_from_dict(self):
        """Test SearchResult from_dict() method."""
        chunk_data = {
            "uuid": "550e8400-e29b-41d4-a716-446655440000",
            "type": "DocBlock",
            "body": "Test chunk content",
            "text": "Test chunk content"
        }
        
        result_data = {
            "chunk_id": "550e8400-e29b-41d4-a716-446655440000",
            "chunk": chunk_data,
            "bm25_score": 0.85,
            "semantic_score": 0.9,
            "hybrid_score": 0.87,
            "rank": 1,
            "matched_fields": ["body", "text"],
            "highlights": {"body": ["Test chunk content"]}
        }
        
        result = SearchResult.from_dict(result_data)
        
        assert result.chunk_id == "550e8400-e29b-41d4-a716-446655440000"
        assert result.bm25_score == 0.85
        assert result.semantic_score == 0.9
        assert result.hybrid_score == 0.87
        assert result.rank == 1
        assert result.matched_fields == ["body", "text"]
        assert result.highlights == {"body": ["Test chunk content"]}
        assert result.chunk.uuid == "550e8400-e29b-41d4-a716-446655440000"


class TestChunkQueryResponse:
    """Tests for ChunkQueryResponse class."""
    
    def test_response_success_parsing(self):
        """Test parsing successful response."""
        chunk_data = {
            "uuid": "550e8400-e29b-41d4-a716-446655440000",
            "type": "DocBlock",
            "body": "Test chunk content",
            "text": "Test chunk content"
        }
        
        response_data = {
            "status": "success",
            "data": {
                "results": [
                    {
                        "chunk_id": "550e8400-e29b-41d4-a716-446655440000",
                        "chunk": chunk_data,
                        "bm25_score": 0.85,
                        "semantic_score": 0.9,
                        "hybrid_score": 0.87,
                        "rank": 1
                    }
                ],
                "metadata": {"query_time": 0.1},
                "total_results": 1,
                "search_time": 0.05,
                "query_time": 0.1
            }
        }
        
        response = ChunkQueryResponse(response_data)
        
        assert response.is_success is True
        assert len(response.results) == 1
        assert response.results[0].chunk_id == "550e8400-e29b-41d4-a716-446655440000"
        assert response.results[0].bm25_score == 0.85
        assert response.total_results == 1
        assert response.search_time == 0.05
        assert response.query_time == 0.1
    
    def test_response_error_parsing(self):
        """Test parsing error response."""
        response_data = {
            "status": "error",
            "error": "Invalid query parameters"
        }
        
        response = ChunkQueryResponse(response_data)
        
        assert response.is_success is False
        assert response.error_message == "Invalid query parameters"
        assert len(response.results) == 0
        assert response.total_results == 0
    
    def test_response_validation_missing_status(self):
        """Test response validation with missing status."""
        response_data = {
            "data": {"results": []}
        }
        
        with pytest.raises(ValueError, match="Missing required field in response: status"):
            ChunkQueryResponse(response_data)
    
    def test_response_validation_missing_data(self):
        """Test response validation with missing data."""
        response_data = {
            "status": "success"
        }
        
        with pytest.raises(ValueError, match="Missing required field in response: data"):
            ChunkQueryResponse(response_data)
    
    def test_response_validation_invalid_status(self):
        """Test response validation with invalid status."""
        response_data = {
            "status": "invalid",
            "data": {"results": []}
        }
        
        with pytest.raises(ValueError, match="Invalid status in response: invalid"):
            ChunkQueryResponse(response_data)
    
    def test_get_results_with_limit(self):
        """Test get_results() with limit."""
        chunk_data = {"uuid": "550e8400-e29b-41d4-a716-446655440000", "type": "DocBlock", "body": "Test", "text": "Test"}
        
        response_data = {
            "status": "success",
            "data": {
                "results": [
                    {"chunk_id": "test-1", "chunk": chunk_data, "rank": 1},
                    {"chunk_id": "test-2", "chunk": chunk_data, "rank": 2},
                    {"chunk_id": "test-3", "chunk": chunk_data, "rank": 3}
                ],
                "total_results": 3
            }
        }
        
        response = ChunkQueryResponse(response_data)
        
        limited_results = response.get_results(limit=2)
        assert len(limited_results) == 2
        assert limited_results[0].chunk_id == "test-1"
        assert limited_results[1].chunk_id == "test-2"
    
    def test_get_top_results(self):
        """Test get_top_results() method."""
        chunk_data = {"uuid": "550e8400-e29b-41d4-a716-446655440000", "type": "DocBlock", "body": "Test", "text": "Test"}
        
        response_data = {
            "status": "success",
            "data": {
                "results": [
                    {"chunk_id": "test-1", "chunk": chunk_data, "bm25_score": 0.5, "rank": 1},
                    {"chunk_id": "test-2", "chunk": chunk_data, "bm25_score": 0.9, "rank": 2},
                    {"chunk_id": "test-3", "chunk": chunk_data, "bm25_score": 0.7, "rank": 3}
                ],
                "total_results": 3
            }
        }
        
        response = ChunkQueryResponse(response_data)
        
        top_results = response.get_top_results(n=2)
        assert len(top_results) == 2
        assert top_results[0].chunk_id == "test-2"  # Highest score
        assert top_results[1].chunk_id == "test-3"  # Second highest score
    
    def test_get_results_by_score_threshold(self):
        """Test get_results_by_score_threshold() method."""
        chunk_data = {"uuid": "550e8400-e29b-41d4-a716-446655440000", "type": "DocBlock", "body": "Test", "text": "Test"}
        
        response_data = {
            "status": "success",
            "data": {
                "results": [
                    {"chunk_id": "test-1", "chunk": chunk_data, "bm25_score": 0.5, "rank": 1},
                    {"chunk_id": "test-2", "chunk": chunk_data, "bm25_score": 0.9, "rank": 2},
                    {"chunk_id": "test-3", "chunk": chunk_data, "bm25_score": 0.7, "rank": 3}
                ],
                "total_results": 3
            }
        }
        
        response = ChunkQueryResponse(response_data)
        
        high_score_results = response.get_results_by_score_threshold(0.6)
        assert len(high_score_results) == 2
        assert high_score_results[0].chunk_id == "test-2"
        assert high_score_results[1].chunk_id == "test-3"
    
    def test_get_statistics(self):
        """Test get_statistics() method."""
        chunk_data = {"uuid": "550e8400-e29b-41d4-a716-446655440000", "type": "DocBlock", "body": "Test", "text": "Test"}
        
        response_data = {
            "status": "success",
            "data": {
                "results": [
                    {"chunk_id": "test-1", "chunk": chunk_data, "bm25_score": 0.5, "rank": 1},
                    {"chunk_id": "test-2", "chunk": chunk_data, "bm25_score": 0.9, "rank": 2},
                    {"chunk_id": "test-3", "chunk": chunk_data, "bm25_score": 0.7, "rank": 3}
                ],
                "metadata": {"query_time": 0.1},
                "total_results": 3,
                "search_time": 0.05,
                "query_time": 0.1
            }
        }
        
        response = ChunkQueryResponse(response_data)
        
        stats = response.get_statistics()
        
        assert stats["total_results"] == 3
        assert stats["returned_results"] == 3
        assert stats["search_time"] == 0.05
        assert stats["query_time"] == 0.1
        assert stats["min_score"] == 0.5
        assert stats["max_score"] == 0.9
        assert abs(stats["avg_score"] - 0.7) < 0.001
        assert "score_distribution" in stats
    
    def test_from_json(self):
        """Test from_json() method."""
        chunk_data = {"uuid": "550e8400-e29b-41d4-a716-446655440000", "type": "DocBlock", "body": "Test", "text": "Test"}
        
        response_data = {
            "status": "success",
            "data": {
                "results": [
                    {"chunk_id": "test-uuid", "chunk": chunk_data, "bm25_score": 0.85, "rank": 1}
                ],
                "total_results": 1
            }
        }
        
        json_str = json.dumps(response_data)
        response = ChunkQueryResponse.from_json(json_str)
        
        assert response.is_success is True
        assert len(response.results) == 1
        assert response.results[0].bm25_score == 0.85
    
    def test_from_json_invalid(self):
        """Test from_json() with invalid JSON."""
        with pytest.raises(ValueError, match="Invalid JSON response"):
            ChunkQueryResponse.from_json("invalid json")


class TestSearchResponseBuilder:
    """Tests for SearchResponseBuilder class."""
    
    def test_builder_basic_usage(self):
        """Test basic usage of SearchResponseBuilder."""
        chunk = SemanticChunk(
            uuid="550e8400-e29b-41d4-a716-446655440000",
            type=ChunkType.DOC_BLOCK,
            body="Test chunk content",
            text="Test chunk content"
        )
        
        result = SearchResult(
            chunk_id="test-uuid",
            chunk=chunk,
            bm25_score=0.85,
            rank=1
        )
        
        builder = SearchResponseBuilder()
        response = builder.add_result(result).build()
        
        assert response.is_success is True
        assert len(response.results) == 1
        assert response.results[0].chunk_id == "test-uuid"
        assert response.results[0].bm25_score == 0.85
    
    def test_builder_with_metadata(self):
        """Test SearchResponseBuilder with metadata."""
        chunk = SemanticChunk(
            uuid="550e8400-e29b-41d4-a716-446655440000",
            type=ChunkType.DOC_BLOCK,
            body="Test chunk content",
            text="Test chunk content"
        )
        
        result = SearchResult(
            chunk_id="test-uuid",
            chunk=chunk,
            bm25_score=0.85,
            rank=1
        )
        
        metadata = {"query_type": "bm25", "index_version": "1.0"}
        
        builder = SearchResponseBuilder()
        response = builder.add_result(result).set_metadata(metadata).build()
        
        assert response.metadata == metadata
    
    def test_builder_with_timing(self):
        """Test SearchResponseBuilder with timing information."""
        chunk = SemanticChunk(
            uuid="550e8400-e29b-41d4-a716-446655440000",
            type=ChunkType.DOC_BLOCK,
            body="Test chunk content",
            text="Test chunk content"
        )
        
        result = SearchResult(
            chunk_id="test-uuid",
            chunk=chunk,
            bm25_score=0.85,
            rank=1
        )
        
        builder = SearchResponseBuilder()
        response = builder.add_result(result).set_timing(0.05, 0.1).build()
        
        assert response.search_time == 0.05
        assert response.query_time == 0.1
    
    def test_builder_error_response(self):
        """Test SearchResponseBuilder error response."""
        builder = SearchResponseBuilder()
        response = builder.build_error("Invalid query parameters")
        
        assert response.is_success is False
        assert response.error_message == "Invalid query parameters"
        assert len(response.results) == 0
