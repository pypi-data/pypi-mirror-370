"""
Tests for BM25 examples coverage.

This module tests the BM25 examples modules to achieve 90%+ coverage
by testing all functions and functionality.
"""

import pytest
from unittest.mock import patch, MagicMock
from chunk_metadata_adapter.examples import bm25_search_examples, bm25_usage_examples
from chunk_metadata_adapter import ChunkQuery, SemanticChunk
from chunk_metadata_adapter.data_types import ChunkType, LanguageEnum


class TestBM25SearchExamplesCoverage:
    """Tests for bm25_search_examples module coverage."""
    
    def test_basic_bm25_search_example(self):
        """Test basic_bm25_search_example function."""
        with patch('builtins.print') as mock_print:
            bm25_search_examples.basic_bm25_search_example()
            
            # Verify that print was called multiple times
            assert mock_print.call_count > 0
            
            # Check that the function executed without errors
            calls = [str(call) for call in mock_print.call_args_list]
            assert any("Basic BM25 Search Example" in call for call in calls)
            assert any("Search query:" in call for call in calls)
            assert any("Search fields:" in call for call in calls)
    
    def test_hybrid_search_example(self):
        """Test hybrid_search_example function."""
        with patch('builtins.print') as mock_print:
            bm25_search_examples.hybrid_search_example()
            
            # Verify that print was called multiple times
            assert mock_print.call_count > 0
            
            # Check that the function executed without errors
            calls = [str(call) for call in mock_print.call_args_list]
            assert any("Hybrid Search Example" in call for call in calls)
            assert any("Hybrid search:" in call for call in calls)
            assert any("BM25 weight:" in call for call in calls)
    
    def test_bm25_with_metadata_filters_example(self):
        """Test bm25_with_metadata_filters_example function."""
        with patch('builtins.print') as mock_print:
            bm25_search_examples.bm25_with_metadata_filters_example()
            
            # Verify that print was called multiple times
            assert mock_print.call_count > 0
            
            # Check that the function executed without errors
            calls = [str(call) for call in mock_print.call_args_list]
            assert any("BM25 with Metadata Filters" in call for call in calls)
    
    def test_complex_filter_expressions_with_bm25_example(self):
        """Test complex_filter_expression_with_bm25_example function."""
        with patch('builtins.print') as mock_print:
            bm25_search_examples.complex_filter_expression_with_bm25_example()
            
            # Verify that print was called multiple times
            assert mock_print.call_count > 0
            
            # Check that the function executed without errors
            calls = [str(call) for call in mock_print.call_args_list]
            assert any("Complex Filter Expression" in call for call in calls)
    
    def test_bm25_parameter_tuning_example(self):
        """Test bm25_parameter_tuning_example function."""
        with patch('builtins.print') as mock_print:
            bm25_search_examples.bm25_parameter_tuning_example()
            
            # Verify that print was called multiple times
            assert mock_print.call_count > 0
            
            # Check that the function executed without errors
            calls = [str(call) for call in mock_print.call_args_list]
            assert any("BM25 Parameter Tuning" in call for call in calls)
    
    def test_search_field_selection_example(self):
        """Test search_field_selection_example function."""
        with patch('builtins.print') as mock_print:
            bm25_search_examples.search_field_selection_example()
            
            # Verify that print was called multiple times
            assert mock_print.call_count > 0
            
            # Check that the function executed without errors
            calls = [str(call) for call in mock_print.call_args_list]
            assert any("Search Field Selection" in call for call in calls)
    
    def test_result_ranking_example(self):
        """Test result_ranking_example function."""
        with patch('builtins.print') as mock_print:
            bm25_search_examples.result_ranking_example()
            
            # Verify that print was called multiple times
            assert mock_print.call_count > 0
            
            # Check that the function executed without errors
            calls = [str(call) for call in mock_print.call_args_list]
            assert any("Result Ranking" in call for call in calls)
    
    def test_validation_examples(self):
        """Test validation_examples function."""
        with patch('builtins.print') as mock_print:
            bm25_search_examples.validation_examples()
            
            # Verify that print was called multiple times
            assert mock_print.call_count > 0
            
            # Check that the function executed without errors
            calls = [str(call) for call in mock_print.call_args_list]
            assert any("Validation Examples" in call for call in calls)
    
    def test_all_examples_function(self):
        """Test main function."""
        with patch('builtins.print') as mock_print:
            bm25_search_examples.main()
            
            # Verify that print was called multiple times
            assert mock_print.call_count > 0
            
            # Check that the function executed without errors
            calls = [str(call) for call in mock_print.call_args_list]
            assert any("BM25 Search Examples" in call for call in calls)
    
    def test_example_query_creation(self):
        """Test that examples create valid queries."""
        # Test basic BM25 query creation
        query = ChunkQuery(
            search_query="python machine learning",
            search_fields=["body", "text", "summary", "title"],
            bm25_k1=1.2,
            bm25_b=0.75,
            max_results=50
        )
        
        assert query.search_query == "python machine learning"
        assert query.search_fields == ["body", "text", "summary", "title"]
        assert query.bm25_k1 == 1.2
        assert query.bm25_b == 0.75
        assert query.max_results == 50
        
        # Test hybrid query creation
        hybrid_query = ChunkQuery(
            search_query="artificial intelligence neural networks",
            search_fields=["body", "text", "summary"],
            hybrid_search=True,
            bm25_weight=0.3,
            semantic_weight=0.7,
            bm25_k1=1.5,
            bm25_b=0.8,
            min_score=0.6,
            max_results=100
        )
        
        assert hybrid_query.hybrid_search == True
        assert hybrid_query.bm25_weight == 0.3
        assert hybrid_query.semantic_weight == 0.7
        assert hybrid_query.min_score == 0.6
    
    def test_example_validation(self):
        """Test that examples create valid queries."""
        # Test basic query validation
        query = ChunkQuery(
            search_query="python machine learning",
            search_fields=["body", "text", "summary", "title"]
        )
        
        validation = query.validate_bm25_parameters()
        assert validation.is_valid == True
        
        # Test hybrid query validation
        hybrid_query = ChunkQuery(
            search_query="test",
            hybrid_search=True,
            bm25_weight=0.6,
            semantic_weight=0.4
        )
        
        validation = hybrid_query.validate_bm25_parameters()
        assert validation.is_valid == True
    
    def test_example_api_request_creation(self):
        """Test that examples can create API requests."""
        query = ChunkQuery(
            search_query="python machine learning",
            search_fields=["body", "text", "summary", "title"],
            hybrid_search=True,
            bm25_weight=0.6,
            semantic_weight=0.4
        )
        
        api_request = query.to_api_request()
        assert "search_query" in api_request
        assert "search_fields" in api_request
        assert "hybrid_search" in api_request
        assert "bm25_weight" in api_request
        assert "semantic_weight" in api_request
        assert api_request["api_version"] == "3.3.0"


