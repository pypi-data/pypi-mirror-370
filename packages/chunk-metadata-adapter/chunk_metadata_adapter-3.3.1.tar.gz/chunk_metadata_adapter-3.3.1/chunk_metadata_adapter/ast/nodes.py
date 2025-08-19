"""
AST nodes for filter expression parsing and execution.

This module provides the core data structures for representing filter expressions
as Abstract Syntax Trees (AST). It includes typed nodes for field conditions,
logical operators, and parenthesized expressions.

Key features:
- TypedValue: Type-safe value representation with validation
- FieldCondition: Field comparison conditions (age > 18)
- LogicalOperator: Logical operations (AND, OR, NOT)
- ParenExpression: Parenthesized expressions for precedence

Usage examples:
    >>> from ast.nodes import FieldCondition, TypedValue
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

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Union, Literal, Optional, Any, Dict
from datetime import datetime
import re


@dataclass
class TypedValue:
    """
    Type-safe value representation with validation.

    This class represents a value with its associated type information,
    enabling type-safe operations and validation. It supports various
    data types including primitives, collections, and special values.

    Attributes:
        type (Literal): The type of the value
            - "int": Integer values
            - "float": Floating-point values
            - "str": String values
            - "list": List values
            - "dict": Dictionary values
            - "date": Date/time values
            - "null": Null/None values
            - "bool": Boolean values
        value (Union): The actual value, must match the specified type

    Usage examples:
        >>> int_val = TypedValue("int", 42)
        >>> str_val = TypedValue("str", "hello")
        >>> list_val = TypedValue("list", [1, 2, 3])
        >>> null_val = TypedValue("null", None)

    Notes:
        - Type and value are validated on creation
        - Date values should be datetime objects
        - Null values should have None as the value
    """
    
    type: Literal["int", "float", "str", "list", "dict", "date", "null", "bool"]
    value: Union[int, float, str, List, Dict, datetime, None, bool]
    
    def __post_init__(self) -> None:
        """Validate type and value consistency."""
        self._validate_type()
        self._validate_value()
    
    def _validate_type(self) -> None:
        """Validate that type and value are consistent."""
        if self.type == "null" and self.value is not None:
            raise ValueError("Null type must have None value")
        elif self.type != "null" and self.value is None:
            raise ValueError(f"Type {self.type} cannot have None value")
        
        # Type-specific validations
        if self.type == "int" and not isinstance(self.value, int):
            raise ValueError(f"Int type requires int value, got {type(self.value)}")
        elif self.type == "float" and not isinstance(self.value, (int, float)):
            raise ValueError(f"Float type requires numeric value, got {type(self.value)}")
        elif self.type == "str" and not isinstance(self.value, str):
            raise ValueError(f"Str type requires string value, got {type(self.value)}")
        elif self.type == "list" and not isinstance(self.value, list):
            raise ValueError(f"List type requires list value, got {type(self.value)}")
        elif self.type == "dict" and not isinstance(self.value, dict):
            raise ValueError(f"Dict type requires dict value, got {type(self.value)}")
        elif self.type == "date" and not isinstance(self.value, (datetime, str)):
            raise ValueError(f"Date type requires datetime or string value, got {type(self.value)}")
        elif self.type == "bool" and not isinstance(self.value, bool):
            raise ValueError(f"Bool type requires bool value, got {type(self.value)}")
    
    def _validate_value(self) -> None:
        """Validate value-specific constraints."""
        if self.type == "int":
            # Check for overflow
            if not (-2**63 <= self.value <= 2**63 - 1):
                raise ValueError("Integer value out of range")
        elif self.type == "float":
            # Check for special values
            if not (self.value == self.value):  # NaN check
                raise ValueError("Float value cannot be NaN")
        elif self.type == "str":
            # Check for maximum length
            if len(self.value) > 10000:
                raise ValueError("String value too long")
        elif self.type == "list":
            # Check for maximum size
            if len(self.value) > 1000:
                raise ValueError("List value too large")
        elif self.type == "dict":
            # Check for maximum size
            if len(self.value) > 100:
                raise ValueError("Dict value too large")
    
    def __str__(self) -> str:
        """String representation of the value."""
        if self.type == "str":
            return f'"{self.value}"'
        elif self.type == "null":
            return "null"
        else:
            return str(self.value)
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"TypedValue(type='{self.type}', value={self.value})"
    
    def to_json(self) -> Dict[str, Any]:
        """
        Serialize TypedValue to JSON-compatible dictionary.
        
        Returns:
            Dict[str, Any]: JSON representation of the typed value
            
        Usage examples:
            >>> value = TypedValue("int", 42)
            >>> json_data = value.to_json()
            >>> print(json_data)  # {'type': 'int', 'value': 42}
        """
        if self.type == "date" and isinstance(self.value, datetime):
            return {
                "type": self.type,
                "value": self.value.isoformat()
            }
        else:
            return {
                "type": self.type,
                "value": self.value
            }
    
    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'TypedValue':
        """
        Create TypedValue from JSON-compatible dictionary.
        
        Args:
            data (Dict[str, Any]): JSON data containing type and value
            
        Returns:
            TypedValue: Reconstructed typed value
            
        Raises:
            ValueError: If data is invalid or missing required fields
            
        Usage examples:
            >>> json_data = {'type': 'int', 'value': 42}
            >>> value = TypedValue.from_json(json_data)
            >>> print(value)  # TypedValue(type='int', value=42)
        """
        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary")
        
        if "type" not in data or "value" not in data:
            raise ValueError("Data must contain 'type' and 'value' fields")
        
        type_name = data["type"]
        value = data["value"]
        
        # Handle date deserialization
        if type_name == "date" and isinstance(value, str):
            try:
                from datetime import datetime
                value = datetime.fromisoformat(value.replace('Z', '+00:00'))
            except ValueError as e:
                raise ValueError(f"Invalid date format: {e}")
        
        return cls(type=type_name, value=value)


class ASTNode(ABC):
    """
    Abstract base class for all AST nodes.
    
    This class provides the foundation for the Abstract Syntax Tree
    representation of filter expressions. All specific node types
    inherit from this class.
    
    Attributes:
        node_type (str): Type identifier for the node
        children (List['ASTNode']): Child nodes (if any)
    """
    
    def __init__(self, node_type: str, children: List['ASTNode']):
        """Initialize AST node."""
        self.node_type = node_type
        self.children = children
        self._validate_node()
    
    @abstractmethod
    def _validate_node(self) -> None:
        """Validate node-specific constraints."""
        raise NotImplementedError("Subclasses must implement _validate_node")
    
    @abstractmethod
    def evaluate(self, data: Any) -> bool:
        """Evaluate node against data."""
        raise NotImplementedError("Subclasses must implement evaluate")
    
    def accept(self, visitor: 'ASTVisitor') -> Any:
        """Accept visitor for traversal."""
        return visitor.visit(self)
    
    @property
    def is_leaf(self) -> bool:
        """Check if node is a leaf (no children)."""
        return len(self.children) == 0
    
    @property
    def depth(self) -> int:
        """Get depth of the node in the tree."""
        if self.is_leaf:
            return 0
        return 1 + max(child.depth for child in self.children)
    
    def __str__(self) -> str:
        """String representation of the node."""
        return f"{self.__class__.__name__}({self.node_type})"
    
    def to_json(self) -> Dict[str, Any]:
        """
        Serialize AST node to JSON-compatible dictionary.
        
        Returns:
            Dict[str, Any]: JSON representation of the AST node
            
        Usage examples:
            >>> node = FieldCondition("age", ">", TypedValue("int", 18))
            >>> json_data = node.to_json()
            >>> print(json_data)  # {'node_type': 'field_condition', 'field': 'age', ...}
        """
        raise NotImplementedError("Subclasses must implement to_json")
    
    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'ASTNode':
        """
        Create AST node from JSON-compatible dictionary.
        
        Args:
            data (Dict[str, Any]): JSON data containing node information
            
        Returns:
            ASTNode: Reconstructed AST node
            
        Raises:
            ValueError: If data is invalid or missing required fields
            
        Usage examples:
            >>> json_data = {'node_type': 'field_condition', 'field': 'age', ...}
            >>> node = ASTNode.from_json(json_data)
            >>> print(type(node))  # <class 'FieldCondition'>
        """
        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary")
        
        if "node_type" not in data:
            raise ValueError("Data must contain 'node_type' field")
        
        node_type = data["node_type"]
        
        # Route to appropriate class based on node type
        if node_type == "field_condition":
            return FieldCondition.from_json(data)
        elif node_type == "logical_operator":
            return LogicalOperator.from_json(data)
        elif node_type == "paren_expression":
            return ParenExpression.from_json(data)
        else:
            raise ValueError(f"Unknown node type: {node_type}")


@dataclass
class FieldCondition(ASTNode):
    """
    Condition for filtering by field value.
    
    This node represents a comparison between a field and a value.
    It supports various operators and nested field access.
    
    Attributes:
        field (str): Field name (supports dot notation for nesting)
        operator (str): Comparison operator
        value (TypedValue): Value to compare against
    """
    
    field: str
    operator: str
    value: TypedValue
    
    def __post_init__(self) -> None:
        """Initialize base class and validate fields."""
        super().__init__("field_condition", [])  # Field conditions are leaf nodes
        self._validate_node()
    
    def _validate_node(self) -> None:
        """Validate field condition constraints."""
        if not self.field or not self.field.strip():
            raise ValueError("Field name cannot be empty")
        
        if not self.operator or not self.operator.strip():
            raise ValueError("Operator cannot be empty")
        
        # Validate field name format
        if not self._is_valid_field_name(self.field):
            raise ValueError(f"Invalid field name: {self.field}")
        
        # Validate operator
        if not self._is_valid_operator(self.operator):
            raise ValueError(f"Invalid operator: {self.operator}")
    
    def _is_valid_field_name(self, field: str) -> bool:
        """Check if field name is valid."""
        # Allow alphanumeric, underscore, and dot for nesting
        pattern = r'^[a-zA-Z_][a-zA-Z0-9_]*(\.[a-zA-Z_][a-zA-Z0-9_]*)*$'
        return bool(re.match(pattern, field))
    
    def _is_valid_operator(self, operator: str) -> bool:
        """Check if operator is valid."""
        valid_operators = {
            # Comparison operators
            "=", "!=", ">", ">=", "<", "<=",
            # String operators
            "like", "~", "!~",
            # Inclusion operators
            "in", "not_in", "intersects",
            # Dictionary operators
            "contains_key", "contains_value"
        }
        return operator in valid_operators
    
    def evaluate(self, data: Any) -> bool:
        """Evaluate field condition against data."""
        # This will be implemented in FilterExecutor
        raise NotImplementedError("Evaluation implemented in FilterExecutor")
    
    def __str__(self) -> str:
        """String representation of the condition."""
        return f"{self.field} {self.operator} {self.value}"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"FieldCondition(field='{self.field}', operator='{self.operator}', value={self.value})"
    
    def to_json(self) -> Dict[str, Any]:
        """
        Serialize FieldCondition to JSON-compatible dictionary.
        
        Returns:
            Dict[str, Any]: JSON representation of the field condition
            
        Usage examples:
            >>> condition = FieldCondition("age", ">", TypedValue("int", 18))
            >>> json_data = condition.to_json()
            >>> print(json_data)  # {'node_type': 'field_condition', 'field': 'age', ...}
        """
        return {
            "node_type": self.node_type,
            "field": self.field,
            "operator": self.operator,
            "value": self.value.to_json()
        }
    
    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'FieldCondition':
        """
        Create FieldCondition from JSON-compatible dictionary.
        
        Args:
            data (Dict[str, Any]): JSON data containing field condition information
            
        Returns:
            FieldCondition: Reconstructed field condition
            
        Raises:
            ValueError: If data is invalid or missing required fields
            
        Usage examples:
            >>> json_data = {'node_type': 'field_condition', 'field': 'age', ...}
            >>> condition = FieldCondition.from_json(json_data)
            >>> print(condition)  # age > 18
        """
        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary")
        
        required_fields = ["node_type", "field", "operator", "value"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Data must contain '{field}' field")
        
        if data["node_type"] != "field_condition":
            raise ValueError(f"Expected node_type 'field_condition', got '{data['node_type']}'")
        
        # Deserialize TypedValue
        value = TypedValue.from_json(data["value"])
        
        return cls(
            field=data["field"],
            operator=data["operator"],
            value=value
        )


@dataclass
class LogicalOperator(ASTNode):
    """
    Logical operator node (AND, OR, NOT).
    
    This node represents logical operations between multiple conditions.
    It supports AND, OR, and NOT operations with arbitrary numbers of children.
    
    Attributes:
        operator (Literal): The logical operator ("AND", "OR", "NOT")
        children (List[ASTNode]): Child nodes
    """
    
    operator: Literal["AND", "OR", "NOT", "XOR"]
    children: List['ASTNode']
    
    def __post_init__(self) -> None:
        """Initialize base class and validate operator."""
        super().__init__("logical_operator", self.children)
        self._validate_node()
    
    def _validate_node(self) -> None:
        """Validate logical operator constraints."""
        if not self.operator:
            raise ValueError("Operator cannot be empty")
        
        # Validate operator value
        if self.operator not in ["AND", "OR", "NOT", "XOR"]:
            raise ValueError(f"Invalid logical operator: {self.operator}")
        
        # Validate children count
        if self.operator == "NOT" and len(self.children) != 1:
            raise ValueError("NOT operator must have exactly one child")
        elif self.operator in ["AND", "OR", "XOR"] and len(self.children) < 2:
            raise ValueError(f"{self.operator} operator must have at least two children")
    
    def evaluate(self, data: Any) -> bool:
        """Evaluate logical operator against data."""
        # This will be implemented in FilterExecutor
        raise NotImplementedError("Evaluation implemented in FilterExecutor")
    
    def __str__(self) -> str:
        """String representation of the operator."""
        if self.operator == "NOT":
            return f"NOT ({self.children[0]})"
        else:
            return f" {self.operator} ".join(f"({child})" for child in self.children)
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"LogicalOperator(operator='{self.operator}', children={len(self.children)})"
    
    def to_json(self) -> Dict[str, Any]:
        """
        Serialize LogicalOperator to JSON-compatible dictionary.
        
        Returns:
            Dict[str, Any]: JSON representation of the logical operator
            
        Usage examples:
            >>> operator = LogicalOperator("AND", [condition1, condition2])
            >>> json_data = operator.to_json()
            >>> print(json_data)  # {'node_type': 'logical_operator', 'operator': 'AND', ...}
        """
        return {
            "node_type": self.node_type,
            "operator": self.operator,
            "children": [child.to_json() for child in self.children]
        }
    
    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'LogicalOperator':
        """
        Create LogicalOperator from JSON-compatible dictionary.
        
        Args:
            data (Dict[str, Any]): JSON data containing logical operator information
            
        Returns:
            LogicalOperator: Reconstructed logical operator
            
        Raises:
            ValueError: If data is invalid or missing required fields
            
        Usage examples:
            >>> json_data = {'node_type': 'logical_operator', 'operator': 'AND', ...}
            >>> operator = LogicalOperator.from_json(json_data)
            >>> print(operator)  # (condition1) AND (condition2)
        """
        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary")
        
        required_fields = ["node_type", "operator", "children"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Data must contain '{field}' field")
        
        if data["node_type"] != "logical_operator":
            raise ValueError(f"Expected node_type 'logical_operator', got '{data['node_type']}'")
        
        if not isinstance(data["children"], list):
            raise ValueError("Children must be a list")
        
        # Deserialize children
        children = [ASTNode.from_json(child_data) for child_data in data["children"]]
        
        return cls(
            operator=data["operator"],
            children=children
        )


@dataclass
class ParenExpression(ASTNode):
    """
    Parenthesized expression node.
    
    This node represents an expression wrapped in parentheses.
    It is used to control operator precedence in complex expressions.
    
    Attributes:
        expression (ASTNode): The expression inside parentheses
    """
    
    expression: ASTNode
    
    def __post_init__(self) -> None:
        """Initialize base class and validate expression."""
        super().__init__("paren_expression", [self.expression])  # Wrap expression as child
        self._validate_node()
    
    def _validate_node(self) -> None:
        """Validate parenthesized expression constraints."""
        if self.expression is None:
            raise ValueError("Expression cannot be None")
        
        if not isinstance(self.expression, ASTNode):
            raise ValueError("Expression must be an ASTNode")
    
    def evaluate(self, data: Any) -> bool:
        """Evaluate parenthesized expression against data."""
        return self.expression.evaluate(data)
    
    def __str__(self) -> str:
        """String representation of the expression."""
        return f"({self.expression})"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"ParenExpression(expression={self.expression})"
    
    def to_json(self) -> Dict[str, Any]:
        """
        Serialize ParenExpression to JSON-compatible dictionary.
        
        Returns:
            Dict[str, Any]: JSON representation of the parenthesized expression
            
        Usage examples:
            >>> paren = ParenExpression(condition)
            >>> json_data = paren.to_json()
            >>> print(json_data)  # {'node_type': 'paren_expression', 'expression': {...}}
        """
        return {
            "node_type": self.node_type,
            "expression": self.expression.to_json()
        }
    
    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'ParenExpression':
        """
        Create ParenExpression from JSON-compatible dictionary.
        
        Args:
            data (Dict[str, Any]): JSON data containing parenthesized expression information
            
        Returns:
            ParenExpression: Reconstructed parenthesized expression
            
        Raises:
            ValueError: If data is invalid or missing required fields
            
        Usage examples:
            >>> json_data = {'node_type': 'paren_expression', 'expression': {...}}
            >>> paren = ParenExpression.from_json(json_data)
            >>> print(paren)  # (condition)
        """
        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary")
        
        required_fields = ["node_type", "expression"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Data must contain '{field}' field")
        
        if data["node_type"] != "paren_expression":
            raise ValueError(f"Expected node_type 'paren_expression', got '{data['node_type']}'")
        
        # Deserialize expression
        expression = ASTNode.from_json(data["expression"])
        
        return cls(expression=expression) 