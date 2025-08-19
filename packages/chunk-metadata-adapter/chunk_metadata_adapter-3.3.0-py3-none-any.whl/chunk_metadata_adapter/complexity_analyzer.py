"""
Complexity analyzer for AST nodes.

This module provides functionality to analyze the complexity of AST structures,
including depth analysis, condition counting, and performance metrics.
"""

from typing import Dict, Any, List
from .ast import ASTNode, ASTVisitor, FieldCondition, LogicalOperator, ParenExpression


class ComplexityAnalyzer(ASTVisitor):
    """
    Analyzer for AST complexity metrics.
    
    This visitor calculates various complexity metrics for AST structures:
    - Maximum depth
    - Total number of conditions
    - Operator distribution
    - Field distribution
    """
    
    def __init__(self):
        self.max_depth = 0
        self.total_conditions = 0
        self.operator_distribution = {}
        self.field_distribution = {}
        self.current_depth = 0
    
    def visit_field_condition(self, node: FieldCondition) -> Dict[str, Any]:
        """Analyze field condition complexity."""
        self.current_depth += 1
        self.max_depth = max(self.max_depth, self.current_depth)
        self.total_conditions += 1
        
        # Track operator distribution
        self.operator_distribution[node.operator] = self.operator_distribution.get(node.operator, 0) + 1
        
        # Track field distribution
        self.field_distribution[node.field] = self.field_distribution.get(node.field, 0) + 1
        
        self.current_depth -= 1
        
        return {
            "type": "field_condition",
            "field": node.field,
            "operator": node.operator,
            "depth": self.current_depth + 1,
            "condition_count": 1
        }
    
    def visit_logical_operator(self, node: LogicalOperator) -> Dict[str, Any]:
        """Analyze logical operator complexity."""
        self.current_depth += 1
        self.max_depth = max(self.max_depth, self.current_depth)
        
        # Analyze children
        children_results = []
        total_conditions = 0
        
        for child in node.children:
            child_result = child.accept(self)
            children_results.append(child_result)
            total_conditions += child_result.get("condition_count", 0)
        
        self.total_conditions += total_conditions
        
        # Track operator distribution
        self.operator_distribution[node.operator] = self.operator_distribution.get(node.operator, 0) + 1
        
        self.current_depth -= 1
        
        return {
            "type": "logical_operator",
            "operator": node.operator,
            "children": children_results,
            "max_depth": self.max_depth,
            "total_conditions": total_conditions,
            "operator_distribution": self.operator_distribution.copy(),
            "field_distribution": self.field_distribution.copy()
        }
    
    def visit_paren_expression(self, node: ParenExpression) -> Dict[str, Any]:
        """Analyze parenthesized expression complexity."""
        self.current_depth += 1
        self.max_depth = max(self.max_depth, self.current_depth)
        
        # Analyze inner expression
        inner_result = node.expression.accept(self)
        
        self.current_depth -= 1
        
        return {
            "type": "paren_expression",
            "expression": inner_result,
            "max_depth": self.max_depth,
            "total_conditions": inner_result.get("total_conditions", 0),
            "operator_distribution": self.operator_distribution.copy(),
            "field_distribution": self.field_distribution.copy()
        }
    
    def get_complexity_metrics(self) -> Dict[str, Any]:
        """Get final complexity metrics."""
        return {
            "max_depth": self.max_depth,
            "total_conditions": self.total_conditions,
            "operator_distribution": self.operator_distribution,
            "field_distribution": self.field_distribution
        }


def analyze_complexity(ast: ASTNode) -> Dict[str, Any]:
    """
    Analyze complexity of an AST node.
    
    Args:
        ast: AST node to analyze
        
    Returns:
        Dict with complexity metrics
    """
    analyzer = ComplexityAnalyzer()
    result = ast.accept(analyzer)
    
    # Ensure we have the metrics at the top level
    metrics = analyzer.get_complexity_metrics()
    
    # Merge with structural result
    if isinstance(result, dict):
        result.update(metrics)
    
    return result 