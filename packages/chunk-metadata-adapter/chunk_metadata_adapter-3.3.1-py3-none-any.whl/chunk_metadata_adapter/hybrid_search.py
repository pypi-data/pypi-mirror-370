"""
Hybrid search functionality for combining BM25 and semantic search.

This module provides classes and utilities for hybrid search operations,
including different fusion strategies and validation methods.

Key features:
- HybridStrategy enum for different fusion methods
- HybridSearchHelper for score calculations
- Validation methods for hybrid search parameters
- Score normalization and fusion algorithms

Author: Development Team
Created: 2024-01-20
"""

from enum import Enum
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass
import math


class HybridStrategy(Enum):
    """
    Available hybrid search strategies.
    
    Different methods for combining BM25 and semantic search scores:
    - WEIGHTED_SUM: Simple weighted combination
    - RECIPROCAL_RANK: Reciprocal rank fusion
    - COMB_SUM: CombSUM fusion method
    - COMB_MNZ: CombMNZ fusion method
    """
    WEIGHTED_SUM = "weighted_sum"
    RECIPROCAL_RANK = "reciprocal_rank"
    COMB_SUM = "comb_sum"
    COMB_MNZ = "comb_mnz"


@dataclass
class HybridSearchConfig:
    """
    Configuration for hybrid search operations.
    
    This class holds all parameters needed for hybrid search,
    including weights, strategy, and validation settings.
    """
    bm25_weight: float = 0.5
    semantic_weight: float = 0.5
    strategy: HybridStrategy = HybridStrategy.WEIGHTED_SUM
    normalize_scores: bool = True
    min_score_threshold: float = 0.0
    max_score_threshold: float = 1.0
    
    def __post_init__(self) -> None:
        """Validate configuration parameters."""
        self._validate_weights()
        self._validate_thresholds()
    
    def _validate_weights(self) -> None:
        """Validate weight parameters."""
        # First check individual weight ranges
        if not (0.0 <= self.bm25_weight <= 1.0):
            raise ValueError(f"BM25 weight must be between 0.0 and 1.0, got: {self.bm25_weight}")
        
        if not (0.0 <= self.semantic_weight <= 1.0):
            raise ValueError(f"Semantic weight must be between 0.0 and 1.0, got: {self.semantic_weight}")
        
        # Then check if weights sum to approximately 1.0 (allowing for floating point precision)
        weight_sum = self.bm25_weight + self.semantic_weight
        if abs(weight_sum - 1.0) > 0.001:
            raise ValueError(f"Weights must sum to 1.0, got: {weight_sum}")
    
    def _validate_thresholds(self) -> None:
        """Validate score threshold parameters."""
        if not (0.0 <= self.min_score_threshold <= 1.0):
            raise ValueError(f"Min score threshold must be between 0.0 and 1.0, got: {self.min_score_threshold}")
        
        if not (0.0 <= self.max_score_threshold <= 1.0):
            raise ValueError(f"Max score threshold must be between 0.0 and 1.0, got: {self.max_score_threshold}")
        
        if self.min_score_threshold >= self.max_score_threshold:
            raise ValueError(f"Min threshold must be less than max threshold")


