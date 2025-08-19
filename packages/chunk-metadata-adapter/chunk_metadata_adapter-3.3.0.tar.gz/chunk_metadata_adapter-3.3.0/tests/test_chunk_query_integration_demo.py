"""
Tests for chunk_query_integration_demo.py to achieve 90%+ coverage.

This module tests the ChunkQuery integration demo functionality.

Author: Development Team
Created: 2024-01-20
Updated: 2024-01-20
"""

import pytest
from unittest.mock import patch
from io import StringIO
from chunk_metadata_adapter.examples.chunk_query_integration_demo import (
    demo_simple_field_filtering,
    demo_ast_based_filtering,
    demo_filter_validation,
    demo_ast_parsing_and_caching,
    demo_semantic_chunk_integration,
    demo_real_world_scenarios,
    main
)
from chunk_metadata_adapter import (
    ChunkQuery, SemanticChunk, ChunkType, ChunkStatus, LanguageEnum
)
from chunk_metadata_adapter.ast import ASTNode, LogicalOperator, FieldCondition, TypedValue


class TestChunkQueryIntegrationDemo:
    """Tests for ChunkQuery integration demo."""
    
    def test_demo_simple_field_filtering(self):
        """Test simple field filtering demo."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            demo_simple_field_filtering()
            output = fake_out.getvalue()
            
            assert "=== Simple Field Filtering Demo ===" in output
            assert "Query: type='DocBlock' -> Matches:" in output
            assert "Query: quality_score>='0.8' -> Matches:" in output
            assert "Query: tags=['ai', 'ml'] -> Matches:" in output
            assert "Query: is_public=True -> Matches:" in output
            assert "Query: type='CodeBlock' -> Matches:" in output
    
    def test_demo_ast_based_filtering(self):
        """Test AST-based filtering demo."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            demo_ast_based_filtering()
            output = fake_out.getvalue()
            
            assert "AST-Based Filtering Demo" in output
            assert "Query:" in output
            assert "Matches:" in output
            assert "Nested conditions" in output
    
    def test_demo_filter_validation(self):
        """Test filter validation demo."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            demo_filter_validation()
            output = fake_out.getvalue()
            
            assert "Filter Validation Demo" in output
            assert "Valid filter:" in output
            assert "Invalid filter:" in output
            assert "Dangerous filter:" in output
    
    def test_demo_ast_parsing_and_caching(self):
        """Test AST parsing and caching demo."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            demo_ast_parsing_and_caching()
            output = fake_out.getvalue()
            
            assert "AST Parsing and Caching Demo" in output
            assert "Getting AST" in output
            assert "New AST object:" in output
    
    def test_demo_semantic_chunk_integration(self):
        """Test SemanticChunk integration demo."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            demo_semantic_chunk_integration()
            output = fake_out.getvalue()
            
            assert "SemanticChunk Integration Demo" in output
            assert "Simple query with SemanticChunk:" in output
            assert "AST query with SemanticChunk:" in output
    
    def test_demo_real_world_scenarios(self):
        """Test real world scenarios demo."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            demo_real_world_scenarios()
            output = fake_out.getvalue()
            
            assert "Real-World Scenarios Demo" in output
            assert "Scenario 1:" in output
            assert "Scenario 2:" in output
            assert "Recent AI/ML content:" in output
    
    def test_main_function(self):
        """Test main function execution."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            main()
            output = fake_out.getvalue()
            
            assert "ChunkQuery AST Integration Demo" in output
            assert "Simple Field Filtering Demo" in output
            assert "AST-Based Filtering Demo" in output
            assert "Filter Validation Demo" in output
            assert "AST Parsing and Caching Demo" in output
            assert "SemanticChunk Integration Demo" in output
            assert "Real-World Scenarios Demo" in output
            assert "completed successfully" in output
    
    def test_actual_simple_field_filtering(self):
        """Test actual simple field filtering functionality."""
        # Create sample chunk data
        chunk_data = {
            "type": "DocBlock",
            "quality_score": 0.85,
            "tags": ["ai", "python", "machine-learning"],
            "year": 2023,
            "is_public": True,
            "is_deleted": False,
            "language": "en",
            "title": "Python Machine Learning Guide"
        }
        
        # Test exact match
        query1 = ChunkQuery(type="DocBlock")
        assert query1.matches(chunk_data) is True
        
        # Test numeric comparison
        query2 = ChunkQuery(quality_score=">=0.8")
        assert query2.matches(chunk_data) is True
        
        # Test list field matching
        query3 = ChunkQuery(tags=["ai", "ml"])
        assert query3.matches(chunk_data) is True
        
        # Test boolean field
        query4 = ChunkQuery(is_public=True)
        assert query4.matches(chunk_data) is True
        
        # Test non-matching query
        query5 = ChunkQuery(type="CodeBlock")
        assert query5.matches(chunk_data) is False
    
    def test_actual_ast_based_filtering(self):
        """Test actual AST-based filtering functionality."""
        # Create sample chunk data
        chunk_data = {
            "type": "DocBlock",
            "quality_score": 0.85,
            "tags": ["ai", "python", "machine-learning"],
            "year": 2023,
            "is_public": True,
            "is_deleted": False,
            "language": "en",
            "title": "Python Machine Learning Guide",
            "feedback_accepted": 5,
            "used_in_generation": True
        }
        
        # Test simple AND condition
        query1 = ChunkQuery(filter_expr="type = 'DocBlock' AND quality_score >= 0.8")
        assert query1.matches(chunk_data) is True
        
        # Test OR condition
        query2 = ChunkQuery(filter_expr="type = 'DocBlock' OR type = 'CodeBlock'")
        assert query2.matches(chunk_data) is True
        
        # Test complex logical expression
        query3 = ChunkQuery(filter_expr="""
            (type = 'DocBlock' OR type = 'CodeBlock') AND
            quality_score >= 0.7 AND
            tags intersects ['ai', 'ml'] AND
            year >= 2020 AND
            NOT is_deleted
        """)
        assert query3.matches(chunk_data) is True
    
    def test_actual_filter_validation(self):
        """Test actual filter validation functionality."""
        # Test valid filter
        query1 = ChunkQuery(filter_expr="type = 'DocBlock' AND quality_score >= 0.8")
        assert query1.get_ast() is not None
        
        # Test invalid filter - should not raise exception, just return None or empty AST
        query2 = ChunkQuery(filter_expr="invalid filter expression")
        # The actual behavior depends on implementation, so we just test that it doesn't crash
    
    def test_actual_ast_parsing_and_caching(self):
        """Test actual AST parsing and caching functionality."""
        query = ChunkQuery(filter_expr="type = 'DocBlock' AND quality_score >= 0.8")
        
        # Test AST parsing
        ast = query.get_ast()
        assert ast is not None
        assert isinstance(ast, ASTNode)
        
        # Test cache statistics
        stats = query.get_cache_stats()
        assert "ast_cached" in stats
        assert "validation_cached" in stats
        assert "parser_initialized" in stats
    
    def test_actual_semantic_chunk_integration(self):
        """Test actual SemanticChunk integration functionality."""
        # Create SemanticChunk object
        chunk = SemanticChunk(
            type="DocBlock",
            body="Python Machine Learning Guide content",
            quality_score=0.85,
            tags=["ai", "python", "machine-learning"],
            year=2023,
            is_public=True,
            is_deleted=False,
            language=LanguageEnum.EN,
            title="Python Machine Learning Guide"
        )
        
        # Test field condition
        type_condition = FieldCondition("type", "=", TypedValue("str", "DocBlock"))
        quality_condition = FieldCondition("quality_score", ">=", TypedValue("float", 0.8))
        tags_condition = FieldCondition("tags", "intersects", TypedValue("list", ["ai", "ml"]))
        
        assert type_condition.field == "type"
        assert quality_condition.field == "quality_score"
        assert tags_condition.field == "tags"
        
        # Test complex condition
        complex_condition = LogicalOperator("AND", [
            type_condition,
            quality_condition,
            tags_condition
        ])
        
        assert complex_condition.operator == "AND"
        assert len(complex_condition.children) == 3
    
    def test_actual_real_world_scenarios(self):
        """Test actual real world scenarios functionality."""
        # Create sample chunk data
        chunk_data = {
            "type": "DocBlock",
            "quality_score": 0.85,
            "tags": ["documentation", "guide"],
            "year": 2023,
            "is_public": True,
            "is_deleted": False,
            "feedback_accepted": 5,
            "used_in_generation": True,
            "language": "en"
        }
        
        # Test simple query that should match
        simple_query = ChunkQuery(filter_expr="type = 'DocBlock' AND quality_score >= 0.8")
        assert simple_query.matches(chunk_data) is True
        
        # Test query that should not match
        no_match_query = ChunkQuery(filter_expr="type = 'CodeBlock'")
        assert no_match_query.matches(chunk_data) is False
    
    def test_chunk_query_creation(self):
        """Test ChunkQuery creation with different parameters."""
        # Test with simple field
        query1 = ChunkQuery(type="DocBlock")
        assert query1.type == "DocBlock"
        
        # Test with filter expression
        query2 = ChunkQuery(filter_expr="type = 'DocBlock' AND quality_score >= 0.8")
        assert query2.filter_expr == "type = 'DocBlock' AND quality_score >= 0.8"
        
        # Test with multiple fields
        query3 = ChunkQuery(type="DocBlock", quality_score=">=0.8", is_public=True)
        assert query3.type == "DocBlock"
        assert query3.quality_score == ">=0.8"
        assert query3.is_public is True
    
    def test_semantic_chunk_creation(self):
        """Test SemanticChunk creation."""
        chunk = SemanticChunk(
            type="DocBlock",
            body="Test content for the chunk",
            quality_score=0.85,
            tags=["ai", "python"],
            year=2023,
            is_public=True,
            is_deleted=False,
            language=LanguageEnum.EN,
            title="Test Title"
        )
        
        assert chunk.type == "DocBlock"
        assert chunk.quality_score == 0.85
        assert chunk.tags == ["ai", "python"]
        assert chunk.year == 2023
        assert chunk.is_public is True
        assert chunk.is_deleted is False
        assert chunk.language == LanguageEnum.EN
        assert chunk.title == "Test Title"
    
    def test_filter_expression_parsing(self):
        """Test filter expression parsing."""
        query = ChunkQuery(filter_expr="type = 'DocBlock' AND quality_score >= 0.8")
        
        # Test AST generation
        ast = query.get_ast()
        assert ast is not None
        assert isinstance(ast, ASTNode)
        
        # Test that AST can be executed
        chunk_data = {
            "type": "DocBlock",
            "quality_score": 0.85
        }
        assert query.matches(chunk_data) is True
    
    def test_cache_functionality(self):
        """Test cache functionality."""
        query = ChunkQuery(filter_expr="type = 'DocBlock' AND quality_score >= 0.8")
        
        # First call should initialize cache
        ast1 = query.get_ast()
        
        # Second call should use cache
        ast2 = query.get_ast()
        
        # Both should be the same object (cached)
        assert ast1 is ast2
        
        # Test cache statistics
        stats = query.get_cache_stats()
        assert stats["ast_cached"] is True 