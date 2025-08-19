"""
Tests for filter_executor_usage.py to achieve 90%+ coverage.

This module tests the FilterExecutor usage example functionality.

Author: Development Team
Created: 2024-01-20
Updated: 2024-01-20
"""

import pytest
import time
from unittest.mock import patch
from io import StringIO
from chunk_metadata_adapter.examples.filter_executor_usage import (
    basic_usage_example,
    logical_operations_example,
    nested_fields_example,
    list_operations_example,
    string_operations_example,
    complex_expression_example,
    semantic_chunk_example,
    performance_example,
    main
)
from chunk_metadata_adapter.filter_executor import FilterExecutor
from chunk_metadata_adapter.ast import (
    FieldCondition, LogicalOperator, ParenExpression, TypedValue,
    ASTNodeFactory
)
from chunk_metadata_adapter.semantic_chunk import SemanticChunk
from chunk_metadata_adapter.data_types import ChunkType, LanguageEnum


class TestFilterExecutorUsage:
    """Tests for FilterExecutor usage example."""
    
    def test_basic_usage_example(self):
        """Test basic usage example."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            basic_usage_example()
            output = fake_out.getvalue()
            
            assert "=== Basic Usage Example ===" in output
            assert "Data:" in output
            assert "Result:" in output
            assert "True" in output
            assert "False" in output
    
    def test_logical_operations_example(self):
        """Test logical operations example."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            logical_operations_example()
            output = fake_out.getvalue()
            
            assert "=== Logical Operations Example ===" in output
            assert "AND condition" in output
            assert "OR condition" in output
            assert "Data:" in output
            assert "Result:" in output
    
    def test_nested_fields_example(self):
        """Test nested fields example."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            nested_fields_example()
            output = fake_out.getvalue()
            
            assert "=== Nested Fields Example ===" in output
            assert "Nested field condition" in output
            assert "Data:" in output
            assert "Result:" in output
    
    def test_list_operations_example(self):
        """Test list operations example."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            list_operations_example()
            output = fake_out.getvalue()
            
            assert "List Operations Example" in output
            assert "IN condition" in output
            assert "Data:" in output
            assert "Result:" in output
    
    def test_string_operations_example(self):
        """Test string operations example."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            string_operations_example()
            output = fake_out.getvalue()
            
            assert "String Operations Example" in output
            assert "LIKE condition" in output
            assert "Data:" in output
            assert "Result:" in output
    
    def test_complex_expression_example(self):
        """Test complex expression example."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            complex_expression_example()
            output = fake_out.getvalue()
            
            assert "Complex Expression Example" in output
            assert "Complex condition:" in output
            assert "Data:" in output
            assert "Result:" in output
    
    def test_semantic_chunk_example(self):
        """Test semantic chunk example."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            semantic_chunk_example()
            output = fake_out.getvalue()
            
            assert "SemanticChunk Example" in output
            assert "Filter:" in output
            assert "Chunk 1:" in output
            assert "Result:" in output
    
    def test_performance_example(self):
        """Test performance example."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            performance_example()
            output = fake_out.getvalue()
            
            assert "Performance Example" in output
            assert "Executing same condition" in output
            assert "Cache stats:" in output
    
    def test_main_function(self):
        """Test main function execution."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            main()
            output = fake_out.getvalue()
            
            assert "FilterExecutor Usage Examples" in output
            assert "Basic Usage Example" in output
            assert "Logical Operations Example" in output
            assert "Nested Fields Example" in output
            assert "List Operations Example" in output
            assert "String Operations Example" in output
            assert "Complex Expression Example" in output
            assert "SemanticChunk Example" in output
            assert "Performance Example" in output
            assert "completed successfully" in output
    
    def test_actual_basic_usage_functionality(self):
        """Test actual basic usage functionality."""
        executor = FilterExecutor()
        condition = FieldCondition("age", ">", TypedValue("int", 18))
        
        data1 = {"age": 25, "name": "John"}
        data2 = {"age": 15, "name": "Jane"}
        
        result1 = executor.execute(condition, data1)
        result2 = executor.execute(condition, data2)
        
        assert result1 is True
        assert result2 is False
    
    def test_actual_logical_operations_functionality(self):
        """Test actual logical operations functionality."""
        executor = FilterExecutor()
        
        age_condition = FieldCondition("age", ">=", TypedValue("int", 18))
        status_condition = FieldCondition("status", "=", TypedValue("str", "active"))
        vip_condition = FieldCondition("vip", "=", TypedValue("bool", True))
        
        and_condition = LogicalOperator("AND", [age_condition, status_condition])
        or_condition = LogicalOperator("OR", [age_condition, vip_condition])
        
        data1 = {"age": 25, "status": "active", "vip": False}
        data2 = {"age": 15, "status": "inactive", "vip": True}
        data3 = {"age": 15, "status": "inactive", "vip": False}
        
        # Test AND
        assert executor.execute(and_condition, data1) is True
        assert executor.execute(and_condition, data2) is False
        assert executor.execute(and_condition, data3) is False
        
        # Test OR
        assert executor.execute(or_condition, data1) is True
        assert executor.execute(or_condition, data2) is True
        assert executor.execute(or_condition, data3) is False
    
    def test_actual_nested_fields_functionality(self):
        """Test actual nested fields functionality."""
        executor = FilterExecutor()
        condition = FieldCondition("user.profile.age", ">", TypedValue("int", 18))
        
        data1 = {
            "user": {
                "profile": {
                    "age": 25,
                    "name": "John"
                }
            }
        }
        
        data2 = {
            "user": {
                "profile": {
                    "age": 15,
                    "name": "Jane"
                }
            }
        }
        
        assert executor.execute(condition, data1) is True
        assert executor.execute(condition, data2) is False
    
    def test_actual_list_operations_functionality(self):
        """Test actual list operations functionality."""
        executor = FilterExecutor()
        
        # Test intersection
        intersects_condition = FieldCondition("tags", "intersects", TypedValue("list", ["ai", "ml"]))
        data1 = {"tags": ["ai", "python", "machine-learning"]}
        data2 = {"tags": ["web", "javascript"]}
        
        assert executor.execute(intersects_condition, data1) is True
        assert executor.execute(intersects_condition, data2) is False
        
        # Test inclusion
        in_condition = FieldCondition("category", "in", TypedValue("list", ["tech", "science"]))
        data3 = {"category": "tech"}
        data4 = {"category": "sports"}
        
        assert executor.execute(in_condition, data3) is True
        assert executor.execute(in_condition, data4) is False
    
    def test_actual_string_operations_functionality(self):
        """Test actual string operations functionality."""
        executor = FilterExecutor()
        
        # Test like operator
        like_condition = FieldCondition("title", "like", TypedValue("str", "Python"))
        data1 = {"title": "Python Machine Learning Guide"}
        data2 = {"title": "JavaScript Tutorial"}
        
        assert executor.execute(like_condition, data1) is True
        assert executor.execute(like_condition, data2) is False
        
        # Test regex operator
        regex_condition = FieldCondition("content", "~", TypedValue("str", r"machine.*learning"))
        data3 = {"content": "This is about machine learning algorithms"}
        data4 = {"content": "This is about web development"}
        
        assert executor.execute(regex_condition, data3) is True
        assert executor.execute(regex_condition, data4) is False
    
    def test_actual_complex_expression_functionality(self):
        """Test actual complex expression functionality."""
        executor = FilterExecutor()
        
        # Create complex expression: (age > 18 AND status = 'active') OR (vip = true)
        age_condition = FieldCondition("age", ">", TypedValue("int", 18))
        status_condition = FieldCondition("status", "=", TypedValue("str", "active"))
        vip_condition = FieldCondition("vip", "=", TypedValue("bool", True))
        
        and_operator = LogicalOperator("AND", [age_condition, status_condition])
        paren_expression = ParenExpression(and_operator)
        or_operator = LogicalOperator("OR", [paren_expression, vip_condition])
        
        data1 = {"age": 25, "status": "active", "vip": False}
        data2 = {"age": 15, "status": "inactive", "vip": True}
        data3 = {"age": 15, "status": "inactive", "vip": False}
        
        assert executor.execute(or_operator, data1) is True
        assert executor.execute(or_operator, data2) is True
        assert executor.execute(or_operator, data3) is False
    
    def test_actual_semantic_chunk_functionality(self):
        """Test actual SemanticChunk functionality."""
        executor = FilterExecutor()
        
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
        
        assert executor.execute(type_condition, chunk) is True
        assert executor.execute(quality_condition, chunk) is True
        assert executor.execute(tags_condition, chunk) is True
        
        # Test complex condition
        complex_condition = LogicalOperator("AND", [
            type_condition,
            quality_condition,
            tags_condition
        ])
        
        assert executor.execute(complex_condition, chunk) is True
    
    def test_actual_performance_functionality(self):
        """Test actual performance functionality."""
        executor = FilterExecutor()
        
        # Create simple condition
        condition = FieldCondition("age", ">", TypedValue("int", 18))
        
        # Test data
        data = {"age": 25}
        
        # Measure execution time
        start_time = time.time()
        for _ in range(1000):
            result = executor.execute(condition, data)
        execution_time = time.time() - start_time
        
        assert result is True
        assert execution_time < 1.0  # Should be very fast
    
    def test_filter_executor_creation(self):
        """Test FilterExecutor creation."""
        executor = FilterExecutor()
        assert executor is not None
        assert isinstance(executor, FilterExecutor)
    
    def test_typed_value_creation(self):
        """Test TypedValue creation."""
        int_value = TypedValue("int", 18)
        str_value = TypedValue("str", "active")
        float_value = TypedValue("float", 0.8)
        bool_value = TypedValue("bool", True)
        list_value = TypedValue("list", ["ai", "ml"])
        
        assert int_value.type == "int"
        assert int_value.value == 18
        assert str_value.type == "str"
        assert str_value.value == "active"
        assert float_value.type == "float"
        assert float_value.value == 0.8
        assert bool_value.type == "bool"
        assert bool_value.value is True
        assert list_value.type == "list"
        assert list_value.value == ["ai", "ml"]
    
    def test_field_condition_creation(self):
        """Test FieldCondition creation."""
        condition = FieldCondition("age", ">", TypedValue("int", 18))
        
        assert condition.field == "age"
        assert condition.operator == ">"
        assert condition.value.type == "int"
        assert condition.value.value == 18
        assert condition.node_type == "field_condition"
    
    def test_logical_operator_creation(self):
        """Test LogicalOperator creation."""
        age_condition = FieldCondition("age", ">", TypedValue("int", 18))
        status_condition = FieldCondition("status", "=", TypedValue("str", "active"))
        and_operator = LogicalOperator("AND", [age_condition, status_condition])
        
        assert and_operator.operator == "AND"
        assert len(and_operator.children) == 2
        assert and_operator.children[0] == age_condition
        assert and_operator.children[1] == status_condition
        assert and_operator.node_type == "logical_operator"
    
    def test_paren_expression_creation(self):
        """Test ParenExpression creation."""
        age_condition = FieldCondition("age", ">", TypedValue("int", 18))
        paren_expr = ParenExpression(age_condition)
        
        assert paren_expr.expression == age_condition
        assert paren_expr.node_type == "paren_expression"
    
    def test_ast_node_factory(self):
        """Test ASTNodeFactory functionality."""
        # Test field condition creation
        condition = ASTNodeFactory.create_field_condition("age", ">", TypedValue("int", 18))
        assert isinstance(condition, FieldCondition)
        assert condition.field == "age"
        assert condition.operator == ">"
        assert condition.value.value == 18 