class HybridSearchHelper:
    """
    Helper class for hybrid search calculations.
    
    This class provides static methods for different fusion strategies
    and score normalization techniques.
    """
    
    @staticmethod
    def normalize_scores(scores: List[float], min_score: float = 0.0, max_score: float = 1.0) -> List[float]:
        """
        Normalize scores to the specified range.
        
        Args:
            scores: List of scores to normalize
            min_score: Minimum value in target range
            max_score: Maximum value in target range
            
        Returns:
            List[float]: Normalized scores
            
        Raises:
            ValueError: If score range is invalid
        """
        if not scores:
            return []
        
        if min_score >= max_score:
            raise ValueError(f"Min score must be less than max score: {min_score} >= {max_score}")
        
        score_min = min(scores)
        score_max = max(scores)
        
        # Handle case where all scores are the same
        if score_max == score_min:
            return [max_score] * len(scores)
        
        normalized = []
        for score in scores:
            normalized_score = min_score + (score - score_min) * (max_score - min_score) / (score_max - score_min)
            # Round to avoid floating point precision issues
            normalized_score = round(normalized_score, 10)
            normalized.append(normalized_score)
        
        return normalized
    
    @staticmethod
    def weighted_sum(bm25_scores: List[float], semantic_scores: List[float],
                    bm25_weight: float, semantic_weight: float) -> List[float]:
        """
        Calculate weighted sum of scores.
        
        Args:
            bm25_scores: List of BM25 scores
            semantic_scores: List of semantic scores
            bm25_weight: Weight for BM25 scores
            semantic_weight: Weight for semantic scores
            
        Returns:
            List[float]: Combined hybrid scores
            
        Raises:
            ValueError: If score lists have different lengths
        """
        if len(bm25_scores) != len(semantic_scores):
            raise ValueError(f"Score lists must have the same length: {len(bm25_scores)} != {len(semantic_scores)}")
        
        hybrid_scores = []
        for bm25_score, semantic_score in zip(bm25_scores, semantic_scores):
            hybrid_score = (bm25_weight * bm25_score + semantic_weight * semantic_score)
            hybrid_scores.append(hybrid_score)
        
        return hybrid_scores
    
    @staticmethod
    def reciprocal_rank(bm25_ranks: List[int], semantic_ranks: List[int],
                       bm25_weight: float, semantic_weight: float, k: int = 60) -> List[float]:
        """
        Calculate reciprocal rank fusion.
        
        Args:
            bm25_ranks: List of BM25 ranks (1-based)
            semantic_ranks: List of semantic ranks (1-based)
            bm25_weight: Weight for BM25 reciprocal ranks
            semantic_weight: Weight for semantic reciprocal ranks
            k: Constant for reciprocal rank calculation
            
        Returns:
            List[float]: Combined hybrid scores
            
        Raises:
            ValueError: If rank lists have different lengths
        """
        if len(bm25_ranks) != len(semantic_ranks):
            raise ValueError(f"Rank lists must have the same length: {len(bm25_ranks)} != {len(semantic_ranks)}")
        
        hybrid_scores = []
        for bm25_rank, semantic_rank in zip(bm25_ranks, semantic_ranks):
            # Reciprocal rank: 1 / (rank + k)
            bm25_rr = 1 / (bm25_rank + k)
            semantic_rr = 1 / (semantic_rank + k)
            
            hybrid_score = (bm25_weight * bm25_rr + semantic_weight * semantic_rr)
            hybrid_scores.append(hybrid_score)
        
        return hybrid_scores
    
    @staticmethod
    def comb_sum(bm25_scores: List[float], semantic_scores: List[float]) -> List[float]:
        """
        Calculate CombSUM fusion.
        
        Args:
            bm25_scores: List of BM25 scores
            semantic_scores: List of semantic scores
            
        Returns:
            List[float]: Combined hybrid scores
            
        Raises:
            ValueError: If score lists have different lengths
        """
        if len(bm25_scores) != len(semantic_scores):
            raise ValueError(f"Score lists must have the same length: {len(bm25_scores)} != {len(semantic_scores)}")
        
        hybrid_scores = []
        for bm25_score, semantic_score in zip(bm25_scores, semantic_scores):
            hybrid_score = bm25_score + semantic_score
            hybrid_scores.append(hybrid_score)
        
        return hybrid_scores
    
    @staticmethod
    def comb_mnz(bm25_scores: List[float], semantic_scores: List[float]) -> List[float]:
        """
        Calculate CombMNZ fusion.
        
        Args:
            bm25_scores: List of BM25 scores
            semantic_scores: List of semantic scores
            
        Returns:
            List[float]: Combined hybrid scores
            
        Raises:
            ValueError: If score lists have different lengths
        """
        if len(bm25_scores) != len(semantic_scores):
            raise ValueError(f"Score lists must have the same length: {len(bm25_scores)} != {len(semantic_scores)}")
        
        hybrid_scores = []
        for bm25_score, semantic_score in zip(bm25_scores, semantic_scores):
            # Count non-zero scores
            non_zero_count = sum(1 for score in [bm25_score, semantic_score] if score > 0)
            hybrid_score = (bm25_score + semantic_score) * non_zero_count
            hybrid_scores.append(hybrid_score)
        
        return hybrid_scores
    
    @staticmethod
    def calculate_hybrid_scores(bm25_scores: List[float], semantic_scores: List[float],
                              config: HybridSearchConfig) -> List[float]:
        """
        Calculate hybrid scores using the specified strategy.
        
        Args:
            bm25_scores: List of BM25 scores
            semantic_scores: List of semantic scores
            config: Hybrid search configuration
            
        Returns:
            List[float]: Combined hybrid scores
        """
        # Normalize scores if requested
        if config.normalize_scores:
            bm25_scores = HybridSearchHelper.normalize_scores(
                bm25_scores, config.min_score_threshold, config.max_score_threshold
            )
            semantic_scores = HybridSearchHelper.normalize_scores(
                semantic_scores, config.min_score_threshold, config.max_score_threshold
            )
        
        # Apply fusion strategy
        if config.strategy == HybridStrategy.WEIGHTED_SUM:
            hybrid_scores = HybridSearchHelper.weighted_sum(
                bm25_scores, semantic_scores, config.bm25_weight, config.semantic_weight
            )
        elif config.strategy == HybridStrategy.COMB_SUM:
            hybrid_scores = HybridSearchHelper.comb_sum(bm25_scores, semantic_scores)
        elif config.strategy == HybridStrategy.COMB_MNZ:
            hybrid_scores = HybridSearchHelper.comb_mnz(bm25_scores, semantic_scores)
        else:
            raise ValueError(f"Unsupported hybrid strategy: {config.strategy}")
        
        return hybrid_scores


