"""
Tests for AST Visitor pattern and concrete visitors.

This module provides comprehensive tests for the Visitor pattern implementation,
including ASTPrinter, ASTValidator, ASTAnalyzer, and ASTOptimizer visitors.

Author: Development Team
Created: 2024-01-15
Updated: 2024-01-20
"""

import pytest
from datetime import datetime
from typing import Any, Dict
from chunk_metadata_adapter.ast import (
    TypedValue,
    FieldCondition,
    LogicalOperator,
    ParenExpression,
    ASTVisitor,
    ASTPrinter,
    ASTValidator,
    ASTAnalyzer,
    ASTOptimizer
)


class TestASTVisitor:
    """Tests for abstract ASTVisitor class."""
    
    def test_visitor_is_abstract(self):
        """Test that ASTVisitor is abstract and cannot be instantiated."""
        with pytest.raises(TypeError):
            ASTVisitor()
    
    def test_visitor_interface_methods(self):
        """Test that visitor interface methods exist."""
        # Create a concrete visitor for testing
        class TestVisitor(ASTVisitor):
            def visit_field_condition(self, node: FieldCondition) -> Any:
                return "field_visited"
            
            def visit_logical_operator(self, node: LogicalOperator) -> Any:
                return "logical_visited"
            
            def visit_paren_expression(self, node: ParenExpression) -> Any:
                return "paren_visited"
        
        visitor = TestVisitor()
        assert hasattr(visitor, 'visit_field_condition')
        assert hasattr(visitor, 'visit_logical_operator')
        assert hasattr(visitor, 'visit_paren_expression')
        assert hasattr(visitor, 'visit')


class TestASTPrinter:
    """Tests for ASTPrinter visitor."""
    
    def test_print_simple_field_condition(self):
        """Test printing a simple field condition."""
        condition = FieldCondition("age", ">", TypedValue("int", 18))
        printer = ASTPrinter()
        result = condition.accept(printer)
        
        expected = "FieldCondition: age > 18"
        assert result == expected
    
    def test_print_logical_operator(self):
        """Test printing a logical operator."""
        left = FieldCondition("age", ">", TypedValue("int", 18))
        right = FieldCondition("status", "=", TypedValue("str", "active"))
        op = LogicalOperator("AND", [left, right])
        
        printer = ASTPrinter()
        result = op.accept(printer)
        
        expected_lines = [
            "LogicalOperator: AND",
            "  FieldCondition: age > 18",
            "  FieldCondition: status = \"active\""
        ]
        assert result == "\n".join(expected_lines)
    
    def test_print_paren_expression(self):
        """Test printing a parenthesized expression."""
        inner = FieldCondition("age", ">", TypedValue("int", 18))
        paren = ParenExpression(inner)
        
        printer = ASTPrinter()
        result = paren.accept(printer)
        
        expected_lines = [
            "ParenExpression:",
            "  FieldCondition: age > 18"
        ]
        assert result == "\n".join(expected_lines)
    
    def test_print_complex_expression(self):
        """Test printing a complex expression with multiple levels."""
        # Create: (age > 18 AND status = 'active') OR (type = 'DocBlock')
        
        # Left side: age > 18 AND status = 'active'
        age_condition = FieldCondition("age", ">", TypedValue("int", 18))
        status_condition = FieldCondition("status", "=", TypedValue("str", "active"))
        left_and = LogicalOperator("AND", [age_condition, status_condition])
        left_paren = ParenExpression(left_and)
        
        # Right side: type = 'DocBlock'
        type_condition = FieldCondition("type", "=", TypedValue("str", "DocBlock"))
        
        # Root: OR
        root_or = LogicalOperator("OR", [left_paren, type_condition])
        
        printer = ASTPrinter()
        result = root_or.accept(printer)
        
        expected_lines = [
            "LogicalOperator: OR",
            "  ParenExpression:",
            "    LogicalOperator: AND",
            "      FieldCondition: age > 18",
            "      FieldCondition: status = \"active\"",
            "  FieldCondition: type = \"DocBlock\""
        ]
        assert result == "\n".join(expected_lines)
    
    def test_print_with_custom_indent(self):
        """Test printing with custom indentation."""
        condition = FieldCondition("age", ">", TypedValue("int", 18))
        printer = ASTPrinter(indent=2)
        result = condition.accept(printer)
        
        expected = "    FieldCondition: age > 18"
        assert result == expected


