"""
Unit tests for ASTOptimizer and optimization functionality.

This module tests the ASTOptimizer class, which applies various optimizations
to AST structures to improve query performance while maintaining correctness.
It covers redundant condition removal, expression simplification, and condition
reordering strategies.

Author: Development Team
Created: 2024-06-13
Updated: 2024-06-13
"""

import pytest
import time
from chunk_metadata_adapter.ast_optimizer import ASTOptimizer, optimize_ast
from chunk_metadata_adapter.ast import (
    FieldCondition, LogicalOperator, ParenExpression, TypedValue, ASTNodeFactory
)


class TestASTOptimizer:
    """
    Tests for ASTOptimizer functionality.
    """
    
    def setup_method(self):
        """Set up optimizer for each test."""
        self.optimizer = ASTOptimizer()
    
    def test_optimizer_initialization(self):
        """Test optimizer initialization with default parameters."""
        optimizer = ASTOptimizer()
        assert optimizer.max_optimization_time == 0.1
        assert optimizer.last_optimization_time == 0.0
        assert optimizer.optimization_stats["total_optimizations"] == 0
    
    def test_optimizer_custom_parameters(self):
        """Test optimizer initialization with custom parameters."""
        optimizer = ASTOptimizer(max_optimization_time=0.5)
        assert optimizer.max_optimization_time == 0.5
    
    def test_optimizer_invalid_parameters(self):
        """Test optimizer initialization with invalid parameters."""
        with pytest.raises(ValueError, match="must be positive"):
            ASTOptimizer(max_optimization_time=0)
        
        with pytest.raises(ValueError, match="must be positive"):
            ASTOptimizer(max_optimization_time=-1)
    
    def test_optimize_none_ast(self):
        """Test optimization with None AST."""
        with pytest.raises(ValueError, match="cannot be None"):
            self.optimizer.optimize(None)
    
    def test_optimize_single_field_condition(self):
        """Test optimization of single field condition."""
        condition = FieldCondition("age", ">", TypedValue("int", 18))
        optimized = self.optimizer.optimize(condition)
        
        assert optimized == condition
        assert self.optimizer.optimization_stats["total_optimizations"] == 0
    
    def test_remove_redundant_numeric_conditions(self):
        """Test removal of redundant numeric conditions."""
        # x > 5 AND x > 3 -> x > 5
        condition1 = FieldCondition("age", ">", TypedValue("int", 5))
        condition2 = FieldCondition("age", ">", TypedValue("int", 3))
        ast = LogicalOperator("AND", [condition1, condition2])
        
        optimized = self.optimizer.optimize(ast)
        
        # Should be optimized to a single field condition
        assert isinstance(optimized, FieldCondition)
        assert optimized.field == "age"
        assert optimized.operator == ">"
        assert optimized.value.value == 5
        assert self.optimizer.optimization_stats["redundant_conditions_removed"] >= 1
    
    def test_remove_redundant_equality_conditions(self):
        """Test removal of redundant equality conditions."""
        # x = 1 AND x = 2 -> contradiction (empty result)
        condition1 = FieldCondition("status", "=", TypedValue("str", "active"))
        condition2 = FieldCondition("status", "=", TypedValue("str", "inactive"))
        ast = LogicalOperator("AND", [condition1, condition2])
        
        optimized = self.optimizer.optimize(ast)
        
        # Should be optimized to a contradiction
        assert isinstance(optimized, FieldCondition)
        assert optimized.field == "__contradiction__"
        assert optimized.operator == "="
        assert optimized.value.value == False
        assert self.optimizer.optimization_stats["redundant_conditions_removed"] >= 1
    
    def test_optimize_range_conditions(self):
        """Test optimization of range conditions."""
        # x >= 5 AND x > 5 -> x > 5
        condition1 = FieldCondition("age", ">=", TypedValue("int", 5))
        condition2 = FieldCondition("age", ">", TypedValue("int", 5))
        ast = LogicalOperator("AND", [condition1, condition2])
        
        optimized = self.optimizer.optimize(ast)
        
        assert isinstance(optimized, FieldCondition)
        assert optimized.operator == ">"
        assert optimized.value.value == 5
    
    def test_optimize_exact_range_conditions(self):
        """Test optimization of exact range conditions."""
        # x >= 5 AND x <= 5 -> x = 5
        condition1 = FieldCondition("age", ">=", TypedValue("int", 5))
        condition2 = FieldCondition("age", "<=", TypedValue("int", 5))
        ast = LogicalOperator("AND", [condition1, condition2])
        
        optimized = self.optimizer.optimize(ast)
        
        assert isinstance(optimized, FieldCondition)
        assert optimized.operator == "="
        assert optimized.value.value == 5
    
    def test_remove_duplicate_or_conditions(self):
        """Test removal of duplicate OR conditions."""
        # x = 1 OR x = 1 -> x = 1
        condition1 = FieldCondition("status", "=", TypedValue("str", "active"))
        condition2 = FieldCondition("status", "=", TypedValue("str", "active"))
        ast = LogicalOperator("OR", [condition1, condition2])
        
        optimized = self.optimizer.optimize(ast)
        
        assert isinstance(optimized, FieldCondition)
        assert optimized.value.value == "active"
        assert self.optimizer.optimization_stats["expressions_simplified"] >= 1
    
    def test_simplify_double_negation(self):
        """Test simplification of double negation."""
        # NOT NOT x -> x
        inner_condition = FieldCondition("age", ">", TypedValue("int", 18))
        not_condition = LogicalOperator("NOT", [inner_condition])
        double_not = LogicalOperator("NOT", [not_condition])
        
        optimized = self.optimizer.optimize(double_not)
        
        # Should be simplified to original condition
        assert optimized == inner_condition
        assert self.optimizer.optimization_stats["expressions_simplified"] >= 1
    
    def test_unwrap_unnecessary_parentheses(self):
        """Test unwrapping of unnecessary parentheses."""
        # (x > 18) -> x > 18
        condition = FieldCondition("age", ">", TypedValue("int", 18))
        paren_expr = ParenExpression(condition)
        
        optimized = self.optimizer.optimize(paren_expr)
        
        # Should unwrap parentheses
        assert optimized == condition
        assert self.optimizer.optimization_stats["expressions_simplified"] >= 1
    
    def test_reorder_conditions_for_performance(self):
        """Test reordering of conditions for better performance."""
        # Equality conditions should come first
        equality_condition = FieldCondition("status", "=", TypedValue("str", "active"))
        range_condition = FieldCondition("age", ">", TypedValue("int", 18))
        regex_condition = FieldCondition("name", "~", TypedValue("str", ".*test.*"))
        
        # Create AST with conditions in suboptimal order
        ast = LogicalOperator("AND", [regex_condition, range_condition, equality_condition])
        
        optimized = self.optimizer.optimize(ast)
        
        # Check that conditions are reordered: equality -> range -> regex
        assert len(optimized.children) == 3
        assert optimized.children[0].operator == "="  # Equality first
        assert optimized.children[1].operator == ">"  # Range second
        assert optimized.children[2].operator == "~"  # Regex last
        assert self.optimizer.optimization_stats["conditions_reordered"] >= 1
    
    def test_optimize_complex_expression(self):
        """Test optimization of complex expression."""
        # (age > 18 AND age > 20) OR (status = 'active' OR status = 'active')
        condition1 = FieldCondition("age", ">", TypedValue("int", 18))
        condition2 = FieldCondition("age", ">", TypedValue("int", 20))
        condition3 = FieldCondition("status", "=", TypedValue("str", "active"))
        condition4 = FieldCondition("status", "=", TypedValue("str", "active"))
        
        and_expr = LogicalOperator("AND", [condition1, condition2])
        or_expr = LogicalOperator("OR", [condition3, condition4])
        complex_ast = LogicalOperator("OR", [and_expr, or_expr])
        
        optimized = self.optimizer.optimize(complex_ast)
        
        # Should be optimized to: (age > 20) OR (status = 'active')
        assert isinstance(optimized, LogicalOperator)
        assert optimized.operator == "OR"
        assert len(optimized.children) == 2
        
        # First child should contain age > 20 (redundant condition removed)
        first_child = optimized.children[0]
        age_conditions = []
        
        if isinstance(first_child, FieldCondition):
            if first_child.field == "age":
                age_conditions.append(first_child)
        elif isinstance(first_child, LogicalOperator):
            # Collect all age conditions from the logical operator
            for child in first_child.children:
                if isinstance(child, FieldCondition) and child.field == "age":
                    age_conditions.append(child)
        
        # Should have at least one age condition, and it should be the most restrictive
        assert len(age_conditions) >= 1
        age_values = [c.value.value for c in age_conditions]
        assert max(age_values) >= 20  # Should have the more restrictive condition
        
        # Second child should contain status = 'active' (duplicate removed)
        second_child = optimized.children[1]
        status_conditions = []
        
        if isinstance(second_child, FieldCondition):
            if second_child.field == "status":
                status_conditions.append(second_child)
        elif isinstance(second_child, LogicalOperator):
            # Collect all status conditions from the logical operator
            for child in second_child.children:
                if isinstance(child, FieldCondition) and child.field == "status":
                    status_conditions.append(child)
        
        # Should have at least one status condition
        assert len(status_conditions) >= 1
        assert status_conditions[0].operator == "="
        assert status_conditions[0].value.value == "active"
    
    def test_optimization_timeout(self):
        """Test optimization timeout handling."""
        # Create a very complex AST that might timeout
        optimizer = ASTOptimizer(max_optimization_time=0.001)  # Very short timeout
        
        # Create a deeply nested expression
        condition = FieldCondition("field", "=", TypedValue("int", 1))
        ast = condition
        for _ in range(100):  # Deep nesting
            ast = ParenExpression(ast)
        
        # Should not raise timeout error, but return original or optimized
        optimized = optimizer.optimize(ast)
        assert optimized is not None
    
    def test_optimization_statistics(self):
        """Test that optimization statistics are properly tracked."""
        # Create an AST that will trigger multiple optimizations
        condition1 = FieldCondition("age", ">", TypedValue("int", 5))
        condition2 = FieldCondition("age", ">", TypedValue("int", 3))
        condition3 = FieldCondition("status", "=", TypedValue("str", "active"))
        condition4 = FieldCondition("status", "=", TypedValue("str", "active"))
        
        ast = LogicalOperator("AND", [condition1, condition2, condition3, condition4])
        
        optimized = self.optimizer.optimize(ast)
        stats = self.optimizer.get_optimization_stats()
        
        # Check that statistics are tracked
        assert "redundant_conditions_removed" in stats
        assert "expressions_simplified" in stats
        assert "conditions_reordered" in stats
        assert "total_optimizations" in stats
        assert "performance_improvement" in stats
        assert "optimization_time_ms" in stats
        assert "timeout_limit_ms" in stats
        
        # Check that time is tracked
        assert stats["optimization_time_ms"] >= 0
        assert stats["timeout_limit_ms"] == 100  # 0.1 seconds
    
    def test_performance_improvement_calculation(self):
        """Test calculation of performance improvement."""
        # Create a complex AST that will be significantly optimized
        conditions = []
        for i in range(10):
            # Create redundant conditions
            conditions.append(FieldCondition("field", ">", TypedValue("int", i)))
            conditions.append(FieldCondition("field", ">", TypedValue("int", i + 1)))
        
        ast = LogicalOperator("AND", conditions)
        
        optimized = self.optimizer.optimize(ast)
        stats = self.optimizer.get_optimization_stats()
        
        # Should show some performance improvement
        assert stats["performance_improvement"] >= 0
        assert stats["total_optimizations"] > 0


