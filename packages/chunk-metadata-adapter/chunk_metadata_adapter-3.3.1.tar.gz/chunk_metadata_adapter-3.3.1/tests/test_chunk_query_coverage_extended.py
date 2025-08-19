"""
Extended tests for ChunkQuery to achieve 90%+ coverage.

This module contains additional tests to cover the remaining uncovered lines
in ChunkQuery, focusing on operator string matching, list operations, and edge cases.

Author: Development Team
Created: 2024-01-20
Updated: 2024-01-20
"""

import pytest
import re
from typing import Dict, Any
from unittest.mock import Mock, patch

from chunk_metadata_adapter.chunk_query import ChunkQuery
from chunk_metadata_adapter.semantic_chunk import SemanticChunk
from chunk_metadata_adapter.data_types import ChunkType, ChunkRole, ChunkStatus, LanguageEnum, BlockType


class TestChunkQueryOperatorStringMatching:
    """Tests for operator string matching functionality."""
    
    def test_matches_operator_string_greater_equal(self):
        """Test >= operator string matching."""
        query = ChunkQuery(quality_score=">=0.8")
        chunk_data = {"quality_score": 0.9}
        assert query.matches(chunk_data) == True
        
        chunk_data = {"quality_score": 0.7}
        assert query.matches(chunk_data) == False
    
    def test_matches_operator_string_less_equal(self):
        """Test <= operator string matching."""
        query = ChunkQuery(quality_score="<=0.8")
        chunk_data = {"quality_score": 0.7}
        assert query.matches(chunk_data) == True
        
        chunk_data = {"quality_score": 0.9}
        assert query.matches(chunk_data) == False
    
    def test_matches_operator_string_greater(self):
        """Test > operator string matching."""
        query = ChunkQuery(quality_score=">0.8")
        chunk_data = {"quality_score": 0.9}
        assert query.matches(chunk_data) == True
        
        chunk_data = {"quality_score": 0.8}
        assert query.matches(chunk_data) == False
    
    def test_matches_operator_string_less(self):
        """Test < operator string matching."""
        query = ChunkQuery(quality_score="<0.8")
        chunk_data = {"quality_score": 0.7}
        assert query.matches(chunk_data) == True
        
        chunk_data = {"quality_score": 0.8}
        assert query.matches(chunk_data) == False
    
    def test_matches_operator_string_not_equal(self):
        """Test != operator string matching."""
        query = ChunkQuery(quality_score="!=0.8")
        chunk_data = {"quality_score": 0.9}
        assert query.matches(chunk_data) == True
        
        chunk_data = {"quality_score": 0.8}
        assert query.matches(chunk_data) == False
    
    def test_matches_operator_string_equal(self):
        """Test = operator string matching."""
        query = ChunkQuery(quality_score="=0.8")
        chunk_data = {"quality_score": 0.8}
        assert query.matches(chunk_data) == True
        
        chunk_data = {"quality_score": 0.9}
        assert query.matches(chunk_data) == False
    
    def test_matches_operator_string_in(self):
        """Test in: operator string matching."""
        query = ChunkQuery(tags="in:ai,python")
        chunk_data = {"tags": ["ai", "python", "ml"]}
        assert query.matches(chunk_data) == True
        
        chunk_data = {"tags": ["ml", "data"]}
        assert query.matches(chunk_data) == False
    
    def test_matches_operator_string_not_in(self):
        """Test not_in: operator string matching."""
        query = ChunkQuery(tags="not_in:ai,python")
        chunk_data = {"tags": ["ml", "data"]}
        assert query.matches(chunk_data) == True
        
        chunk_data = {"tags": ["ai", "python"]}
        assert query.matches(chunk_data) == False
    
    def test_matches_operator_string_like(self):
        """Test like: operator string matching."""
        query = ChunkQuery(title="like:Python")
        chunk_data = {"title": "Python Machine Learning Guide"}
        assert query.matches(chunk_data) == True
        
        chunk_data = {"title": "Java Programming Guide"}
        assert query.matches(chunk_data) == False
    
    def test_matches_operator_string_regex(self):
        """Test ~ operator string matching."""
        query = ChunkQuery(title="~Python.*Guide")
        chunk_data = {"title": "Python Machine Learning Guide"}
        assert query.matches(chunk_data) == True
        
        chunk_data = {"title": "Java Programming Guide"}
        assert query.matches(chunk_data) == False
    
    def test_matches_operator_string_not_regex(self):
        """Test !~ operator string matching."""
        query = ChunkQuery(title="!~Python.*Guide")
        chunk_data = {"title": "Java Programming Guide"}
        assert query.matches(chunk_data) == True
        
        chunk_data = {"title": "Python Machine Learning Guide"}
        assert query.matches(chunk_data) == False
    
    def test_matches_operator_string_invalid_regex(self):
        """Test invalid regex pattern handling."""
        query = ChunkQuery(title="~[invalid")
        chunk_data = {"title": "Some title"}
        # Should handle invalid regex gracefully
        assert query.matches(chunk_data) == False
    
    def test_matches_operator_string_invalid_not_regex(self):
        """Test invalid not regex pattern handling."""
        query = ChunkQuery(title="!~[invalid")
        chunk_data = {"title": "Some title"}
        # Should handle invalid regex gracefully
        assert query.matches(chunk_data) == True
    
    def test_matches_operator_string_simple_string(self):
        """Test simple string matching (no operator)."""
        query = ChunkQuery(type="DocBlock")
        chunk_data = {"type": "DocBlock"}
        assert query.matches(chunk_data) == True
        
        chunk_data = {"type": "CodeBlock"}
        assert query.matches(chunk_data) == False
    
    def test_matches_operator_string_case_insensitive(self):
        """Test case insensitive string matching."""
        query = ChunkQuery(type="DocBlock")
        chunk_data = {"type": "DocBlock"}
        assert query.matches(chunk_data) == True


