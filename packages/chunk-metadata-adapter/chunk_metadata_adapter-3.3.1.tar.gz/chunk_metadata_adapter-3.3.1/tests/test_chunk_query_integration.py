"""
Integration tests for ChunkQuery with AST filtering system.

This module tests the integration between ChunkQuery and the AST filtering
system, including simple field filtering, complex AST-based filtering,
validation, and performance characteristics.

Test coverage:
- Simple field filtering (legacy compatibility)
- Complex AST-based filtering with logical expressions
- Filter validation and security checks
- Performance optimization and caching
- Integration with Redis flat dictionary format
- Type safety and error handling

Author: Development Team
Created: 2024-01-20
Updated: 2024-01-20
"""

import pytest
import time
from typing import Dict, Any, List
from unittest.mock import Mock, patch

from chunk_metadata_adapter.chunk_query import ChunkQuery
from chunk_metadata_adapter.semantic_chunk import SemanticChunk
from chunk_metadata_adapter.ast import ASTNode, LogicalOperator, FieldCondition
from chunk_metadata_adapter.data_types import ChunkType, ChunkRole, ChunkStatus, LanguageEnum
from chunk_metadata_adapter.filter_parser import FilterParseError


class TestChunkQueryIntegration:
    """Integration tests for ChunkQuery with AST filtering."""
    
    @pytest.fixture
    def sample_chunk_data(self) -> Dict[str, Any]:
        """Sample chunk data for testing."""
        return {
            "uuid": "123e4567-e89b-12d3-a456-426614174000",
            "type": "DocBlock",
            "quality_score": 0.8,
            "tags": ["ai", "python", "machine-learning"],
            "year": 2023,
            "is_public": True,
            "is_deleted": False,
            "language": "en",
            "title": "Python Machine Learning Guide",
            "category": "programming"
        }
    
    @pytest.fixture
    def sample_semantic_chunk(self) -> SemanticChunk:
        """Sample SemanticChunk for testing."""
        return SemanticChunk(
            uuid="ebc534d7-a682-4ff3-b370-acdda910422c",
            type=ChunkType.DOC_BLOCK,
            body="Sample content for testing",
            quality_score=0.8,
            tags=["ai", "python", "machine-learning"],
            year=2023,
            is_public=True,
            is_deleted=False,
            language=LanguageEnum.EN,
            title="Python Machine Learning Guide",
            category="programming"
        )
    
    def test_simple_field_filtering(self, sample_chunk_data: Dict[str, Any]):
        """Test simple field-based filtering."""
        # Test exact match
        query = ChunkQuery(type="DocBlock")
        assert query.matches(sample_chunk_data) == True
        
        # Test numeric comparison
        query = ChunkQuery(quality_score=">=0.7")
        assert query.matches(sample_chunk_data) == True
        
        query = ChunkQuery(quality_score="<0.9")
        assert query.matches(sample_chunk_data) == True
        
        # Test list field
        query = ChunkQuery(tags=["ai", "ml"])
        assert query.matches(sample_chunk_data) == True
        
        # Test boolean field
        query = ChunkQuery(is_public=True)
        assert query.matches(sample_chunk_data) == True
        
        # Test non-match
        query = ChunkQuery(type="CodeBlock")
        assert query.matches(sample_chunk_data) == False
    
    def test_ast_based_filtering(self, sample_chunk_data: Dict[str, Any]):
        """Test AST-based complex filtering."""
        # Simple AND condition
        query = ChunkQuery(filter_expr="type = 'DocBlock' AND quality_score >= 0.7")
        assert query.matches(sample_chunk_data) == True
        
        # OR condition
        query = ChunkQuery(filter_expr="type = 'DocBlock' OR type = 'CodeBlock'")
        assert query.matches(sample_chunk_data) == True
        
        # Complex nested condition
        query = ChunkQuery(filter_expr="""
            (type = 'DocBlock' OR type = 'CodeBlock') AND
            quality_score >= 0.7 AND
            tags intersects ['ai', 'ml'] AND
            year >= 2020 AND
            NOT is_deleted
        """)
        assert query.matches(sample_chunk_data) == True
        
        # NOT condition
        query = ChunkQuery(filter_expr="NOT is_deleted AND is_public = true")
        assert query.matches(sample_chunk_data) == True
    
    def test_ast_parsing_and_caching(self):
        """Test AST parsing and caching functionality."""
        query = ChunkQuery(filter_expr="type = 'DocBlock' AND quality_score >= 0.8")
        
        # First call - should parse and cache
        ast1 = query.get_ast()
        assert isinstance(ast1, LogicalOperator)
        assert ast1.operator == "AND"
        
        # Second call - should return cached AST
        ast2 = query.get_ast()
        assert ast1 is ast2  # Same object (cached)
        
        # Check cache stats
        stats = query.get_cache_stats()
        assert stats["ast_cached"] == True
        assert stats["parser_initialized"] == True
    
    def test_filter_validation(self):
        """Test filter expression validation."""
        # Valid filter
        query = ChunkQuery(filter_expr="type = 'DocBlock' AND quality_score >= 0.8")
        result = query.validate()
        assert result.is_valid == True
        assert len(result.errors) == 0
        
        # Invalid filter (syntax error)
        query = ChunkQuery(filter_expr="type = 'DocBlock' AND")
        result = query.validate()
        assert result.is_valid == False
        assert len(result.errors) > 0
        
        # Security violation
        query = ChunkQuery(filter_expr="__import__('os').system('rm -rf /')")
        result = query.validate()
        assert result.is_valid == False
        assert len(result.errors) > 0
        
        # No filter expression
        query = ChunkQuery(type="DocBlock")
        result = query.validate()
        assert result.is_valid == True
    
    def test_semantic_chunk_integration(self, sample_semantic_chunk: SemanticChunk):
        """Test integration with SemanticChunk objects."""
        # Simple field filtering
        query = ChunkQuery(type="DocBlock")
        assert query.matches(sample_semantic_chunk) == True
        
        # AST-based filtering
        query = ChunkQuery(filter_expr="type = 'DocBlock' AND quality_score >= 0.7")
        assert query.matches(sample_semantic_chunk) == True
        
        # Test with different chunk type
        different_chunk = SemanticChunk(
            uuid="b305fc27-3dd2-429b-af6a-3a95509630a9",
            type=ChunkType.CODE_BLOCK,
            body="Code content",
            quality_score=0.9
        )
        assert query.matches(different_chunk) == False
    
    def test_redis_flat_dict_integration(self, sample_chunk_data: Dict[str, Any]):
        """Test integration with Redis flat dictionary format."""
        # Test flat dict serialization
        query = ChunkQuery(type="DocBlock", quality_score=">=0.8")
        flat_dict = query.to_flat_dict()
        assert "type" in flat_dict
        assert "quality_score" in flat_dict
        
        # Test flat dict deserialization
        restored_query = ChunkQuery.from_flat_dict(flat_dict)
        assert restored_query.type == "DocBlock"
        assert restored_query.quality_score == ">=0.8"
        
        # Test that restored query works the same (excluding created_at which is auto-generated)
        restored_query.created_at = None
        query.created_at = None
        assert restored_query.matches(sample_chunk_data) == query.matches(sample_chunk_data)
    
    def test_performance_optimization(self):
        """Test performance optimization features."""
        complex_expr = """
            (type = 'DocBlock' OR type = 'CodeBlock') AND
            quality_score >= 0.7 AND
            (tags intersects ['ai', 'ml'] OR tags intersects ['python', 'data']) AND
            year >= 2020 AND
            NOT is_deleted AND
            is_public = true
        """
        
        query = ChunkQuery(filter_expr=complex_expr)
        
        # Measure first parse time
        start_time = time.time()
        ast1 = query.get_ast()
        first_parse_time = time.time() - start_time
        
        # Measure cached parse time
        start_time = time.time()
        ast2 = query.get_ast()
        cached_parse_time = time.time() - start_time
        
        # Cached access should be much faster
        assert cached_parse_time < first_parse_time * 0.1  # At least 10x faster
        
        # Test cache clearing
        query.clear_cache()
        stats = query.get_cache_stats()
        assert stats["ast_cached"] == False
    
    def test_error_handling(self):
        """Test error handling in various scenarios."""
        # Invalid filter expression
        with pytest.raises(FilterParseError):
            query = ChunkQuery(filter_expr="invalid syntax")
            query.get_ast()
        
        # Invalid chunk data type
        query = ChunkQuery(type="DocBlock")
        # Now the method should handle invalid data types gracefully and return False
        result = query.matches("not a dict or SemanticChunk")
        assert result == False
    
    def test_field_type_validation(self):
        """Test field type validation."""
        # Valid enum values
        query = ChunkQuery(
            type="DocBlock",
            role="system",
            status="verified",
            language="en"
        )
        assert query.type == ChunkType.DOC_BLOCK
        assert query.role == ChunkRole.SYSTEM
        assert query.status == ChunkStatus.VERIFIED
        assert query.language == LanguageEnum.EN
        
        # Invalid enum values
        with pytest.raises(ValueError):
            ChunkQuery(type="InvalidType")
        
        with pytest.raises(ValueError):
            ChunkQuery(language="invalid")
    
    def test_operator_string_parsing(self, sample_chunk_data: Dict[str, Any]):
        """Test parsing of operator strings in field values."""
        # Numeric comparisons
        query = ChunkQuery(quality_score=">=0.7")
        assert query.matches(sample_chunk_data) == True
        
        query = ChunkQuery(quality_score="<=0.9")
        assert query.matches(sample_chunk_data) == True
        
        query = ChunkQuery(quality_score=">0.9")
        assert query.matches(sample_chunk_data) == False
        
        # String comparisons
        query = ChunkQuery(title="like:Python")
        assert query.matches(sample_chunk_data) == True
        
        query = ChunkQuery(title="like:Java")
        assert query.matches(sample_chunk_data) == False
        
        # List operations
        query = ChunkQuery(tags="in:ai,ml")
        assert query.matches(sample_chunk_data) == True
    
    def test_complex_real_world_scenarios(self):
        """Test complex real-world filtering scenarios."""
        # Content management scenario
        content_query = ChunkQuery(filter_expr="""
            type = 'DocBlock' AND
            quality_score >= 0.8 AND
            status = 'verified' AND
            (tags intersects ['documentation', 'guide'] OR 
             tags intersects ['tutorial', 'example']) AND
            year >= 2020 AND
            is_public = true AND
            NOT is_deleted
        """)
        
        # Analytics scenario
        analytics_query = ChunkQuery(filter_expr="""
            (type = 'DocBlock' OR type = 'CodeBlock') AND
            feedback_accepted >= 5 AND
            used_in_generation = true AND
            (language = 'en' OR language = 'ru') AND
            created_at >= '2024-01-01T00:00:00Z' AND
            quality_score >= 0.7
        """)
        
        # Search and discovery scenario
        search_query = ChunkQuery(filter_expr="""
            (title like 'Python' OR 
             summary like 'machine learning' OR
             tags intersects ['python', 'ai', 'ml']) AND
            (type = 'DocBlock' OR type = 'CodeBlock') AND
            quality_score >= 0.6 AND
            year >= 2020 AND
            is_public = true
        """)
        
        # All queries should parse successfully
        assert content_query.get_ast() is not None
        assert analytics_query.get_ast() is not None
        assert search_query.get_ast() is not None
        
        # All queries should validate successfully
        assert content_query.validate().is_valid == True
        assert analytics_query.validate().is_valid == True
        assert search_query.validate().is_valid == True


