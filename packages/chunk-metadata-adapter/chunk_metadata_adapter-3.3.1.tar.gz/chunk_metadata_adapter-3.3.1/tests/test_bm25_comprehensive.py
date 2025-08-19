"""
Comprehensive tests for BM25 and hybrid search functionality.

This module provides comprehensive testing of all BM25 and hybrid search
features, including integration tests, performance tests, and compatibility tests.

Test coverage:
- Complete BM25 functionality
- Hybrid search strategies
- API integration
- Performance benchmarks
- Compatibility testing
- Error handling

Author: Development Team
Created: 2024-01-20
"""

import pytest
import time
from unittest.mock import Mock, patch
from typing import List, Dict, Any

from chunk_metadata_adapter import (
    ChunkQuery, SemanticChunk, SearchResult, ChunkQueryResponse,
    HybridStrategy, HybridSearchConfig, HybridSearchHelper, HybridSearchValidator
)


class TestBM25Comprehensive:
    """Comprehensive tests for BM25 functionality."""
    
    def test_complete_bm25_workflow(self):
        """Test complete BM25 search workflow."""
        # Create query with BM25 parameters
        query = ChunkQuery(
            search_query="python machine learning",
            search_fields=["body", "text", "summary"],
            bm25_k1=1.2,
            bm25_b=0.75,
            min_score=0.5,
            max_results=50
        )
        
        # Validate query
        validation = query.validate_bm25_parameters()
        assert validation.is_valid is True
        assert len(validation.errors) == 0
        
        # Check BM25 search availability
        assert query.has_bm25_search() is True
        
        # Get search parameters
        search_params = query.get_search_params()
        assert search_params['search_query'] == "python machine learning"
        assert search_params['search_fields'] == ["body", "text", "summary"]
        assert search_params['bm25_k1'] == 1.2
        assert search_params['bm25_b'] == 0.75
        
        # Create API request
        api_request = query.to_api_request()
        assert api_request['search_query'] == "python machine learning"
        assert api_request['api_version'] == '3.3.0'
        assert 'timestamp' in api_request
    
    def test_hybrid_search_workflow(self):
        """Test complete hybrid search workflow."""
        # Create query with hybrid search
        query = ChunkQuery(
            search_query="artificial intelligence",
            search_fields=["title", "body"],
            hybrid_search=True,
            bm25_weight=0.6,
            semantic_weight=0.4,
            min_score=0.7,
            max_results=100
        )
        
        # Validate hybrid parameters
        validation = query.validate_bm25_parameters()
        assert validation.is_valid is True
        
        # Create API request
        api_request = query.to_api_request()
        assert api_request['hybrid_search'] is True
        assert api_request['bm25_weight'] == 0.6
        assert api_request['semantic_weight'] == 0.4
        
        # Test hybrid score calculation
        bm25_scores = [0.8, 0.6, 0.9]
        semantic_scores = [0.7, 0.5, 0.8]
        
        config = HybridSearchConfig(
            bm25_weight=0.6,
            semantic_weight=0.4,
            strategy=HybridStrategy.WEIGHTED_SUM
        )
        
        hybrid_scores = HybridSearchHelper.calculate_hybrid_scores(
            bm25_scores, semantic_scores, config
        )
        
        assert len(hybrid_scores) == 3
        assert all(0.0 <= score <= 1.0 for score in hybrid_scores)
    
    def test_all_hybrid_strategies(self):
        """Test all hybrid search strategies."""
        bm25_scores = [0.8, 0.6, 0.9]
        semantic_scores = [0.7, 0.5, 0.8]
        
        # Test Weighted Sum
        config = HybridSearchConfig(strategy=HybridStrategy.WEIGHTED_SUM)
        scores = HybridSearchHelper.calculate_hybrid_scores(
            bm25_scores, semantic_scores, config
        )
        assert len(scores) == 3
        
        # Test CombSUM
        config = HybridSearchConfig(strategy=HybridStrategy.COMB_SUM)
        scores = HybridSearchHelper.calculate_hybrid_scores(
            bm25_scores, semantic_scores, config
        )
        assert len(scores) == 3
        
        # Test CombMNZ
        config = HybridSearchConfig(strategy=HybridStrategy.COMB_MNZ)
        scores = HybridSearchHelper.calculate_hybrid_scores(
            bm25_scores, semantic_scores, config
        )
        assert len(scores) == 3
        
        # Test Reciprocal Rank
        bm25_ranks = [1, 3, 2]
        semantic_ranks = [2, 1, 3]
        scores = HybridSearchHelper.reciprocal_rank(
            bm25_ranks, semantic_ranks, 0.6, 0.4
        )
        assert len(scores) == 3
    
    def test_error_handling(self):
        """Test error handling in BM25 and hybrid search."""
        # Test invalid weights
        with pytest.raises(ValueError):
            HybridSearchConfig(bm25_weight=1.5, semantic_weight=0.5)
        
        # Test invalid strategy
        with pytest.raises(ValueError):
            HybridSearchValidator.validate_strategy("invalid_strategy")
        
        # Test invalid score lists
        with pytest.raises(ValueError):
            HybridSearchHelper.weighted_sum([0.8, 0.6], [0.7], 0.5, 0.5)
        
        # Test invalid query without search query
        query = ChunkQuery(
            bm25_k1=1.5,
            hybrid_search=True
        )
        validation = query.validate_bm25_parameters()
        assert len(validation.warnings) > 0
    
    def test_performance_benchmarks(self):
        """Test performance of BM25 and hybrid search operations."""
        # Test query creation performance
        start_time = time.time()
        for _ in range(1000):
            query = ChunkQuery(
                search_query="test query",
                hybrid_search=True,
                bm25_weight=0.6,
                semantic_weight=0.4
            )
        creation_time = time.time() - start_time
        assert creation_time < 1.0  # Should be very fast
        
        # Test validation performance
        start_time = time.time()
        for _ in range(1000):
            validation = query.validate_bm25_parameters()
        validation_time = time.time() - start_time
        assert validation_time < 1.0
        
        # Test hybrid score calculation performance
        bm25_scores = [0.8] * 1000
        semantic_scores = [0.7] * 1000
        config = HybridSearchConfig()
        
        start_time = time.time()
        hybrid_scores = HybridSearchHelper.calculate_hybrid_scores(
            bm25_scores, semantic_scores, config
        )
        calculation_time = time.time() - start_time
        assert calculation_time < 0.1  # Should be very fast
        assert len(hybrid_scores) == 1000
    
    def test_compatibility_with_existing_queries(self):
        """Test compatibility with existing ChunkQuery usage."""
        # Test that existing queries still work
        query = ChunkQuery(
            type="DocBlock",
            quality_score=">=0.8",
            tags="in:ai,ml"
        )
        
        # Should work without BM25 parameters
        validation = query.validate_bm25_parameters()
        assert validation.is_valid is True
        
        # Should not have BM25 search
        assert query.has_bm25_search() is False
        
        # API request should not include BM25 parameters
        api_request = query.to_api_request(include_search_params=False)
        assert 'search_query' not in api_request
        assert 'hybrid_search' not in api_request
    
    def test_serialization_compatibility(self):
        """Test serialization compatibility."""
        # Test flat dictionary serialization
        query = ChunkQuery(
            search_query="test query",
            hybrid_search=True,
            bm25_weight=0.6,
            semantic_weight=0.4
        )
        
        flat_dict = query.to_flat_dict()
        assert 'search_query' in flat_dict
        assert 'hybrid_search' in flat_dict
        assert 'bm25_weight' in flat_dict
        assert 'semantic_weight' in flat_dict
        
        # Test deserialization
        restored_query = ChunkQuery.from_flat_dict(flat_dict)
        assert restored_query.search_query == "test query"
        assert restored_query.hybrid_search is True
        assert restored_query.bm25_weight == 0.6
        assert restored_query.semantic_weight == 0.4
    
    def test_response_handling(self):
        """Test handling of search responses."""
        # Mock response data
        response_data = {
            'status': 'success',
            'data': {
                'results': [
                    {
                        'chunk_id': 'chunk_1',
                        'chunk': {
                            'type': 'DocBlock',
                            'body': 'Test content',
                            'quality_score': 0.8
                        },
                        'bm25_score': 0.85,
                        'semantic_score': 0.72,
                        'hybrid_score': 0.78,
                        'rank': 1,
                        'matched_fields': ['title', 'body']
                    }
                ],
                'total_results': 1,
                'search_time': 0.045
            }
        }
        
        # Create response object
        response = ChunkQueryResponse(response_data)
        
        # Test response properties
        assert response.is_success is True
        assert len(response.results) == 1
        assert response.total_results == 1
        
        # Test result properties
        result = response.results[0]
        assert result.bm25_score == 0.85
        assert result.semantic_score == 0.72
        assert result.hybrid_score == 0.78
        assert result.rank == 1
        assert result.matched_fields == ['title', 'body']
    
    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        # Test empty search query
        query = ChunkQuery(search_query="")
        assert query.has_bm25_search() is False
        
        # Test very long search query
        long_query = "a" * 10000
        query = ChunkQuery(search_query=long_query)
        validation = query.validate_bm25_parameters()
        assert validation.is_valid is True
        
        # Test extreme weights
        query = ChunkQuery(
            search_query="test",
            hybrid_search=True,
            bm25_weight=0.99,
            semantic_weight=0.01
        )
        validation = query.validate_bm25_parameters()
        assert validation.is_valid is True
        assert len(validation.warnings) > 0  # Should warn about extreme weights
        
        # Test zero scores
        bm25_scores = [0.0, 0.0, 0.0]
        semantic_scores = [0.0, 0.0, 0.0]
        config = HybridSearchConfig(normalize_scores=False)  # Don't normalize zero scores
        
        hybrid_scores = HybridSearchHelper.calculate_hybrid_scores(
            bm25_scores, semantic_scores, config
        )
        assert len(hybrid_scores) == 3
        assert all(score == 0.0 for score in hybrid_scores)
    
    def test_integration_scenarios(self):
        """Test real-world integration scenarios."""
        # Scenario 1: Content search
        content_query = ChunkQuery(
            search_query="machine learning algorithms",
            search_fields=["title", "body", "summary"],
            hybrid_search=True,
            bm25_weight=0.7,
            semantic_weight=0.3,
            min_score=0.6,
            max_results=20
        )
        
        validation = content_query.validate_bm25_parameters()
        assert validation.is_valid is True
        
        # Scenario 2: Code search
        code_query = ChunkQuery(
            search_query="def train_model",
            search_fields=["body"],
            hybrid_search=False,  # BM25 only for code
            min_score=0.8,
            max_results=10
        )
        
        validation = code_query.validate_bm25_parameters()
        assert validation.is_valid is True
        
        # Scenario 3: Mixed search
        mixed_query = ChunkQuery(
            search_query="python data science",
            search_fields=["title", "body", "summary"],
            hybrid_search=True,
            bm25_weight=0.5,
            semantic_weight=0.5,
            filter_expr="type = 'DocBlock' OR type = 'CodeBlock'",
            min_score=0.5,
            max_results=50
        )
        
        validation = mixed_query.validate_bm25_parameters()
        assert validation.is_valid is True