class TestASTValidator:
    """Tests for ASTValidator visitor."""
    
    def test_validate_valid_field_condition(self):
        """Test validation of valid field condition."""
        condition = FieldCondition("age", ">", TypedValue("int", 18))
        validator = ASTValidator()
        result = condition.accept(validator)
        
        assert result == True
        assert len(validator.errors) == 0
    
    def test_validate_invalid_field_condition(self):
        """Test validation of invalid field condition."""
        # Create invalid condition (will be caught by __post_init__)
        with pytest.raises(ValueError):
            FieldCondition("123field", ">", TypedValue("int", 18))
    
    def test_validate_valid_logical_operator(self):
        """Test validation of valid logical operator."""
        left = FieldCondition("age", ">", TypedValue("int", 18))
        right = FieldCondition("status", "=", TypedValue("str", "active"))
        op = LogicalOperator("AND", [left, right])
        
        validator = ASTValidator()
        result = op.accept(validator)
        
        assert result == True
        assert len(validator.errors) == 0
    
    def test_validate_invalid_logical_operator(self):
        """Test validation of invalid logical operator."""
        # NOT with wrong number of children
        child = FieldCondition("age", ">", TypedValue("int", 18))
        with pytest.raises(ValueError):
            LogicalOperator("NOT", [child, child])
    
    def test_validate_paren_expression(self):
        """Test validation of parenthesized expression."""
        inner = FieldCondition("age", ">", TypedValue("int", 18))
        paren = ParenExpression(inner)
        
        validator = ASTValidator()
        result = paren.accept(validator)
        
        assert result == True
        assert len(validator.errors) == 0
    
    def test_validate_complex_expression(self):
        """Test validation of complex expression."""
        # Create complex expression
        age_condition = FieldCondition("age", ">", TypedValue("int", 18))
        status_condition = FieldCondition("status", "=", TypedValue("str", "active"))
        and_op = LogicalOperator("AND", [age_condition, status_condition])
        paren = ParenExpression(and_op)
        
        validator = ASTValidator()
        result = paren.accept(validator)
        
        assert result == True
        assert len(validator.errors) == 0


