"""
Unit tests for BM25 functionality in ChunkQuery.

This module tests the new BM25 search fields and validation functionality
added to ChunkQuery for full-text search capabilities.

Test coverage:
- BM25 field validation
- Hybrid search parameter validation
- Search field validation
- Parameter consistency validation
- Error handling for invalid parameters

Author: Development Team
Created: 2024-01-20
"""

import pytest
from pydantic import ValidationError
from chunk_metadata_adapter import ChunkQuery
from chunk_metadata_adapter.query_validator import ValidationResult


class TestChunkQueryBM25Fields:
    """Tests for BM25 search fields in ChunkQuery."""
    
    def test_basic_bm25_fields_creation(self):
        """Test creating ChunkQuery with basic BM25 fields."""
        query = ChunkQuery(
            search_query="python machine learning",
            search_fields=["body", "text", "summary"],
            bm25_k1=1.5,
            bm25_b=0.8
        )
        
        assert query.search_query == "python machine learning"
        assert query.search_fields == ["body", "text", "summary"]
        assert query.bm25_k1 == 1.5
        assert query.bm25_b == 0.8
    
    def test_bm25_fields_default_values(self):
        """Test default values for BM25 fields."""
        query = ChunkQuery()
        
        assert query.search_query is None
        assert query.search_fields == ["body", "text", "summary", "title"]
        assert query.bm25_k1 == 1.2
        assert query.bm25_b == 0.75
        assert query.hybrid_search is False
        assert query.bm25_weight == 0.5
        assert query.semantic_weight == 0.5
        assert query.min_score == 0.0
        assert query.max_results == 100
    
    def test_hybrid_search_fields_creation(self):
        """Test creating ChunkQuery with hybrid search fields."""
        query = ChunkQuery(
            search_query="artificial intelligence",
            hybrid_search=True,
            bm25_weight=0.3,
            semantic_weight=0.7,
            min_score=0.5,
            max_results=50
        )
        
        assert query.search_query == "artificial intelligence"
        assert query.hybrid_search is True
        assert query.bm25_weight == 0.3
        assert query.semantic_weight == 0.7
        assert query.min_score == 0.5
        assert query.max_results == 50


class TestChunkQueryBM25Validation:
    """Tests for BM25 field validation in ChunkQuery."""
    
    def test_search_fields_validation_valid(self):
        """Test validation of valid search fields."""
        query = ChunkQuery(
            search_fields=["body", "text", "summary", "title"]
        )
        assert query.search_fields == ["body", "text", "summary", "title"]
    
    def test_search_fields_validation_invalid(self):
        """Test validation of invalid search fields."""
        with pytest.raises(ValidationError) as exc_info:
            ChunkQuery(search_fields=["body", "invalid_field", "text"])
        
        assert "Invalid search fields" in str(exc_info.value)
    
    def test_bm25_k1_validation_valid(self):
        """Test validation of valid BM25 k1 parameter."""
        query = ChunkQuery(bm25_k1=2.0)
        assert query.bm25_k1 == 2.0
    
    def test_bm25_k1_validation_invalid_range(self):
        """Test validation of BM25 k1 parameter outside valid range."""
        with pytest.raises(ValidationError) as exc_info:
            ChunkQuery(bm25_k1=5.0)
        
        assert "Input should be less than or equal to 3" in str(exc_info.value)
    
    def test_bm25_k1_validation_negative(self):
        """Test validation of negative BM25 k1 parameter."""
        with pytest.raises(ValidationError) as exc_info:
            ChunkQuery(bm25_k1=-1.0)
        
        assert "Input should be greater than or equal to 0" in str(exc_info.value)
    
    def test_bm25_b_validation_valid(self):
        """Test validation of valid BM25 b parameter."""
        query = ChunkQuery(bm25_b=0.9)
        assert query.bm25_b == 0.9
    
    def test_bm25_b_validation_invalid_range(self):
        """Test validation of BM25 b parameter outside valid range."""
        with pytest.raises(ValidationError) as exc_info:
            ChunkQuery(bm25_b=1.5)
        
        assert "Input should be less than or equal to 1" in str(exc_info.value)
    
    def test_search_weights_validation_valid(self):
        """Test validation of valid search weights."""
        query = ChunkQuery(bm25_weight=0.3, semantic_weight=0.7)
        assert query.bm25_weight == 0.3
        assert query.semantic_weight == 0.7
    
    def test_search_weights_validation_invalid_range(self):
        """Test validation of search weights outside valid range."""
        with pytest.raises(ValidationError) as exc_info:
            ChunkQuery(bm25_weight=1.5)
        
        assert "Input should be less than or equal to 1" in str(exc_info.value)
    
    def test_min_score_validation_valid(self):
        """Test validation of valid minimum score."""
        query = ChunkQuery(min_score=0.8)
        assert query.min_score == 0.8
    
    def test_min_score_validation_invalid_range(self):
        """Test validation of minimum score outside valid range."""
        with pytest.raises(ValidationError) as exc_info:
            ChunkQuery(min_score=1.5)
        
        assert "Input should be less than or equal to 1" in str(exc_info.value)
    
    def test_max_results_validation_valid(self):
        """Test validation of valid maximum results."""
        query = ChunkQuery(max_results=500)
        assert query.max_results == 500
    
    def test_max_results_validation_invalid_range(self):
        """Test validation of maximum results outside valid range."""
        with pytest.raises(ValidationError) as exc_info:
            ChunkQuery(max_results=1500)
        
        assert "Input should be less than or equal to 1000" in str(exc_info.value)
    
    def test_max_results_validation_zero(self):
        """Test validation of zero maximum results."""
        with pytest.raises(ValidationError) as exc_info:
            ChunkQuery(max_results=0)
        
        assert "Input should be greater than or equal to 1" in str(exc_info.value)
    
    def test_hybrid_search_validation_valid(self):
        """Test validation of valid hybrid search flag."""
        query = ChunkQuery(hybrid_search=True)
        assert query.hybrid_search is True
    
    def test_hybrid_search_validation_invalid_type(self):
        """Test validation of invalid hybrid search flag type."""
        # Pydantic automatically converts string "true" to boolean True
        # So this test should pass without raising an error
        query = ChunkQuery(hybrid_search="true")
        assert query.hybrid_search is True