class TestBM25PropertyBased:
    """Property-based tests for BM25 functionality."""
    
    def test_weight_validation_properties(self):
        """Test properties of weight validation."""
        # Property: Valid weights should pass validation
        valid_weights = [(0.5, 0.5), (0.0, 1.0), (1.0, 0.0), (0.3, 0.7)]
        for bm25_weight, semantic_weight in valid_weights:
            assert HybridSearchValidator.validate_weights(bm25_weight, semantic_weight)
        
        # Property: Invalid weights should raise ValueError
        invalid_weights = [(0.5, 0.6), (-0.1, 1.1), (1.1, -0.1)]
        for bm25_weight, semantic_weight in invalid_weights:
            with pytest.raises(ValueError):
                HybridSearchValidator.validate_weights(bm25_weight, semantic_weight)
    
    def test_score_normalization_properties(self):
        """Test properties of score normalization."""
        # Property: Normalized scores should be in [0, 1] range
        scores = [0.2, 0.5, 0.8]
        normalized = HybridSearchHelper.normalize_scores(scores)
        assert all(0.0 <= score <= 1.0 for score in normalized)
        
        # Property: Min and max values should be preserved
        assert normalized[0] == 0.0  # Min becomes 0.0
        assert normalized[2] == 1.0  # Max becomes 1.0
        
        # Property: Order should be preserved
        assert normalized[0] <= normalized[1] <= normalized[2]
    
    def test_hybrid_score_properties(self):
        """Test properties of hybrid score calculation."""
        bm25_scores = [0.8, 0.6, 0.9]
        semantic_scores = [0.7, 0.5, 0.8]
        config = HybridSearchConfig()
        
        hybrid_scores = HybridSearchHelper.calculate_hybrid_scores(
            bm25_scores, semantic_scores, config
        )
        
        # Property: Number of scores should be preserved
        assert len(hybrid_scores) == len(bm25_scores)
        
        # Property: Scores should be in valid range
        assert all(0.0 <= score <= 1.0 for score in hybrid_scores)
        
        # Property: Order should be preserved for weighted sum
        if config.strategy == HybridStrategy.WEIGHTED_SUM:
            # If bm25_score[i] > bm25_score[j] and semantic_score[i] > semantic_score[j]
            # then hybrid_score[i] should be > hybrid_score[j]
            for i in range(len(hybrid_scores)):
                for j in range(len(hybrid_scores)):
                    if (bm25_scores[i] > bm25_scores[j] and 
                        semantic_scores[i] > semantic_scores[j]):
                        assert hybrid_scores[i] > hybrid_scores[j]


