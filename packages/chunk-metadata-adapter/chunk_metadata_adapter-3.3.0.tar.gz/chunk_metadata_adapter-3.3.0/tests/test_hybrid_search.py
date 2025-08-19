"""
Unit tests for hybrid search functionality.

This module tests the hybrid search classes and utilities,
including fusion strategies, validation, and configuration.

Test coverage:
- HybridStrategy enum
- HybridSearchConfig validation
- HybridSearchHelper calculations
- HybridSearchValidator methods
- Integration with ChunkQuery

Author: Development Team
Created: 2024-01-20
"""

import pytest
from chunk_metadata_adapter import (
    HybridStrategy, HybridSearchConfig, HybridSearchHelper, HybridSearchValidator,
    ChunkQuery
)


class TestHybridStrategy:
    """Tests for HybridStrategy enum."""
    
    def test_hybrid_strategy_values(self):
        """Test that all hybrid strategies have correct values."""
        assert HybridStrategy.WEIGHTED_SUM.value == "weighted_sum"
        assert HybridStrategy.RECIPROCAL_RANK.value == "reciprocal_rank"
        assert HybridStrategy.COMB_SUM.value == "comb_sum"
        assert HybridStrategy.COMB_MNZ.value == "comb_mnz"
    
    def test_hybrid_strategy_names(self):
        """Test that all hybrid strategies have correct names."""
        assert HybridStrategy.WEIGHTED_SUM.name == "WEIGHTED_SUM"
        assert HybridStrategy.RECIPROCAL_RANK.name == "RECIPROCAL_RANK"
        assert HybridStrategy.COMB_SUM.name == "COMB_SUM"
        assert HybridStrategy.COMB_MNZ.name == "COMB_MNZ"
    
    def test_hybrid_strategy_count(self):
        """Test that all expected strategies are present."""
        strategies = list(HybridStrategy)
        assert len(strategies) == 4
        assert HybridStrategy.WEIGHTED_SUM in strategies
        assert HybridStrategy.RECIPROCAL_RANK in strategies
        assert HybridStrategy.COMB_SUM in strategies
        assert HybridStrategy.COMB_MNZ in strategies


class TestHybridSearchConfig:
    """Tests for HybridSearchConfig class."""
    
    def test_default_config(self):
        """Test creating config with default values."""
        config = HybridSearchConfig()
        
        assert config.bm25_weight == 0.5
        assert config.semantic_weight == 0.5
        assert config.strategy == HybridStrategy.WEIGHTED_SUM
        assert config.normalize_scores is True
        assert config.min_score_threshold == 0.0
        assert config.max_score_threshold == 1.0
    
    def test_custom_config(self):
        """Test creating config with custom values."""
        config = HybridSearchConfig(
            bm25_weight=0.3,
            semantic_weight=0.7,
            strategy=HybridStrategy.COMB_SUM,
            normalize_scores=False,
            min_score_threshold=0.1,
            max_score_threshold=0.9
        )
        
        assert config.bm25_weight == 0.3
        assert config.semantic_weight == 0.7
        assert config.strategy == HybridStrategy.COMB_SUM
        assert config.normalize_scores is False
        assert config.min_score_threshold == 0.1
        assert config.max_score_threshold == 0.9
    
    def test_invalid_weights_validation(self):
        """Test validation of invalid weights."""
        # Test weights that don't sum to 1.0
        with pytest.raises(ValueError, match="Weights must sum to 1.0"):
            HybridSearchConfig(bm25_weight=0.3, semantic_weight=0.6)
        
        # Test negative weights - check semantic_weight first
        with pytest.raises(ValueError, match="Semantic weight must be between 0.0 and 1.0"):
            HybridSearchConfig(bm25_weight=0.5, semantic_weight=-0.1)
        
        with pytest.raises(ValueError, match="BM25 weight must be between 0.0 and 1.0"):
            HybridSearchConfig(bm25_weight=-0.1, semantic_weight=0.5)
    
    def test_invalid_thresholds_validation(self):
        """Test validation of invalid thresholds."""
        # Test min threshold >= max threshold
        with pytest.raises(ValueError, match="Min threshold must be less than max threshold"):
            HybridSearchConfig(min_score_threshold=0.5, max_score_threshold=0.5)
        
        with pytest.raises(ValueError, match="Min threshold must be less than max threshold"):
            HybridSearchConfig(min_score_threshold=0.6, max_score_threshold=0.5)
        
        # Test thresholds outside valid range
        with pytest.raises(ValueError, match="Min score threshold must be between 0.0 and 1.0"):
            HybridSearchConfig(min_score_threshold=-0.1)
        
        with pytest.raises(ValueError, match="Max score threshold must be between 0.0 and 1.0"):
            HybridSearchConfig(max_score_threshold=1.1)


