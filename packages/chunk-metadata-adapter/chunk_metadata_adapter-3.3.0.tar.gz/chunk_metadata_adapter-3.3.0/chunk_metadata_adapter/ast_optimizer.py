"""
AST optimizer for query performance improvement.

This module provides the ASTOptimizer class, which applies various optimizations
to Abstract Syntax Trees to improve query performance while maintaining correctness.
It includes strategies for removing redundant conditions, simplifying expressions,
and reordering conditions for better execution efficiency.

Key features:
- Redundant condition removal (x > 5 AND x > 3 -> x > 5)
- Expression simplification (NOT NOT x -> x, x AND x -> x)
- Condition reordering for better performance
- Performance analysis and optimization metrics
- Safety validation to ensure correctness

Usage examples:
    >>> optimizer = ASTOptimizer()
    >>> optimized_ast = optimizer.optimize(original_ast)
    >>> print(f"Optimization time: {optimizer.last_optimization_time}ms")

Dependencies:
- ast_nodes: For AST structures and visitors
- filter_parser: For parsing queries into AST
- query_validator: For validation after optimization
- complexity_analyzer: For complexity analysis

Author: Development Team
Created: 2024-06-13
Updated: 2024-06-13
"""

import time
from typing import List, Dict, Any, Optional, Tuple
from .ast import (
    ASTNode, ASTVisitor, FieldCondition, LogicalOperator, 
    ParenExpression, TypedValue, ASTNodeFactory
)
from .query_validator import QueryValidator
from .complexity_analyzer import analyze_complexity


