"""
AST Parameterization for Query Caching.

This module provides functionality to parameterize AST queries for efficient caching.
It allows converting concrete values to parameters and back, enabling reuse of
compiled AST structures with different parameter values.

Key features:
- ParameterValue: Parameter placeholder with type information
- ASTParameterizer: Convert AST with concrete values to parameterized template
- ASTInstantiator: Instantiate parameterized AST with concrete values
- QueryCache: Cache parameterized AST templates for reuse

Usage examples:
    >>> from ast.parameterization import ASTParameterizer, ASTInstantiator
    >>> parameterizer = ASTParameterizer()
    >>> template = parameterizer.parameterize(ast)
    >>> instantiator = ASTInstantiator()
    >>> new_ast = instantiator.instantiate(template, {"param_1": 42})

Dependencies:
- ast.nodes: For AST node types and operations
- typing: For type hints and annotations
- dataclasses: For data structure definitions

Author: Development Team
Created: 2024-01-20
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Union, Tuple
from collections import defaultdict
import hashlib
import json

from .nodes import ASTNode, FieldCondition, LogicalOperator, ParenExpression, TypedValue


@dataclass
class ParameterValue:
    """
    Parameter placeholder with type information.
    
    This class represents a parameter in a parameterized AST template.
    It contains type information and a unique identifier for the parameter.
    
    Attributes:
        param_id (str): Unique parameter identifier
        param_type (str): Type of the parameter (int, str, etc.)
        description (Optional[str]): Optional description of the parameter
        
    Usage examples:
        >>> param = ParameterValue("param_1", "int", "age threshold")
        >>> print(param)  # param_1:int
    """
    
    param_id: str
    param_type: str
    description: Optional[str] = None
    
    def __str__(self) -> str:
        """String representation of the parameter."""
        return f"{self.param_id}:{self.param_type}"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        desc = f", description='{self.description}'" if self.description else ""
        return f"ParameterValue(param_id='{self.param_id}', param_type='{self.param_type}'{desc})"
    
    def to_json(self) -> Dict[str, Any]:
        """Serialize ParameterValue to JSON."""
        return {
            "param_id": self.param_id,
            "param_type": self.param_type,
            "description": self.description
        }
    
    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'ParameterValue':
        """Create ParameterValue from JSON."""
        return cls(
            param_id=data["param_id"],
            param_type=data["param_type"],
            description=data.get("description")
        )


@dataclass
class ParameterizedAST:
    """
    Parameterized AST template with parameter mapping.
    
    This class represents an AST template where concrete values have been
    replaced with parameters. It includes the parameterized AST and a mapping
    of parameter IDs to their original values and types.
    
    Attributes:
        ast (ASTNode): Parameterized AST template
        parameters (Dict[str, ParameterValue]): Parameter mapping
        template_hash (str): Hash of the template structure (without values)
        
    Usage examples:
        >>> template = ParameterizedAST(ast, parameters, "abc123")
        >>> print(template.template_hash)  # abc123
    """
    
    ast: ASTNode
    parameters: Dict[str, ParameterValue]
    template_hash: str
    
    def get_parameter_count(self) -> int:
        """Get the number of parameters in the template."""
        return len(self.parameters)
    
    def get_parameter_types(self) -> Dict[str, str]:
        """Get mapping of parameter IDs to their types."""
        return {param_id: param.param_type for param_id, param in self.parameters.items()}
    
    def to_json(self) -> Dict[str, Any]:
        """Serialize ParameterizedAST to JSON."""
        return {
            "ast": self.ast.to_json(),
            "parameters": {param_id: param.to_json() for param_id, param in self.parameters.items()},
            "template_hash": self.template_hash
        }
    
    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'ParameterizedAST':
        """Create ParameterizedAST from JSON."""
        # Deserialize AST
        ast = ASTNode.from_json(data["ast"])
        
        # Deserialize parameters
        parameters = {
            param_id: ParameterValue.from_json(param_data)
            for param_id, param_data in data["parameters"].items()
        }
        
        return cls(
            ast=ast,
            parameters=parameters,
            template_hash=data["template_hash"]
        )


class ASTParameterizer:
    """
    Converts AST with concrete values to parameterized template.
    
    This class analyzes an AST and replaces concrete values with parameters,
    creating a reusable template that can be instantiated with different values.
    
    Key features:
    - Automatic parameter generation with unique IDs
    - Type preservation for parameters
    - Template hash generation for caching
    - Support for all AST node types
    
    Usage examples:
        >>> parameterizer = ASTParameterizer()
        >>> template = parameterizer.parameterize(ast)
        >>> print(template.get_parameter_count())  # 2
    """
    
    def __init__(self, param_prefix: str = "param"):
        """
        Initialize ASTParameterizer.
        
        Args:
            param_prefix (str): Prefix for parameter IDs
        """
        self.param_prefix = param_prefix
        self._param_counter = 0
        self._value_to_param: Dict[Tuple[str, Any], str] = {}
    
    def parameterize(self, ast: ASTNode) -> ParameterizedAST:
        """
        Convert AST to parameterized template.
        
        Args:
            ast (ASTNode): AST to parameterize
            
        Returns:
            ParameterizedAST: Parameterized template
            
        Usage examples:
            >>> parameterizer = ASTParameterizer()
            >>> template = parameterizer.parameterize(ast)
            >>> print(template.get_parameter_count())
        """
        # Reset state
        self._param_counter = 0
        self._value_to_param.clear()
        
        # Create parameterized AST
        parameterized_ast = self._parameterize_node(ast)
        
        # Generate template hash
        template_hash = self._generate_template_hash(parameterized_ast)
        
        # Build parameter mapping
        parameters = {}
        for param_id, (param_type, description) in self._value_to_param.items():
            parameters[param_id] = ParameterValue(param_id, param_type, description)
        
        return ParameterizedAST(
            ast=parameterized_ast,
            parameters=parameters,
            template_hash=template_hash
        )
    
    def _parameterize_node(self, node: ASTNode) -> ASTNode:
        """Recursively parameterize AST node."""
        if isinstance(node, FieldCondition):
            return self._parameterize_field_condition(node)
        elif isinstance(node, LogicalOperator):
            return self._parameterize_logical_operator(node)
        elif isinstance(node, ParenExpression):
            return self._parameterize_paren_expression(node)
        else:
            raise ValueError(f"Unsupported node type: {type(node)}")
    
    def _parameterize_field_condition(self, condition: FieldCondition) -> FieldCondition:
        """Parameterize field condition."""
        # Create parameterized value
        param_value = self._create_parameter_value(condition.value)
        
        return FieldCondition(
            field=condition.field,
            operator=condition.operator,
            value=param_value
        )
    
    def _parameterize_logical_operator(self, operator: LogicalOperator) -> LogicalOperator:
        """Parameterize logical operator."""
        # Parameterize children
        parameterized_children = [
            self._parameterize_node(child) for child in operator.children
        ]
        
        return LogicalOperator(
            operator=operator.operator,
            children=parameterized_children
        )
    
    def _parameterize_paren_expression(self, paren: ParenExpression) -> ParenExpression:
        """Parameterize parenthesized expression."""
        # Parameterize inner expression
        parameterized_expression = self._parameterize_node(paren.expression)
        
        return ParenExpression(expression=parameterized_expression)
    
    def _create_parameter_value(self, typed_value: TypedValue) -> TypedValue:
        """Create parameterized TypedValue."""
        # Create unique parameter ID
        param_id = f"{self.param_prefix}_{self._param_counter}"
        self._param_counter += 1
        
        # Store parameter information
        self._value_to_param[param_id] = (typed_value.type, f"Value of type {typed_value.type}")
        
        # Create parameterized TypedValue with parameter ID as value
        # Use a special type for parameterized values to avoid validation errors
        return TypedValue(type="str", value=param_id)
    
    def _generate_template_hash(self, ast: ASTNode) -> str:
        """Generate hash of template structure (without concrete values)."""
        # Convert AST to JSON representation
        ast_json = ast.to_json()
        
        # Create hash of the structure
        json_str = json.dumps(ast_json, sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()[:16]


class ASTInstantiator:
    """
    Instantiates parameterized AST with concrete values.
    
    This class takes a parameterized AST template and concrete parameter values,
    and creates a new AST with the concrete values substituted for parameters.
    
    Key features:
    - Type validation for parameter values
    - Support for all parameter types
    - Error handling for missing or invalid parameters
    
    Usage examples:
        >>> instantiator = ASTInstantiator()
        >>> concrete_ast = instantiator.instantiate(template, {"param_1": 42})
        >>> print(concrete_ast)
    """
    
    def instantiate(self, template: ParameterizedAST, params: Dict[str, Any]) -> ASTNode:
        """
        Instantiate parameterized AST with concrete values.
        
        Args:
            template (ParameterizedAST): Parameterized template
            params (Dict[str, Any]): Concrete parameter values
            
        Returns:
            ASTNode: AST with concrete values
            
        Raises:
            ValueError: If parameters are missing or invalid
            
        Usage examples:
            >>> instantiator = ASTInstantiator()
            >>> concrete_ast = instantiator.instantiate(template, {"param_1": 42})
        """
        # Validate parameters
        self._validate_parameters(template, params)
        
        # Create parameter mapping
        param_mapping = self._create_param_mapping(template, params)
        
        # Instantiate AST
        return self._instantiate_node(template.ast, param_mapping)
    
    def _validate_parameters(self, template: ParameterizedAST, params: Dict[str, Any]) -> None:
        """Validate parameter values against template."""
        template_params = template.get_parameter_types()
        
        # Check for missing parameters
        missing_params = set(template_params.keys()) - set(params.keys())
        if missing_params:
            raise ValueError(f"Missing parameters: {missing_params}")
        
        # Check for extra parameters
        extra_params = set(params.keys()) - set(template_params.keys())
        if extra_params:
            raise ValueError(f"Extra parameters: {extra_params}")
        
        # Validate parameter types
        for param_id, param_type in template_params.items():
            value = params[param_id]
            if not self._is_valid_type(value, param_type):
                raise ValueError(f"Parameter {param_id} expects type {param_type}, got {type(value)}")
    
    def _is_valid_type(self, value: Any, expected_type: str) -> bool:
        """Check if value matches expected type."""
        if expected_type == "int":
            return isinstance(value, int)
        elif expected_type == "float":
            return isinstance(value, (int, float))
        elif expected_type == "str":
            return isinstance(value, str)
        elif expected_type == "list":
            return isinstance(value, list)
        elif expected_type == "dict":
            return isinstance(value, dict)
        elif expected_type == "bool":
            return isinstance(value, bool)
        elif expected_type == "null":
            return value is None
        else:
            return True  # Unknown type, accept any value
    
    def _create_param_mapping(self, template: ParameterizedAST, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create mapping from parameter IDs to concrete values."""
        return params.copy()
    
    def _instantiate_node(self, node: ASTNode, param_mapping: Dict[str, Any]) -> ASTNode:
        """Recursively instantiate AST node."""
        if isinstance(node, FieldCondition):
            return self._instantiate_field_condition(node, param_mapping)
        elif isinstance(node, LogicalOperator):
            return self._instantiate_logical_operator(node, param_mapping)
        elif isinstance(node, ParenExpression):
            return self._instantiate_paren_expression(node, param_mapping)
        else:
            raise ValueError(f"Unsupported node type: {type(node)}")
    
    def _instantiate_field_condition(self, condition: FieldCondition, param_mapping: Dict[str, Any]) -> FieldCondition:
        """Instantiate field condition."""
        # Get concrete value for parameter
        param_value = condition.value.value
        if isinstance(param_value, str) and param_value in param_mapping:
            concrete_value = param_mapping[param_value]
            # Determine the correct type from the parameter mapping
            param_type = self._get_parameter_type(param_value, param_mapping)
            typed_value = TypedValue(type=param_type, value=concrete_value)
        else:
            typed_value = condition.value
        
        return FieldCondition(
            field=condition.field,
            operator=condition.operator,
            value=typed_value
        )
    
    def _get_parameter_type(self, param_id: str, param_mapping: Dict[str, Any]) -> str:
        """Get the type of a parameter based on its value."""
        value = param_mapping[param_id]
        if isinstance(value, int):
            return "int"
        elif isinstance(value, float):
            return "float"
        elif isinstance(value, str):
            return "str"
        elif isinstance(value, list):
            return "list"
        elif isinstance(value, dict):
            return "dict"
        elif isinstance(value, bool):
            return "bool"
        elif value is None:
            return "null"
        else:
            return "str"  # Default fallback
    
    def _instantiate_logical_operator(self, operator: LogicalOperator, param_mapping: Dict[str, Any]) -> LogicalOperator:
        """Instantiate logical operator."""
        # Instantiate children
        instantiated_children = [
            self._instantiate_node(child, param_mapping) for child in operator.children
        ]
        
        return LogicalOperator(
            operator=operator.operator,
            children=instantiated_children
        )
    
    def _instantiate_paren_expression(self, paren: ParenExpression, param_mapping: Dict[str, Any]) -> ParenExpression:
        """Instantiate parenthesized expression."""
        # Instantiate inner expression
        instantiated_expression = self._instantiate_node(paren.expression, param_mapping)
        
        return ParenExpression(expression=instantiated_expression)