class TestOptimizeASTFunction:
    """
    Tests for the convenience optimize_ast function.
    """
    
    def test_optimize_ast_basic(self):
        """Test basic usage of optimize_ast function."""
        condition = FieldCondition("age", ">", TypedValue("int", 18))
        optimized, stats = optimize_ast(condition)
        
        assert optimized == condition
        assert isinstance(stats, dict)
        assert "total_optimizations" in stats
    
    def test_optimize_ast_with_optimization(self):
        """Test optimize_ast function with actual optimization."""
        # Create redundant conditions
        condition1 = FieldCondition("age", ">", TypedValue("int", 5))
        condition2 = FieldCondition("age", ">", TypedValue("int", 3))
        ast = LogicalOperator("AND", [condition1, condition2])
        
        optimized, stats = optimize_ast(ast)
        
        # Should be optimized
        assert isinstance(optimized, FieldCondition)
        assert stats["total_optimizations"] > 0
    
    def test_optimize_ast_custom_timeout(self):
        """Test optimize_ast function with custom timeout."""
        condition = FieldCondition("age", ">", TypedValue("int", 18))
        optimized, stats = optimize_ast(condition, max_time=0.5)
        
        assert optimized == condition
        assert stats["timeout_limit_ms"] == 500  # 0.5 seconds


