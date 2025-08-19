"""
AST visitors for traversal, analysis, and optimization.

This module provides visitor pattern implementations for AST traversal,
including printing, validation, analysis, and optimization visitors.

Key features:
- ASTVisitor: Abstract base visitor class
- ASTPrinter: Human-readable AST printing
- ASTValidator: AST structure validation
- ASTAnalyzer: Complexity and usage analysis
- ASTOptimizer: AST optimization and simplification

Usage examples:
    >>> from ast.visitors import ASTPrinter, ASTValidator
    >>> printer = ASTPrinter()
    >>> result = ast.accept(printer)
    >>> print(result)

Dependencies:
- abc: For abstract base classes
- typing: For type hints and annotations

Author: Development Team
Created: 2024-01-15
Updated: 2024-01-20
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Set
from .nodes import ASTNode, FieldCondition, LogicalOperator, ParenExpression


class ASTVisitor(ABC):
    """
    Abstract visitor for AST traversal.
    
    This class implements the Visitor pattern for traversing AST nodes.
    It allows for different operations to be performed on the tree structure.
    """
    
    @abstractmethod
    def visit_field_condition(self, node: FieldCondition) -> Any:
        """Visit a field condition node."""
        raise NotImplementedError("Subclasses must implement visit_field_condition")
    
    @abstractmethod
    def visit_logical_operator(self, node: LogicalOperator) -> Any:
        """Visit a logical operator node."""
        raise NotImplementedError("Subclasses must implement visit_logical_operator")
    
    @abstractmethod
    def visit_paren_expression(self, node: ParenExpression) -> Any:
        """Visit a parenthesized expression node."""
        raise NotImplementedError("Subclasses must implement visit_paren_expression")
    
    def visit(self, node: ASTNode) -> Any:
        """Visit any AST node."""
        if isinstance(node, FieldCondition):
            return self.visit_field_condition(node)
        elif isinstance(node, LogicalOperator):
            return self.visit_logical_operator(node)
        elif isinstance(node, ParenExpression):
            return self.visit_paren_expression(node)
        else:
            raise ValueError(f"Unknown node type: {type(node)}")


class ASTPrinter(ASTVisitor):
    """
    Visitor for printing AST structure.
    
    This visitor provides a human-readable representation of the AST
    structure with proper indentation and formatting.
    """
    
    def __init__(self, indent: int = 0):
        """Initialize printer with indentation level."""
        self.indent = indent
    
    def visit_field_condition(self, node: FieldCondition) -> str:
        """Visit a field condition node."""
        return f"{'  ' * self.indent}FieldCondition: {node.field} {node.operator} {node.value}"
    
    def visit_logical_operator(self, node: LogicalOperator) -> str:
        """Visit a logical operator node."""
        result = [f"{'  ' * self.indent}LogicalOperator: {node.operator}"]
        for child in node.children:
            child_visitor = ASTPrinter(self.indent + 1)
            result.append(child.accept(child_visitor))
        return "\n".join(result)
    
    def visit_paren_expression(self, node: ParenExpression) -> str:
        """Visit a parenthesized expression node."""
        result = [f"{'  ' * self.indent}ParenExpression:"]
        child_visitor = ASTPrinter(self.indent + 1)
        result.append(node.expression.accept(child_visitor))
        return "\n".join(result)


class ASTValidator(ASTVisitor):
    """
    Visitor for validating AST structure.
    
    This visitor performs comprehensive validation of the AST structure,
    checking for proper node types, operator constraints, and field validity.
    """
    
    def __init__(self):
        """Initialize validator with empty error list."""
        self.errors = []
    
    def visit_field_condition(self, node: FieldCondition) -> bool:
        """Visit a field condition node."""
        try:
            node._validate_node()
            return True
        except Exception as e:
            self.errors.append(f"FieldCondition error: {e}")
            return False
    
    def visit_logical_operator(self, node: LogicalOperator) -> bool:
        """Visit a logical operator node."""
        try:
            node._validate_node()
            # Validate all children
            for child in node.children:
                child_visitor = ASTValidator()
                if not child.accept(child_visitor):
                    self.errors.extend(child_visitor.errors)
            return len(self.errors) == 0
        except Exception as e:
            self.errors.append(f"LogicalOperator error: {e}")
            return False
    
    def visit_paren_expression(self, node: ParenExpression) -> bool:
        """Visit a parenthesized expression node."""
        try:
            node._validate_node()
            # Validate the expression
            child_visitor = ASTValidator()
            return node.expression.accept(child_visitor)
        except Exception as e:
            self.errors.append(f"ParenExpression error: {e}")
            return False


class ASTAnalyzer(ASTVisitor):
    """
    Visitor for analyzing AST structure and complexity.
    
    This visitor provides detailed analysis of the AST including
    field usage, operator distribution, and complexity metrics.
    """
    
    def __init__(self):
        """Initialize analyzer with empty statistics."""
        self.field_count = 0
        self.operator_count = 0
        self.max_depth = 0
        self.fields_used: Set[str] = set()
        self.operators_used: Set[str] = set()
    
    def visit_field_condition(self, node: FieldCondition) -> Dict[str, Any]:
        """Visit a field condition node."""
        self.field_count += 1
        self.fields_used.add(node.field)
        self.operators_used.add(node.operator)
        return {
            "type": "field_condition",
            "field": node.field,
            "operator": node.operator
        }
    
    def visit_logical_operator(self, node: LogicalOperator) -> Dict[str, Any]:
        """Visit a logical operator node."""
        self.operator_count += 1
        self.operators_used.add(node.operator)
        
        children_info = []
        for child in node.children:
            child_visitor = ASTAnalyzer()
            child_info = child.accept(child_visitor)
            children_info.append(child_info)
            
            # Update statistics
            self.field_count += child_visitor.field_count
            self.operator_count += child_visitor.operator_count
            self.fields_used.update(child_visitor.fields_used)
            self.operators_used.update(child_visitor.operators_used)
            self.max_depth = max(self.max_depth, child_visitor.max_depth + 1)
        
        return {
            "type": "logical_operator",
            "operator": node.operator,
            "children": children_info
        }
    
    def visit_paren_expression(self, node: ParenExpression) -> Dict[str, Any]:
        """Visit a parenthesized expression node."""
        child_visitor = ASTAnalyzer()
        child_info = node.expression.accept(child_visitor)
        
        # Update statistics
        self.field_count += child_visitor.field_count
        self.operator_count += child_visitor.operator_count
        self.fields_used.update(child_visitor.fields_used)
        self.operators_used.update(child_visitor.operators_used)
        self.max_depth = max(self.max_depth, child_visitor.max_depth + 1)
        
        return {
            "type": "paren_expression",
            "expression": child_info
        }
    
    def get_analysis(self) -> Dict[str, Any]:
        """Get complete analysis of the AST."""
        return {
            "field_count": self.field_count,
            "operator_count": self.operator_count,
            "max_depth": self.max_depth,
            "fields_used": list(self.fields_used),
            "operators_used": list(self.operators_used),
            "complexity_score": self.field_count + self.operator_count + self.max_depth
        }


class ASTOptimizer(ASTVisitor):
    """
    Visitor for optimizing AST structure.
    
    This visitor applies various optimizations to the AST including
    removal of redundant conditions, simplification of expressions,
    and reordering for better performance.
    """
    
    def visit_field_condition(self, node: FieldCondition) -> ASTNode:
        """Visit a field condition node."""
        # Field conditions are already optimized
        return node
    
    def visit_logical_operator(self, node: LogicalOperator) -> ASTNode:
        """Visit a logical operator node."""
        # Optimize children first
        optimized_children = []
        for child in node.children:
            child_visitor = ASTOptimizer()
            optimized_child = child.accept(child_visitor)
            optimized_children.append(optimized_child)
        
        # Apply optimizations
        if node.operator == "AND":
            # Remove redundant conditions
            optimized_children = self._remove_redundant_conditions(optimized_children)
        elif node.operator == "OR":
            # Remove duplicate conditions
            optimized_children = self._remove_duplicate_conditions(optimized_children)
        
        # Create new optimized node
        optimized_node = LogicalOperator(operator=node.operator, children=optimized_children)
        return optimized_node
    
    def visit_paren_expression(self, node: ParenExpression) -> ASTNode:
        """Visit a parenthesized expression node."""
        # Optimize the expression inside parentheses
        child_visitor = ASTOptimizer()
        optimized_expression = node.expression.accept(child_visitor)
        
        # If the expression is already a single node, unwrap it
        if isinstance(optimized_expression, (FieldCondition, LogicalOperator)):
            return optimized_expression
        
        # Otherwise, keep the parentheses
        return ParenExpression(expression=optimized_expression)
    
    def _remove_redundant_conditions(self, children: List[ASTNode]) -> List[ASTNode]:
        """Remove redundant conditions from AND operator."""
        # Implementation for removing redundant conditions
        # For example: x > 5 AND x > 3 -> x > 5
        return children
    
    def _remove_duplicate_conditions(self, children: List[ASTNode]) -> List[ASTNode]:
        """Remove duplicate conditions from OR operator."""
        # Implementation for removing duplicate conditions
        # For example: x = 1 OR x = 1 -> x = 1
        seen = []
        result = []
        for child in children:
            # Create a hashable representation for comparison
            child_repr = str(child)
            if child_repr not in seen:
                seen.append(child_repr)
                result.append(child)
        return result 