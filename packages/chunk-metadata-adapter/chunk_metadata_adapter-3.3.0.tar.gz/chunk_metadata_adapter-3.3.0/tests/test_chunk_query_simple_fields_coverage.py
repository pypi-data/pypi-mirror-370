"""
Tests for simple fields coverage in chunk_query.py.

This module contains tests specifically for the _matches_simple_fields method
to achieve higher coverage.
"""

import pytest
from chunk_metadata_adapter import ChunkQuery
from chunk_metadata_adapter.data_types import ChunkType, ChunkRole, ChunkStatus, LanguageEnum, BlockType


class TestChunkQuerySimpleFieldsCoverage:
    """Tests for simple fields matching in ChunkQuery."""
    
    def test_matches_simple_fields_type_field(self):
        """Test _matches_simple_fields with type field (lines 1023-1024)."""
        # Test matching type
        query = ChunkQuery(type=ChunkType.DOC_BLOCK)
        chunk_dict = {"type": ChunkType.DOC_BLOCK}
        assert query._matches_simple_fields(chunk_dict) == True
        
        # Test non-matching type
        chunk_dict = {"type": ChunkType.CODE_BLOCK}
        assert query._matches_simple_fields(chunk_dict) == False
        
        # Test missing type in chunk
        chunk_dict = {}
        assert query._matches_simple_fields(chunk_dict) == False
    
    def test_matches_simple_fields_role_field(self):
        """Test _matches_simple_fields with role field (lines 1025-1026)."""
        # Test matching role
        query = ChunkQuery(role=ChunkRole.USER)
        chunk_dict = {"role": ChunkRole.USER}
        assert query._matches_simple_fields(chunk_dict) == True
        
        # Test non-matching role
        chunk_dict = {"role": ChunkRole.ASSISTANT}
        assert query._matches_simple_fields(chunk_dict) == False
        
        # Test missing role in chunk
        chunk_dict = {}
        assert query._matches_simple_fields(chunk_dict) == False
    
    def test_matches_simple_fields_status_field(self):
        """Test _matches_simple_fields with status field (lines 1027-1028)."""
        # Test matching status
        query = ChunkQuery(status=ChunkStatus.NEW)
        chunk_dict = {"status": ChunkStatus.NEW}
        assert query._matches_simple_fields(chunk_dict) == True
        
        # Test non-matching status
        chunk_dict = {"status": ChunkStatus.RAW}
        assert query._matches_simple_fields(chunk_dict) == False
        
        # Test missing status in chunk
        chunk_dict = {}
        assert query._matches_simple_fields(chunk_dict) == False
    
    def test_matches_simple_fields_language_field(self):
        """Test _matches_simple_fields with language field (lines 1029-1030)."""
        # Test matching language
        query = ChunkQuery(language=LanguageEnum.EN)
        chunk_dict = {"language": LanguageEnum.EN}
        assert query._matches_simple_fields(chunk_dict) == True
        
        # Test non-matching language
        chunk_dict = {"language": LanguageEnum.RU}
        assert query._matches_simple_fields(chunk_dict) == False
        
        # Test missing language in chunk
        chunk_dict = {}
        assert query._matches_simple_fields(chunk_dict) == False
    
    def test_matches_simple_fields_block_type_field(self):
        """Test _matches_simple_fields with block_type field (lines 1031-1032)."""
        # Test matching block_type
        query = ChunkQuery(block_type=BlockType.PARAGRAPH)
        chunk_dict = {"block_type": BlockType.PARAGRAPH}
        assert query._matches_simple_fields(chunk_dict) == True
        
        # Test non-matching block_type
        chunk_dict = {"block_type": BlockType.MESSAGE}
        assert query._matches_simple_fields(chunk_dict) == False
        
        # Test missing block_type in chunk
        chunk_dict = {}
        assert query._matches_simple_fields(chunk_dict) == False
    
    def test_matches_simple_fields_numeric_fields(self):
        """Test _matches_simple_fields with numeric fields."""
        # Test quality_score field (lines 1033-1034)
        query = ChunkQuery(quality_score=">=0.8")
        chunk_dict = {"quality_score": 0.9}
        # This will fail because simple fields don't handle operators
        assert query._matches_simple_fields(chunk_dict) == False
        
        # Test exact match
        query = ChunkQuery(quality_score=0.8)
        chunk_dict = {"quality_score": 0.8}
        assert query._matches_simple_fields(chunk_dict) == True
        
        # Test coverage field (lines 1035-1036)
        query = ChunkQuery(coverage=0.7)
        chunk_dict = {"coverage": 0.7}
        assert query._matches_simple_fields(chunk_dict) == True
        
        chunk_dict = {"coverage": 0.8}
        assert query._matches_simple_fields(chunk_dict) == False
        
        # Test cohesion field (lines 1037-1038)
        query = ChunkQuery(cohesion=0.6)
        chunk_dict = {"cohesion": 0.6}
        assert query._matches_simple_fields(chunk_dict) == True
        
        chunk_dict = {"cohesion": 0.7}
        assert query._matches_simple_fields(chunk_dict) == False
        
        # Test boundary_prev field (lines 1039-1040)
        query = ChunkQuery(boundary_prev=0.5)
        chunk_dict = {"boundary_prev": 0.5}
        assert query._matches_simple_fields(chunk_dict) == True
        
        chunk_dict = {"boundary_prev": 0.6}
        assert query._matches_simple_fields(chunk_dict) == False
    
    def test_matches_simple_fields_more_numeric_fields(self):
        """Test _matches_simple_fields with more numeric fields."""
        # Test boundary_next field
        query = ChunkQuery(boundary_next=0.4)
        chunk_dict = {"boundary_next": 0.4}
        assert query._matches_simple_fields(chunk_dict) == True
        
        # Test feedback_accepted field
        query = ChunkQuery(feedback_accepted=5)
        chunk_dict = {"feedback_accepted": 5}
        assert query._matches_simple_fields(chunk_dict) == True
        
        # Test feedback_rejected field
        query = ChunkQuery(feedback_rejected=2)
        chunk_dict = {"feedback_rejected": 2}
        assert query._matches_simple_fields(chunk_dict) == True
        
        # Test start field
        query = ChunkQuery(start=100)
        chunk_dict = {"start": 100}
        assert query._matches_simple_fields(chunk_dict) == True
        
        # Test end field
        query = ChunkQuery(end=200)
        chunk_dict = {"end": 200}
        assert query._matches_simple_fields(chunk_dict) == True
        
        # Test year field
        query = ChunkQuery(year=2024)
        chunk_dict = {"year": 2024}
        assert query._matches_simple_fields(chunk_dict) == True
        
        # Test ordinal field
        query = ChunkQuery(ordinal=1)
        chunk_dict = {"ordinal": 1}
        assert query._matches_simple_fields(chunk_dict) == True
        
        # Test source_lines_start field
        query = ChunkQuery(source_lines_start=10)
        chunk_dict = {"source_lines_start": 10}
        assert query._matches_simple_fields(chunk_dict) == True
        
        # Test source_lines_end field
        query = ChunkQuery(source_lines_end=20)
        chunk_dict = {"source_lines_end": 20}
        assert query._matches_simple_fields(chunk_dict) == True
        
        # Test block_index field
        query = ChunkQuery(block_index=5)
        chunk_dict = {"block_index": 5}
        assert query._matches_simple_fields(chunk_dict) == True
    
    def test_matches_simple_fields_boolean_fields(self):
        """Test _matches_simple_fields with boolean fields."""
        # Test is_deleted field
        query = ChunkQuery(is_deleted=False)
        chunk_dict = {"is_deleted": False}
        assert query._matches_simple_fields(chunk_dict) == True
        
        chunk_dict = {"is_deleted": True}
        assert query._matches_simple_fields(chunk_dict) == False
        
        # Test is_public field
        query = ChunkQuery(is_public=True)
        chunk_dict = {"is_public": True}
        assert query._matches_simple_fields(chunk_dict) == True
        
        chunk_dict = {"is_public": False}
        assert query._matches_simple_fields(chunk_dict) == False
        
        # Test used_in_generation field
        query = ChunkQuery(used_in_generation=True)
        chunk_dict = {"used_in_generation": True}
        assert query._matches_simple_fields(chunk_dict) == True
        
        chunk_dict = {"used_in_generation": False}
        assert query._matches_simple_fields(chunk_dict) == False
    
    def test_matches_simple_fields_list_fields(self):
        """Test _matches_simple_fields with list fields."""
        # Test tags field
        query = ChunkQuery(tags=["ai", "ml"])
        chunk_dict = {"tags": ["ai", "ml"]}
        assert query._matches_simple_fields(chunk_dict) == True
        
        chunk_dict = {"tags": ["python", "data"]}
        assert query._matches_simple_fields(chunk_dict) == False
        
        # Test links field
        query = ChunkQuery(links=["link1", "link2"])
        chunk_dict = {"links": ["link1", "link2"]}
        assert query._matches_simple_fields(chunk_dict) == True
        
        chunk_dict = {"links": ["link3", "link4"]}
        assert query._matches_simple_fields(chunk_dict) == False
    
    def test_matches_simple_fields_dict_fields(self):
        """Test _matches_simple_fields with dict fields."""
        # Test block_meta field
        query = ChunkQuery(block_meta={"key": "value"})
        chunk_dict = {"block_meta": {"key": "value"}}
        assert query._matches_simple_fields(chunk_dict) == True
        
        chunk_dict = {"block_meta": {"other": "data"}}
        assert query._matches_simple_fields(chunk_dict) == False
    
    def test_matches_simple_fields_string_fields(self):
        """Test _matches_simple_fields with string fields."""
        # Test tags_flat field
        query = ChunkQuery(tags_flat="ai,ml")
        chunk_dict = {"tags_flat": "ai,ml"}
        assert query._matches_simple_fields(chunk_dict) == True
        
        chunk_dict = {"tags_flat": "python,data"}
        assert query._matches_simple_fields(chunk_dict) == False
        
        # Test UUID fields
        uuid_val = "550e8400-e29b-41d4-a716-446655440000"
        
        # Test link_related field
        query = ChunkQuery(link_related=uuid_val)
        chunk_dict = {"link_related": uuid_val}
        assert query._matches_simple_fields(chunk_dict) == True
        
        chunk_dict = {"link_related": "other-uuid"}
        assert query._matches_simple_fields(chunk_dict) == False
        
        # Test link_parent field
        query = ChunkQuery(link_parent=uuid_val)
        chunk_dict = {"link_parent": uuid_val}
        assert query._matches_simple_fields(chunk_dict) == True
        
        chunk_dict = {"link_parent": "other-uuid"}
        assert query._matches_simple_fields(chunk_dict) == False
    
    def test_matches_simple_fields_multiple_fields(self):
        """Test _matches_simple_fields with multiple fields."""
        # Test multiple matching fields
        query = ChunkQuery(
            type=ChunkType.DOC_BLOCK,
            role=ChunkRole.USER,
            quality_score=0.8,
            is_public=True
        )
        
        chunk_dict = {
            "type": ChunkType.DOC_BLOCK,
            "role": ChunkRole.USER,
            "quality_score": 0.8,
            "is_public": True
        }
        assert query._matches_simple_fields(chunk_dict) == True
        
        # Test one non-matching field
        chunk_dict = {
            "type": ChunkType.DOC_BLOCK,
            "role": ChunkRole.USER,
            "quality_score": 0.8,
            "is_public": False  # Different value
        }
        assert query._matches_simple_fields(chunk_dict) == False
        
        # Test missing field
        chunk_dict = {
            "type": ChunkType.DOC_BLOCK,
            "role": ChunkRole.USER,
            "quality_score": 0.8
            # Missing is_public
        }
        assert query._matches_simple_fields(chunk_dict) == False
    
    def test_matches_simple_fields_none_values(self):
        """Test _matches_simple_fields with None values in query."""
        # Test query with all None values (should match anything)
        query = ChunkQuery()
        
        chunk_dict = {
            "type": ChunkType.DOC_BLOCK,
            "role": ChunkRole.USER,
            "quality_score": 0.8,
            "is_public": True
        }
        assert query._matches_simple_fields(chunk_dict) == True
        
        # Empty chunk dict should also match
        chunk_dict = {}
        assert query._matches_simple_fields(chunk_dict) == True
    
    def test_matches_field_value_with_operators(self):
        """Test _matches_field_value method with operators."""
        query = ChunkQuery()
        
        # Test numeric operators
        assert query._matches_field_value(25, ">=18", "age") == False  # Not implemented in simple matching
        assert query._matches_field_value(25, 25, "age") == True  # Exact match
        
        # Test with None query value (should match anything)
        assert query._matches_field_value(25, None, "age") == True
        
        # Test with None chunk value
        assert query._matches_field_value(None, 25, "age") == False