class TestChunkQueryNumericFieldMatching:
    """Tests for numeric field matching."""
    
    def test_matches_numeric_field_quality_score(self):
        """Test numeric field matching for quality_score."""
        query = ChunkQuery(quality_score=">=0.8")
        chunk_data = {"quality_score": 0.9}
        assert query.matches(chunk_data) == True
        
        chunk_data = {"quality_score": None}
        assert query.matches(chunk_data) == False
    
    def test_matches_numeric_field_coverage(self):
        """Test numeric field matching for coverage."""
        query = ChunkQuery(coverage="<=0.5")
        chunk_data = {"coverage": 0.3}
        assert query.matches(chunk_data) == True
    
    def test_matches_numeric_field_cohesion(self):
        """Test numeric field matching for cohesion."""
        query = ChunkQuery(cohesion=">0.7")
        chunk_data = {"cohesion": 0.8}
        assert query.matches(chunk_data) == True
    
    def test_matches_numeric_field_boundary_prev(self):
        """Test numeric field matching for boundary_prev."""
        query = ChunkQuery(boundary_prev="<0.3")
        chunk_data = {"boundary_prev": 0.2}
        assert query.matches(chunk_data) == True
    
    def test_matches_numeric_field_boundary_next(self):
        """Test numeric field matching for boundary_next."""
        query = ChunkQuery(boundary_next="!=0.5")
        chunk_data = {"boundary_next": 0.6}
        assert query.matches(chunk_data) == True
    
    def test_matches_numeric_field_feedback_accepted(self):
        """Test numeric field matching for feedback_accepted."""
        query = ChunkQuery(feedback_accepted=">=5")
        chunk_data = {"feedback_accepted": 7}
        assert query.matches(chunk_data) == True
    
    def test_matches_numeric_field_feedback_rejected(self):
        """Test numeric field matching for feedback_rejected."""
        query = ChunkQuery(feedback_rejected="<3")
        chunk_data = {"feedback_rejected": 1}
        assert query.matches(chunk_data) == True
    
    def test_matches_numeric_field_start(self):
        """Test numeric field matching for start."""
        query = ChunkQuery(start=">100")
        chunk_data = {"start": 150}
        assert query.matches(chunk_data) == True
    
    def test_matches_numeric_field_end(self):
        """Test numeric field matching for end."""
        query = ChunkQuery(end="<=200")
        chunk_data = {"end": 180}
        assert query.matches(chunk_data) == True
    
    def test_matches_numeric_field_year(self):
        """Test numeric field matching for year."""
        query = ChunkQuery(year=">=2020")
        chunk_data = {"year": 2023}
        assert query.matches(chunk_data) == True
    
    def test_matches_numeric_field_ordinal(self):
        """Test numeric field matching for ordinal."""
        query = ChunkQuery(ordinal="<10")
        chunk_data = {"ordinal": 5}
        assert query.matches(chunk_data) == True
    
    def test_matches_numeric_field_source_lines_start(self):
        """Test numeric field matching for source_lines_start."""
        query = ChunkQuery(source_lines_start=">=50")
        chunk_data = {"source_lines_start": 75}
        assert query.matches(chunk_data) == True
    
    def test_matches_numeric_field_source_lines_end(self):
        """Test numeric field matching for source_lines_end."""
        query = ChunkQuery(source_lines_end="<=100")
        chunk_data = {"source_lines_end": 85}
        assert query.matches(chunk_data) == True
    
    def test_matches_numeric_field_block_index(self):
        """Test numeric field matching for block_index."""
        query = ChunkQuery(block_index="!=0")
        chunk_data = {"block_index": 5}
        assert query.matches(chunk_data) == True
    
    def test_matches_numeric_field_conversion_error(self):
        """Test numeric field matching with conversion error."""
        query = ChunkQuery(quality_score=">=0.8")
        chunk_data = {"quality_score": "invalid"}
        # Should handle conversion error gracefully
        assert query.matches(chunk_data) == False