class TestASTAnalyzer:
    """Tests for ASTAnalyzer visitor."""
    
    def test_analyze_simple_field_condition(self):
        """Test analysis of simple field condition."""
        condition = FieldCondition("age", ">", TypedValue("int", 18))
        analyzer = ASTAnalyzer()
        result = condition.accept(analyzer)
        
        assert result["type"] == "field_condition"
        assert result["field"] == "age"
        assert result["operator"] == ">"
        
        analysis = analyzer.get_analysis()
        assert analysis["field_count"] == 1
        assert analysis["operator_count"] == 0
        assert analysis["max_depth"] == 0
        assert "age" in analysis["fields_used"]
        assert ">" in analysis["operators_used"]
    
    def test_analyze_logical_operator(self):
        """Test analysis of logical operator."""
        left = FieldCondition("age", ">", TypedValue("int", 18))
        right = FieldCondition("status", "=", TypedValue("str", "active"))
        op = LogicalOperator("AND", [left, right])
        
        analyzer = ASTAnalyzer()
        result = op.accept(analyzer)
        
        assert result["type"] == "logical_operator"
        assert result["operator"] == "AND"
        assert len(result["children"]) == 2
        
        analysis = analyzer.get_analysis()
        assert analysis["field_count"] == 2
        assert analysis["operator_count"] == 1
        assert analysis["max_depth"] == 1
        assert "age" in analysis["fields_used"]
        assert "status" in analysis["fields_used"]
        assert ">" in analysis["operators_used"]
        assert "=" in analysis["operators_used"]
        assert "AND" in analysis["operators_used"]
    
    def test_analyze_paren_expression(self):
        """Test analysis of parenthesized expression."""
        inner = FieldCondition("age", ">", TypedValue("int", 18))
        paren = ParenExpression(inner)
        
        analyzer = ASTAnalyzer()
        result = paren.accept(analyzer)
        
        assert result["type"] == "paren_expression"
        assert "expression" in result
        
        analysis = analyzer.get_analysis()
        assert analysis["field_count"] == 1
        assert analysis["operator_count"] == 0
        assert analysis["max_depth"] == 1
    
    def test_analyze_complex_expression(self):
        """Test analysis of complex expression."""
        # Create complex expression
        age_condition = FieldCondition("age", ">", TypedValue("int", 18))
        status_condition = FieldCondition("status", "=", TypedValue("str", "active"))
        and_op = LogicalOperator("AND", [age_condition, status_condition])
        type_condition = FieldCondition("type", "=", TypedValue("str", "DocBlock"))
        or_op = LogicalOperator("OR", [and_op, type_condition])
        
        analyzer = ASTAnalyzer()
        result = or_op.accept(analyzer)
        
        analysis = analyzer.get_analysis()
        assert analysis["field_count"] == 3
        assert analysis["operator_count"] == 2
        assert analysis["max_depth"] == 2
        assert len(analysis["fields_used"]) == 3
        assert len(analysis["operators_used"]) == 4  # >, =, AND, OR
        assert analysis["complexity_score"] == 7  # 3 + 2 + 2
    
    def test_analyze_real_world_expression(self):
        """Test analysis with real-world SemanticChunk fields."""
        conditions = [
            FieldCondition("type", "=", TypedValue("str", "DocBlock")),
            FieldCondition("quality_score", ">=", TypedValue("float", 0.8)),
            FieldCondition("year", ">=", TypedValue("int", 2020)),
            FieldCondition("is_public", "=", TypedValue("bool", True)),
            FieldCondition("tags", "intersects", TypedValue("list", ["ai", "ml"])),
        ]
        
        and_op = LogicalOperator("AND", conditions)
        
        analyzer = ASTAnalyzer()
        result = and_op.accept(analyzer)
        
        analysis = analyzer.get_analysis()
        assert analysis["field_count"] == 5
        assert analysis["operator_count"] == 1
        assert len(analysis["fields_used"]) == 5
        assert "type" in analysis["fields_used"]
        assert "quality_score" in analysis["fields_used"]
        assert "year" in analysis["fields_used"]
        assert "is_public" in analysis["fields_used"]
        assert "tags" in analysis["fields_used"]


class TestASTOptimizer:
    """Tests for ASTOptimizer visitor."""
    
    def test_optimize_field_condition(self):
        """Test optimization of field condition."""
        condition = FieldCondition("age", ">", TypedValue("int", 18))
        optimizer = ASTOptimizer()
        result = condition.accept(optimizer)
        
        # Field conditions should remain unchanged
        assert result == condition
        assert result.field == "age"
        assert result.operator == ">"
    
    def test_optimize_logical_operator(self):
        """Test optimization of logical operator."""
        left = FieldCondition("age", ">", TypedValue("int", 18))
        right = FieldCondition("status", "=", TypedValue("str", "active"))
        op = LogicalOperator("AND", [left, right])
        
        optimizer = ASTOptimizer()
        result = op.accept(optimizer)
        
        assert isinstance(result, LogicalOperator)
        assert result.operator == "AND"
        assert len(result.children) == 2
    
    def test_optimize_paren_expression(self):
        """Test optimization of parenthesized expression."""
        inner = FieldCondition("age", ">", TypedValue("int", 18))
        paren = ParenExpression(inner)
        
        optimizer = ASTOptimizer()
        result = paren.accept(optimizer)
        
        # Single field condition should be unwrapped
        assert isinstance(result, FieldCondition)
        assert result.field == "age"
        assert result.operator == ">"
    
    def test_optimize_complex_expression(self):
        """Test optimization of complex expression."""
        # Create: ((age > 18)) AND (status = 'active')
        inner = FieldCondition("age", ">", TypedValue("int", 18))
        paren1 = ParenExpression(inner)
        paren2 = ParenExpression(paren1)
        
        status_condition = FieldCondition("status", "=", TypedValue("str", "active"))
        paren3 = ParenExpression(status_condition)
        
        and_op = LogicalOperator("AND", [paren2, paren3])
        
        optimizer = ASTOptimizer()
        result = and_op.accept(optimizer)
        
        assert isinstance(result, LogicalOperator)
        assert result.operator == "AND"
        assert len(result.children) == 2
        
        # Both children should be unwrapped field conditions
        assert isinstance(result.children[0], FieldCondition)
        assert isinstance(result.children[1], FieldCondition)
        assert result.children[0].field == "age"
        assert result.children[1].field == "status"
    
    def test_remove_duplicate_conditions(self):
        """Test removal of duplicate conditions in OR operator."""
        condition1 = FieldCondition("age", ">", TypedValue("int", 18))
        condition2 = FieldCondition("status", "=", TypedValue("str", "active"))
        
        # Create OR with duplicate conditions
        or_op = LogicalOperator("OR", [condition1, condition1, condition2])
        
        optimizer = ASTOptimizer()
        result = or_op.accept(optimizer)
        
        assert isinstance(result, LogicalOperator)
        assert result.operator == "OR"
        # Duplicate should be removed
        assert len(result.children) == 2


