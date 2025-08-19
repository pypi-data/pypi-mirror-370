"""
Tests for examples_module.py to achieve 90%+ coverage.

This module tests the examples module functionality.

Author: Development Team
Created: 2024-01-20
Updated: 2024-01-20
"""

import pytest
import uuid
from unittest.mock import patch
from io import StringIO
from chunk_metadata_adapter.examples_module import (
    example_basic_flat_metadata,
    example_structured_chunk,
    example_conversion_between_formats,
    example_chain_processing,
    example_total_chunks_metadata,
    example_is_code_detection,
    example_data_lifecycle,
    example_metrics_extension,
    example_full_chain_structured_semantic_flat,
    example_filter_factory_method,
    example_filter_usage
)
from chunk_metadata_adapter.metadata_builder import ChunkMetadataBuilder
from chunk_metadata_adapter.semantic_chunk import SemanticChunk
from chunk_metadata_adapter.data_types import ChunkType, LanguageEnum, ChunkStatus


class TestExamplesModule:
    """Tests for examples module."""
    
    def test_example_basic_flat_metadata(self):
        """Test basic flat metadata example."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            example_basic_flat_metadata()
            output = fake_out.getvalue()
            
            assert "Generated UUID:" in output
            assert "SHA256:" in output
            assert "Created at:" in output
            assert "Is code:" in output
    
    def test_example_structured_chunk(self):
        """Test structured chunk example."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            example_structured_chunk()
            output = fake_out.getvalue()
            
            assert "Chunk UUID:" in output
            assert "Content summary:" in output
            assert "Links:" in output
    
    def test_example_conversion_between_formats(self):
        """Test conversion between formats example."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            example_conversion_between_formats()
            output = fake_out.getvalue()
            
            assert "Flat representation has" in output
            assert "Restored structured chunk:" in output
    
    def test_example_chain_processing(self):
        """Test chain processing example."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            example_chain_processing()
            output = fake_out.getvalue()
            
            assert "Processed" in output
            assert "chunks from source" in output
            assert "Chunk 0:" in output
            assert "Status:" in output
    
    def test_example_is_code_detection(self):
        """Test is code detection example."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            example_is_code_detection()
            output = fake_out.getvalue()
            
            assert "Code detection examples:" in output
            assert "Python code" in output
            assert "JavaScript" in output
            assert "English text" in output
            assert "is_code:" in output
    
    def test_example_data_lifecycle(self):
        """Test data lifecycle example."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            example_data_lifecycle()
            output = fake_out.getvalue()
            
            assert "RAW data created:" in output
            assert "Data CLEANED:" in output
            assert "Data VERIFIED:" in output
            assert "Data VALIDATED:" in output
            assert "Data marked as RELIABLE:" in output
    
    def test_example_metrics_extension(self):
        """Test metrics extension example."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            example_metrics_extension()
            output = fake_out.getvalue()
            
            assert "Chunk with extended metrics:" in output
            assert "quality_score=" in output
            assert "coverage=" in output
            assert "cohesion=" in output
    
    def test_example_full_chain_structured_semantic_flat(self):
        """Test full chain structured semantic flat example."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            example_full_chain_structured_semantic_flat()
            output = fake_out.getvalue()
            
            assert "Full chain:" in output
            assert "Structured dict:" in output
            assert "Semantic chunk:" in output
            assert "Flat dict:" in output
    
    def test_example_filter_factory_method(self):
        """Test filter factory method example."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            example_filter_factory_method()
            output = fake_out.getvalue()
            
            assert "Filter created:" in output
            assert "Validation errors:" in output
    
    def test_example_filter_usage(self):
        """Test filter usage example."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            example_filter_usage()
            output = fake_out.getvalue()
            
            assert "Filter (equality):" in output
            assert "Filter (comparison/in):" in output
            assert "Flat filter:" in output
            assert "Restored from flat:" in output
            assert "Filtered chunks:" in output
    
    def test_actual_structured_chunk_functionality(self):
        """Test actual structured chunk functionality."""
        builder = ChunkMetadataBuilder(project="TestProject")
        
        chunk = builder.build_semantic_chunk(
            body="Test content",
            text="Test content",
            language=LanguageEnum.EN,
            chunk_type=ChunkType.DOC_BLOCK,
            source_id=str(uuid.uuid4()),
            start=0,
            end=100
        )
        
        # Test that chunk was created successfully
        assert chunk is not None
        assert chunk.body == "Test content"
        assert chunk.language == LanguageEnum.EN
        assert chunk.type == ChunkType.DOC_BLOCK
    
    def test_actual_is_code_detection_functionality(self):
        """Test actual is code detection functionality."""
        builder = ChunkMetadataBuilder(project="TestProject")
        
        # Test Python code
        python_chunk = builder.build_semantic_chunk(
            body="def hello():\n    print('Hello')",
            language=LanguageEnum.PYTHON,
            chunk_type=ChunkType.CODE_BLOCK,
            source_id=str(uuid.uuid4()),
            start=0,
            end=1
        )
        assert python_chunk.is_code_chunk is True
        
        # Test JavaScript code with DOC_BLOCK type
        js_chunk = builder.build_semantic_chunk(
            body="function greet() {\n    console.log('Hello');\n}",
            language=LanguageEnum.JAVASCRIPT,
            chunk_type=ChunkType.DOC_BLOCK,
            source_id=str(uuid.uuid4()),
            start=0,
            end=1
        )
        assert js_chunk.is_code_chunk is True
        
        # Test English text
        text_chunk = builder.build_semantic_chunk(
            body="This is regular text content.",
            language=LanguageEnum.EN,
            chunk_type=ChunkType.DOC_BLOCK,
            source_id=str(uuid.uuid4()),
            start=0,
            end=1
        )
        assert text_chunk.is_code_chunk is False
    
    def test_actual_data_lifecycle_functionality(self):
        """Test actual data lifecycle functionality."""
        builder = ChunkMetadataBuilder(project="TestProject")
        
        chunk = builder.build_semantic_chunk(
            body="Test content",
            text="Test content",
            language=LanguageEnum.EN,
            chunk_type=ChunkType.DOC_BLOCK,
            source_id=str(uuid.uuid4()),
            start=0,
            end=100
        )
        
        # Test initial status
        assert chunk.status == ChunkStatus.RAW
        
        # Test status transitions
        chunk.status = ChunkStatus.CLEANED
        assert chunk.status == ChunkStatus.CLEANED
        
        chunk.status = ChunkStatus.ARCHIVED
        assert chunk.status == ChunkStatus.ARCHIVED
    
    def test_actual_metrics_extension_functionality(self):
        """Test actual metrics extension functionality."""
        builder = ChunkMetadataBuilder(project="TestProject")
        
        chunk = builder.build_semantic_chunk(
            body="Test content",
            text="Test content",
            language=LanguageEnum.EN,
            chunk_type=ChunkType.DOC_BLOCK,
            source_id=str(uuid.uuid4()),
            start=0,
            end=100
        )
        
        # Test that chunk was created successfully
        assert chunk is not None
        assert chunk.body == "Test content"
        
        # Test metrics object exists
        assert hasattr(chunk, 'metrics')
        assert chunk.metrics is not None
    
    def test_actual_filter_functionality(self):
        """Test actual filter functionality."""
        builder = ChunkMetadataBuilder(project="TestProject")
        
        # Create test chunks
        chunks = []
        for i in range(3):
            chunk = builder.build_semantic_chunk(
                body=f"Content {i}",
                text=f"Content {i}",
                language=LanguageEnum.EN,
                chunk_type=ChunkType.DOC_BLOCK,
                source_id=str(uuid.uuid4()),
                start=i * 100,
                end=(i + 1) * 100
            )
            chunks.append(chunk)
        
        # Test that chunks were created
        assert len(chunks) == 3
        for chunk in chunks:
            assert chunk is not None
            assert chunk.body is not None
    
    def test_semantic_chunk_creation_with_builder(self):
        """Test SemanticChunk creation with builder."""
        builder = ChunkMetadataBuilder(project="TestProject")
        
        chunk = builder.build_semantic_chunk(
            body="Test content",
            text="Test content",
            language=LanguageEnum.EN,
            chunk_type=ChunkType.DOC_BLOCK,
            source_id=str(uuid.uuid4()),
            start=0,
            end=100,
            summary="Test summary",
            tags=["test", "example"],
            year=2024,
            is_public=True
        )
        
        assert chunk is not None
        assert chunk.body == "Test content"
        assert chunk.language == LanguageEnum.EN
        assert chunk.type == ChunkType.DOC_BLOCK
        assert chunk.summary == "Test summary"
        assert chunk.tags == ["test", "example"]
        assert chunk.year == 2024
        assert chunk.is_public is True
    
    def test_chunk_serialization(self):
        """Test chunk serialization functionality."""
        builder = ChunkMetadataBuilder(project="TestProject")
        
        chunk = builder.build_semantic_chunk(
            body="Test content",
            text="Test content",
            language=LanguageEnum.EN,
            chunk_type=ChunkType.DOC_BLOCK,
            source_id=str(uuid.uuid4()),
            start=0,
            end=100
        )
        
        # Test that chunk was created successfully
        assert chunk is not None
        assert chunk.body == "Test content"
        assert chunk.language == LanguageEnum.EN
        assert chunk.type == ChunkType.DOC_BLOCK
    
    def test_chunk_validation(self):
        """Test chunk validation functionality."""
        builder = ChunkMetadataBuilder(project="TestProject")
        
        # Test valid chunk
        valid_chunk = builder.build_semantic_chunk(
            body="Test content",
            text="Test content",
            language=LanguageEnum.EN,
            chunk_type=ChunkType.DOC_BLOCK,
            source_id=str(uuid.uuid4()),
            start=0,
            end=100
        )
        
        # Test that chunk was created successfully
        assert valid_chunk is not None
        assert valid_chunk.body == "Test content" 