class HybridSearchValidator:
    """
    Validator for hybrid search parameters.
    
    This class provides validation methods for hybrid search configuration
    and parameter consistency.
    """
    
    @staticmethod
    def validate_weights(bm25_weight: float, semantic_weight: float, tolerance: float = 0.001) -> bool:
        """
        Validate that weights sum to 1.0 within tolerance.
        
        Args:
            bm25_weight: Weight for BM25 scores
            semantic_weight: Weight for semantic scores
            tolerance: Tolerance for floating point comparison
            
        Returns:
            bool: True if weights are valid
            
        Raises:
            ValueError: If weights are invalid
        """
        # First check individual weight ranges
        if not (0.0 <= bm25_weight <= 1.0):
            raise ValueError(f"BM25 weight must be between 0.0 and 1.0, got: {bm25_weight}")
        
        if not (0.0 <= semantic_weight <= 1.0):
            raise ValueError(f"Semantic weight must be between 0.0 and 1.0, got: {semantic_weight}")
        
        # Then check if weights sum to 1.0 within tolerance
        weight_sum = bm25_weight + semantic_weight
        if abs(weight_sum - 1.0) > tolerance:
            raise ValueError(f"Weights must sum to 1.0, got: {weight_sum}")
        
        return True
    
    @staticmethod
    def validate_strategy(strategy: str) -> bool:
        """
        Validate hybrid search strategy.
        
        Args:
            strategy: Strategy name to validate
            
        Returns:
            bool: True if strategy is valid
            
        Raises:
            ValueError: If strategy is invalid
        """
        allowed_strategies = [s.value for s in HybridStrategy]
        if strategy not in allowed_strategies:
            raise ValueError(f"Invalid hybrid strategy: {strategy}. Allowed: {allowed_strategies}")
        
        return True
    
    @staticmethod
    def validate_score_lists(bm25_scores: List[float], semantic_scores: List[float]) -> bool:
        """
        Validate score lists for hybrid search.
        
        Args:
            bm25_scores: List of BM25 scores
            semantic_scores: List of semantic scores
            
        Returns:
            bool: True if score lists are valid
            
        Raises:
            ValueError: If score lists are invalid
        """
        if len(bm25_scores) != len(semantic_scores):
            raise ValueError(f"Score lists must have the same length: {len(bm25_scores)} != {len(semantic_scores)}")
        
        if not bm25_scores:
            raise ValueError("Score lists cannot be empty")
        
        # Validate score ranges
        for i, (bm25_score, semantic_score) in enumerate(zip(bm25_scores, semantic_scores)):
            if not (0.0 <= bm25_score <= 1.0):
                raise ValueError(f"BM25 score at index {i} must be between 0.0 and 1.0, got: {bm25_score}")
            
            if not (0.0 <= semantic_score <= 1.0):
                raise ValueError(f"Semantic score at index {i} must be between 0.0 and 1.0, got: {semantic_score}")
        
        return True
    
    @staticmethod
    def validate_config(config: HybridSearchConfig) -> bool:
        """
        Validate hybrid search configuration.
        
        Args:
            config: Configuration to validate
            
        Returns:
            bool: True if configuration is valid
            
        Raises:
            ValueError: If configuration is invalid
        """
        HybridSearchValidator.validate_weights(config.bm25_weight, config.semantic_weight)
        HybridSearchValidator.validate_strategy(config.strategy.value)
        
        if config.min_score_threshold >= config.max_score_threshold:
            raise ValueError(f"Min threshold must be less than max threshold: {config.min_score_threshold} >= {config.max_score_threshold}")
        
        return True
