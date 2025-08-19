"""
AST (Abstract Syntax Tree) module for filter expression parsing and execution.

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
- JSON serialization: Full serialization/deserialization support
- Visitor pattern: AST traversal and analysis

Usage examples:
    >>> from chunk_metadata_adapter.ast import FieldCondition, TypedValue
    >>> condition = FieldCondition("age", ">", TypedValue("int", 18))
    >>> result = condition.evaluate({"age": 25})

Dependencies:
- dataclasses: For data structure definitions
- typing: For type hints and annotations
- datetime: For date/time value support
- json: For serialization support

Author: Development Team
Created: 2024-01-15
Updated: 2024-01-20
"""

# Re-export all necessary classes from ast submodule for backward compatibility
from .ast.nodes import (
    ASTNode, FieldCondition, LogicalOperator, ParenExpression, TypedValue
)

from .ast.visitors import (
    ASTVisitor, ASTPrinter, ASTValidator, ASTAnalyzer, ASTOptimizer
)

from .ast.factory import ASTNodeFactory

from .ast.serialization import (
    ast_to_json, ast_from_json, ast_to_json_string, ast_from_json_string
)

from .ast.parameterization import (
    ParameterValue, ParameterizedAST, ASTParameterizer, ASTInstantiator, QueryCache
)

__all__ = [
    # Core AST classes
    "ASTNode",
    "FieldCondition", 
    "LogicalOperator",
    "ParenExpression",
    "TypedValue",
    
    # Visitor pattern
    "ASTVisitor",
    "ASTPrinter",
    "ASTValidator", 
    "ASTAnalyzer",
    "ASTOptimizer",
    
    # Factory
    "ASTNodeFactory",
    
    # JSON serialization
    "ast_to_json",
    "ast_from_json", 
    "ast_to_json_string",
    "ast_from_json_string",
    
    # Parameterization and caching
    "ParameterValue",
    "ParameterizedAST", 
    "ASTParameterizer",
    "ASTInstantiator",
    "QueryCache",
] 