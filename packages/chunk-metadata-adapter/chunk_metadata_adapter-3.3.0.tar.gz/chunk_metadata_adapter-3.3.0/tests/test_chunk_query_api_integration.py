"""
Integration tests for BM25 API integration in ChunkQuery.

This module tests the integration of BM25 parameters with the API,
including request formation, parameter transmission, and response handling.

Test coverage:
- API request formation with BM25 parameters
- Parameter transmission to server
- Response parsing and handling
- Error handling for API responses
- Compatibility with existing API

Author: Development Team
Created: 2024-01-20
"""

import pytest
import json
from unittest.mock import Mock, patch
from datetime import datetime

from chunk_metadata_adapter import ChunkQuery, SearchResult, ChunkQueryResponse
from chunk_metadata_adapter.search_response import SearchResponseBuilder


class TestChunkQueryAPIIntegration:
    """Integration tests for ChunkQuery API functionality."""
    
    def test_to_api_request_basic(self):
        """Test basic API request formation."""
        query = ChunkQuery(
            type="DocBlock",
            search_query="python programming",
            search_fields=["body", "text"],
            bm25_k1=1.5,
            bm25_b=0.8
        )
        
        request = query.to_api_request()
        
        # Check API metadata
        assert request['api_version'] == '3.3.0'
        assert request['request_type'] == 'chunk_query'
        assert 'timestamp' in request
        
        # Check query parameters
        assert request['type'] == "DocBlock"
        assert request['search_query'] == "python programming"
        assert request['search_fields'] == ["body", "text"]
        assert request['bm25_k1'] == 1.5
        assert request['bm25_b'] == 0.8
    
    def test_to_api_request_hybrid_search(self):
        """Test API request formation with hybrid search."""
        query = ChunkQuery(
            search_query="machine learning",
            hybrid_search=True,
            bm25_weight=0.3,
            semantic_weight=0.7,
            min_score=0.5,
            max_results=50
        )
        
        request = query.to_api_request()
        
        # Check hybrid search parameters
        assert request['search_query'] == "machine learning"
        assert request['hybrid_search'] is True
        assert request['bm25_weight'] == 0.3
        assert request['semantic_weight'] == 0.7
        assert request['min_score'] == 0.5
        assert request['max_results'] == 50
    
    def test_to_api_request_without_search_params(self):
        """Test API request formation without search parameters."""
        query = ChunkQuery(
            type="DocBlock",
            quality_score=">=0.8",
            tags="in:ai,ml"
        )
        
        request = query.to_api_request(include_search_params=False)
        
        # Check that search parameters are not included
        assert 'search_query' not in request
        assert 'search_fields' not in request
        assert 'bm25_k1' not in request
        assert 'bm25_b' not in request
        
        # Check that regular parameters are included
        assert request['type'] == "DocBlock"
        assert request['quality_score'] == ">=0.8"
        assert request['tags'] == "in:ai,ml"
    
    def test_to_api_request_with_filter_expression(self):
        """Test API request formation with filter expression."""
        query = ChunkQuery(
            filter_expr="(type = 'DocBlock' OR type = 'CodeBlock') AND quality_score >= 0.7",
            search_query="artificial intelligence",
            hybrid_search=True
        )
        
        request = query.to_api_request()
        
        # Check filter expression
        assert request['filter_expr'] == "(type = 'DocBlock' OR type = 'CodeBlock') AND quality_score >= 0.7"
        
        # Check search parameters
        assert request['search_query'] == "artificial intelligence"
        assert request['hybrid_search'] is True
    
    def test_to_flat_dict_with_bm25_params(self):
        """Test flat dictionary conversion with BM25 parameters."""
        query = ChunkQuery(
            search_query="python",
            search_fields=["body", "text"],
            bm25_k1=1.2,
            bm25_b=0.75,
            hybrid_search=True,
            bm25_weight=0.6,
            semantic_weight=0.4
        )
        
        flat_dict = query.to_flat_dict()
        
        # Check that BM25 parameters are properly serialized
        assert flat_dict['search_query'] == "python"
        # Note: search_fields is serialized as list, not JSON string in current implementation
        assert flat_dict['search_fields'] == ["body", "text"]
        assert flat_dict['bm25_k1'] == "1.2"
        assert flat_dict['bm25_b'] == "0.75"
        assert flat_dict['hybrid_search'] == "true"
        assert flat_dict['bm25_weight'] == "0.6"
        assert flat_dict['semantic_weight'] == "0.4"
    
    def test_from_flat_dict_with_bm25_params(self):
        """Test flat dictionary deserialization with BM25 parameters."""
        flat_data = {
            'search_query': 'machine learning',
            'search_fields': '["body", "text", "summary"]',
            'bm25_k1': '1.5',
            'bm25_b': '0.8',
            'hybrid_search': 'true',
            'bm25_weight': '0.3',
            'semantic_weight': '0.7'
        }
        
        query = ChunkQuery.from_flat_dict(flat_data)
        
        # Check that BM25 parameters are properly deserialized
        assert query.search_query == "machine learning"
        assert query.search_fields == ["body", "text", "summary"]
        assert query.bm25_k1 == 1.5
        assert query.bm25_b == 0.8
        assert query.hybrid_search is True
        assert query.bm25_weight == 0.3
        assert query.semantic_weight == 0.7