class ASTOptimizer(ASTVisitor):
    """
    Optimizer for Abstract Syntax Trees.
    
    This class applies various optimizations to AST structures to improve
    query performance while maintaining semantic correctness. It uses
    the Visitor pattern to traverse and transform AST nodes.
    
    Attributes:
        max_optimization_time (float): Maximum time for optimization in seconds
        last_optimization_time (float): Time taken for last optimization
        optimization_stats (Dict[str, Any]): Statistics about optimizations applied
        validator (QueryValidator): Validator for ensuring correctness
    
    Methods:
        optimize(ast): Optimize AST for better performance
        _remove_redundant_conditions(ast): Remove redundant conditions
        _simplify_expressions(ast): Simplify expressions
        _reorder_conditions(ast): Reorder conditions for performance
    
    Usage examples:
        >>> optimizer = ASTOptimizer()
        >>> optimized_ast = optimizer.optimize(original_ast)
        >>> print(f"Optimizations applied: {optimizer.optimization_stats}")
    
    Raises:
        ValueError: When optimization parameters are invalid
        TimeoutError: When optimization exceeds time limit
    """
    
    def __init__(self, max_optimization_time: float = 0.1) -> None:
        """
        Initialize ASTOptimizer with optimization parameters.
        
        Args:
            max_optimization_time: Maximum time for optimization in seconds
        
        Raises:
            ValueError: When max_optimization_time is not positive
        """
        if max_optimization_time <= 0:
            raise ValueError("max_optimization_time must be positive")
        
        self.max_optimization_time = max_optimization_time
        self.last_optimization_time = 0.0
        self.optimization_stats = {
            "redundant_conditions_removed": 0,
            "expressions_simplified": 0,
            "conditions_reordered": 0,
            "total_optimizations": 0,
            "performance_improvement": 0.0
        }
        self.validator = QueryValidator()
        self.start_time = 0.0
    
    def optimize(self, ast: ASTNode) -> ASTNode:
        """
        Optimize AST for better performance.
        
        This method applies a series of optimizations to the AST:
        1. Remove redundant conditions
        2. Simplify expressions
        3. Reorder conditions for better performance
        
        Args:
            ast: AST node to optimize
            
        Returns:
            ASTNode: Optimized AST node
            
        Raises:
            TimeoutError: When optimization exceeds time limit
            ValueError: When AST is invalid
        """
        if ast is None:
            raise ValueError("AST cannot be None")
        
        self.start_time = time.time()
        self.optimization_stats = {
            "redundant_conditions_removed": 0,
            "expressions_simplified": 0,
            "conditions_reordered": 0,
            "total_optimizations": 0,
            "performance_improvement": 0.0
        }
        
        try:
            # Apply optimizations
            optimized = ast.accept(self)
            
            # Validate that optimization didn't break correctness
            validation_result = self.validator.validate_ast(optimized)
            if not validation_result.is_valid:
                # If optimization broke something, return original
                return ast
            
            # Calculate performance improvement
            original_complexity = analyze_complexity(ast)
            optimized_complexity = analyze_complexity(optimized)
            
            original_score = original_complexity.get("complexity_score", 0)
            optimized_score = optimized_complexity.get("complexity_score", 0)
            
            if original_score > 0:
                self.optimization_stats["performance_improvement"] = (
                    (original_score - optimized_score) / original_score * 100
                )
            
            return optimized
            
        except Exception as e:
            # If optimization fails, return original AST
            return ast
        finally:
            self.last_optimization_time = time.time() - self.start_time
    
    def visit_field_condition(self, node: FieldCondition) -> ASTNode:
        """
        Visit a field condition node.
        
        Field conditions are already optimized, so we return them as-is.
        
        Args:
            node: Field condition node to visit
            
        Returns:
            ASTNode: The same field condition node
        """
        return node
    
    def visit_logical_operator(self, node: LogicalOperator) -> ASTNode:
        """
        Visit a logical operator node.
        
        This method applies optimizations specific to logical operators:
        - For AND: Remove redundant conditions
        - For OR: Remove duplicate conditions
        - For NOT: Simplify double negations
        
        Args:
            node: Logical operator node to visit
            
        Returns:
            ASTNode: Optimized logical operator node
        """
        self._check_timeout()
        
        # Handle double negation first (before optimizing children)
        if node.operator == "NOT" and len(node.children) == 1:
            child = node.children[0]
            if isinstance(child, LogicalOperator) and child.operator == "NOT":
                self.optimization_stats["expressions_simplified"] += 1
                # Optimize the inner expression and return it
                child_visitor = ASTOptimizer(self.max_optimization_time)
                return child.children[0].accept(child_visitor)
        
        # Optimize children
        optimized_children = []
        for child in node.children:
            child_visitor = ASTOptimizer(self.max_optimization_time)
            optimized_child = child.accept(child_visitor)
            optimized_children.append(optimized_child)
        
        # Apply operator-specific optimizations
        if node.operator == "AND":
            optimized_children = self._remove_redundant_conditions(optimized_children)
            optimized_children = self._reorder_conditions(optimized_children)
        elif node.operator == "OR":
            optimized_children = self._remove_duplicate_conditions(optimized_children)
        
        # If we have no children after optimization, return a contradiction
        if len(optimized_children) == 0:
            # Return a condition that is always false
            return FieldCondition("__contradiction__", "=", TypedValue("bool", False))
        
        # If we have only one child after optimization, return it directly
        if len(optimized_children) == 1:
            return optimized_children[0]
        
        # Create new optimized node
        optimized_node = LogicalOperator(operator=node.operator, children=optimized_children)
        return optimized_node
    
    def visit_paren_expression(self, node: ParenExpression) -> ASTNode:
        """
        Visit a parenthesized expression node.
        
        This method optimizes the expression inside parentheses and
        may unwrap unnecessary parentheses.
        
        Args:
            node: Parenthesized expression node to visit
            
        Returns:
            ASTNode: Optimized expression (may be unwrapped)
        """
        self._check_timeout()
        
        # Optimize the expression inside parentheses
        child_visitor = ASTOptimizer(self.max_optimization_time)
        optimized_expression = node.expression.accept(child_visitor)
        
        # If the expression is already a single node, unwrap it
        if isinstance(optimized_expression, (FieldCondition, LogicalOperator)):
            self.optimization_stats["expressions_simplified"] += 1
            return optimized_expression
        
        # Otherwise, keep the parentheses
        return ParenExpression(expression=optimized_expression)
    
    def _remove_redundant_conditions(self, children: List[ASTNode]) -> List[ASTNode]:
        """
        Remove redundant conditions from AND operator.
        
        Examples:
            - x > 5 AND x > 3 -> x > 5
            - x = 1 AND x = 2 -> False (contradiction)
            - x >= 5 AND x > 5 -> x > 5
        
        Args:
            children: List of child nodes
            
        Returns:
            List[ASTNode]: List with redundant conditions removed
        """
        if len(children) < 2:
            return children
        
        # Group conditions by field
        field_conditions: Dict[str, List[FieldCondition]] = {}
        other_conditions = []
        
        for child in children:
            if isinstance(child, FieldCondition):
                field = child.field
                if field not in field_conditions:
                    field_conditions[field] = []
                field_conditions[field].append(child)
            else:
                other_conditions.append(child)
        
        # Optimize each field's conditions
        optimized_conditions = []
        for field, conditions in field_conditions.items():
            if len(conditions) == 1:
                optimized_conditions.append(conditions[0])
            else:
                # Apply field-specific optimizations
                optimized = self._optimize_field_conditions(conditions)
                optimized_conditions.extend(optimized)
        
        # Add back other conditions
        optimized_conditions.extend(other_conditions)
        
        removed_count = len(children) - len(optimized_conditions)
        self.optimization_stats["redundant_conditions_removed"] += removed_count
        self.optimization_stats["total_optimizations"] += removed_count
        
        return optimized_conditions
    
    def _optimize_field_conditions(self, conditions: List[FieldCondition]) -> List[FieldCondition]:
        """
        Optimize conditions for a specific field.
        
        Args:
            conditions: List of conditions for the same field
            
        Returns:
            List[FieldCondition]: Optimized conditions
        """
        if len(conditions) <= 1:
            return conditions
        
        # Group by operator type
        numeric_conditions = []
        equality_conditions = []
        other_conditions = []
        
        for condition in conditions:
            if condition.operator in [">", ">=", "<", "<="]:
                numeric_conditions.append(condition)
            elif condition.operator in ["=", "!="]:
                equality_conditions.append(condition)
            else:
                other_conditions.append(condition)
        
        optimized = []
        
        # Optimize numeric conditions
        if numeric_conditions:
            best_numeric = self._find_best_numeric_condition(numeric_conditions)
            if best_numeric:
                optimized.append(best_numeric)
        
        # Optimize equality conditions
        if equality_conditions:
            optimized_equality = self._optimize_equality_conditions(equality_conditions)
            optimized.extend(optimized_equality)
        
        # Add other conditions
        optimized.extend(other_conditions)
        
        return optimized
    
    def _find_best_numeric_condition(self, conditions: List[FieldCondition]) -> Optional[FieldCondition]:
        """
        Find the most restrictive numeric condition.
        
        Args:
            conditions: List of numeric conditions
            
        Returns:
            Optional[FieldCondition]: Best condition or None if contradiction
        """
        if not conditions:
            return None
        
        # Separate lower and upper bounds
        lower_bounds = []
        upper_bounds = []
        
        for condition in conditions:
            if condition.operator in [">", ">="]:
                lower_bounds.append(condition)
            elif condition.operator in ["<", "<="]:
                upper_bounds.append(condition)
        
        # Find best lower bound
        best_lower = None
        if lower_bounds:
            # Group by value and find the most restrictive
            value_groups = {}
            for condition in lower_bounds:
                value = self._get_numeric_value(condition)
                if value not in value_groups:
                    value_groups[value] = []
                value_groups[value].append(condition)
            
            # Find the highest value
            max_value = max(value_groups.keys())
            max_conditions = value_groups[max_value]
            
            # Among conditions with the same value, prefer the more restrictive operator
            if len(max_conditions) > 1:
                # Prefer ">" over ">=" for the same value
                strict_conditions = [c for c in max_conditions if c.operator == ">"]
                if strict_conditions:
                    best_lower = strict_conditions[0]
                else:
                    best_lower = max_conditions[0]
            else:
                best_lower = max_conditions[0]
        
        # Find best upper bound
        best_upper = None
        if upper_bounds:
            # Group by value and find the most restrictive
            value_groups = {}
            for condition in upper_bounds:
                value = self._get_numeric_value(condition)
                if value not in value_groups:
                    value_groups[value] = []
                value_groups[value].append(condition)
            
            # Find the lowest value
            min_value = min(value_groups.keys())
            min_conditions = value_groups[min_value]
            
            # Among conditions with the same value, prefer the more restrictive operator
            if len(min_conditions) > 1:
                # Prefer "<" over "<=" for the same value
                strict_conditions = [c for c in min_conditions if c.operator == "<"]
                if strict_conditions:
                    best_upper = strict_conditions[0]
                else:
                    best_upper = min_conditions[0]
            else:
                best_upper = min_conditions[0]
        
        # Check for contradictions
        if best_lower and best_upper:
            lower_val = self._get_numeric_value(best_lower)
            upper_val = self._get_numeric_value(best_upper)
            
            if lower_val > upper_val:
                return None  # Contradiction
            elif lower_val == upper_val:
                # Check if both are inclusive
                if (best_lower.operator == ">=" and best_upper.operator == "<="):
                    return ASTNodeFactory.create_field_condition(
                        best_lower.field, "=", best_lower.value
                    )
        
        # Return the most restrictive condition
        if best_lower and best_upper:
            return best_lower  # Prefer lower bound
        elif best_lower:
            return best_lower
        elif best_upper:
            return best_upper
        

        
        return None
    
    def _get_numeric_value(self, condition: FieldCondition) -> float:
        """Get numeric value from condition for comparison."""
        if condition.value.type in ["int", "float"]:
            return float(condition.value.value)
        return 0.0
    
    def _optimize_equality_conditions(self, conditions: List[FieldCondition]) -> List[FieldCondition]:
        """
        Optimize equality conditions.
        
        Args:
            conditions: List of equality conditions
            
        Returns:
            List[FieldCondition]: Optimized conditions
        """
        if len(conditions) <= 1:
            return conditions
        
        # Check for contradictions: x = 1 AND x = 2
        values = set()
        for condition in conditions:
            if condition.operator == "=":
                values.add(str(condition.value))
            elif condition.operator == "!=":
                # For != conditions, we need to keep them
                pass
        
        if len(values) > 1:
            # Contradiction found
            return []
        
        # Return the most specific condition
        return [conditions[0]]
    
    def _remove_duplicate_conditions(self, children: List[ASTNode]) -> List[ASTNode]:
        """
        Remove duplicate conditions from OR operator.
        
        Examples:
            - x = 1 OR x = 1 -> x = 1
            - x > 5 OR x > 5 -> x > 5
        
        Args:
            children: List of child nodes
            
        Returns:
            List[ASTNode]: List with duplicates removed
        """
        seen = []
        result = []
        
        for child in children:
            # Create a hashable representation for comparison
            child_repr = str(child)
            if child_repr not in seen:
                seen.append(child_repr)
                result.append(child)
        
        removed_count = len(children) - len(result)
        self.optimization_stats["expressions_simplified"] += removed_count
        self.optimization_stats["total_optimizations"] += removed_count
        
        return result
    
    def _reorder_conditions(self, children: List[ASTNode]) -> List[ASTNode]:
        """
        Reorder conditions for better performance.
        
        This method reorders conditions to put faster operations first:
        1. Equality conditions (fastest)
        2. Simple comparisons
        3. Complex operations (regex, list operations)
        
        Args:
            children: List of child nodes
            
        Returns:
            List[ASTNode]: Reordered list of conditions
        """
        if len(children) < 2:
            return children
        
        # Categorize conditions by performance
        fast_conditions = []
        medium_conditions = []
        slow_conditions = []
        
        for child in children:
            if isinstance(child, FieldCondition):
                if child.operator in ["=", "!="]:
                    fast_conditions.append(child)
                elif child.operator in [">", ">=", "<", "<="]:
                    medium_conditions.append(child)
                else:
                    slow_conditions.append(child)
            else:
                # Complex expressions go last
                slow_conditions.append(child)
        
        # Reorder: fast -> medium -> slow
        reordered = fast_conditions + medium_conditions + slow_conditions
        
        if reordered != children:
            self.optimization_stats["conditions_reordered"] += 1
            self.optimization_stats["total_optimizations"] += 1
        
        return reordered
    
    def _check_timeout(self) -> None:
        """Check if optimization has exceeded time limit."""
        if time.time() - self.start_time > self.max_optimization_time:
            raise TimeoutError("Optimization exceeded time limit")
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """
        Get statistics about optimizations applied.
        
        Returns:
            Dict[str, Any]: Optimization statistics
        """
        return {
            **self.optimization_stats,
            "optimization_time_ms": self.last_optimization_time * 1000,
            "timeout_limit_ms": self.max_optimization_time * 1000
        }


def optimize_ast(ast: ASTNode, max_time: float = 0.1) -> Tuple[ASTNode, Dict[str, Any]]:
    """
    Convenience function to optimize an AST.
    
    Args:
        ast: AST node to optimize
        max_time: Maximum optimization time in seconds
        
    Returns:
        Tuple[ASTNode, Dict[str, Any]]: Optimized AST and statistics
    """
    optimizer = ASTOptimizer(max_time)
    optimized_ast = optimizer.optimize(ast)
    stats = optimizer.get_optimization_stats()
    return optimized_ast, stats 