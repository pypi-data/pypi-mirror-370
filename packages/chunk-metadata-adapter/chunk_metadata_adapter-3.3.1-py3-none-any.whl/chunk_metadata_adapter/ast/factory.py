"""
AST node factory for convenient node creation.

This module provides a factory class for creating various types of AST nodes
with proper validation and convenient methods.

Key features:
- ASTNodeFactory: Factory for creating AST nodes
- Convenient methods for common node types
- Automatic validation and error handling

Usage examples:
    >>> from ast.factory import ASTNodeFactory
    >>> condition = ASTNodeFactory.create_simple_condition("age", ">", "int", 18)
    >>> operator = ASTNodeFactory.create_and_operator([condition1, condition2])

Dependencies:
- typing: For type hints and annotations
- .nodes: For AST node classes

Author: Development Team
Created: 2024-01-15
Updated: 2024-01-20
"""

from typing import List, Literal, Any
from .nodes import ASTNode, FieldCondition, LogicalOperator, ParenExpression, TypedValue


class ASTNodeFactory:
    """
    Factory for creating AST nodes.

    This class provides convenient methods for creating
    various types of AST nodes with proper validation.
    """

    @staticmethod
    def create_field_condition(field: str, operator: str, value: TypedValue) -> FieldCondition:
        """Create a field condition node."""
        return FieldCondition(field=field, operator=operator, value=value)

    @staticmethod
    def create_logical_operator(operator: Literal["AND", "OR", "NOT", "XOR"],
                               children: List[ASTNode]) -> LogicalOperator:
        """Create a logical operator node."""
        return LogicalOperator(operator=operator, children=children)

    @staticmethod
    def create_paren_expression(expression: ASTNode) -> ParenExpression:
        """Create a parenthesized expression node."""
        return ParenExpression(expression=expression)

    @staticmethod
    def create_typed_value(type_name: str, value: Any) -> TypedValue:
        """Create a typed value."""
        return TypedValue(type=type_name, value=value)

    @staticmethod
    def create_and_operator(children: List[ASTNode]) -> LogicalOperator:
        """Create an AND operator node."""
        return ASTNodeFactory.create_logical_operator("AND", children)

    @staticmethod
    def create_or_operator(children: List[ASTNode]) -> LogicalOperator:
        """Create an OR operator node."""
        return ASTNodeFactory.create_logical_operator("OR", children)

    @staticmethod
    def create_not_operator(child: ASTNode) -> LogicalOperator:
        """Create a NOT operator node."""
        return ASTNodeFactory.create_logical_operator("NOT", [child])

    @staticmethod
    def create_simple_condition(field: str, operator: str, type_name: str, value: Any) -> FieldCondition:
        """Create a simple field condition with automatic typed value creation."""
        typed_value = ASTNodeFactory.create_typed_value(type_name, value)
        return ASTNodeFactory.create_field_condition(field, operator, typed_value)

    @staticmethod
    def create_complex_expression(conditions: List[tuple],
                                 operator: Literal["AND", "OR"] = "AND") -> LogicalOperator:
        """Create a complex expression from a list of conditions."""
        field_conditions = []
        for field, op, type_name, value in conditions:
            condition = ASTNodeFactory.create_simple_condition(field, op, type_name, value)
            field_conditions.append(condition)
        if operator == "AND":
            return ASTNodeFactory.create_and_operator(field_conditions)
        else:
            return ASTNodeFactory.create_or_operator(field_conditions) 