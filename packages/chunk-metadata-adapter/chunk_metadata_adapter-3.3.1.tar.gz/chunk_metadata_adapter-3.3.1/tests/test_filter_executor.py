"""
Tests for FilterExecutor class.

This module provides comprehensive tests for the FilterExecutor class,
covering all comparison operators, data types, nested field access,
and edge cases.

Test coverage:
- All comparison operators (=, !=, >, >=, <, <=, in, not_in, intersects)
- All data types (int, float, str, list, dict, date, bool, null)
- Nested field access (user.profile.name)
- String operations with regex (like, ~, !~)
- Logical operations (AND, OR, NOT)
- Error handling and edge cases
- Performance and timeout protection

Author: Development Team
Created: 2024-01-20
Updated: 2024-01-20
"""

import pytest
import re
from datetime import datetime, timezone
from typing import Any, Dict, List

from chunk_metadata_adapter.filter_executor import FilterExecutor, TimeoutError
from chunk_metadata_adapter.ast import (
    FieldCondition, LogicalOperator, ParenExpression, TypedValue,
    ASTNodeFactory
)


class TestFilterExecutorBasic:
    """Basic tests for FilterExecutor initialization and core functionality."""
    
    def test_initialization_with_valid_timeout(self):
        """Test FilterExecutor initialization with valid timeout."""
        executor = FilterExecutor(regex_timeout=1.0)
        assert executor.regex_timeout == 1.0
        assert executor._field_cache == {}
        assert executor._comparison_cache == {}
    
    def test_initialization_with_invalid_timeout(self):
        """Test FilterExecutor initialization with invalid timeout."""
        with pytest.raises(ValueError, match="regex_timeout must be between 0 and 10 seconds"):
            FilterExecutor(regex_timeout=0)
        
        with pytest.raises(ValueError, match="regex_timeout must be between 0 and 10 seconds"):
            FilterExecutor(regex_timeout=-1)
        
        with pytest.raises(ValueError, match="regex_timeout must be between 0 and 10 seconds"):
            FilterExecutor(regex_timeout=15)
    
    def test_execute_with_none_ast(self):
        """Test execute method with None AST."""
        executor = FilterExecutor()
        with pytest.raises(ValueError, match="AST cannot be None"):
            executor.execute(None, {"test": "data"})
    
    def test_execute_with_none_data(self):
        """Test execute method with None data."""
        executor = FilterExecutor()
        condition = FieldCondition("test", "=", TypedValue("str", "value"))
        with pytest.raises(ValueError, match="Data cannot be None"):
            executor.execute(condition, None)
    
    def test_clear_cache(self):
        """Test cache clearing functionality."""
        executor = FilterExecutor()
        
        # Populate caches
        executor._field_cache["test"] = "value"
        executor._comparison_cache["test"] = True
        
        assert len(executor._field_cache) > 0
        assert len(executor._comparison_cache) > 0
        
        executor.clear_cache()
        
        assert len(executor._field_cache) == 0
        assert len(executor._comparison_cache) == 0
    
    def test_get_cache_stats(self):
        """Test cache statistics functionality."""
        executor = FilterExecutor()
        
        # Populate caches
        executor._field_cache["field1"] = "value1"
        executor._field_cache["field2"] = "value2"
        executor._comparison_cache["comp1"] = True
        
        stats = executor.get_cache_stats()
        
        assert stats["field_cache_size"] == 2
        assert stats["comparison_cache_size"] == 1


