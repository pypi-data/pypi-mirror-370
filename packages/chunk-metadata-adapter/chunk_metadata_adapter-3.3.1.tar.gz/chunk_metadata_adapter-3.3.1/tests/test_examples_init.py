"""
Tests for examples/__init__.py to achieve 100% coverage.

This module tests the examples package initialization and exports.

Author: Development Team
Created: 2024-01-20
Updated: 2024-01-20
"""

import pytest
from chunk_metadata_adapter.examples import __all__


class TestExamplesInit:
    """Tests for examples package initialization."""
    
    def test_all_exports(self):
        """Test that __all__ contains all expected exports."""
        expected_exports = [
            "ast_basic_usage",
            "ast_visitor_pattern_usage", 
            "chunk_query_integration_demo",
            "filter_executor_usage",
            "filter_parser_total_chunks_example",
        ]
        
        assert __all__ == expected_exports
        assert len(__all__) == 5
    
    def test_import_examples_package(self):
        """Test that examples package can be imported."""
        import chunk_metadata_adapter.examples
        assert chunk_metadata_adapter.examples.__all__ is not None 