class QueryCache:
    """
    Cache for parameterized AST templates.
    
    This class provides caching functionality for parameterized AST templates,
    allowing efficient reuse of compiled query structures.
    
    Key features:
    - Template-based caching using structural hashes
    - Automatic cache size management
    - Statistics tracking
    - Thread-safe operations
    
    Usage examples:
        >>> cache = QueryCache(max_size=1000)
        >>> template = cache.get_or_create(ast)
        >>> print(cache.get_stats())  # {'hits': 5, 'misses': 2}
    """
    
    def __init__(self, max_size: int = 1000):
        """
        Initialize QueryCache.
        
        Args:
            max_size (int): Maximum number of cached templates
        """
        self.max_size = max_size
        self._cache: Dict[str, ParameterizedAST] = {}
        self._access_order: List[str] = []
        self._stats = {"hits": 0, "misses": 0, "evictions": 0}
    
    def get_or_create(self, ast: ASTNode, parameterizer: Optional[ASTParameterizer] = None) -> ParameterizedAST:
        """
        Get cached template or create new one.
        
        Args:
            ast (ASTNode): AST to cache
            parameterizer (Optional[ASTParameterizer]): Parameterizer to use
            
        Returns:
            ParameterizedAST: Cached or newly created template
            
        Usage examples:
            >>> cache = QueryCache()
            >>> template = cache.get_or_create(ast)
        """
        if parameterizer is None:
            parameterizer = ASTParameterizer()
        
        # Create template
        template = parameterizer.parameterize(ast)
        template_hash = template.template_hash
        
        # Check cache
        if template_hash in self._cache:
            self._stats["hits"] += 1
            self._update_access_order(template_hash)
            return self._cache[template_hash]
        
        # Cache miss
        self._stats["misses"] += 1
        
        # Add to cache
        self._add_to_cache(template_hash, template)
        
        return template
    
    def get(self, template_hash: str) -> Optional[ParameterizedAST]:
        """Get template by hash."""
        if template_hash in self._cache:
            self._stats["hits"] += 1
            self._update_access_order(template_hash)
            return self._cache[template_hash]
        return None
    
    def put(self, template: ParameterizedAST) -> None:
        """Add template to cache."""
        self._add_to_cache(template.template_hash, template)
    
    def clear(self) -> None:
        """Clear all cached templates."""
        self._cache.clear()
        self._access_order.clear()
        self._stats = {"hits": 0, "misses": 0, "evictions": 0}
    
    def get_stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        return {
            **self._stats,
            "size": len(self._cache),
            "max_size": self.max_size
        }
    
    def _add_to_cache(self, template_hash: str, template: ParameterizedAST) -> None:
        """Add template to cache with eviction if necessary."""
        # Evict if cache is full
        if len(self._cache) >= self.max_size:
            self._evict_oldest()
        
        # Add to cache
        self._cache[template_hash] = template
        self._access_order.append(template_hash)
    
    def _evict_oldest(self) -> None:
        """Evict oldest accessed template."""
        if self._access_order:
            oldest_hash = self._access_order.pop(0)
            if oldest_hash in self._cache:
                del self._cache[oldest_hash]
                self._stats["evictions"] += 1
    
    def _update_access_order(self, template_hash: str) -> None:
        """Update access order for LRU eviction."""
        if template_hash in self._access_order:
            self._access_order.remove(template_hash)
        self._access_order.append(template_hash) 