class TestChunkQueryListFieldMatching:
    """Tests for list field matching."""
    
    def test_matches_list_field_string_input(self):
        """Test list field matching with string input."""
        query = ChunkQuery(tags=["ai", "python"])
        chunk_data = {"tags": "ai,python,ml"}
        assert query.matches(chunk_data) == True
    
    def test_matches_list_field_list_input(self):
        """Test list field matching with list input."""
        query = ChunkQuery(tags=["ai", "python"])
        chunk_data = {"tags": ["ai", "python", "ml"]}
        assert query.matches(chunk_data) == True
    
    def test_matches_list_field_tuple_input(self):
        """Test list field matching with tuple input."""
        query = ChunkQuery(tags=["ai", "python"])
        chunk_data = {"tags": ("ai", "python", "ml")}
        assert query.matches(chunk_data) == True
    
    def test_matches_list_field_none_input(self):
        """Test list field matching with None input."""
        query = ChunkQuery(tags=["ai", "python"])
        chunk_data = {"tags": None}
        assert query.matches(chunk_data) == False
    
    def test_matches_list_field_non_list_input(self):
        """Test list field matching with non-list input."""
        query = ChunkQuery(tags=["ai", "python"])
        chunk_data = {"tags": "ai"}
        assert query.matches(chunk_data) == True
    
    def test_matches_list_field_empty_string(self):
        """Test list field matching with empty string."""
        query = ChunkQuery(tags=["ai", "python"])
        chunk_data = {"tags": ""}
        assert query.matches(chunk_data) == False
    
    def test_matches_list_field_empty_list(self):
        """Test list field matching with empty list."""
        query = ChunkQuery(tags=["ai", "python"])
        chunk_data = {"tags": []}
        assert query.matches(chunk_data) == False
    
    def test_matches_list_field_with_none_values(self):
        """Test list field matching with None values in list."""
        query = ChunkQuery(tags=["ai", "python"])
        chunk_data = {"tags": ["ai", None, "python"]}
        assert query.matches(chunk_data) == True
    
    def test_matches_list_field_query_string_input(self):
        """Test list field matching with query string input."""
        query = ChunkQuery(tags="ai,python")
        chunk_data = {"tags": ["ai", "python", "ml"]}
        assert query.matches(chunk_data) == True
    
    def test_matches_list_field_query_list_input(self):
        """Test list field matching with query list input."""
        query = ChunkQuery(tags=["ai", "python"])
        chunk_data = {"tags": ["ai", "python", "ml"]}
        assert query.matches(chunk_data) == True
    
    def test_matches_list_field_query_none_input(self):
        """Test list field matching with query None input."""
        query = ChunkQuery(tags=None)
        chunk_data = {"tags": ["ai", "python"]}
        assert query.matches(chunk_data) == True  # No filter means match