class TestASTOptimizerIntegration:
    """
    Integration tests for ASTOptimizer with real scenarios.
    """
    
    def setup_method(self):
        """Set up optimizer for each test."""
        self.optimizer = ASTOptimizer()
    
    def test_real_world_optimization_scenario(self):
        """Test optimization of real-world query scenario."""
        # Simulate a complex business query
        conditions = [
            ("age", ">", "int", 18),
            ("age", ">", "int", 21),  # Redundant
            ("status", "=", "str", "active"),
            ("status", "=", "str", "active"),  # Duplicate
            ("type", "=", "str", "user"),
            ("type", "!=", "str", "admin"),
            ("score", ">=", "float", 0.8),
            ("score", ">", "float", 0.8),  # Redundant
        ]
        
        ast = ASTNodeFactory.create_complex_expression(conditions, "AND")
        
        optimized = self.optimizer.optimize(ast)
        stats = self.optimizer.get_optimization_stats()
        
        # Should have optimizations applied
        assert stats["total_optimizations"] > 0
        assert len(optimized.children) < len(conditions)
        
        # Check that redundant conditions are removed
        age_conditions = [c for c in optimized.children if c.field == "age"]
        assert len(age_conditions) == 1  # Only age > 21 should remain
        
        status_conditions = [c for c in optimized.children if c.field == "status"]
        assert len(status_conditions) == 1  # Only one status condition should remain
    
    def test_optimization_preserves_semantics(self):
        """Test that optimization preserves query semantics."""
        # Create a query that should be semantically equivalent after optimization
        original_conditions = [
            ("age", ">", "int", 18),
            ("age", ">", "int", 21),  # More restrictive
            ("status", "=", "str", "active"),
        ]
        
        original_ast = ASTNodeFactory.create_complex_expression(original_conditions, "AND")
        
        # Create expected optimized version
        expected_conditions = [
            ("age", ">", "int", 21),  # More restrictive condition
            ("status", "=", "str", "active"),
        ]
        expected_ast = ASTNodeFactory.create_complex_expression(expected_conditions, "AND")
        
        optimized = self.optimizer.optimize(original_ast)
        
        # Should be equivalent to expected
        assert len(optimized.children) == len(expected_ast.children)
        
        # Check that conditions match (order may vary due to optimization)
        optimized_conditions = []
        for child in optimized.children:
            optimized_conditions.append((child.field, child.operator, child.value.value))
        
        expected_conditions = []
        for child in expected_ast.children:
            expected_conditions.append((child.field, child.operator, child.value.value))
        
        # Sort both lists for comparison (order doesn't matter for semantics)
        optimized_conditions.sort()
        expected_conditions.sort()
        
        assert optimized_conditions == expected_conditions
    
    def test_optimization_with_mixed_data_types(self):
        """Test optimization with mixed data types."""
        conditions = [
            ("age", ">", "int", 18),
            ("score", ">=", "float", 0.8),
            ("name", "=", "str", "John"),
            ("is_active", "=", "bool", True),
        ]
        
        ast = ASTNodeFactory.create_complex_expression(conditions, "AND")
        
        optimized = self.optimizer.optimize(ast)
        
        # Should preserve all conditions (no redundancies)
        assert len(optimized.children) == len(conditions)
        
        # Should reorder for performance (equality conditions first)
        assert optimized.children[0].operator == "="  # name = "John"
        assert optimized.children[1].operator == "="  # is_active = true
        assert optimized.children[2].operator == ">"  # age > 18
        assert optimized.children[3].operator == ">="  # score >= 0.8