class TestSearchResponseHandling:
    """Tests for search response handling."""
    
    def test_search_result_creation(self):
        """Test creating SearchResult with BM25 scores."""
        from chunk_metadata_adapter.semantic_chunk import SemanticChunk
        
        chunk = SemanticChunk(
            id="chunk_1",
            type="DocBlock",
            title="Test Document",
            body="Test content about Python programming"
        )
        
        result = SearchResult(
            chunk_id="chunk_1",
            chunk=chunk,
            bm25_score=0.85,
            semantic_score=0.72,
            hybrid_score=0.78,
            rank=1,
            matched_fields=["title", "body"],
            highlights={
                "title": ["Test <em>Document</em>"],
                "body": ["Test <em>content</em> about Python programming"]
            }
        )
        
        assert result.chunk_id == "chunk_1"
        assert result.bm25_score == 0.85
        assert result.semantic_score == 0.72
        assert result.hybrid_score == 0.78
        assert result.rank == 1
        assert result.matched_fields == ["title", "body"]
        assert result.highlights["title"] == ["Test <em>Document</em>"]
    
    def test_search_result_score_validation(self):
        """Test score validation in SearchResult."""
        from chunk_metadata_adapter.semantic_chunk import SemanticChunk
        
        chunk = SemanticChunk(
            id="chunk_1",
            type="DocBlock",
            title="Test",
            body="Test content"
        )
        
        # Test valid scores
        result = SearchResult(
            chunk_id="chunk_1",
            chunk=chunk,
            bm25_score=0.5,
            semantic_score=0.7,
            hybrid_score=0.6
        )
        assert result.bm25_score == 0.5
        
        # Test invalid scores
        with pytest.raises(ValueError, match="bm25_score must be between 0.0 and 1.0"):
            SearchResult(
                chunk_id="chunk_1",
                chunk=chunk,
                bm25_score=1.5
            )
        
        with pytest.raises(ValueError, match="semantic_score must be between 0.0 and 1.0"):
            SearchResult(
                chunk_id="chunk_1",
                chunk=chunk,
                semantic_score=-0.1
            )
    
    def test_search_result_primary_score(self):
        """Test primary score calculation."""
        from chunk_metadata_adapter.semantic_chunk import SemanticChunk
        
        chunk = SemanticChunk(
            id="chunk_1",
            type="DocBlock",
            title="Test",
            body="Test content"
        )
        
        # Test hybrid score as primary
        result = SearchResult(
            chunk_id="chunk_1",
            chunk=chunk,
            bm25_score=0.8,
            semantic_score=0.6,
            hybrid_score=0.7
        )
        assert result.primary_score == 0.7
        
        # Test BM25 score as primary (no hybrid)
        result = SearchResult(
            chunk_id="chunk_1",
            chunk=chunk,
            bm25_score=0.8,
            semantic_score=0.6
        )
        assert result.primary_score == 0.8
        
        # Test semantic score as primary (no BM25 or hybrid)
        result = SearchResult(
            chunk_id="chunk_1",
            chunk=chunk,
            semantic_score=0.6
        )
        assert result.primary_score == 0.6
        
        # Test no scores
        result = SearchResult(
            chunk_id="chunk_1",
            chunk=chunk
        )
        assert result.primary_score is None
    
    def test_search_result_to_dict(self):
        """Test SearchResult serialization to dictionary."""
        from chunk_metadata_adapter.semantic_chunk import SemanticChunk
        
        chunk = SemanticChunk(
            id="chunk_1",
            type="DocBlock",
            title="Test Document",
            body="Test content"
        )
        
        result = SearchResult(
            chunk_id="chunk_1",
            chunk=chunk,
            bm25_score=0.85,
            semantic_score=0.72,
            hybrid_score=0.78,
            rank=1,
            matched_fields=["title", "body"],
            highlights={
                "title": ["Test <em>Document</em>"],
                "body": ["Test <em>content</em>"]
            }
        )
        
        result_dict = result.to_dict()
        
        assert result_dict['chunk_id'] == "chunk_1"
        assert result_dict['bm25_score'] == 0.85
        assert result_dict['semantic_score'] == 0.72
        assert result_dict['hybrid_score'] == 0.78
        assert result_dict['rank'] == 1
        assert result_dict['matched_fields'] == ["title", "body"]
        assert result_dict['highlights']['title'] == ["Test <em>Document</em>"]
        assert 'chunk' in result_dict