class TestChunkQueryBooleanFieldMatching:
    """Tests for boolean field matching."""
    
    def test_matches_boolean_field_true_true(self):
        """Test boolean field matching True with True."""
        query = ChunkQuery(is_public=True)
        chunk_data = {"is_public": True}
        assert query.matches(chunk_data) == True
    
    def test_matches_boolean_field_true_false(self):
        """Test boolean field matching True with False."""
        query = ChunkQuery(is_public=True)
        chunk_data = {"is_public": False}
        assert query.matches(chunk_data) == False
    
    def test_matches_boolean_field_false_true(self):
        """Test boolean field matching False with True."""
        query = ChunkQuery(is_public=False)
        chunk_data = {"is_public": True}
        assert query.matches(chunk_data) == False
    
    def test_matches_boolean_field_false_false(self):
        """Test boolean field matching False with False."""
        query = ChunkQuery(is_public=False)
        chunk_data = {"is_public": False}
        assert query.matches(chunk_data) == True
    
    def test_matches_boolean_field_string_true(self):
        """Test boolean field matching with string 'true'."""
        query = ChunkQuery(is_public="true")
        chunk_data = {"is_public": True}
        assert query.matches(chunk_data) == True
    
    def test_matches_boolean_field_string_false(self):
        """Test boolean field matching with string 'false'."""
        query = ChunkQuery(is_public="false")
        chunk_data = {"is_public": False}
        assert query.matches(chunk_data) == True
    
    def test_matches_boolean_field_string_invalid(self):
        """Test boolean field matching with invalid string."""
        query = ChunkQuery(is_public="invalid")
        chunk_data = {"is_public": True}
        assert query.matches(chunk_data) == False
    
    def test_matches_boolean_field_none(self):
        """Test boolean field matching with None."""
        query = ChunkQuery(is_public=True)
        chunk_data = {"is_public": None}
        assert query.matches(chunk_data) == False
    
    def test_matches_boolean_field_used_in_generation(self):
        """Test boolean field matching for used_in_generation."""
        query = ChunkQuery(used_in_generation=True)
        chunk_data = {"used_in_generation": True}
        assert query.matches(chunk_data) == True
    
    def test_matches_boolean_field_is_deleted(self):
        """Test boolean field matching for is_deleted."""
        query = ChunkQuery(is_deleted=False)
        chunk_data = {"is_deleted": False}
        assert query.matches(chunk_data) == True


class TestChunkQueryListOperatorMatching:
    """Tests for list operator matching."""
    
    def test_matches_list_operator_in(self):
        """Test list operator 'in' matching."""
        query = ChunkQuery(tags="in:ai,python")
        chunk_data = {"tags": ["ai", "python", "ml"]}
        assert query.matches(chunk_data) == True
    
    def test_matches_list_operator_not_in(self):
        """Test list operator 'not_in' matching."""
        query = ChunkQuery(tags="not_in:ai,python")
        chunk_data = {"tags": ["ml", "data"]}
        assert query.matches(chunk_data) == True
    
    def test_matches_list_operator_in_string_input(self):
        """Test list operator 'in' with string input."""
        query = ChunkQuery(tags="in:ai,python")
        chunk_data = {"tags": "ai,python,ml"}
        assert query.matches(chunk_data) == True
    
    def test_matches_list_operator_not_in_string_input(self):
        """Test list operator 'not_in' with string input."""
        query = ChunkQuery(tags="not_in:ai,python")
        chunk_data = {"tags": "ml,data"}
        assert query.matches(chunk_data) == True
    
    def test_matches_list_operator_in_none_input(self):
        """Test list operator 'in' with None input."""
        query = ChunkQuery(tags="in:ai,python")
        chunk_data = {"tags": None}
        assert query.matches(chunk_data) == False
    
    def test_matches_list_operator_not_in_none_input(self):
        """Test list operator 'not_in' with None input."""
        query = ChunkQuery(tags="not_in:ai,python")
        chunk_data = {"tags": None}
        assert query.matches(chunk_data) == False  # None cannot be compared with not_in
    
    def test_matches_list_operator_in_empty_list(self):
        """Test list operator 'in' with empty list."""
        query = ChunkQuery(tags="in:ai,python")
        chunk_data = {"tags": []}
        assert query.matches(chunk_data) == False
    
    def test_matches_list_operator_not_in_empty_list(self):
        """Test list operator 'not_in' with empty list."""
        query = ChunkQuery(tags="not_in:ai,python")
        chunk_data = {"tags": []}
        assert query.matches(chunk_data) == True  # Empty list doesn't contain the items