class TestFilterExecutorNumericComparisons:
    """Tests for numeric comparison operations."""
    
    @pytest.fixture
    def executor(self):
        """Create FilterExecutor instance for tests."""
        return FilterExecutor()
    
    def test_int_equality(self, executor):
        """Test integer equality comparison."""
        condition = FieldCondition("age", "=", TypedValue("int", 25))
        
        assert executor.execute(condition, {"age": 25}) == True
        assert executor.execute(condition, {"age": 30}) == False
        assert executor.execute(condition, {"age": "25"}) == True  # String conversion
    
    def test_int_inequality(self, executor):
        """Test integer inequality comparison."""
        condition = FieldCondition("age", "!=", TypedValue("int", 25))
        
        assert executor.execute(condition, {"age": 30}) == True
        assert executor.execute(condition, {"age": 25}) == False
    
    def test_int_greater_than(self, executor):
        """Test integer greater than comparison."""
        condition = FieldCondition("age", ">", TypedValue("int", 18))
        
        assert executor.execute(condition, {"age": 25}) == True
        assert executor.execute(condition, {"age": 18}) == False
        assert executor.execute(condition, {"age": 15}) == False
    
    def test_int_greater_equal(self, executor):
        """Test integer greater than or equal comparison."""
        condition = FieldCondition("age", ">=", TypedValue("int", 18))
        
        assert executor.execute(condition, {"age": 25}) == True
        assert executor.execute(condition, {"age": 18}) == True
        assert executor.execute(condition, {"age": 15}) == False
    
    def test_int_less_than(self, executor):
        """Test integer less than comparison."""
        condition = FieldCondition("age", "<", TypedValue("int", 18))
        
        assert executor.execute(condition, {"age": 15}) == True
        assert executor.execute(condition, {"age": 18}) == False
        assert executor.execute(condition, {"age": 25}) == False
    
    def test_int_less_equal(self, executor):
        """Test integer less than or equal comparison."""
        condition = FieldCondition("age", "<=", TypedValue("int", 18))
        
        assert executor.execute(condition, {"age": 15}) == True
        assert executor.execute(condition, {"age": 18}) == True
        assert executor.execute(condition, {"age": 25}) == False
    
    def test_float_comparisons(self, executor):
        """Test float comparison operations."""
        condition = FieldCondition("score", ">", TypedValue("float", 7.5))
        
        assert executor.execute(condition, {"score": 8.0}) == True
        assert executor.execute(condition, {"score": 7.5}) == False
        assert executor.execute(condition, {"score": 7.0}) == False
        assert executor.execute(condition, {"score": "8.0"}) == True  # String conversion
    
    def test_numeric_with_none_values(self, executor):
        """Test numeric comparisons with None values."""
        condition = FieldCondition("age", ">", TypedValue("int", 18))
        
        assert executor.execute(condition, {"age": None}) == False
        assert executor.execute(condition, {}) == False  # Missing field
    
    def test_invalid_numeric_operators(self, executor):
        """Test invalid operators for numeric types."""
        condition = FieldCondition("age", "like", TypedValue("int", 18))
        
        # Should return False for invalid operators
        assert executor.execute(condition, {"age": 25}) == False