class TestChunkQueryResponseHandling:
    """Tests for ChunkQueryResponse handling."""
    
    def test_successful_response_parsing(self):
        """Test parsing successful server response."""
        response_data = {
            'status': 'success',
            'data': {
                'results': [
                    {
                        'chunk_id': 'chunk_1',
                        'chunk': {
                            'id': 'chunk_1',
                            'type': 'DocBlock',
                            'title': 'Test Document',
                            'body': 'Test content'
                        },
                        'bm25_score': 0.85,
                        'semantic_score': 0.72,
                        'hybrid_score': 0.78,
                        'rank': 1,
                        'matched_fields': ['title', 'body'],
                        'highlights': {
                            'title': ['Test <em>Document</em>'],
                            'body': ['Test <em>content</em>']
                        }
                    }
                ],
                'total_results': 1,
                'search_time': 0.045
            }
        }
        
        response = ChunkQueryResponse(response_data)
        
        assert response.is_success is True
        assert response.total_results == 1
        assert response.search_time == 0.045
        
        results = response.get_results()
        assert len(results) == 1
        
        result = results[0]
        assert result.chunk_id == 'chunk_1'
        assert result.bm25_score == 0.85
        assert result.semantic_score == 0.72
        assert result.hybrid_score == 0.78
        assert result.rank == 1
        assert result.matched_fields == ['title', 'body']
    
    def test_error_response_handling(self):
        """Test handling of error responses."""
        error_response = {
            'status': 'error',
            'data': {},  # Required field
            'error': 'Invalid search query',
            'error_code': 'INVALID_QUERY'
        }
        
        response = ChunkQueryResponse(error_response)
        
        assert response.is_success is False
        assert response.error_message == 'Invalid search query'
        
        # get_results should return empty list for error responses
        results = response.get_results()
        assert len(results) == 0
    
    def test_empty_response_handling(self):
        """Test handling of empty response."""
        empty_response = {
            'status': 'success',
            'data': {
                'results': [],
                'total_results': 0
            }
        }
        
        response = ChunkQueryResponse(empty_response)
        
        assert response.is_success is True
        assert response.total_results == 0
        assert len(response.get_results()) == 0
    
    def test_response_statistics(self):
        """Test response statistics."""
        response_data = {
            'status': 'success',
            'data': {
                'results': [],
                'total_results': 0,
                'search_time': 0.123,
                'query_time': 0.045,
                'metadata': {
                    'search_type': 'hybrid',
                    'bm25_weight': 0.6,
                    'semantic_weight': 0.4
                }
            }
        }
        
        response = ChunkQueryResponse(response_data)
        
        stats = response.get_statistics()
        assert stats['total_results'] == 0
        assert stats['search_time'] == 0.123
        assert stats['query_time'] == 0.045
        assert stats['metadata']['search_type'] == 'hybrid'
        assert stats['metadata']['bm25_weight'] == 0.6