class TestBM25Performance:
    """Performance tests for BM25 functionality."""
    
    def test_large_scale_queries(self):
        """Test performance with large-scale queries."""
        # Create many queries
        queries = []
        start_time = time.time()
        
        for i in range(1000):
            query = ChunkQuery(
                search_query=f"query {i}",
                hybrid_search=True,
                bm25_weight=0.6,
                semantic_weight=0.4
            )
            queries.append(query)
        
        creation_time = time.time() - start_time
        assert creation_time < 5.0  # Should be fast
        
        # Validate all queries
        start_time = time.time()
        for query in queries:
            validation = query.validate_bm25_parameters()
            assert validation.is_valid is True
        
        validation_time = time.time() - start_time
        assert validation_time < 5.0  # Should be fast
    
    def test_large_score_calculations(self):
        """Test performance with large score calculations."""
        # Large score lists
        size = 10000
        bm25_scores = [0.8] * size
        semantic_scores = [0.7] * size
        config = HybridSearchConfig()
        
        start_time = time.time()
        hybrid_scores = HybridSearchHelper.calculate_hybrid_scores(
            bm25_scores, semantic_scores, config
        )
        calculation_time = time.time() - start_time
        
        assert calculation_time < 1.0  # Should be very fast
        assert len(hybrid_scores) == size
        assert all(0.0 <= score <= 1.0 for score in hybrid_scores)
    
    def test_memory_usage(self):
        """Test memory usage with large datasets."""
        # Create large configuration
        config = HybridSearchConfig()
        
        # Large score lists
        bm25_scores = [0.8] * 100000
        semantic_scores = [0.7] * 100000
        
        # Should not cause memory issues
        hybrid_scores = HybridSearchHelper.calculate_hybrid_scores(
            bm25_scores, semantic_scores, config
        )
        
        assert len(hybrid_scores) == 100000
        assert all(isinstance(score, float) for score in hybrid_scores)