class TestVisitorIntegration:
    """Integration tests for visitor pattern."""
    
    def test_full_visitor_workflow(self):
        """Test complete visitor workflow on complex AST."""
        # Create complex AST: (age > 18 AND status = 'active') OR (type = 'DocBlock')
        
        # Left side: age > 18 AND status = 'active'
        age_condition = FieldCondition("age", ">", TypedValue("int", 18))
        status_condition = FieldCondition("status", "=", TypedValue("str", "active"))
        left_and = LogicalOperator("AND", [age_condition, status_condition])
        left_paren = ParenExpression(left_and)
        
        # Right side: type = 'DocBlock'
        type_condition = FieldCondition("type", "=", TypedValue("str", "DocBlock"))
        
        # Root: OR
        root_or = LogicalOperator("OR", [left_paren, type_condition])
        
        # Test all visitors
        # 1. Printer
        printer = ASTPrinter()
        print_result = root_or.accept(printer)
        assert "LogicalOperator: OR" in print_result
        assert "FieldCondition: age > 18" in print_result
        
        # 2. Validator
        validator = ASTValidator()
        valid_result = root_or.accept(validator)
        assert valid_result == True
        assert len(validator.errors) == 0
        
        # 3. Analyzer
        analyzer = ASTAnalyzer()
        analysis_result = root_or.accept(analyzer)
        analysis = analyzer.get_analysis()
        assert analysis["field_count"] == 3
        assert analysis["operator_count"] == 2
        assert analysis["max_depth"] == 3
        
        # 4. Optimizer
        optimizer = ASTOptimizer()
        optimized_result = root_or.accept(optimizer)
        assert isinstance(optimized_result, LogicalOperator)
        assert optimized_result.operator == "OR"
    
    def test_visitor_with_real_world_data(self):
        """Test visitors with real-world SemanticChunk filter expressions."""
        # Real-world filter: quality_score >= 0.8 AND (type = 'DocBlock' OR type = 'CodeBlock')
        
        quality_condition = FieldCondition("quality_score", ">=", TypedValue("float", 0.8))
        
        type1_condition = FieldCondition("type", "=", TypedValue("str", "DocBlock"))
        type2_condition = FieldCondition("type", "=", TypedValue("str", "CodeBlock"))
        type_or = LogicalOperator("OR", [type1_condition, type2_condition])
        type_paren = ParenExpression(type_or)
        
        root_and = LogicalOperator("AND", [quality_condition, type_paren])
        
        # Test analyzer
        analyzer = ASTAnalyzer()
        analyzer.visit(root_and)
        analysis = analyzer.get_analysis()
        
        assert analysis["field_count"] == 3
        assert analysis["operator_count"] == 2
        assert "quality_score" in analysis["fields_used"]
        assert "type" in analysis["fields_used"]
        assert ">=" in analysis["operators_used"]
        assert "=" in analysis["operators_used"]
        assert "AND" in analysis["operators_used"]
        assert "OR" in analysis["operators_used"]
        
        # Test optimizer
        optimizer = ASTOptimizer()
        optimized = optimizer.visit(root_and)
        assert isinstance(optimized, LogicalOperator)
        assert optimized.operator == "AND"
        assert len(optimized.children) == 2 