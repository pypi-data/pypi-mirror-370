"""
Tests for ast_visitor_pattern_usage.py to achieve 90%+ coverage.

This module tests the AST visitor pattern usage example functionality.

Author: Development Team
Created: 2024-01-20
Updated: 2024-01-20
"""

import pytest
from unittest.mock import patch
from io import StringIO
from chunk_metadata_adapter.examples.ast_visitor_pattern_usage import main
from chunk_metadata_adapter.ast import (
    TypedValue,
    FieldCondition,
    LogicalOperator,
    ParenExpression,
    ASTPrinter,
    ASTValidator,
    ASTAnalyzer,
    ASTOptimizer
)


class TestASTVisitorPatternUsage:
    """Tests for AST visitor pattern usage example."""
    
    def test_main_function_execution(self):
        """Test that main function executes without errors."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            main()
            output = fake_out.getvalue()
            
            # Check that output contains expected content
            assert "=== AST Visitor Pattern Usage Example ===" in output
            assert "1. Creating complex AST:" in output
            assert "2. AST Structure (using ASTPrinter):" in output
            assert "3. AST Validation (using ASTValidator):" in output
            assert "4. AST Analysis (using ASTAnalyzer):" in output
            assert "5. AST Optimization (using ASTOptimizer):" in output
            assert "6. Real-world SemanticChunk filter analysis:" in output
    
    def test_ast_printer_functionality(self):
        """Test ASTPrinter functionality used in demo."""
        # Create AST structure
        age_condition = FieldCondition("age", ">", TypedValue("int", 18))
        status_condition = FieldCondition("status", "=", TypedValue("str", "active"))
        left_and = LogicalOperator("AND", [age_condition, status_condition])
        left_paren = ParenExpression(left_and)
        
        type_condition = FieldCondition("type", "=", TypedValue("str", "DocBlock"))
        quality_condition = FieldCondition("quality_score", ">=", TypedValue("float", 0.8))
        right_and = LogicalOperator("AND", [type_condition, quality_condition])
        
        root_or = LogicalOperator("OR", [left_paren, right_and])
        
        # Test printer
        printer = ASTPrinter()
        result = root_or.accept(printer)
        
        assert isinstance(result, str)
        assert "OR" in result
        assert "AND" in result
        assert "age" in result
        assert "status" in result
        assert "type" in result
        assert "quality_score" in result
    
    def test_ast_validator_functionality(self):
        """Test ASTValidator functionality used in demo."""
        # Create valid AST
        age_condition = FieldCondition("age", ">", TypedValue("int", 18))
        status_condition = FieldCondition("status", "=", TypedValue("str", "active"))
        and_operator = LogicalOperator("AND", [age_condition, status_condition])
        
        # Test validator
        validator = ASTValidator()
        is_valid = and_operator.accept(validator)
        
        assert is_valid is True
        assert len(validator.errors) == 0
    
    def test_ast_analyzer_functionality(self):
        """Test ASTAnalyzer functionality used in demo."""
        # Create AST structure
        age_condition = FieldCondition("age", ">", TypedValue("int", 18))
        status_condition = FieldCondition("status", "=", TypedValue("str", "active"))
        and_operator = LogicalOperator("AND", [age_condition, status_condition])
        
        # Test analyzer
        analyzer = ASTAnalyzer()
        analyzer.visit(and_operator)
        analysis = analyzer.get_analysis()
        
        assert "field_count" in analysis
        assert "operator_count" in analysis
        assert "max_depth" in analysis
        assert "fields_used" in analysis
        assert "operators_used" in analysis
        assert "complexity_score" in analysis
        
        assert analysis["field_count"] == 2
        assert analysis["operator_count"] == 1
        assert analysis["max_depth"] >= 1
        assert "age" in analysis["fields_used"]
        assert "status" in analysis["fields_used"]
        assert "AND" in analysis["operators_used"]
    
    def test_ast_optimizer_functionality(self):
        """Test ASTOptimizer functionality used in demo."""
        # Create AST structure
        age_condition = FieldCondition("age", ">", TypedValue("int", 18))
        status_condition = FieldCondition("status", "=", TypedValue("str", "active"))
        and_operator = LogicalOperator("AND", [age_condition, status_condition])
        
        # Test optimizer
        optimizer = ASTOptimizer()
        optimized = optimizer.visit(and_operator)
        
        assert optimized is not None
        assert isinstance(optimized, LogicalOperator)
        assert optimized.operator == "AND"
        assert len(optimized.children) == 2
    
    def test_complex_ast_structure(self):
        """Test complex AST structure creation."""
        # Left side: age > 18 AND status = 'active'
        age_condition = FieldCondition("age", ">", TypedValue("int", 18))
        status_condition = FieldCondition("status", "=", TypedValue("str", "active"))
        left_and = LogicalOperator("AND", [age_condition, status_condition])
        left_paren = ParenExpression(left_and)
        
        # Right side: type = 'DocBlock' AND quality_score >= 0.8
        type_condition = FieldCondition("type", "=", TypedValue("str", "DocBlock"))
        quality_condition = FieldCondition("quality_score", ">=", TypedValue("float", 0.8))
        right_and = LogicalOperator("AND", [type_condition, quality_condition])
        
        # Root: OR
        root_or = LogicalOperator("OR", [left_paren, right_and])
        
        # Test structure
        assert root_or.operator == "OR"
        assert len(root_or.children) == 2
        assert isinstance(root_or.children[0], ParenExpression)
        assert isinstance(root_or.children[1], LogicalOperator)
        
        # Test nested structure
        paren_expr = root_or.children[0]
        assert isinstance(paren_expr.expression, LogicalOperator)
        assert paren_expr.expression.operator == "AND"
        
        right_side = root_or.children[1]
        assert right_side.operator == "AND"
        assert len(right_side.children) == 2
    
    def test_visitor_pattern_accept_method(self):
        """Test accept method for visitor pattern."""
        age_condition = FieldCondition("age", ">", TypedValue("int", 18))
        
        # Test with different visitors
        printer = ASTPrinter()
        validator = ASTValidator()
        analyzer = ASTAnalyzer()
        
        print_result = age_condition.accept(printer)
        valid_result = age_condition.accept(validator)
        analyzer.visit(age_condition)
        
        assert isinstance(print_result, str)
        assert isinstance(valid_result, bool)
        assert valid_result is True
    
    def test_typed_value_creation(self):
        """Test TypedValue creation in demo."""
        int_value = TypedValue("int", 18)
        str_value = TypedValue("str", "active")
        float_value = TypedValue("float", 0.8)
        
        assert int_value.type == "int"
        assert int_value.value == 18
        assert str_value.type == "str"
        assert str_value.value == "active"
        assert float_value.type == "float"
        assert float_value.value == 0.8
    
    def test_field_condition_creation(self):
        """Test FieldCondition creation in demo."""
        condition = FieldCondition("age", ">", TypedValue("int", 18))
        
        assert condition.field == "age"
        assert condition.operator == ">"
        assert condition.value.type == "int"
        assert condition.value.value == 18
        assert condition.node_type == "field_condition"
    
    def test_logical_operator_creation(self):
        """Test LogicalOperator creation in demo."""
        age_condition = FieldCondition("age", ">", TypedValue("int", 18))
        status_condition = FieldCondition("status", "=", TypedValue("str", "active"))
        and_operator = LogicalOperator("AND", [age_condition, status_condition])
        
        assert and_operator.operator == "AND"
        assert len(and_operator.children) == 2
        assert and_operator.children[0] == age_condition
        assert and_operator.children[1] == status_condition
        assert and_operator.node_type == "logical_operator"
    
    def test_paren_expression_creation(self):
        """Test ParenExpression creation in demo."""
        age_condition = FieldCondition("age", ">", TypedValue("int", 18))
        paren_expr = ParenExpression(age_condition)
        
        assert paren_expr.expression == age_condition
        assert paren_expr.node_type == "paren_expression"
    
    def test_ast_depth_calculation(self):
        """Test AST depth calculation."""
        age_condition = FieldCondition("age", ">", TypedValue("int", 18))
        status_condition = FieldCondition("status", "=", TypedValue("str", "active"))
        and_operator = LogicalOperator("AND", [age_condition, status_condition])
        paren_expr = ParenExpression(and_operator)
        
        assert age_condition.depth == 0
        assert and_operator.depth == 1
        assert paren_expr.depth == 2
    
    def test_ast_is_leaf_property(self):
        """Test AST is_leaf property."""
        age_condition = FieldCondition("age", ">", TypedValue("int", 18))
        status_condition = FieldCondition("status", "=", TypedValue("str", "active"))
        and_operator = LogicalOperator("AND", [age_condition, status_condition])
        
        assert age_condition.is_leaf is True
        assert and_operator.is_leaf is False 