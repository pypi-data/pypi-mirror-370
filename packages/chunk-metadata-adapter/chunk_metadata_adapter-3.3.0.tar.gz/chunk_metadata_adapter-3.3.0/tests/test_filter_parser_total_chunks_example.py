"""
Tests for filter_parser_total_chunks_example.py to achieve 90%+ coverage.

This module tests the filter parser total chunks example functionality.

Author: Development Team
Created: 2024-01-20
Updated: 2024-01-20
"""

import pytest
import uuid
from unittest.mock import patch
from io import StringIO
from chunk_metadata_adapter.examples.filter_parser_total_chunks_example import (
    example_filter_parser_with_total_chunks,
    example_nested_field_access
)
from chunk_metadata_adapter.filter_parser import FilterParser
from chunk_metadata_adapter.filter_executor import FilterExecutor
from chunk_metadata_adapter.semantic_chunk import SemanticChunk, ChunkStatus
from chunk_metadata_adapter.ast import TypedValue


class TestFilterParserTotalChunksExample:
    """Tests for filter parser total chunks example."""
    
    def test_example_filter_parser_with_total_chunks(self):
        """Test filter parser with total chunks example."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            example_filter_parser_with_total_chunks()
            output = fake_out.getvalue()
            
            assert "=== Filter Parser with Total Chunks Example ===" in output
            assert "Created" in output
            assert "chunks with total_chunks_in_source=" in output
            assert "=== Testing Query Parsing ===" in output
            assert "Parsed:" in output
            assert "AST Type:" in output
            assert "Matches:" in output
            assert "Positions:" in output
    
    def test_example_nested_field_access(self):
        """Test nested field access example."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            example_nested_field_access()
            output = fake_out.getvalue()
            
            assert "Nested Field Access Example" in output
            assert "1. ✅" in output
            assert "Result:" in output
    
    def test_actual_filter_parser_functionality(self):
        """Test actual filter parser functionality."""
        parser = FilterParser()
        executor = FilterExecutor()
        
        # Test basic total chunks query
        query = "block_meta.total_chunks_in_source = 5"
        ast = parser.parse(query)
        
        assert ast is not None
        assert hasattr(ast, 'field')
        assert ast.field == "block_meta.total_chunks_in_source"
        assert ast.operator == "="
        assert ast.value.type == "int"
        assert ast.value.value == 5
    
    def test_actual_chunk_creation(self):
        """Test actual chunk creation functionality."""
        total_chunks = 5
        chunks = []
        
        for i in range(total_chunks):
            chunk = SemanticChunk(
                uuid=str(uuid.uuid4()),
                body=f"Content of chunk {i+1}",
                type="DocBlock",
                content=f"Content of chunk {i+1}",
                quality_score=0.8 + (i * 0.02),
                tags=["example", "metadata"],
                year=2024,
                ordinal=i,
                block_meta={
                    "total_chunks_in_source": total_chunks,
                    "is_last_chunk": (i == total_chunks - 1),
                    "is_first_chunk": (i == 0),
                    "chunk_position": f"{i+1}/{total_chunks}",
                    "chunk_percentage": (i / (total_chunks - 1)) * 100 if total_chunks > 1 else 0
                }
            )
            chunks.append(chunk)
        
        assert len(chunks) == total_chunks
        
        # Test chunk properties
        for i, chunk in enumerate(chunks):
            assert chunk.block_meta["total_chunks_in_source"] == total_chunks
            assert chunk.ordinal == i
            assert chunk.block_meta["chunk_position"] == f"{i+1}/{total_chunks}"
            
            if i == 0:
                assert chunk.block_meta["is_first_chunk"] is True
                assert chunk.block_meta["is_last_chunk"] is False
            elif i == total_chunks - 1:
                assert chunk.block_meta["is_first_chunk"] is False
                assert chunk.block_meta["is_last_chunk"] is True
    
    def test_actual_query_execution(self):
        """Test actual query execution functionality."""
        parser = FilterParser()
        executor = FilterExecutor()
        
        # Create test chunk
        chunk = SemanticChunk(
            uuid=str(uuid.uuid4()),
            body="Test content",
            type="DocBlock",
            content="Test content",
            quality_score=0.85,
            tags=["test"],
            year=2024,
            ordinal=0,
            block_meta={
                "total_chunks_in_source": 5,
                "is_last_chunk": False,
                "is_first_chunk": True,
                "chunk_position": "1/5",
                "chunk_percentage": 0.0
            }
        )
        
        # Test total chunks query
        query1 = "block_meta.total_chunks_in_source = 5"
        ast1 = parser.parse(query1)
        result1 = executor.execute(ast1, chunk)
        assert result1 is True
        
        # Test first chunk query
        query2 = "block_meta.is_first_chunk = true"
        ast2 = parser.parse(query2)
        result2 = executor.execute(ast2, chunk)
        assert result2 is True
        
        # Test last chunk query (should be false)
        query3 = "block_meta.is_last_chunk = true"
        ast3 = parser.parse(query3)
        result3 = executor.execute(ast3, chunk)
        assert result3 is False
    
    def test_actual_nested_field_access(self):
        """Test actual nested field access functionality."""
        parser = FilterParser()
        executor = FilterExecutor()
        
        # Create test chunk
        chunk = SemanticChunk(
            uuid=str(uuid.uuid4()),
            body="Test content",
            type="DocBlock",
            content="Test content",
            quality_score=0.85,
            tags=["test"],
            year=2024,
            ordinal=0,
            block_meta={
                "total_chunks_in_source": 5,
                "chunk_position": "1/5",
                "nested": {
                    "deep": {
                        "value": 42
                    }
                }
            }
        )
        
        # Test nested field access
        query = "block_meta.nested.deep.value = 42"
        ast = parser.parse(query)
        result = executor.execute(ast, chunk)
        assert result is True
        
        # Test non-matching nested field
        query2 = "block_meta.nested.deep.value = 100"
        ast2 = parser.parse(query2)
        result2 = executor.execute(ast2, chunk)
        assert result2 is False
    
    def test_actual_complex_queries(self):
        """Test actual complex queries functionality."""
        parser = FilterParser()
        executor = FilterExecutor()
        
        # Create test chunk
        chunk = SemanticChunk(
            uuid=str(uuid.uuid4()),
            body="Test content",
            type="DocBlock",
            content="Test content",
            quality_score=0.85,
            tags=["test"],
            year=2024,
            ordinal=0,
            block_meta={
                "total_chunks_in_source": 5,
                "is_first_chunk": True,
                "chunk_percentage": 0.0
            }
        )
        
        # Test complex AND query
        query1 = "block_meta.total_chunks_in_source >= 5 AND block_meta.is_first_chunk = true"
        ast1 = parser.parse(query1)
        result1 = executor.execute(ast1, chunk)
        assert result1 is True
        
        # Test complex OR query
        query2 = "quality_score >= 0.8 OR block_meta.chunk_percentage > 50"
        ast2 = parser.parse(query2)
        result2 = executor.execute(ast2, chunk)
        assert result2 is True
        
        # Test complex mixed query
        query3 = "type = 'DocBlock' AND block_meta.is_first_chunk = true AND year = 2024"
        ast3 = parser.parse(query3)
        result3 = executor.execute(ast3, chunk)
        assert result3 is True
    
    def test_actual_percentage_queries(self):
        """Test actual percentage queries functionality."""
        parser = FilterParser()
        executor = FilterExecutor()
        
        # Create test chunks with different percentages
        chunks = []
        for i in range(5):
            chunk = SemanticChunk(
                uuid=str(uuid.uuid4()),
                body=f"Content {i}",
                type="DocBlock",
                content=f"Content {i}",
                quality_score=0.8,
                tags=["test"],
                year=2024,
                ordinal=i,
                block_meta={
                    "total_chunks_in_source": 5,
                    "chunk_percentage": (i / 4) * 100
                }
            )
            chunks.append(chunk)
        
        # Test percentage > 50
        query = "block_meta.chunk_percentage > 50"
        ast = parser.parse(query)
        
        matching_chunks = [chunk for chunk in chunks if executor.execute(ast, chunk)]
        assert len(matching_chunks) == 2  # Chunks with 75% and 100%
        
        # Test percentage <= 25
        query2 = "block_meta.chunk_percentage <= 25"
        ast2 = parser.parse(query2)
        
        matching_chunks2 = [chunk for chunk in chunks if executor.execute(ast2, chunk)]
        assert len(matching_chunks2) == 2  # Chunks with 0% and 25%
    
    def test_actual_position_queries(self):
        """Test actual position queries functionality."""
        parser = FilterParser()
        executor = FilterExecutor()
        
        # Create test chunk
        chunk = SemanticChunk(
            uuid=str(uuid.uuid4()),
            body="Test content",
            type="DocBlock",
            content="Test content",
            quality_score=0.85,
            tags=["test"],
            year=2024,
            ordinal=0,
            block_meta={
                "total_chunks_in_source": 5,
                "chunk_position": "1/5"
            }
        )
        
        # Test position query
        query = "block_meta.chunk_position = '1/5'"
        ast = parser.parse(query)
        result = executor.execute(ast, chunk)
        assert result is True
        
        # Test non-matching position
        query2 = "block_meta.chunk_position = '3/5'"
        ast2 = parser.parse(query2)
        result2 = executor.execute(ast2, chunk)
        assert result2 is False
    
    def test_actual_ordinal_queries(self):
        """Test actual ordinal queries functionality."""
        parser = FilterParser()
        executor = FilterExecutor()
        
        # Create test chunk
        chunk = SemanticChunk(
            uuid=str(uuid.uuid4()),
            body="Test content",
            type="DocBlock",
            content="Test content",
            quality_score=0.85,
            tags=["test"],
            year=2024,
            ordinal=0,
            block_meta={
                "total_chunks_in_source": 5,
                "is_first_chunk": True
            }
        )
        
        # Test ordinal query
        query = "ordinal = 0 AND block_meta.is_first_chunk = true"
        ast = parser.parse(query)
        result = executor.execute(ast, chunk)
        assert result is True
        
        # Test non-matching ordinal
        query2 = "ordinal = 2 AND block_meta.is_first_chunk = true"
        ast2 = parser.parse(query2)
        result2 = executor.execute(ast2, chunk)
        assert result2 is False
    
    def test_filter_parser_creation(self):
        """Test FilterParser creation."""
        parser = FilterParser()
        assert parser is not None
        assert isinstance(parser, FilterParser)
    
    def test_filter_executor_creation(self):
        """Test FilterExecutor creation."""
        executor = FilterExecutor()
        assert executor is not None
        assert isinstance(executor, FilterExecutor)
    
    def test_semantic_chunk_creation(self):
        """Test SemanticChunk creation."""
        chunk = SemanticChunk(
            uuid=str(uuid.uuid4()),
            body="Test content",
            type="DocBlock",
            content="Test content",
            quality_score=0.85,
            tags=["test"],
            year=2024,
            ordinal=0,
            block_meta={
                "total_chunks_in_source": 5,
                "is_first_chunk": True
            }
        )
        
        assert chunk.uuid is not None
        assert chunk.body == "Test content"
        assert chunk.type == "DocBlock"
        assert chunk.quality_score == 0.85
        assert chunk.tags == ["test"]
        assert chunk.year == 2024
        assert chunk.ordinal == 0
        assert chunk.block_meta["total_chunks_in_source"] == 5
        assert chunk.block_meta["is_first_chunk"] is True
    
    def test_typed_value_creation(self):
        """Test TypedValue creation."""
        int_value = TypedValue("int", 5)
        str_value = TypedValue("str", "true")
        float_value = TypedValue("float", 50.0)
        bool_value = TypedValue("bool", True)
        
        assert int_value.type == "int"
        assert int_value.value == 5
        assert str_value.type == "str"
        assert str_value.value == "true"
        assert float_value.type == "float"
        assert float_value.value == 50.0
        assert bool_value.type == "bool"
        assert bool_value.value is True 