class TestChunkQueryBM25ParameterValidation:
    """Tests for BM25 parameter consistency validation."""
    
    def test_validate_bm25_parameters_no_search_query_warning(self):
        """Test validation when BM25 parameters are set but no search query."""
        query = ChunkQuery(
            bm25_k1=2.0,
            bm25_b=0.8,
            hybrid_search=True
        )
        
        result = query.validate_bm25_parameters()
        assert result.is_valid is True
        assert len(result.warnings) > 0
        assert "BM25 parameters set but no search query provided" in result.warnings[0]
    
    def test_validate_bm25_parameters_hybrid_search_missing_weights(self):
        """Test validation when hybrid search is enabled but weights are missing."""
        # Weights have default values, so this should be valid
        query = ChunkQuery(
            search_query="test query",
            hybrid_search=True
        )
        
        result = query.validate_bm25_parameters()
        assert result.is_valid is True
        # Default weights (0.5, 0.5) sum to 1.0, so no warning
        assert len(result.warnings) == 0
    
    def test_validate_bm25_parameters_hybrid_search_weights_sum_warning(self):
        """Test validation when hybrid search weights don't sum to 1.0."""
        query = ChunkQuery(
            search_query="test query",
            hybrid_search=True,
            bm25_weight=0.3,
            semantic_weight=0.3
        )
        
        result = query.validate_bm25_parameters()
        assert result.is_valid is True
        assert len(result.warnings) > 0
        assert "Weights should sum to 1.0" in result.warnings[0]
    
    def test_validate_bm25_parameters_empty_search_fields(self):
        """Test validation when search fields are empty."""
        query = ChunkQuery(
            search_query="test query",
            search_fields=[]
        )
        
        result = query.validate_bm25_parameters()
        assert result.is_valid is False
        assert "Search fields cannot be empty when search query is provided" in result.errors[0]
    
    def test_validate_bm25_parameters_duplicate_search_fields(self):
        """Test validation when search fields contain duplicates."""
        query = ChunkQuery(
            search_query="test query",
            search_fields=["body", "text", "body"]
        )
        
        result = query.validate_bm25_parameters()
        assert result.is_valid is False
        assert "Duplicate search fields are not allowed" in result.errors[0]
    
    def test_validate_bm25_parameters_high_min_score_warning(self):
        """Test validation when minimum score is high with large result set."""
        query = ChunkQuery(
            search_query="test query",
            min_score=0.95,
            max_results=500
        )
        
        result = query.validate_bm25_parameters()
        assert result.is_valid is True
        assert len(result.warnings) > 0
        assert "High minimum score with large result set may return few results" in result.warnings[0]
    
    def test_validate_bm25_parameters_valid_configuration(self):
        """Test validation of valid BM25 configuration."""
        query = ChunkQuery(
            search_query="python machine learning",
            search_fields=["body", "text", "summary"],
            hybrid_search=True,
            bm25_weight=0.4,
            semantic_weight=0.6,
            bm25_k1=1.5,
            bm25_b=0.8,
            min_score=0.3,
            max_results=100
        )
        
        result = query.validate_bm25_parameters()
        assert result.is_valid is True
        assert len(result.errors) == 0
        assert len(result.warnings) == 0