class TestHybridSearchHelper:
    """Tests for HybridSearchHelper class."""
    
    def test_normalize_scores_empty_list(self):
        """Test normalizing empty score list."""
        scores = []
        normalized = HybridSearchHelper.normalize_scores(scores)
        assert normalized == []
    
    def test_normalize_scores_single_value(self):
        """Test normalizing single score value."""
        scores = [0.5]
        normalized = HybridSearchHelper.normalize_scores(scores)
        assert normalized == [1.0]  # Should be normalized to max_score
    
    def test_normalize_scores_multiple_values(self):
        """Test normalizing multiple score values."""
        scores = [0.2, 0.5, 0.8]
        normalized = HybridSearchHelper.normalize_scores(scores)
        
        assert len(normalized) == 3
        assert normalized[0] == 0.0  # Min value becomes 0.0
        assert normalized[1] == 0.5  # Middle value becomes 0.5
        assert normalized[2] == 1.0  # Max value becomes 1.0
    
    def test_normalize_scores_custom_range(self):
        """Test normalizing scores to custom range."""
        scores = [0.2, 0.5, 0.8]
        normalized = HybridSearchHelper.normalize_scores(scores, min_score=0.1, max_score=0.9)
        
        assert len(normalized) == 3
        assert normalized[0] == 0.1  # Min value becomes 0.1
        assert normalized[1] == 0.5  # Middle value becomes 0.5
        assert normalized[2] == 0.9  # Max value becomes 0.9
    
    def test_normalize_scores_invalid_range(self):
        """Test normalizing scores with invalid range."""
        with pytest.raises(ValueError, match="Min score must be less than max score"):
            HybridSearchHelper.normalize_scores([0.5], min_score=0.5, max_score=0.5)
    
    def test_weighted_sum_calculation(self):
        """Test weighted sum calculation."""
        bm25_scores = [0.8, 0.6, 0.9]
        semantic_scores = [0.7, 0.5, 0.8]
        bm25_weight = 0.6
        semantic_weight = 0.4
        
        hybrid_scores = HybridSearchHelper.weighted_sum(
            bm25_scores, semantic_scores, bm25_weight, semantic_weight
        )
        
        expected_scores = [
            0.6 * 0.8 + 0.4 * 0.7,  # 0.76
            0.6 * 0.6 + 0.4 * 0.5,  # 0.56
            0.6 * 0.9 + 0.4 * 0.8   # 0.86
        ]
        
        assert len(hybrid_scores) == 3
        for actual, expected in zip(hybrid_scores, expected_scores):
            assert abs(actual - expected) < 0.001
    
    def test_weighted_sum_different_lengths(self):
        """Test weighted sum with different length lists."""
        bm25_scores = [0.8, 0.6]
        semantic_scores = [0.7, 0.5, 0.8]
        
        with pytest.raises(ValueError, match="Score lists must have the same length"):
            HybridSearchHelper.weighted_sum(bm25_scores, semantic_scores, 0.5, 0.5)
    
    def test_reciprocal_rank_calculation(self):
        """Test reciprocal rank calculation."""
        bm25_ranks = [1, 3, 2]
        semantic_ranks = [2, 1, 3]
        bm25_weight = 0.6
        semantic_weight = 0.4
        k = 60
        
        hybrid_scores = HybridSearchHelper.reciprocal_rank(
            bm25_ranks, semantic_ranks, bm25_weight, semantic_weight, k
        )
        
        expected_scores = [
            0.6 * (1/(1+k)) + 0.4 * (1/(2+k)),  # bm25_rank=1, semantic_rank=2
            0.6 * (1/(3+k)) + 0.4 * (1/(1+k)),  # bm25_rank=3, semantic_rank=1
            0.6 * (1/(2+k)) + 0.4 * (1/(3+k))   # bm25_rank=2, semantic_rank=3
        ]
        
        assert len(hybrid_scores) == 3
        for actual, expected in zip(hybrid_scores, expected_scores):
            assert abs(actual - expected) < 0.001
    
    def test_comb_sum_calculation(self):
        """Test CombSUM calculation."""
        bm25_scores = [0.8, 0.6, 0.9]
        semantic_scores = [0.7, 0.5, 0.8]
        
        hybrid_scores = HybridSearchHelper.comb_sum(bm25_scores, semantic_scores)
        
        expected_scores = [0.8 + 0.7, 0.6 + 0.5, 0.9 + 0.8]  # [1.5, 1.1, 1.7]
        
        assert len(hybrid_scores) == 3
        for actual, expected in zip(hybrid_scores, expected_scores):
            assert abs(actual - expected) < 0.001
    
    def test_comb_mnz_calculation(self):
        """Test CombMNZ calculation."""
        bm25_scores = [0.8, 0.0, 0.9]
        semantic_scores = [0.7, 0.5, 0.0]
        
        hybrid_scores = HybridSearchHelper.comb_mnz(bm25_scores, semantic_scores)
        
        # First: both non-zero (count=2), score = (0.8 + 0.7) * 2 = 3.0
        # Second: one non-zero (count=1), score = (0.0 + 0.5) * 1 = 0.5
        # Third: one non-zero (count=1), score = (0.9 + 0.0) * 1 = 0.9
        expected_scores = [3.0, 0.5, 0.9]
        
        assert len(hybrid_scores) == 3
        for actual, expected in zip(hybrid_scores, expected_scores):
            assert abs(actual - expected) < 0.001
    
    def test_calculate_hybrid_scores_weighted_sum(self):
        """Test hybrid score calculation with weighted sum strategy."""
        bm25_scores = [0.8, 0.6, 0.9]
        semantic_scores = [0.7, 0.5, 0.8]
        config = HybridSearchConfig(
            bm25_weight=0.6,
            semantic_weight=0.4,
            strategy=HybridStrategy.WEIGHTED_SUM,
            normalize_scores=False
        )
        
        hybrid_scores = HybridSearchHelper.calculate_hybrid_scores(
            bm25_scores, semantic_scores, config
        )
        
        expected_scores = [
            0.6 * 0.8 + 0.4 * 0.7,  # 0.76
            0.6 * 0.6 + 0.4 * 0.5,  # 0.56
            0.6 * 0.9 + 0.4 * 0.8   # 0.86
        ]
        
        assert len(hybrid_scores) == 3
        for actual, expected in zip(hybrid_scores, expected_scores):
            assert abs(actual - expected) < 0.001
    
    def test_calculate_hybrid_scores_comb_sum(self):
        """Test hybrid score calculation with comb sum strategy."""
        bm25_scores = [0.8, 0.6, 0.9]
        semantic_scores = [0.7, 0.5, 0.8]
        config = HybridSearchConfig(
            strategy=HybridStrategy.COMB_SUM,
            normalize_scores=False
        )
        
        hybrid_scores = HybridSearchHelper.calculate_hybrid_scores(
            bm25_scores, semantic_scores, config
        )
        
        expected_scores = [0.8 + 0.7, 0.6 + 0.5, 0.9 + 0.8]  # [1.5, 1.1, 1.7]
        
        assert len(hybrid_scores) == 3
        for actual, expected in zip(hybrid_scores, expected_scores):
            assert abs(actual - expected) < 0.001
    
    def test_calculate_hybrid_scores_unsupported_strategy(self):
        """Test hybrid score calculation with unsupported strategy."""
        bm25_scores = [0.8, 0.6, 0.9]
        semantic_scores = [0.7, 0.5, 0.8]
        config = HybridSearchConfig(
            strategy=HybridStrategy.RECIPROCAL_RANK,  # Not implemented in calculate_hybrid_scores
            normalize_scores=False
        )
        
        with pytest.raises(ValueError, match="Unsupported hybrid strategy"):
            HybridSearchHelper.calculate_hybrid_scores(bm25_scores, semantic_scores, config)