class TestBM25Compatibility:
    """Compatibility tests for BM25 functionality."""
    
    def test_backward_compatibility(self):
        """Test backward compatibility with existing code."""
        # Test that existing queries work
        query = ChunkQuery(
            type="DocBlock",
            quality_score=">=0.8",
            tags="in:ai,ml"
        )
        
        # Should work without BM25
        assert query.has_bm25_search() is False
        
        # Should serialize correctly
        flat_dict = query.to_flat_dict()
        restored_query = ChunkQuery.from_flat_dict(flat_dict)
        assert restored_query.type == query.type
        assert restored_query.quality_score == query.quality_score
        
        # Should create API request without BM25
        api_request = query.to_api_request(include_search_params=False)
        assert 'search_query' not in api_request
        assert 'hybrid_search' not in api_request
    
    def test_forward_compatibility(self):
        """Test forward compatibility with new features."""
        # Test that new features work alongside existing ones
        query = ChunkQuery(
            type="DocBlock",
            quality_score=">=0.8",
            search_query="python programming",
            hybrid_search=True,
            bm25_weight=0.6,
            semantic_weight=0.4
        )
        
        # Should have both old and new features
        assert query.type == "DocBlock"
        assert query.has_bm25_search() is True
        
        # Should serialize both old and new fields
        flat_dict = query.to_flat_dict()
        restored_query = ChunkQuery.from_flat_dict(flat_dict)
        assert restored_query.type == query.type
        assert restored_query.search_query == query.search_query
        assert restored_query.hybrid_search == query.hybrid_search
    
    def test_api_compatibility(self):
        """Test API compatibility."""
        # Test that API requests are compatible
        query = ChunkQuery(
            search_query="test query",
            hybrid_search=True,
            bm25_weight=0.6,
            semantic_weight=0.4
        )
        
        api_request = query.to_api_request()
        
        # Should include all required fields
        required_fields = ['api_version', 'request_type', 'timestamp']
        for field in required_fields:
            assert field in api_request
        
        # Should include BM25 fields when requested
        bm25_fields = ['search_query', 'hybrid_search', 'bm25_weight', 'semantic_weight']
        for field in bm25_fields:
            assert field in api_request
        
        # Should not include BM25 fields when not requested
        api_request_no_bm25 = query.to_api_request(include_search_params=False)
        for field in bm25_fields:
            assert field not in api_request_no_bm25