class TestBM25UsageExamplesCoverage:
    """Tests for bm25_usage_examples module coverage."""
    
    def test_example_basic_bm25_search(self):
        """Test example_basic_bm25_search function."""
        with patch('builtins.print') as mock_print:
            bm25_usage_examples.example_basic_bm25_search()
            
            # Verify that print was called multiple times
            assert mock_print.call_count > 0
            
            # Check that the function executed without errors
            calls = [str(call) for call in mock_print.call_args_list]
            assert any("Basic BM25 Search Example" in call for call in calls)
            assert any("Query valid:" in call for call in calls)
            assert any("Has BM25 search:" in call for call in calls)
    
    def test_example_hybrid_search_basic(self):
        """Test example_hybrid_search_basic function."""
        with patch('builtins.print') as mock_print:
            bm25_usage_examples.example_hybrid_search_basic()
            
            # Verify that print was called multiple times
            assert mock_print.call_count > 0
            
            # Check that the function executed without errors
            calls = [str(call) for call in mock_print.call_args_list]
            assert any("Basic Hybrid Search Example" in call for call in calls)
            assert any("Query valid:" in call for call in calls)
            assert any("Hybrid search:" in call for call in calls)
    
    def test_example_hybrid_search_strategies(self):
        """Test example_hybrid_search_strategies function."""
        with patch('builtins.print') as mock_print:
            bm25_usage_examples.example_hybrid_search_strategies()
            
            # Verify that print was called multiple times
            assert mock_print.call_count > 0
            
            # Check that the function executed without errors
            calls = [str(call) for call in mock_print.call_args_list]
            assert any("Hybrid Search Strategies" in call for call in calls)
    
    def test_example_real_world_scenarios(self):
        """Test example_real_world_scenarios function."""
        with patch('builtins.print') as mock_print:
            bm25_usage_examples.example_real_world_scenarios()
            
            # Verify that print was called multiple times
            assert mock_print.call_count > 0
            
            # Check that the function executed without errors
            calls = [str(call) for call in mock_print.call_args_list]
            assert any("Real-World Scenarios" in call for call in calls)
    
    def test_example_performance_optimization(self):
        """Test example_performance_optimization function."""
        with patch('builtins.print') as mock_print:
            bm25_usage_examples.example_performance_optimization()
            
            # Verify that print was called multiple times
            assert mock_print.call_count > 0
            
            # Check that the function executed without errors
            calls = [str(call) for call in mock_print.call_args_list]
            assert any("Performance Optimization" in call for call in calls)
    
    def test_example_error_handling(self):
        """Test example_error_handling function."""
        with patch('builtins.print') as mock_print:
            bm25_usage_examples.example_error_handling()
            
            # Verify that print was called multiple times
            assert mock_print.call_count > 0
            
            # Check that the function executed without errors
            calls = [str(call) for call in mock_print.call_args_list]
            assert any("Error Handling" in call for call in calls)
    
    def test_example_advanced_configuration(self):
        """Test example_advanced_configuration function."""
        with patch('builtins.print') as mock_print:
            bm25_usage_examples.example_advanced_configuration()
            
            # Verify that print was called multiple times
            assert mock_print.call_count > 0
            
            # Check that the function executed without errors
            calls = [str(call) for call in mock_print.call_args_list]
            assert any("Advanced Configuration" in call for call in calls)
    
    def test_example_serialization(self):
        """Test example_serialization function."""
        with patch('builtins.print') as mock_print:
            bm25_usage_examples.example_serialization()
            
            # Verify that print was called multiple times
            assert mock_print.call_count > 0
            
            # Check that the function executed without errors
            calls = [str(call) for call in mock_print.call_args_list]
            assert any("Serialization Example" in call for call in calls)
    
    def test_run_all_usage_examples(self):
        """Test run_all_examples function."""
        with patch('builtins.print') as mock_print:
            bm25_usage_examples.run_all_examples()
            
            # Verify that print was called multiple times
            assert mock_print.call_count > 0
            
            # Check that the function executed without errors
            calls = [str(call) for call in mock_print.call_args_list]
            assert any("BM25 and Hybrid Search Examples" in call for call in calls)
    
    def test_usage_example_query_creation(self):
        """Test that usage examples create valid queries."""
        # Test basic BM25 query
        query = ChunkQuery(
            search_query="python machine learning",
            search_fields=["title", "body", "summary"],
            min_score=0.5,
            max_results=20
        )
        
        assert query.search_query == "python machine learning"
        assert query.search_fields == ["title", "body", "summary"]
        assert query.min_score == 0.5
        assert query.max_results == 20
        
        # Test hybrid query
        hybrid_query = ChunkQuery(
            search_query="artificial intelligence algorithms",
            search_fields=["title", "body", "summary"],
            hybrid_search=True,
            bm25_weight=0.6,
            semantic_weight=0.4,
            min_score=0.6,
            max_results=50
        )
        
        assert hybrid_query.hybrid_search == True
        assert hybrid_query.bm25_weight == 0.6
        assert hybrid_query.semantic_weight == 0.4
    
    def test_usage_example_validation(self):
        """Test that usage examples create valid queries."""
        query = ChunkQuery(
            search_query="python machine learning",
            search_fields=["title", "body", "summary"]
        )
        
        validation = query.validate_bm25_parameters()
        assert validation.is_valid == True
        
        # Test that has_bm25_search works
        assert query.has_bm25_search() == True
        
        # Test that get_search_params works
        params = query.get_search_params()
        assert "search_query" in params
        assert "search_fields" in params
    
    def test_usage_example_api_integration(self):
        """Test that usage examples can create API requests."""
        query = ChunkQuery(
            search_query="artificial intelligence algorithms",
            search_fields=["title", "body", "summary"],
            hybrid_search=True,
            bm25_weight=0.6,
            semantic_weight=0.4
        )
        
        api_request = query.to_api_request()
        assert "search_query" in api_request
        assert "hybrid_search" in api_request
        assert "bm25_weight" in api_request
        assert "semantic_weight" in api_request
        assert api_request["hybrid_search"] == True
        assert api_request["bm25_weight"] == 0.6
        assert api_request["semantic_weight"] == 0.4