class TestHybridSearchValidator:
    """Tests for HybridSearchValidator class."""
    
    def test_validate_weights_valid(self):
        """Test validation of valid weights."""
        assert HybridSearchValidator.validate_weights(0.6, 0.4) is True
        assert HybridSearchValidator.validate_weights(0.5, 0.5) is True
        assert HybridSearchValidator.validate_weights(0.0, 1.0) is True
        assert HybridSearchValidator.validate_weights(1.0, 0.0) is True
    
    def test_validate_weights_invalid_sum(self):
        """Test validation of weights that don't sum to 1.0."""
        with pytest.raises(ValueError, match="Weights must sum to 1.0"):
            HybridSearchValidator.validate_weights(0.6, 0.5)
        
        with pytest.raises(ValueError, match="Weights must sum to 1.0"):
            HybridSearchValidator.validate_weights(0.3, 0.4)
    
    def test_validate_weights_invalid_range(self):
        """Test validation of weights outside valid range."""
        with pytest.raises(ValueError, match="Semantic weight must be between 0.0 and 1.0"):
            HybridSearchValidator.validate_weights(0.5, -0.1)
        
        with pytest.raises(ValueError, match="BM25 weight must be between 0.0 and 1.0"):
            HybridSearchValidator.validate_weights(-0.1, 0.5)
    
    def test_validate_strategy_valid(self):
        """Test validation of valid strategies."""
        for strategy in HybridStrategy:
            assert HybridSearchValidator.validate_strategy(strategy.value) is True
    
    def test_validate_strategy_invalid(self):
        """Test validation of invalid strategy."""
        with pytest.raises(ValueError, match="Invalid hybrid strategy"):
            HybridSearchValidator.validate_strategy("invalid_strategy")
    
    def test_validate_score_lists_valid(self):
        """Test validation of valid score lists."""
        bm25_scores = [0.8, 0.6, 0.9]
        semantic_scores = [0.7, 0.5, 0.8]
        
        assert HybridSearchValidator.validate_score_lists(bm25_scores, semantic_scores) is True
    
    def test_validate_score_lists_different_lengths(self):
        """Test validation of score lists with different lengths."""
        bm25_scores = [0.8, 0.6]
        semantic_scores = [0.7, 0.5, 0.8]
        
        with pytest.raises(ValueError, match="Score lists must have the same length"):
            HybridSearchValidator.validate_score_lists(bm25_scores, semantic_scores)
    
    def test_validate_score_lists_empty(self):
        """Test validation of empty score lists."""
        with pytest.raises(ValueError, match="Score lists cannot be empty"):
            HybridSearchValidator.validate_score_lists([], [])
    
    def test_validate_score_lists_invalid_range(self):
        """Test validation of scores outside valid range."""
        bm25_scores = [0.8, 1.1, 0.9]
        semantic_scores = [0.7, 0.5, 0.8]
        
        with pytest.raises(ValueError, match="BM25 score at index 1 must be between 0.0 and 1.0"):
            HybridSearchValidator.validate_score_lists(bm25_scores, semantic_scores)
        
        bm25_scores = [0.8, 0.6, 0.9]
        semantic_scores = [0.7, -0.1, 0.8]
        
        with pytest.raises(ValueError, match="Semantic score at index 1 must be between 0.0 and 1.0"):
            HybridSearchValidator.validate_score_lists(bm25_scores, semantic_scores)
    
    def test_validate_config_valid(self):
        """Test validation of valid configuration."""
        config = HybridSearchConfig(
            bm25_weight=0.6,
            semantic_weight=0.4,
            strategy=HybridStrategy.WEIGHTED_SUM
        )
        
        assert HybridSearchValidator.validate_config(config) is True
    
    def test_validate_config_invalid(self):
        """Test validation of invalid configuration."""
        # Test that creating config with invalid thresholds raises an error
        with pytest.raises(ValueError, match="Min threshold must be less than max threshold"):
            HybridSearchConfig(
                bm25_weight=0.6,
                semantic_weight=0.4,
                min_score_threshold=0.5,
                max_score_threshold=0.4  # Invalid: min >= max
            )