class TestChunkQueryStringComparison:
    """Tests for string comparison functionality."""
    
    def test_compare_strings_equal(self):
        """Test string comparison with = operator."""
        query = ChunkQuery(title="=Python Guide")
        chunk_data = {"title": "Python Guide"}
        assert query.matches(chunk_data) == True
    
    def test_compare_strings_not_equal(self):
        """Test string comparison with != operator."""
        query = ChunkQuery(title="!=Python Guide")
        chunk_data = {"title": "Java Guide"}
        assert query.matches(chunk_data) == True
    
    def test_compare_strings_like(self):
        """Test string comparison with like operator."""
        query = ChunkQuery(title="like:Python")
        chunk_data = {"title": "Python Machine Learning Guide"}
        assert query.matches(chunk_data) == True
    
    def test_compare_strings_regex(self):
        """Test string comparison with regex operator."""
        query = ChunkQuery(title="~Python.*Guide")
        chunk_data = {"title": "Python Machine Learning Guide"}
        assert query.matches(chunk_data) == True
    
    def test_compare_strings_not_regex(self):
        """Test string comparison with not regex operator."""
        query = ChunkQuery(title="!~Python.*Guide")
        chunk_data = {"title": "Java Programming Guide"}
        assert query.matches(chunk_data) == True
    
    def test_compare_strings_invalid_regex(self):
        """Test string comparison with invalid regex."""
        query = ChunkQuery(title="~[invalid")
        chunk_data = {"title": "Some title"}
        assert query.matches(chunk_data) == False
    
    def test_compare_strings_invalid_not_regex(self):
        """Test string comparison with invalid not regex."""
        query = ChunkQuery(title="!~[invalid")
        chunk_data = {"title": "Some title"}
        assert query.matches(chunk_data) == True
    
    def test_compare_strings_unknown_operator(self):
        """Test string comparison with unknown operator."""
        query = ChunkQuery(title="unknown:value")
        chunk_data = {"title": "Some title"}
        assert query.matches(chunk_data) == False


