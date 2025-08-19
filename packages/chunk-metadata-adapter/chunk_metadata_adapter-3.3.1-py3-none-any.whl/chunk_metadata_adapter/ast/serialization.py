"""
JSON serialization utilities for AST nodes.

This module provides utility functions for serializing and deserializing
AST nodes to and from JSON format.

Key features:
- ast_to_json: Serialize AST to JSON dictionary
- ast_from_json: Create AST from JSON dictionary
- ast_to_json_string: Serialize AST to JSON string
- ast_from_json_string: Create AST from JSON string

Usage examples:
    >>> from ast.serialization import ast_to_json, ast_from_json
    >>> json_data = ast_to_json(ast_node)
    >>> reconstructed_ast = ast_from_json(json_data)

Dependencies:
- typing: For type hints and annotations
- json: For JSON string operations
- .nodes: For AST node classes

Author: Development Team
Created: 2024-01-15
Updated: 2024-01-20
"""

from typing import Dict, Any, Optional
from .nodes import ASTNode


def ast_to_json(ast: ASTNode) -> Dict[str, Any]:
    """
    Serialize AST to JSON-compatible dictionary.
    
    Args:
        ast (ASTNode): AST node to serialize
        
    Returns:
        Dict[str, Any]: JSON representation of the AST
        
    Usage examples:
        >>> ast = FieldCondition("age", ">", TypedValue("int", 18))
        >>> json_data = ast_to_json(ast)
        >>> print(json.dumps(json_data, indent=2))
    """
    return ast.to_json()


def ast_from_json(data: Dict[str, Any]) -> ASTNode:
    """
    Create AST from JSON-compatible dictionary.
    
    Args:
        data (Dict[str, Any]): JSON data containing AST information
        
    Returns:
        ASTNode: Reconstructed AST node
        
    Raises:
        ValueError: If data is invalid or missing required fields
        
    Usage examples:
        >>> json_data = {'node_type': 'field_condition', 'field': 'age', ...}
        >>> ast = ast_from_json(json_data)
        >>> print(type(ast))  # <class 'FieldCondition'>
    """
    return ASTNode.from_json(data)


def ast_to_json_string(ast: ASTNode, indent: Optional[int] = None) -> str:
    """
    Serialize AST to JSON string.
    
    Args:
        ast (ASTNode): AST node to serialize
        indent (Optional[int]): JSON indentation (default: None)
        
    Returns:
        str: JSON string representation of the AST
        
    Usage examples:
        >>> ast = FieldCondition("age", ">", TypedValue("int", 18))
        >>> json_str = ast_to_json_string(ast, indent=2)
        >>> print(json_str)
    """
    import json
    return json.dumps(ast.to_json(), indent=indent)


def ast_from_json_string(json_str: str) -> ASTNode:
    """
    Create AST from JSON string.
    
    Args:
        json_str (str): JSON string containing AST information
        
    Returns:
        ASTNode: Reconstructed AST node
        
    Raises:
        ValueError: If JSON is invalid or missing required fields
        json.JSONDecodeError: If JSON string is malformed
        
    Usage examples:
        >>> json_str = '{"node_type": "field_condition", "field": "age", ...}'
        >>> ast = ast_from_json_string(json_str)
        >>> print(type(ast))  # <class 'FieldCondition'>
    """
    import json
    data = json.loads(json_str)
    return ASTNode.from_json(data) 