class TestFilterExecutorStringComparisons:
    """Tests for string comparison operations."""
    
    @pytest.fixture
    def executor(self):
        """Create FilterExecutor instance for tests."""
        return FilterExecutor()
    
    def test_string_equality(self, executor):
        """Test string equality comparison."""
        condition = FieldCondition("status", "=", TypedValue("str", "active"))
        
        assert executor.execute(condition, {"status": "active"}) == True
        assert executor.execute(condition, {"status": "inactive"}) == False
        assert executor.execute(condition, {"status": "ACTIVE"}) == False  # Case sensitive
    
    def test_string_inequality(self, executor):
        """Test string inequality comparison."""
        condition = FieldCondition("status", "!=", TypedValue("str", "active"))
        
        assert executor.execute(condition, {"status": "inactive"}) == True
        assert executor.execute(condition, {"status": "active"}) == False
    
    def test_string_like_pattern(self, executor):
        """Test string like pattern matching."""
        condition = FieldCondition("name", "like", TypedValue("str", "John"))
        
        assert executor.execute(condition, {"name": "John Doe"}) == True
        assert executor.execute(condition, {"name": "John Smith"}) == True
        assert executor.execute(condition, {"name": "Jane Doe"}) == False
    
    def test_string_regex_match(self, executor):
        """Test string regex matching."""
        condition = FieldCondition("email", "~", TypedValue("str", r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"))
        
        assert executor.execute(condition, {"email": "test@example.com"}) == True
        assert executor.execute(condition, {"email": "invalid-email"}) == False
    
    def test_string_regex_not_match(self, executor):
        """Test string regex not matching."""
        condition = FieldCondition("email", "!~", TypedValue("str", r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"))
        
        assert executor.execute(condition, {"email": "invalid-email"}) == True
        assert executor.execute(condition, {"email": "test@example.com"}) == False
    
    def test_string_with_none_values(self, executor):
        """Test string comparisons with None values."""
        condition = FieldCondition("name", "=", TypedValue("str", "John"))
        
        assert executor.execute(condition, {"name": None}) == False
        assert executor.execute(condition, {}) == False  # Missing field


class TestFilterExecutorListComparisons:
    """Tests for list comparison operations."""
    
    @pytest.fixture
    def executor(self):
        """Create FilterExecutor instance for tests."""
        return FilterExecutor()
    
    def test_list_equality(self, executor):
        """Test list equality comparison."""
        condition = FieldCondition("tags", "=", TypedValue("list", ["python", "ai"]))
        
        assert executor.execute(condition, {"tags": ["python", "ai"]}) == True
        assert executor.execute(condition, {"tags": ["ai", "python"]}) == False  # Order matters
        assert executor.execute(condition, {"tags": ["python"]}) == False
    
    def test_list_inequality(self, executor):
        """Test list inequality comparison."""
        condition = FieldCondition("tags", "!=", TypedValue("list", ["python", "ai"]))
        
        assert executor.execute(condition, {"tags": ["java", "ml"]}) == True
        assert executor.execute(condition, {"tags": ["python", "ai"]}) == False
    
    def test_list_in_operation(self, executor):
        """Test list in operation."""
        condition = FieldCondition("tag", "in", TypedValue("list", ["python", "ai", "ml"]))
        
        assert executor.execute(condition, {"tag": "python"}) == True
        assert executor.execute(condition, {"tag": "java"}) == False
    
    def test_list_not_in_operation(self, executor):
        """Test list not_in operation."""
        condition = FieldCondition("tag", "not_in", TypedValue("list", ["python", "ai", "ml"]))
        
        assert executor.execute(condition, {"tag": "java"}) == True
        assert executor.execute(condition, {"tag": "python"}) == False
    
    def test_list_intersects_operation(self, executor):
        """Test list intersects operation."""
        condition = FieldCondition("tags", "intersects", TypedValue("list", ["python", "ai"]))
        
        assert executor.execute(condition, {"tags": ["python", "ml"]}) == True
        assert executor.execute(condition, {"tags": ["java", "cpp"]}) == False
        assert executor.execute(condition, {"tags": ["python", "ai", "ml"]}) == True
    
    def test_list_with_none_values(self, executor):
        """Test list comparisons with None values."""
        condition = FieldCondition("tags", "intersects", TypedValue("list", ["python"]))
        
        assert executor.execute(condition, {"tags": None}) == False
        assert executor.execute(condition, {}) == False  # Missing field


class TestFilterExecutorDictComparisons:
    """Tests for dictionary comparison operations."""
    
    @pytest.fixture
    def executor(self):
        """Create FilterExecutor instance for tests."""
        return FilterExecutor()
    
    def test_dict_equality(self, executor):
        """Test dictionary equality comparison."""
        condition = FieldCondition("meta", "=", TypedValue("dict", {"version": "1.0"}))
        
        assert executor.execute(condition, {"meta": {"version": "1.0"}}) == True
        assert executor.execute(condition, {"meta": {"version": "2.0"}}) == False
    
    def test_dict_inequality(self, executor):
        """Test dictionary inequality comparison."""
        condition = FieldCondition("meta", "!=", TypedValue("dict", {"version": "1.0"}))
        
        assert executor.execute(condition, {"meta": {"version": "2.0"}}) == True
        assert executor.execute(condition, {"meta": {"version": "1.0"}}) == False
    
    def test_dict_contains_key(self, executor):
        """Test dictionary contains_key operation."""
        condition = FieldCondition("meta", "contains_key", TypedValue("dict", {"version": None, "author": None}))
        
        assert executor.execute(condition, {"meta": {"version": "1.0", "author": "John"}}) == True
        assert executor.execute(condition, {"meta": {"version": "1.0"}}) == False  # Missing author
    
    def test_dict_contains_value(self, executor):
        """Test dictionary contains_value operation."""
        condition = FieldCondition("meta", "contains_value", TypedValue("dict", {"version": "1.0", "author": "John"}))
        
        assert executor.execute(condition, {"meta": {"version": "1.0", "author": "John"}}) == True
        assert executor.execute(condition, {"meta": {"version": "2.0", "author": "John"}}) == False


class TestFilterExecutorDateComparisons:
    """Tests for date/time comparison operations."""
    
    @pytest.fixture
    def executor(self):
        """Create FilterExecutor instance for tests."""
        return FilterExecutor()
    
    def test_date_equality(self, executor):
        """Test date equality comparison."""
        condition = FieldCondition("created_at", "=", TypedValue("date", "2024-01-15T10:30:00Z"))
        
        assert executor.execute(condition, {"created_at": "2024-01-15T10:30:00Z"}) == True
        assert executor.execute(condition, {"created_at": "2024-01-15T10:30:01Z"}) == False
    
    def test_date_greater_than(self, executor):
        """Test date greater than comparison."""
        condition = FieldCondition("created_at", ">", TypedValue("date", "2024-01-15T10:30:00Z"))
        
        assert executor.execute(condition, {"created_at": "2024-01-15T10:30:01Z"}) == True
        assert executor.execute(condition, {"created_at": "2024-01-15T10:30:00Z"}) == False
        assert executor.execute(condition, {"created_at": "2024-01-15T10:29:59Z"}) == False
    
    def test_date_with_datetime_objects(self, executor):
        """Test date comparisons with datetime objects."""
        dt1 = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
        dt2 = datetime(2024, 1, 15, 10, 30, 1, tzinfo=timezone.utc)
        
        condition = FieldCondition("created_at", ">", TypedValue("date", dt1))
        
        assert executor.execute(condition, {"created_at": dt2}) == True
        assert executor.execute(condition, {"created_at": dt1}) == False


class TestFilterExecutorBooleanComparisons:
    """Tests for boolean comparison operations."""
    
    @pytest.fixture
    def executor(self):
        """Create FilterExecutor instance for tests."""
        return FilterExecutor()
    
    def test_boolean_equality(self, executor):
        """Test boolean equality comparison."""
        condition = FieldCondition("is_active", "=", TypedValue("bool", True))
        
        assert executor.execute(condition, {"is_active": True}) == True
        assert executor.execute(condition, {"is_active": False}) == False
    
    def test_boolean_inequality(self, executor):
        """Test boolean inequality comparison."""
        condition = FieldCondition("is_active", "!=", TypedValue("bool", True))
        
        assert executor.execute(condition, {"is_active": False}) == True
        assert executor.execute(condition, {"is_active": True}) == False


class TestFilterExecutorNullComparisons:
    """Tests for null value comparisons."""
    
    @pytest.fixture
    def executor(self):
        """Create FilterExecutor instance for tests."""
        return FilterExecutor()
    
    def test_null_equality(self, executor):
        """Test null equality comparison."""
        condition = FieldCondition("optional_field", "=", TypedValue("null", None))
        
        assert executor.execute(condition, {"optional_field": None}) == True
        assert executor.execute(condition, {"optional_field": "value"}) == False
    
    def test_null_inequality(self, executor):
        """Test null inequality comparison."""
        condition = FieldCondition("optional_field", "!=", TypedValue("null", None))
        
        assert executor.execute(condition, {"optional_field": "value"}) == True
        assert executor.execute(condition, {"optional_field": None}) == False


class TestFilterExecutorNestedFields:
    """Tests for nested field access."""
    
    @pytest.fixture
    def executor(self):
        """Create FilterExecutor instance for tests."""
        return FilterExecutor()
    
    def test_simple_nested_field(self, executor):
        """Test simple nested field access."""
        condition = FieldCondition("user.name", "=", TypedValue("str", "John"))
        data = {"user": {"name": "John", "age": 30}}
        
        assert executor.execute(condition, data) == True
    
    def test_deep_nested_field(self, executor):
        """Test deep nested field access."""
        condition = FieldCondition("user.profile.preferences.theme", "=", TypedValue("str", "dark"))
        data = {
            "user": {
                "profile": {
                    "preferences": {
                        "theme": "dark",
                        "language": "en"
                    }
                }
            }
        }
        
        assert executor.execute(condition, data) == True
    
    def test_nested_field_with_missing_intermediate(self, executor):
        """Test nested field access with missing intermediate levels."""
        condition = FieldCondition("user.profile.name", "=", TypedValue("str", "John"))
        data = {"user": {"age": 30}}  # Missing profile
        
        assert executor.execute(condition, data) == False
    
    def test_nested_field_with_none_values(self, executor):
        """Test nested field access with None values."""
        condition = FieldCondition("user.profile.name", "=", TypedValue("str", "John"))
        data = {"user": {"profile": None}}
        
        assert executor.execute(condition, data) == False
    
    def test_nested_field_with_object_attributes(self, executor):
        """Test nested field access with object attributes."""
        class User:
            def __init__(self, name, age):
                self.name = name
                self.age = age
        
        class Profile:
            def __init__(self, theme):
                self.theme = theme
        
        user = User("John", 30)
        user.profile = Profile("dark")
        
        condition = FieldCondition("profile.theme", "=", TypedValue("str", "dark"))
        
        assert executor.execute(condition, user) == True


class TestFilterExecutorLogicalOperations:
    """Tests for logical operations (AND, OR, NOT)."""
    
    @pytest.fixture
    def executor(self):
        """Create FilterExecutor instance for tests."""
        return FilterExecutor()
    
    def test_and_operator(self, executor):
        """Test AND logical operator."""
        condition1 = FieldCondition("age", ">", TypedValue("int", 18))
        condition2 = FieldCondition("status", "=", TypedValue("str", "active"))
        and_condition = LogicalOperator("AND", [condition1, condition2])
        
        data1 = {"age": 25, "status": "active"}
        data2 = {"age": 25, "status": "inactive"}
        data3 = {"age": 15, "status": "active"}
        
        assert executor.execute(and_condition, data1) == True
        assert executor.execute(and_condition, data2) == False
        assert executor.execute(and_condition, data3) == False
    
    def test_or_operator(self, executor):
        """Test OR logical operator."""
        condition1 = FieldCondition("age", ">", TypedValue("int", 18))
        condition2 = FieldCondition("status", "=", TypedValue("str", "active"))
        or_condition = LogicalOperator("OR", [condition1, condition2])
        
        data1 = {"age": 25, "status": "inactive"}
        data2 = {"age": 15, "status": "active"}
        data3 = {"age": 15, "status": "inactive"}
        
        assert executor.execute(or_condition, data1) == True
        assert executor.execute(or_condition, data2) == True
        assert executor.execute(or_condition, data3) == False
    
    def test_not_operator(self, executor):
        """Test NOT logical operator."""
        condition = FieldCondition("status", "=", TypedValue("str", "active"))
        not_condition = LogicalOperator("NOT", [condition])
        
        data1 = {"status": "inactive"}
        data2 = {"status": "active"}
        
        assert executor.execute(not_condition, data1) == True
        assert executor.execute(not_condition, data2) == False
    
    def test_complex_logical_expression(self, executor):
        """Test complex logical expression."""
        # (age > 18 AND status = 'active') OR (vip = true)
        age_condition = FieldCondition("age", ">", TypedValue("int", 18))
        status_condition = FieldCondition("status", "=", TypedValue("str", "active"))
        vip_condition = FieldCondition("vip", "=", TypedValue("bool", True))
        
        and_condition = LogicalOperator("AND", [age_condition, status_condition])
        or_condition = LogicalOperator("OR", [and_condition, vip_condition])
        
        data1 = {"age": 25, "status": "active", "vip": False}
        data2 = {"age": 15, "status": "inactive", "vip": True}
        data3 = {"age": 15, "status": "inactive", "vip": False}
        
        assert executor.execute(or_condition, data1) == True
        assert executor.execute(or_condition, data2) == True
        assert executor.execute(or_condition, data3) == False
    
    def test_short_circuit_evaluation(self, executor):
        """Test short-circuit evaluation for logical operators."""
        # Create a condition that would raise an exception if evaluated
        def failing_condition():
            raise ValueError("This should not be evaluated")
        
        # AND with first condition False - second should not be evaluated
        condition1 = FieldCondition("status", "=", TypedValue("str", "active"))
        condition2 = FieldCondition("nonexistent.field", "=", TypedValue("str", "value"))
        and_condition = LogicalOperator("AND", [condition1, condition2])
        
        data = {"status": "inactive"}  # First condition will be False
        
        # Should not raise exception due to short-circuit
        result = executor.execute(and_condition, data)
        assert result == False


class TestFilterExecutorParentheses:
    """Tests for parenthesized expressions."""
    
    @pytest.fixture
    def executor(self):
        """Create FilterExecutor instance for tests."""
        return FilterExecutor()
    
    def test_simple_parentheses(self, executor):
        """Test simple parenthesized expression."""
        inner_condition = FieldCondition("age", ">", TypedValue("int", 18))
        paren_condition = ParenExpression(inner_condition)
        
        data1 = {"age": 25}
        data2 = {"age": 15}
        
        assert executor.execute(paren_condition, data1) == True
        assert executor.execute(paren_condition, data2) == False
    
    def test_nested_parentheses(self, executor):
        """Test nested parenthesized expressions."""
        inner_condition = FieldCondition("age", ">", TypedValue("int", 18))
        paren1 = ParenExpression(inner_condition)
        paren2 = ParenExpression(paren1)
        
        data = {"age": 25}
        
        assert executor.execute(paren2, data) == True


class TestFilterExecutorRegexOperations:
    """Tests for regex operations with timeout protection."""
    
    @pytest.fixture
    def executor(self):
        """Create FilterExecutor instance with short timeout for testing."""
        return FilterExecutor(regex_timeout=0.1)
    
    def test_simple_regex_match(self, executor):
        """Test simple regex matching."""
        condition = FieldCondition("text", "~", TypedValue("str", r"hello.*world"))
        
        assert executor.execute(condition, {"text": "hello beautiful world"}) == True
        assert executor.execute(condition, {"text": "goodbye world"}) == False
    
    def test_regex_like_operator(self, executor):
        """Test regex-like operator."""
        condition = FieldCondition("email", "like", TypedValue("str", "@"))
        
        assert executor.execute(condition, {"email": "test@example.com"}) == True
        assert executor.execute(condition, {"email": "invalid-email"}) == False
    
    def test_regex_not_match(self, executor):
        """Test regex not match operator."""
        condition = FieldCondition("text", "!~", TypedValue("str", r"hello.*world"))
        
        assert executor.execute(condition, {"text": "goodbye world"}) == True
        assert executor.execute(condition, {"text": "hello beautiful world"}) == False
    
    def test_invalid_regex_pattern(self, executor):
        """Test handling of invalid regex patterns."""
        condition = FieldCondition("text", "~", TypedValue("str", r"[invalid"))
        
        # Should return False for invalid patterns
        assert executor.execute(condition, {"text": "test"}) == False


class TestFilterExecutorErrorHandling:
    """Tests for error handling and edge cases."""
    
    @pytest.fixture
    def executor(self):
        """Create FilterExecutor instance for tests."""
        return FilterExecutor()
    
    def test_field_access_errors(self, executor):
        """Test handling of field access errors."""
        condition = FieldCondition("nonexistent.field", "=", TypedValue("str", "value"))
        
        # Should return False for missing fields
        assert executor.execute(condition, {"other_field": "value"}) == False
    
    def test_type_conversion_errors(self, executor):
        """Test handling of type conversion errors."""
        condition = FieldCondition("age", ">", TypedValue("int", 18))
        
        # Should handle non-numeric strings gracefully
        assert executor.execute(condition, {"age": "not_a_number"}) == False
    
    def test_unsupported_operators(self, executor):
        """Test handling of unsupported operators."""
        # Create condition with valid operator first, then modify it
        condition = FieldCondition("age", ">", TypedValue("int", 18))
        condition.operator = "unsupported"  # Modify after creation to bypass validation
        
        # Should return False for unsupported operators
        assert executor.execute(condition, {"age": 25}) == False
    
    def test_malformed_data(self, executor):
        """Test handling of malformed data."""
        condition = FieldCondition("field", "=", TypedValue("str", "value"))
        
        # Should handle various malformed data types
        assert executor.execute(condition, "not_a_dict") == False
        assert executor.execute(condition, 123) == False
        assert executor.execute(condition, []) == False


class TestFilterExecutorPerformance:
    """Tests for performance characteristics."""
    
    @pytest.fixture
    def executor(self):
        """Create FilterExecutor instance for tests."""
        return FilterExecutor()
    
    def test_cache_effectiveness(self, executor):
        """Test that caching improves performance."""
        condition = FieldCondition("deeply.nested.field", "=", TypedValue("str", "value"))
        data = {
            "deeply": {
                "nested": {
                    "field": "value"
                }
            }
        }
        
        # First execution should populate cache
        result1 = executor.execute(condition, data)
        
        # Second execution should use cache
        result2 = executor.execute(condition, data)
        
        assert result1 == result2 == True
        
        # Check cache stats
        stats = executor.get_cache_stats()
        assert stats["field_cache_size"] > 0
    
    def test_large_data_handling(self, executor):
        """Test handling of large data structures."""
        # Create large nested data structure
        data = {}
        current = data
        for i in range(100):
            current[f"level_{i}"] = {}
            current = current[f"level_{i}"]
        current["final_field"] = "value"
        
        condition = FieldCondition("level_0.level_1.level_2.final_field", "=", TypedValue("str", "value"))
        
        # Should handle large structures efficiently
        # Note: The field path doesn't exist in the data structure
        # The test should return False because the field is not found
        assert executor.execute(condition, data) == False
        
        # Test with correct path - need to go through all 100 levels
        path_parts = [f"level_{i}" for i in range(100)]
        path_parts.append("final_field")
        correct_path = ".".join(path_parts)
        condition2 = FieldCondition(correct_path, "=", TypedValue("str", "value"))
        assert executor.execute(condition2, data) == True


class TestFilterExecutorIntegration:
    """Integration tests with real-world scenarios."""
    
    @pytest.fixture
    def executor(self):
        """Create FilterExecutor instance for tests."""
        return FilterExecutor()
    
    def test_semantic_chunk_filtering(self, executor):
        """Test filtering SemanticChunk objects."""
        from chunk_metadata_adapter.semantic_chunk import SemanticChunk
        
        # Create test chunks
        chunk1 = SemanticChunk(
            type="DocBlock",
            body="Python tutorial content",
            quality_score=0.8,
            tags=["python", "tutorial"],
            year=2024,
            is_public=True
        )
        
        chunk2 = SemanticChunk(
            type="CodeBlock",
            body="def hello(): print('world')",
            quality_score=0.6,
            tags=["python", "code"],
            year=2023,
            is_public=False
        )
        
        # Test complex filter - use enum values for type comparison
        condition1 = FieldCondition("type", "=", TypedValue("str", "DocBlock"))  # Will be compared as string
        condition2 = FieldCondition("quality_score", ">=", TypedValue("float", 0.7))
        condition3 = FieldCondition("tags", "intersects", TypedValue("list", ["python"]))
        condition4 = FieldCondition("year", ">=", TypedValue("int", 2024))
        condition5 = FieldCondition("is_public", "=", TypedValue("bool", True))
        
        and_condition = LogicalOperator("AND", [condition1, condition2, condition3, condition4, condition5])
        
        assert executor.execute(and_condition, chunk1) == True
        assert executor.execute(and_condition, chunk2) == False
    
    def test_complex_business_logic(self, executor):
        """Test complex business logic scenarios."""
        # Simulate user data
        user_data = {
            "profile": {
                "age": 25,
                "preferences": {
                    "theme": "dark",
                    "notifications": True
                }
            },
            "subscription": {
                "plan": "premium",
                "expires_at": "2024-12-31T23:59:59Z"
            },
            "activity": {
                "last_login": "2024-01-15T10:30:00Z",
                "login_count": 150
            }
        }
        
        # Complex business rule: Premium users over 18 with dark theme and recent activity
        age_condition = FieldCondition("profile.age", ">=", TypedValue("int", 18))
        plan_condition = FieldCondition("subscription.plan", "=", TypedValue("str", "premium"))
        theme_condition = FieldCondition("profile.preferences.theme", "=", TypedValue("str", "dark"))
        activity_condition = FieldCondition("activity.login_count", ">", TypedValue("int", 100))
        
        complex_condition = LogicalOperator("AND", [
            age_condition,
            plan_condition,
            theme_condition,
            activity_condition
        ])
        
        assert executor.execute(complex_condition, user_data) == True
    
    def test_filter_chain_operations(self, executor):
        """Test chaining multiple filter operations."""
        # Create a chain of filters
        filters = [
            FieldCondition("status", "=", TypedValue("str", "active")),
            FieldCondition("priority", ">=", TypedValue("int", 5)),
            FieldCondition("category", "in", TypedValue("list", ["urgent", "high"]))
        ]
        
        # Combine with OR logic
        or_filter = LogicalOperator("OR", filters)
        
        # Test data
        data1 = {"status": "active", "priority": 3, "category": "low"}
        data2 = {"status": "inactive", "priority": 7, "category": "urgent"}
        data3 = {"status": "active", "priority": 8, "category": "high"}
        data4 = {"status": "inactive", "priority": 2, "category": "low"}
        
        assert executor.execute(or_filter, data1) == True   # status = active
        assert executor.execute(or_filter, data2) == True   # priority >= 5 AND category in list
        assert executor.execute(or_filter, data3) == True   # all conditions
        assert executor.execute(or_filter, data4) == False  # no conditions met 


class TestFilterExecutorEdgeCases:
    """Tests for edge cases and error conditions."""
    
    @pytest.fixture
    def executor(self):
        """Create FilterExecutor instance for tests."""
        return FilterExecutor()
    
    def test_unknown_node_type(self, executor):
        """Test handling of unknown node type."""
        class UnknownNode:
            pass
        
        unknown_node = UnknownNode()
        with pytest.raises(ValueError, match="Unknown node type"):
            executor._evaluate_node(unknown_node, {"test": "data"})
    
    def test_unknown_logical_operator(self, executor):
        """Test handling of unknown logical operator."""
        # Create a mock logical operator with invalid operator
        class MockLogicalOperator:
            def __init__(self):
                self.operator = "XOR"
                self.children = [FieldCondition("test", "=", TypedValue("str", "value"))]
        
        operator = MockLogicalOperator()
        
        with pytest.raises(ValueError, match="Unknown logical operator"):
            executor._evaluate_logical_operator(operator, {"test": "value"})
    
    def test_empty_field_path(self, executor):
        """Test handling of empty field path."""
        with pytest.raises(ValueError, match="Field path cannot be empty"):
            executor._get_field_value("", {"test": "data"})
    
    def test_unsupported_type_comparison(self, executor):
        """Test handling of unsupported type for comparison."""
        # Create a mock TypedValue with unsupported type
        class MockTypedValue:
            def __init__(self):
                self.type = "unsupported"
                self.value = "value"
        
        mock_value = MockTypedValue()
        
        with pytest.raises(ValueError, match="Unsupported type for comparison"):
            executor._perform_typed_comparison("test", "=", mock_value)
    
    def test_regex_timeout(self, executor):
        """Test regex timeout protection."""
        # Create a regex pattern that could cause ReDoS
        evil_pattern = r"^(a+)+$"
        evil_text = "a" * 1000 + "b"  # This will cause exponential backtracking
        
        # Should timeout and raise TimeoutError
        with pytest.raises(TimeoutError, match="Regex operation timed out"):
            executor._safe_regex_match(evil_text, evil_pattern)
    
    def test_invalid_regex_pattern(self, executor):
        """Test handling of invalid regex pattern."""
        with pytest.raises(ValueError, match="Invalid regex pattern"):
            executor._safe_regex_match("test", "[invalid")
    
    def test_unsupported_operators_for_types(self, executor):
        """Test unsupported operators for different types."""
        # Test unsupported operators for int - should return False, not raise
        result = executor._compare_int(25, "like", 18)
        assert result == False
        
        # Test unsupported operators for float - should return False, not raise
        result = executor._compare_float(25.5, "like", 18.0)
        assert result == False
        
        # Test unsupported operators for string - should return False, not raise
        result = executor._compare_string("test", ">", "value")
        assert result == False
        
        # Test unsupported operators for list - should return False, not raise
        result = executor._compare_list(["a"], ">", ["b"])
        assert result == False
        
        # Test unsupported operators for dict - should return False, not raise
        result = executor._compare_dict({"a": 1}, ">", {"b": 2})
        assert result == False
        
        # Test unsupported operators for date - should return False, not raise
        result = executor._compare_date(datetime.now(), "like", datetime.now())
        assert result == False
        
        # Test unsupported operators for bool - should return False, not raise
        result = executor._compare_bool(True, ">", False)
        assert result == False


class TestFilterExecutorAdvancedComparisons:
    """Tests for advanced comparison scenarios."""
    
    @pytest.fixture
    def executor(self):
        """Create FilterExecutor instance for tests."""
        return FilterExecutor()
    
    def test_float_precision_comparison(self, executor):
        """Test float comparison with precision issues."""
        condition = FieldCondition("score", "=", TypedValue("float", 0.1 + 0.2))
        
        # Test with string conversion
        assert executor.execute(condition, {"score": "0.30000000000000004"}) == True
        
        # Test with different precision
        assert executor.execute(condition, {"score": 0.3}) == True
    
    def test_enum_value_handling(self, executor):
        """Test handling of enum values."""
        from enum import Enum
        
        class Status(Enum):
            ACTIVE = "active"
            INACTIVE = "inactive"
        
        condition = FieldCondition("status", "=", TypedValue("str", "active"))
        
        # Test with enum value
        assert executor.execute(condition, {"status": Status.ACTIVE}) == True
        assert executor.execute(condition, {"status": Status.INACTIVE}) == False
    
    def test_complex_nested_object_access(self, executor):
        """Test complex nested object access."""
        class User:
            def __init__(self, profile):
                self.profile = profile
        
        class Profile:
            def __init__(self, settings):
                self.settings = settings
        
        class Settings:
            def __init__(self, theme):
                self.theme = theme
        
        user = User(Profile(Settings("dark")))
        
        condition = FieldCondition("user.profile.settings.theme", "=", TypedValue("str", "dark"))
        assert executor.execute(condition, {"user": user}) == True
    
    def test_cache_key_collision_handling(self, executor):
        """Test cache key collision handling."""
        # Test with different data objects but same field path
        data1 = {"age": 25}
        data2 = {"age": 30}
        
        condition = FieldCondition("age", ">", TypedValue("int", 20))
        
        # Both should work correctly despite potential cache key collision
        assert executor.execute(condition, data1) == True
        assert executor.execute(condition, data2) == True
    
    def test_mixed_type_comparisons(self, executor):
        """Test comparisons with mixed types."""
        # Test string vs int comparison
        condition = FieldCondition("value", "=", TypedValue("str", "25"))
        assert executor.execute(condition, {"value": 25}) == True
        
        # Test int vs string comparison
        condition = FieldCondition("value", "=", TypedValue("int", 25))
        assert executor.execute(condition, {"value": "25"}) == True
    
    def test_none_handling_in_comparisons(self, executor):
        """Test None value handling in comparisons."""
        # Test None vs null type
        condition = FieldCondition("value", "=", TypedValue("null", None))
        assert executor.execute(condition, {"value": None}) == True
        assert executor.execute(condition, {"value": "not null"}) == False
        
        # Test None vs non-null type
        condition = FieldCondition("value", "=", TypedValue("str", "test"))
        assert executor.execute(condition, {"value": None}) == False
    
    def test_inclusion_operators_with_non_list_expected(self, executor):
        """Test inclusion operators with non-list expected values."""
        # Test 'in' with non-list expected
        condition = FieldCondition("value", "in", TypedValue("str", "test"))
        assert executor.execute(condition, {"value": "test"}) == True
        assert executor.execute(condition, {"value": "other"}) == False
        
        # Test 'not_in' with non-list expected
        condition = FieldCondition("value", "not_in", TypedValue("str", "test"))
        assert executor.execute(condition, {"value": "other"}) == True
        assert executor.execute(condition, {"value": "test"}) == False


class TestFilterExecutorErrorRecovery:
    """Tests for error recovery and graceful degradation."""
    
    @pytest.fixture
    def executor(self):
        """Create FilterExecutor instance for tests."""
        return FilterExecutor()
    
    def test_field_access_error_recovery(self, executor):
        """Test recovery from field access errors."""
        condition = FieldCondition("nonexistent.field", "=", TypedValue("str", "value"))
        
        # Should return False instead of raising exception
        result = executor.execute(condition, {"test": "data"})
        assert result == False
    
    def test_type_conversion_error_recovery(self, executor):
        """Test recovery from type conversion errors."""
        condition = FieldCondition("value", ">", TypedValue("int", 18))
        
        # Test with non-convertible value
        result = executor.execute(condition, {"value": "not_a_number"})
        assert result == False
    
    def test_comparison_error_recovery(self, executor):
        """Test recovery from comparison errors."""
        condition = FieldCondition("value", ">", TypedValue("int", 18))
        
        # Test with None value
        result = executor.execute(condition, {"value": None})
        assert result == False
    
    def test_execute_with_exception_handling(self, executor):
        """Test execute method exception handling."""
        # Create a condition that will cause an error during execution
        # Use a valid operator but invalid data type for comparison
        condition = FieldCondition("value", ">", TypedValue("int", 18))
        
        # Test with data that will cause comparison error
        result = executor.execute(condition, {"value": "string_value"})
        assert result == False
    
    def test_execute_with_none_ast_handling(self, executor):
        """Test execute method with None AST handling."""
        with pytest.raises(ValueError, match="AST cannot be None"):
            executor.execute(None, {"test": "data"})
    
    def test_execute_with_none_data_handling(self, executor):
        """Test execute method with None data handling."""
        condition = FieldCondition("test", "=", TypedValue("str", "value"))
        with pytest.raises(ValueError, match="Data cannot be None"):
            executor.execute(condition, None)
    
    def test_execute_with_general_exception_handling(self, executor):
        """Test execute method with general exception handling."""
        # Create a condition that will cause an error during field access
        condition = FieldCondition("value", "=", TypedValue("str", "test"))
        
        # Test with data that will cause attribute error
        class BadData:
            def __getattr__(self, name):
                raise AttributeError("Test error")
        
        result = executor.execute(condition, BadData())
        assert result == False 