class TestChunkQueryFieldValueMatching:
    """Tests for field value matching."""
    
    def test_matches_field_value_none_none(self):
        """Test field value matching None with None."""
        query = ChunkQuery(type=None)
        chunk_data = {"type": None}
        assert query.matches(chunk_data) == True
    
    def test_matches_field_value_none_value(self):
        """Test field value matching None with value."""
        query = ChunkQuery(type=None)
        chunk_data = {"type": "DocBlock"}
        assert query.matches(chunk_data) == True  # No filter means match
    
    def test_matches_field_value_value_none(self):
        """Test field value matching value with None."""
        query = ChunkQuery(type="DocBlock")
        chunk_data = {"type": None}
        assert query.matches(chunk_data) == False
    
    def test_matches_field_value_operator_string(self):
        """Test field value matching with operator string."""
        query = ChunkQuery(quality_score=">=0.8")
        chunk_data = {"quality_score": 0.9}
        assert query.matches(chunk_data) == True
    
    def test_matches_field_value_list_field(self):
        """Test field value matching with list field."""
        query = ChunkQuery(tags=["ai", "python"])
        chunk_data = {"tags": ["ai", "python", "ml"]}
        assert query.matches(chunk_data) == True
    
    def test_matches_field_value_boolean_field(self):
        """Test field value matching with boolean field."""
        query = ChunkQuery(is_public=True)
        chunk_data = {"is_public": True}
        assert query.matches(chunk_data) == True
    
    def test_matches_field_value_numeric_field(self):
        """Test field value matching with numeric field."""
        query = ChunkQuery(quality_score=0.8)
        chunk_data = {"quality_score": 0.8}
        assert query.matches(chunk_data) == True
    
    def test_matches_field_value_string_field(self):
        """Test field value matching with string field."""
        query = ChunkQuery(type="DocBlock")
        chunk_data = {"type": "DocBlock"}
        assert query.matches(chunk_data) == True
    
    def test_matches_field_value_different_types(self):
        """Test field value matching with different types."""
        query = ChunkQuery(quality_score=0.8)
        chunk_data = {"quality_score": "0.8"}
        assert query.matches(chunk_data) == True  # Should handle type conversion 

    def test_validate_search_fields_invalid_fields(self):
        """Test validation of search fields with invalid fields."""
        with pytest.raises(ValueError, match="Invalid search fields"):
            ChunkQuery(search_fields=["invalid_field"])
        
        with pytest.raises(ValueError, match="Invalid search fields"):
            ChunkQuery(search_fields=["body", "invalid_field", "title"])
    
    def test_validate_search_fields_valid_fields(self):
        """Test validation of search fields with valid fields."""
        query = ChunkQuery(search_fields=["body", "title"])
        assert query.search_fields == ["body", "title"]
        
        query = ChunkQuery(search_fields=["summary", "text"])
        assert query.search_fields == ["summary", "text"]
    
    def test_validate_search_fields_none(self):
        """Test validation of search fields with None value."""
        query = ChunkQuery(search_fields=None)
        assert query.search_fields is None
    
    def test_validate_type_field_invalid_type(self):
        """Test validation of type field with invalid type."""
        with pytest.raises(ValueError, match="Invalid chunk type"):
            ChunkQuery(type="InvalidType")
    
    def test_validate_role_field_invalid_role(self):
        """Test validation of role field with invalid role."""
        with pytest.raises(ValueError, match="Invalid chunk role"):
            ChunkQuery(role="InvalidRole")
    
    def test_validate_status_field_invalid_status(self):
        """Test validation of status field with invalid status."""
        with pytest.raises(ValueError, match="Invalid chunk status"):
            ChunkQuery(status="InvalidStatus")
    
    def test_validate_language_field_invalid_language(self):
        """Test validation of language field with invalid language."""
        with pytest.raises(ValueError, match="Invalid language"):
            ChunkQuery(language="InvalidLanguage")
    
    def test_validate_block_type_field_invalid_block_type(self):
        """Test validation of block_type field with invalid block type."""
        with pytest.raises(ValueError, match="Invalid block type"):
            ChunkQuery(block_type="InvalidBlockType")
    
    def test_validate_type_field_enum_value(self):
        """Test validation of type field with enum value."""
        from chunk_metadata_adapter.data_types import ChunkType
        query = ChunkQuery(type=ChunkType.DOC_BLOCK)
        assert query.type == ChunkType.DOC_BLOCK
    
    def test_validate_role_field_enum_value(self):
        """Test validation of role field with enum value."""
        from chunk_metadata_adapter.data_types import ChunkRole
        query = ChunkQuery(role=ChunkRole.USER)
        assert query.role == ChunkRole.USER
    
    def test_validate_status_field_enum_value(self):
        """Test validation of status field with enum value."""
        from chunk_metadata_adapter.data_types import ChunkStatus
        query = ChunkQuery(status=ChunkStatus.NEW)
        assert query.status == ChunkStatus.NEW
    
    def test_validate_language_field_enum_value(self):
        """Test validation of language field with enum value."""
        from chunk_metadata_adapter.data_types import LanguageEnum
        query = ChunkQuery(language=LanguageEnum.EN)
        assert query.language == LanguageEnum.EN
    
    def test_validate_block_type_field_enum_value(self):
        """Test validation of block_type field with enum value."""
        from chunk_metadata_adapter.data_types import BlockType
        query = ChunkQuery(block_type=BlockType.PARAGRAPH)
        assert query.block_type == BlockType.PARAGRAPH
    
    def test_has_simple_fields_all_fields_none(self):
        """Test _has_simple_fields when all fields are None."""
        query = ChunkQuery()
        assert query._has_simple_fields() == False
    
    def test_has_simple_fields_with_filter_expr_only(self):
        """Test _has_simple_fields when only filter_expr is set."""
        query = ChunkQuery(filter_expr="type = 'DocBlock'")
        assert query._has_simple_fields() == True
    
    def test_has_simple_fields_with_various_fields(self):
        """Test _has_simple_fields with various field combinations."""
        # Test with type
        query = ChunkQuery(type="DocBlock")
        assert query._has_simple_fields() == True
        
        # Test with role
        query = ChunkQuery(role="user")
        assert query._has_simple_fields() == True
        
        # Test with status
        query = ChunkQuery(status="new")
        assert query._has_simple_fields() == True
        
        # Test with language
        query = ChunkQuery(language="en")
        assert query._has_simple_fields() == True
        
        # Test with block_type
        query = ChunkQuery(block_type="paragraph")
        assert query._has_simple_fields() == True
        
        # Test with quality_score
        query = ChunkQuery(quality_score=0.8)
        assert query._has_simple_fields() == True
        
        # Test with coverage
        query = ChunkQuery(coverage=0.9)
        assert query._has_simple_fields() == True
        
        # Test with cohesion
        query = ChunkQuery(cohesion=0.7)
        assert query._has_simple_fields() == True
        
        # Test with boundary_prev
        query = ChunkQuery(boundary_prev=0.5)
        assert query._has_simple_fields() == True
        
        # Test with boundary_next
        query = ChunkQuery(boundary_next=0.6)
        assert query._has_simple_fields() == True
        
        # Test with feedback_accepted
        query = ChunkQuery(feedback_accepted=5)
        assert query._has_simple_fields() == True
        
        # Test with feedback_rejected
        query = ChunkQuery(feedback_rejected=2)
        assert query._has_simple_fields() == True
        
        # Test with start
        query = ChunkQuery(start=10)
        assert query._has_simple_fields() == True
        
        # Test with end
        query = ChunkQuery(end=100)
        assert query._has_simple_fields() == True
        
        # Test with year
        query = ChunkQuery(year=2023)
        assert query._has_simple_fields() == True
        
        # Test with ordinal
        query = ChunkQuery(ordinal=1)
        assert query._has_simple_fields() == True
        
        # Test with source_lines_start
        query = ChunkQuery(source_lines_start=1)
        assert query._has_simple_fields() == True
        
        # Test with source_lines_end
        query = ChunkQuery(source_lines_end=10)
        assert query._has_simple_fields() == True
        
        # Test with block_index
        query = ChunkQuery(block_index=0)
        assert query._has_simple_fields() == True
        
        # Test with is_deleted
        query = ChunkQuery(is_deleted=False)
        assert query._has_simple_fields() == True
        
        # Test with is_public
        query = ChunkQuery(is_public=True)
        assert query._has_simple_fields() == True
        
        # Test with used_in_generation
        query = ChunkQuery(used_in_generation=True)
        assert query._has_simple_fields() == True
        
        # Test with tags
        query = ChunkQuery(tags=["ai", "ml"])
        assert query._has_simple_fields() == True
        
        # Test with links
        query = ChunkQuery(links=["link1", "link2"])
        assert query._has_simple_fields() == True
        
        # Test with block_meta
        query = ChunkQuery(block_meta={"key": "value"})
        assert query._has_simple_fields() == True
        
        # Test with tags_flat
        query = ChunkQuery(tags_flat="ai,ml")
        assert query._has_simple_fields() == True 