class TestBM25ExamplesIntegration:
    """Integration tests for BM25 examples."""
    
    def test_examples_module_imports(self):
        """Test that all example modules can be imported."""
        assert bm25_search_examples is not None
        assert bm25_usage_examples is not None
        
        # Test that modules have expected attributes
        assert hasattr(bm25_search_examples, 'basic_bm25_search_example')
        assert hasattr(bm25_search_examples, 'hybrid_search_example')
        assert hasattr(bm25_search_examples, 'main')
        
        assert hasattr(bm25_usage_examples, 'example_basic_bm25_search')
        assert hasattr(bm25_usage_examples, 'example_hybrid_search_basic')
        assert hasattr(bm25_usage_examples, 'run_all_examples')
    
    def test_examples_create_valid_queries(self):
        """Test that examples create valid ChunkQuery objects."""
        # Test search examples query creation
        query = ChunkQuery(
            search_query="python machine learning",
            search_fields=["body", "text", "summary", "title"],
            bm25_k1=1.2,
            bm25_b=0.75,
            max_results=50
        )
        
        assert isinstance(query, ChunkQuery)
        assert query.has_bm25_search() == True
        
        # Test usage examples query creation
        hybrid_query = ChunkQuery(
            search_query="artificial intelligence algorithms",
            search_fields=["title", "body", "summary"],
            hybrid_search=True,
            bm25_weight=0.6,
            semantic_weight=0.4,
            min_score=0.6,
            max_results=50
        )
        
        assert isinstance(hybrid_query, ChunkQuery)
        assert hybrid_query.hybrid_search == True
    
    def test_examples_validation_works(self):
        """Test that examples can validate their queries."""
        query = ChunkQuery(
            search_query="test query",
            search_fields=["body", "text"],
            hybrid_search=True,
            bm25_weight=0.5,
            semantic_weight=0.5
        )
        
        # Test BM25 parameter validation
        validation = query.validate_bm25_parameters()
        assert validation.is_valid == True
        
        # Test general validation
        general_validation = query.validate()
        assert general_validation.is_valid == True
    
    def test_examples_api_integration_works(self):
        """Test that examples can create API requests."""
        query = ChunkQuery(
            search_query="test query",
            search_fields=["body", "text"],
            hybrid_search=True,
            bm25_weight=0.6,
            semantic_weight=0.4
        )
        
        # Test API request creation
        api_request = query.to_api_request()
        assert isinstance(api_request, dict)
        assert "search_query" in api_request
        assert "hybrid_search" in api_request
        assert "api_version" in api_request
        assert api_request["api_version"] == "3.3.0"
        
        # Test search parameters
        search_params = query.get_search_params()
        assert isinstance(search_params, dict)
        assert "search_query" in search_params
        assert "hybrid_search" in search_params
    
    def test_examples_with_real_data(self):
        """Test examples with real SemanticChunk data."""
        # Create a real chunk
        chunk = SemanticChunk(
            type=ChunkType.DOC_BLOCK,
            body="This is a test document about python machine learning",
            text="This is a test document about python machine learning",
            summary="Test document about ML",
            title="Python ML Test",
            quality_score=0.8,
            tags=["python", "machine-learning"]
        )
        
        # Create a query that should match
        query = ChunkQuery(
            search_query="python machine learning",
            search_fields=["body", "text", "summary", "title"],
            type="DocBlock",
            quality_score=">=0.7"
        )
        
        # Test that the query matches the chunk
        assert query.matches(chunk) == True
        
        # Test BM25 search parameters
        assert query.has_bm25_search() == True
        search_params = query.get_search_params()
        assert "search_query" in search_params
        assert search_params["search_query"] == "python machine learning"
