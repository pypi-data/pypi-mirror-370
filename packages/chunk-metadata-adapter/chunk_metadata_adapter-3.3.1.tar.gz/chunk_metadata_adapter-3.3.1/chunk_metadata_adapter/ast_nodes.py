"""
AST nodes for filter expression parsing and execution.

This module provides the core data structures for representing filter expressions
as Abstract Syntax Trees (AST). It includes typed nodes for field conditions,
logical operators, and parenthesized expressions.

This file provides backward compatibility by re-exporting classes from the ast/
submodule structure.

Key features:
- TypedValue: Type-safe value representation with validation
- FieldCondition: Field comparison conditions (age > 18)
- LogicalOperator: Logical operations (AND, OR, NOT)
- ParenExpression: Parenthesized expressions for precedence
- ASTNodeFactory: Factory for creating AST nodes

Usage examples:
    >>> from chunk_metadata_adapter.ast_nodes import FieldCondition, TypedValue
    >>> condition = FieldCondition("age", ">", TypedValue("int", 18))
    >>> result = condition.evaluate({"age": 25})

Dependencies:
- dataclasses: For data structure definitions
- typing: For type hints and annotations
- datetime: For date/time value support

Author: Development Team
Created: 2024-01-15
Updated: 2024-01-20
"""

# Re-export all necessary classes from ast submodule for backward compatibility
from .ast.nodes import (
    ASTNode, FieldCondition, LogicalOperator, ParenExpression, TypedValue
)

from .ast.factory import ASTNodeFactory

__all__ = [
    # Core AST classes
    "ASTNode",
    "FieldCondition", 
    "LogicalOperator",
    "ParenExpression",
    "TypedValue",
    
    # Factory
    "ASTNodeFactory",
] 