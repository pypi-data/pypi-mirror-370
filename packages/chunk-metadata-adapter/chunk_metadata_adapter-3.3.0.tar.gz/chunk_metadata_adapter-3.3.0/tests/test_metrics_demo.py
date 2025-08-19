"""
Tests for metrics demo functionality.

This module tests the metrics demonstration functions to ensure
they work correctly and provide accurate metrics data.
"""

import pytest
from unittest.mock import patch, MagicMock
from io import StringIO
import sys

from chunk_metadata_adapter.examples.metrics_demo import (
    demo_cache_metrics,
    demo_performance_metrics,
    demo_complexity_metrics,
    demo_error_metrics,
    demo_business_metrics,
    demo_resource_metrics,
    generate_prometheus_metrics,
    main
)


class TestMetricsDemo:
    """Tests for metrics demo functions."""
    
    def test_demo_cache_metrics(self):
        """Test cache metrics demonstration."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            demo_cache_metrics()
            output = fake_out.getvalue()
            
            # Check that cache metrics are displayed
            assert "=== Cache Metrics Demo ===" in output
            assert "Cache hits:" in output
            assert "Cache misses:" in output
            assert "Cache evictions:" in output
            assert "Cache size:" in output
            assert "Hit rate:" in output
            assert "Field cache size:" in output
            assert "Comparison cache size:" in output
            assert "AST cached:" in output
            assert "Parser initialized:" in output
    
    def test_demo_performance_metrics(self):
        """Test performance metrics demonstration."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            demo_performance_metrics()
            output = fake_out.getvalue()
            
            # Check that performance metrics are displayed
            assert "=== Performance Metrics Demo ===" in output
            assert "Query Parsing Performance:" in output
            assert "Average parse time:" in output
            assert "Filter Execution Performance:" in output
            assert "Average execution time:" in output
    
    def test_demo_complexity_metrics(self):
        """Test complexity metrics demonstration."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            demo_complexity_metrics()
            output = fake_out.getvalue()
            
            # Check that complexity metrics are displayed
            assert "=== Complexity Metrics Demo ===" in output
            assert "AST Complexity Analysis:" in output
            assert "Max depth:" in output
            assert "Total conditions:" in output
            assert "Operator distribution:" in output
            assert "Field distribution:" in output
            assert "Performance Analysis:" in output
            assert "Estimated complexity:" in output
    
    def test_demo_error_metrics(self):
        """Test error metrics demonstration."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            demo_error_metrics()
            output = fake_out.getvalue()
            
            # Check that error metrics are displayed
            assert "=== Error Metrics Demo ===" in output
            assert "Validation Error Metrics:" in output
            assert "Total queries:" in output
            assert "Valid queries:" in output
            assert "Invalid queries:" in output
            assert "Error rate:" in output
    
    def test_demo_business_metrics(self):
        """Test business metrics demonstration."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            demo_business_metrics()
            output = fake_out.getvalue()
            
            # Check that business metrics are displayed
            assert "=== Business Metrics Demo ===" in output
            assert "Field Usage Statistics:" in output
            assert "Field usage:" in output
            assert "Operator usage:" in output
    
    def test_demo_resource_metrics(self):
        """Test resource metrics demonstration."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            demo_resource_metrics()
            output = fake_out.getvalue()
            
            # Check that resource metrics are displayed
            assert "=== Resource Metrics Demo ===" in output
            assert "Memory Usage Estimation:" in output
            assert "QueryCache memory usage:" in output
            assert "FilterExecutor memory usage:" in output
            assert "Templates cached:" in output
            assert "Cache size:" in output
    
    def test_generate_prometheus_metrics(self):
        """Test Prometheus metrics generation."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            generate_prometheus_metrics()
            output = fake_out.getvalue()
            
            # Check that Prometheus metrics are displayed
            assert "=== Prometheus Metrics Format ===" in output
            assert "Prometheus metrics format:" in output
            assert "cache_hits_total" in output
            assert "cache_misses_total" in output
            assert "cache_hit_rate" in output
            assert "field_cache_size" in output
            assert "ast_cached" in output
    
    def test_main_function(self):
        """Test main function execution."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            main()
            output = fake_out.getvalue()
            
            # Check that all demos are executed
            assert "Metrics Demo for chunk_metadata_adapter" in output
            assert "=== Cache Metrics Demo ===" in output
            assert "=== Performance Metrics Demo ===" in output
            assert "=== Complexity Metrics Demo ===" in output
            assert "=== Error Metrics Demo ===" in output
            assert "=== Business Metrics Demo ===" in output
            assert "=== Resource Metrics Demo ===" in output
            assert "=== Prometheus Metrics Format ===" in output
            assert "All metrics demonstrations completed!" in output
    
    def test_metrics_demo_imports(self):
        """Test that all required imports work correctly."""
        # This test ensures that all imports in metrics_demo.py work
        from chunk_metadata_adapter.examples.metrics_demo import (
            demo_cache_metrics,
            demo_performance_metrics,
            demo_complexity_metrics,
            demo_error_metrics,
            demo_business_metrics,
            demo_resource_metrics,
            generate_prometheus_metrics,
            main
        )
        
        # Verify all functions are callable
        assert callable(demo_cache_metrics)
        assert callable(demo_performance_metrics)
        assert callable(demo_complexity_metrics)
        assert callable(demo_error_metrics)
        assert callable(demo_business_metrics)
        assert callable(demo_resource_metrics)
        assert callable(generate_prometheus_metrics)
        assert callable(main)
    
    def test_metrics_demo_error_handling(self):
        """Test error handling in metrics demo."""
        # Test with invalid queries that should be handled gracefully
        with patch('sys.stdout', new=StringIO()) as fake_out:
            # This should not raise an exception
            demo_error_metrics()
            output = fake_out.getvalue()
            
            # Should show error metrics even with invalid queries
            assert "Error rate:" in output
            assert "Invalid queries:" in output
    
    def test_metrics_demo_performance_under_load(self):
        """Test performance metrics under simulated load."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            demo_performance_metrics()
            output = fake_out.getvalue()
            
            # Should show reasonable performance metrics
            assert "Average parse time:" in output
            assert "Average execution time:" in output
            
            # Parse times should be reasonable (less than 1 second)
            lines = output.split('\n')
            for line in lines:
                if "Average parse time:" in line:
                    time_str = line.split(':')[1].strip()
                    time_value = float(time_str.replace('s', ''))
                    assert time_value < 1.0, f"Parse time {time_value}s is too high"
                elif "Average execution time:" in line:
                    time_str = line.split(':')[1].strip()
                    time_value = float(time_str.replace('s', ''))
                    assert time_value < 0.1, f"Execution time {time_value}s is too high"
    
    def test_metrics_demo_cache_behavior(self):
        """Test cache behavior in metrics demo."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            demo_cache_metrics()
            output = fake_out.getvalue()
            
            # Should show cache hits and misses
            assert "Cache hits:" in output
            assert "Cache misses:" in output
            assert "Hit rate:" in output
            
            # Hit rate should be reasonable (between 0 and 100)
            lines = output.split('\n')
            for line in lines:
                if "Hit rate:" in line:
                    rate_str = line.split(':')[1].strip()
                    rate_value = float(rate_str.replace('%', ''))
                    assert 0 <= rate_value <= 100, f"Hit rate {rate_value}% is invalid"
    
    def test_metrics_demo_complexity_analysis(self):
        """Test complexity analysis in metrics demo."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            demo_complexity_metrics()
            output = fake_out.getvalue()
            
            # Should show complexity metrics
            assert "Max depth:" in output
            assert "Total conditions:" in output
            assert "Operator distribution:" in output
            assert "Field distribution:" in output
            
            # Complexity values should be reasonable
            lines = output.split('\n')
            for line in lines:
                if "Max depth:" in line:
                    depth_str = line.split(':')[1].strip()
                    depth_value = int(depth_str)
                    assert depth_value >= 0, f"Max depth {depth_value} is negative"
                elif "Total conditions:" in line:
                    conditions_str = line.split(':')[1].strip()
                    conditions_value = int(conditions_str)
                    assert conditions_value >= 0, f"Total conditions {conditions_value} is negative" 