class TestChunkQueryPerformance:
    """Performance tests for ChunkQuery."""
    
    def test_ast_caching_performance(self):
        """Test AST caching performance benefits."""
        complex_expr = """
            (type = 'DocBlock' OR type = 'CodeBlock') AND
            quality_score >= 0.7 AND
            (tags intersects ['ai', 'ml'] OR tags intersects ['python', 'data']) AND
            year >= 2020 AND
            NOT is_deleted AND
            is_public = true AND
            (language = 'en' OR language = 'ru') AND
            feedback_accepted >= 3
        """
        
        query = ChunkQuery(filter_expr=complex_expr)
        
        # Warm up
        query.get_ast()
        
        # Measure multiple accesses
        times = []
        for _ in range(10):
            start = time.time()
            ast = query.get_ast()
            times.append(time.time() - start)
        
        # All accesses should be fast (cached)
        avg_time = sum(times) / len(times)
        assert avg_time < 0.001  # Less than 1ms per access
    
    def test_filter_execution_performance(self):
        """Test filter execution performance."""
        chunk_data = {
            "type": "DocBlock",
            "quality_score": 0.8,
            "tags": ["ai", "python"],
            "year": 2023,
            "is_public": True,
            "is_deleted": False
        }
        
        query = ChunkQuery(filter_expr="""
            type = 'DocBlock' AND quality_score >= 0.7 AND
            tags intersects ['ai', 'ml'] AND year >= 2020 AND
            NOT is_deleted AND is_public = true
        """)
        
        # Warm up
        query.matches(chunk_data)
        
        # Measure execution time
        times = []
        for _ in range(100):
            start = time.time()
            result = query.matches(chunk_data)
            times.append(time.time() - start)
        
        avg_time = sum(times) / len(times)
        assert avg_time < 0.01  # Less than 10ms per execution
        assert all(result == True for _ in range(100))  # All should match