class TestChunkQueryBM25Integration:
    """Tests for BM25 integration with existing ChunkQuery functionality."""
    
    def test_bm25_with_existing_fields(self):
        """Test BM25 fields with existing ChunkQuery fields."""
        query = ChunkQuery(
            type="DocBlock",
            quality_score=">=0.8",
            search_query="artificial intelligence",
            search_fields=["body", "text"],
            hybrid_search=True,
            bm25_weight=0.3,
            semantic_weight=0.7
        )
        
        assert query.type == "DocBlock"
        assert query.quality_score == ">=0.8"
        assert query.search_query == "artificial intelligence"
        assert query.search_fields == ["body", "text"]
        assert query.hybrid_search is True
    
    def test_bm25_with_filter_expression(self):
        """Test BM25 fields with AST filter expression."""
        query = ChunkQuery(
            filter_expr="type = 'DocBlock' AND quality_score >= 0.8",
            search_query="machine learning",
            search_fields=["summary", "title"]
        )
        
        assert query.filter_expr == "type = 'DocBlock' AND quality_score >= 0.8"
        assert query.search_query == "machine learning"
        assert query.search_fields == ["summary", "title"]
    
    def test_bm25_serialization(self):
        """Test serialization of ChunkQuery with BM25 fields."""
        query = ChunkQuery(
            search_query="python programming",
            search_fields=["body", "text"],
            hybrid_search=True,
            bm25_weight=0.4,
            semantic_weight=0.6
        )
        
        # Test to_flat_dict
        flat_dict = query.to_flat_dict()
        assert flat_dict["search_query"] == "python programming"
        assert flat_dict["search_fields"] == ["body", "text"]
        assert flat_dict["hybrid_search"] == "true"  # Serialized as string
        assert flat_dict["bm25_weight"] == "0.4"  # Serialized as string
        assert flat_dict["semantic_weight"] == "0.6"  # Serialized as string
        
        # Test from_flat_dict
        restored_query = ChunkQuery.from_flat_dict(flat_dict)
        assert restored_query.search_query == "python programming"
        assert restored_query.search_fields == ["body", "text"]
        assert restored_query.hybrid_search is True  # Deserialized back to boolean
        assert restored_query.bm25_weight == 0.4
        assert restored_query.semantic_weight == 0.6
    
    def test_bm25_from_dict_with_validation_valid(self):
        """Test from_dict_with_validation with valid BM25 parameters."""
        data = {
            "search_query": "data science",
            "search_fields": ["body", "text"],
            "hybrid_search": True,
            "bm25_weight": 0.3,
            "semantic_weight": 0.7
        }
        
        query, errors = ChunkQuery.from_dict_with_validation(data)
        assert query is not None
        assert errors is None
        assert query.search_query == "data science"
        assert query.hybrid_search is True
    
    def test_bm25_from_dict_with_validation_invalid(self):
        """Test from_dict_with_validation with invalid BM25 parameters."""
        data = {
            "search_query": "test",
            "search_fields": ["invalid_field"],  # Invalid search field
        }
        
        query, errors = ChunkQuery.from_dict_with_validation(data)
        assert query is None
        assert errors is not None
        assert "Invalid search fields" in str(errors)


class TestChunkQueryBM25EdgeCases:
    """Tests for edge cases in BM25 functionality."""
    
    def test_bm25_fields_with_none_values(self):
        """Test BM25 fields with None values."""
        query = ChunkQuery(
            search_query=None,
            search_fields=None,
            bm25_k1=None,
            bm25_b=None,
            hybrid_search=None
        )
        
        assert query.search_query is None
        assert query.search_fields is None  # None is preserved, not converted to default
        assert query.bm25_k1 is None  # None is preserved, not converted to default
        assert query.bm25_b is None  # None is preserved, not converted to default
        assert query.hybrid_search is None  # None is preserved, not converted to default
    
    def test_bm25_fields_with_empty_string(self):
        """Test BM25 fields with empty string search query."""
        query = ChunkQuery(search_query="")
        
        assert query.search_query == ""
        
        # Validation should pass for empty string
        result = query.validate_bm25_parameters()
        assert result.is_valid is True
    
    def test_bm25_fields_with_single_search_field(self):
        """Test BM25 fields with single search field."""
        query = ChunkQuery(
            search_query="test",
            search_fields=["body"]
        )
        
        assert query.search_fields == ["body"]
        
        result = query.validate_bm25_parameters()
        assert result.is_valid is True
    
    def test_bm25_fields_with_all_search_fields(self):
        """Test BM25 fields with all available search fields."""
        query = ChunkQuery(
            search_query="test",
            search_fields=["body", "text", "summary", "title"]
        )
        
        assert query.search_fields == ["body", "text", "summary", "title"]
        
        result = query.validate_bm25_parameters()
        assert result.is_valid is True
    
    def test_bm25_fields_boundary_values(self):
        """Test BM25 fields with boundary values."""
        query = ChunkQuery(
            bm25_k1=0.0,
            bm25_b=1.0,
            bm25_weight=0.0,
            semantic_weight=1.0,
            min_score=1.0,
            max_results=1
        )
        
        assert query.bm25_k1 == 0.0
        assert query.bm25_b == 1.0
        assert query.bm25_weight == 0.0
        assert query.semantic_weight == 1.0
        assert query.min_score == 1.0
        assert query.max_results == 1
        
        result = query.validate_bm25_parameters()
        assert result.is_valid is True
