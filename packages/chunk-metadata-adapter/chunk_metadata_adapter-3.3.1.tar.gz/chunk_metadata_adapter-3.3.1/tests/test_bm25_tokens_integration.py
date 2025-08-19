"""
Tests for BM25 tokens integration in SemanticChunk.

This module tests the integration of bm25_tokens field in SemanticChunk,
ensuring it works exactly like the existing tokens field.
"""

import pytest
import json
from chunk_metadata_adapter.semantic_chunk import SemanticChunk, ChunkMetrics
from chunk_metadata_adapter.data_types import ChunkType, LanguageEnum


class TestBM25TokensIntegration:
    """Tests for BM25 tokens integration in SemanticChunk."""
    
    def test_bm25_tokens_in_chunk_metrics(self):
        """Test that bm25_tokens can be set in ChunkMetrics."""
        metrics = ChunkMetrics(
            quality_score=0.8,
            tokens=["hello", "world"],
            bm25_tokens=["hello", "world", "test"]
        )
        
        assert metrics.tokens == ["hello", "world"]
        assert metrics.bm25_tokens == ["hello", "world", "test"]
    
    def test_bm25_tokens_in_semantic_chunk_creation(self):
        """Test creating SemanticChunk with bm25_tokens in metrics."""
        chunk = SemanticChunk(
            type=ChunkType.DOC_BLOCK,
            body="Test content",
            metrics=ChunkMetrics(
                tokens=["test", "content"],
                bm25_tokens=["test", "content", "bm25"]
            )
        )
        
        assert chunk.metrics.tokens == ["test", "content"]
        assert chunk.metrics.bm25_tokens == ["test", "content", "bm25"]
    
    def test_bm25_tokens_from_top_level(self):
        """Test that bm25_tokens from top level is moved to metrics."""
        chunk, errors = SemanticChunk.validate_and_fill({
            "type": "DocBlock",
            "body": "Test content",
            "bm25_tokens": ["test", "content", "top", "level"]
        })
        
        assert errors is None
        assert chunk.metrics.bm25_tokens == ["test", "content", "top", "level"]
        assert chunk.metrics.tokens is None
    
    def test_bm25_tokens_string_parsing(self):
        """Test parsing bm25_tokens from JSON string."""
        chunk, errors = SemanticChunk.validate_and_fill({
            "type": "DocBlock",
            "body": "Test content",
            "bm25_tokens": '["test", "content", "json"]'
        })
        
        assert errors is None
        assert chunk.metrics.bm25_tokens == ["test", "content", "json"]
    
    def test_bm25_tokens_from_flat_dict(self):
        """Test restoring bm25_tokens from flat dictionary."""
        data = {
            "type": "DocBlock",
            "body": "Test content",
            "bm25_tokens": '["test", "content", "flat"]'
        }
        
        chunk = SemanticChunk.from_flat_dict(data)
        assert chunk.metrics.bm25_tokens == ["test", "content", "flat"]
    
    def test_bm25_tokens_redis_round_trip(self):
        """Test bm25_tokens round trip through Redis serialization."""
        original_chunk = SemanticChunk(
            type=ChunkType.DOC_BLOCK,
            body="Test content",
            metrics=ChunkMetrics(
                tokens=["test", "content"],
                bm25_tokens=["test", "content", "redis"]
            )
        )
        
        # Convert to flat dict (Redis format)
        flat_dict = original_chunk.to_flat_dict(for_redis=True)
        
        # Convert back from flat dict
        restored_chunk = SemanticChunk.from_flat_dict(flat_dict, from_redis=True)
        
        assert restored_chunk.metrics.tokens == ["test", "content"]
        assert restored_chunk.metrics.bm25_tokens == ["test", "content", "redis"]
    
    def test_bm25_tokens_priority_metrics_over_top_level(self):
        """Test that metrics bm25_tokens takes priority over top level."""
        chunk, errors = SemanticChunk.validate_and_fill({
            "type": "DocBlock",
            "body": "Test content",
            "bm25_tokens": ["top", "level"],
            "metrics": {
                "bm25_tokens": ["metrics", "level"]
            }
        })
        
        assert errors is None
        assert chunk.metrics.bm25_tokens == ["metrics", "level"]
    
    def test_bm25_tokens_empty_list_handling(self):
        """Test handling of empty bm25_tokens list."""
        chunk, errors = SemanticChunk.validate_and_fill({
            "type": "DocBlock",
            "body": "Test content",
            "bm25_tokens": []
        })
        
        assert errors is None
        assert chunk.metrics.bm25_tokens == []
    
    def test_bm25_tokens_none_handling(self):
        """Test handling of None bm25_tokens."""
        chunk, errors = SemanticChunk.validate_and_fill({
            "type": "DocBlock",
            "body": "Test content",
            "bm25_tokens": None
        })
        
        assert errors is None
        assert chunk.metrics.bm25_tokens is None
    
    def test_bm25_tokens_mixed_types_conversion(self):
        """Test conversion of mixed types to string tokens."""
        chunk, errors = SemanticChunk.validate_and_fill({
            "type": "DocBlock",
            "body": "Test content",
            "bm25_tokens": [123, "string", 45.67, True]
        })
        
        assert errors is None
        assert chunk.metrics.bm25_tokens == ["123", "string", "45.67", "True"]
    
    def test_bm25_tokens_single_value_conversion(self):
        """Test conversion of single value to list."""
        chunk, errors = SemanticChunk.validate_and_fill({
            "type": "DocBlock",
            "body": "Test content",
            "bm25_tokens": "single_token"
        })
        
        assert errors is None
        assert chunk.metrics.bm25_tokens == ["single_token"]