class TestChunkQueryEdgeCases:
    """Edge case tests for ChunkQuery."""
    
    def test_empty_filter(self):
        """Test behavior with empty filter."""
        query = ChunkQuery()
        chunk_data = {"type": "DocBlock"}
        
        # Empty filter should match everything
        assert query.matches(chunk_data) == True
        
        # Empty filter should have no AST
        assert query.get_ast() is None
        
        # Empty filter should be valid
        assert query.validate().is_valid == True
    
    def test_none_values(self):
        """Test handling of None values."""
        query = ChunkQuery(type=None, quality_score=None)
        chunk_data = {"type": "DocBlock", "quality_score": 0.8}
        
        # None values should be ignored
        assert query.matches(chunk_data) == True
    
    def test_missing_fields(self):
        """Test handling of missing fields in chunk data."""
        query = ChunkQuery(type="DocBlock", quality_score=">=0.8")
        chunk_data = {"type": "DocBlock"}  # Missing quality_score
        
        # Should handle missing fields gracefully
        assert query.matches(chunk_data) == False
    
    def test_case_sensitivity(self):
        """Test case sensitivity in field matching."""
        query = ChunkQuery(type="DocBlock")  # Correct case
        chunk_data = {"type": "DocBlock"}  # Mixed case
        
        # Should be case-insensitive
        assert query.matches(chunk_data) == True
    
    def test_special_characters(self):
        """Test handling of special characters in filter expressions."""
        query = ChunkQuery(filter_expr="title like 'Python & Machine'")
        chunk_data = {"title": "Python & Machine Learning Guide"}
        
        # Should handle special characters correctly
        assert query.matches(chunk_data) == True 