class TestSearchResponseBuilder:
    """Tests for SearchResponseBuilder."""
    
    def test_builder_creation(self):
        """Test creating SearchResponseBuilder."""
        builder = SearchResponseBuilder()
        
        assert len(builder.results) == 0
    
    def test_adding_results(self):
        """Test adding results to builder."""
        from chunk_metadata_adapter.semantic_chunk import SemanticChunk
        
        builder = SearchResponseBuilder()
        
        chunk1 = SemanticChunk(
            id="chunk_1",
            type="DocBlock",
            title="Test 1",
            body="Test content 1"
        )
        chunk2 = SemanticChunk(
            id="chunk_2",
            type="DocBlock",
            title="Test 2",
            body="Test content 2"
        )
        
        result1 = SearchResult(
            chunk_id="chunk_1",
            chunk=chunk1,
            bm25_score=0.8,
            rank=1
        )
        
        result2 = SearchResult(
            chunk_id="chunk_2",
            chunk=chunk2,
            bm25_score=0.6,
            rank=2
        )
        
        builder.add_result(result1)
        builder.add_result(result2)
        
        assert len(builder.results) == 2
        assert builder.results[0].chunk_id == "chunk_1"
        assert builder.results[1].chunk_id == "chunk_2"
    
    def test_builder_sorting(self):
        """Test result sorting in builder."""
        from chunk_metadata_adapter.semantic_chunk import SemanticChunk
        
        builder = SearchResponseBuilder()
        
        chunk1 = SemanticChunk(id="chunk_1", type="DocBlock", title="Test 1", body="Content 1")
        chunk2 = SemanticChunk(id="chunk_2", type="DocBlock", title="Test 2", body="Content 2")
        chunk3 = SemanticChunk(id="chunk_3", type="DocBlock", title="Test 3", body="Content 3")
        
        # Add results in random order
        result1 = SearchResult(chunk_id="chunk_1", chunk=chunk1, bm25_score=0.6, rank=3)
        result2 = SearchResult(chunk_id="chunk_2", chunk=chunk2, bm25_score=0.8, rank=1)
        result3 = SearchResult(chunk_id="chunk_3", chunk=chunk3, bm25_score=0.7, rank=2)
        
        builder.add_result(result1)
        builder.add_result(result2)
        builder.add_result(result3)
        
        # Results should be sorted by rank
        results = builder.results
        assert results[0].rank == 1
        assert results[1].rank == 2
        assert results[2].rank == 3
    
    def test_builder_filtering(self):
        """Test result filtering in builder."""
        from chunk_metadata_adapter.semantic_chunk import SemanticChunk
        
        builder = SearchResponseBuilder()
        
        chunk1 = SemanticChunk(id="chunk_1", type="DocBlock", title="Test 1", body="Content 1")
        chunk2 = SemanticChunk(id="chunk_2", type="DocBlock", title="Test 2", body="Content 2")
        chunk3 = SemanticChunk(id="chunk_3", type="DocBlock", title="Test 3", body="Content 3")
        
        result1 = SearchResult(chunk_id="chunk_1", chunk=chunk1, bm25_score=0.9, rank=1)
        result2 = SearchResult(chunk_id="chunk_2", chunk=chunk2, bm25_score=0.5, rank=2)
        result3 = SearchResult(chunk_id="chunk_3", chunk=chunk3, bm25_score=0.7, rank=3)
        
        builder.add_result(result1)
        builder.add_result(result2)
        builder.add_result(result3)
        
        # Filter by score threshold manually
        high_score_results = [r for r in builder.results if r.primary_score and r.primary_score >= 0.7]
        assert len(high_score_results) == 2
        assert high_score_results[0].chunk_id == "chunk_1"
        assert high_score_results[1].chunk_id == "chunk_3"
        
        # Get top results manually
        top_results = sorted(builder.results, key=lambda r: r.rank)[:2]
        assert len(top_results) == 2
        assert top_results[0].chunk_id == "chunk_1"
        assert top_results[1].chunk_id == "chunk_2"


class TestAPICompatibility:
    """Tests for API compatibility."""
    
    def test_backward_compatibility(self):
        """Test backward compatibility with existing API."""
        # Test that existing queries still work
        query = ChunkQuery(
            type="DocBlock",
            quality_score=">=0.8",
            tags="in:ai,ml"
        )
        
        request = query.to_api_request()
        
        # Check that existing fields are preserved
        assert request['type'] == "DocBlock"
        assert request['quality_score'] == ">=0.8"
        assert request['tags'] == "in:ai,ml"
        
        # Check that new fields are not present when not used
        assert 'search_query' not in request
        assert 'bm25_k1' not in request
    
    def test_forward_compatibility(self):
        """Test forward compatibility with new API features."""
        # Test that new features work alongside existing ones
        query = ChunkQuery(
            type="DocBlock",
            quality_score=">=0.8",
            search_query="python programming",
            hybrid_search=True
        )
        
        request = query.to_api_request()
        
        # Check that both old and new fields are present
        assert request['type'] == "DocBlock"
        assert request['quality_score'] == ">=0.8"
        assert request['search_query'] == "python programming"
        assert request['hybrid_search'] is True
    
    def test_serialization_compatibility(self):
        """Test serialization compatibility."""
        query = ChunkQuery(
            type="DocBlock",
            search_query="test",
            bm25_k1=1.2,
            bm25_b=0.75
        )
        
        # Test round-trip serialization
        flat_dict = query.to_flat_dict()
        restored_query = ChunkQuery.from_flat_dict(flat_dict)
        
        assert restored_query.type == query.type
        assert restored_query.search_query == query.search_query
        assert restored_query.bm25_k1 == query.bm25_k1
        assert restored_query.bm25_b == query.bm25_b