class TestHybridSearchIntegration:
    """Integration tests for hybrid search with ChunkQuery."""
    
    def test_chunk_query_hybrid_validation(self):
        """Test hybrid search validation in ChunkQuery."""
        # Valid hybrid search configuration
        query = ChunkQuery(
            search_query="python machine learning",
            hybrid_search=True,
            bm25_weight=0.6,
            semantic_weight=0.4
        )
        
        validation = query.validate_bm25_parameters()
        assert validation.is_valid is True
        assert len(validation.errors) == 0
    
    def test_chunk_query_hybrid_validation_weights_sum(self):
        """Test hybrid search validation with weights that don't sum to 1.0."""
        query = ChunkQuery(
            search_query="python machine learning",
            hybrid_search=True,
            bm25_weight=0.6,
            semantic_weight=0.5  # Sum = 1.1
        )
        
        validation = query.validate_bm25_parameters()
        assert validation.is_valid is True  # Should be valid but with warning
        assert len(validation.warnings) > 0
        assert any("Weights should sum to 1.0" in warning for warning in validation.warnings)
    
    def test_chunk_query_hybrid_validation_missing_weights(self):
        """Test hybrid search validation with missing weights."""
        query = ChunkQuery(
            search_query="python machine learning",
            hybrid_search=True,
            bm25_weight=0.6,
            semantic_weight=None  # Explicitly set to None
        )
        
        validation = query.validate_bm25_parameters()
        assert validation.is_valid is False
        assert len(validation.errors) > 0
        assert any("Both bm25_weight and semantic_weight must be set" in error for error in validation.errors)
    
    def test_chunk_query_hybrid_validation_extreme_weights(self):
        """Test hybrid search validation with extreme weight values."""
        query = ChunkQuery(
            search_query="python machine learning",
            hybrid_search=True,
            bm25_weight=0.05,  # Very low weight
            semantic_weight=0.95
        )
        
        validation = query.validate_bm25_parameters()
        assert validation.is_valid is True  # Should be valid but with warning
        assert len(validation.warnings) > 0
        assert any("Very low BM25 weight may reduce search effectiveness" in warning for warning in validation.warnings)
    
    def test_chunk_query_hybrid_api_request(self):
        """Test that hybrid search parameters are included in API requests."""
        query = ChunkQuery(
            search_query="python machine learning",
            hybrid_search=True,
            bm25_weight=0.6,
            semantic_weight=0.4
        )
        
        request = query.to_api_request()
        
        assert request['hybrid_search'] is True
        assert request['bm25_weight'] == 0.6
        assert request['semantic_weight'] == 0.4
        assert request['search_query'] == "python machine learning"