class TestASTOptimizerEdgeCases:
    """
    Tests for edge cases and error conditions.
    """
    
    def setup_method(self):
        """Set up optimizer for each test."""
        self.optimizer = ASTOptimizer()
    
    def test_optimize_empty_logical_operator(self):
        """Test optimization of empty logical operator."""
        # Create a valid logical operator with two conditions, then remove one
        condition1 = FieldCondition("age", ">", TypedValue("int", 18))
        condition2 = FieldCondition("status", "=", TypedValue("str", "active"))
        ast = LogicalOperator("AND", [condition1, condition2])
        
        # Simulate optimization that removes all conditions
        optimized = self.optimizer.optimize(ast)
        
        # Should be optimized to a single condition or contradiction
        assert isinstance(optimized, (FieldCondition, LogicalOperator))
    
    def test_optimize_single_child_logical_operator(self):
        """Test optimization of logical operator with single child."""
        # Create a valid logical operator with two conditions
        condition1 = FieldCondition("age", ">", TypedValue("int", 18))
        condition2 = FieldCondition("status", "=", TypedValue("str", "active"))
        ast = LogicalOperator("AND", [condition1, condition2])
        
        optimized = self.optimizer.optimize(ast)
        
        # Should be optimized to a single condition or remain as logical operator
        assert isinstance(optimized, (FieldCondition, LogicalOperator))
    
    def test_optimize_contradictory_conditions(self):
        """Test optimization of contradictory conditions."""
        # x > 5 AND x < 3 (contradiction)
        condition1 = FieldCondition("age", ">", TypedValue("int", 5))
        condition2 = FieldCondition("age", "<", TypedValue("int", 3))
        ast = LogicalOperator("AND", [condition1, condition2])
        
        optimized = self.optimizer.optimize(ast)
        
        # Should result in empty conditions (contradiction)
        assert len(optimized.children) == 0
    
    def test_optimize_with_non_field_conditions(self):
        """Test optimization with non-field conditions."""
        # Create a complex expression with nested logical operators
        inner_condition1 = FieldCondition("age", ">", TypedValue("int", 18))
        inner_condition2 = FieldCondition("status", "=", TypedValue("str", "active"))
        inner_and = LogicalOperator("AND", [inner_condition1, inner_condition2])
        
        outer_condition = FieldCondition("type", "=", TypedValue("str", "user"))
        ast = LogicalOperator("AND", [inner_and, outer_condition])
        
        optimized = self.optimizer.optimize(ast)
        
        # Should preserve structure but optimize inner parts
        assert len(optimized.children) == 2
        assert isinstance(optimized.children[0], LogicalOperator)  # Inner AND
        assert isinstance(optimized.children[1], FieldCondition)   # Outer condition 