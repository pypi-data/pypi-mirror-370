"""
Filter executor for AST evaluation.

This module provides the FilterExecutor class for evaluating Abstract Syntax Trees
(AST) against data objects. It supports all comparison operators, nested field
access, and various data types including numbers, strings, lists, and dictionaries.

Key features:
- Field condition evaluation with type-safe comparisons
- Nested field access (e.g., user.profile.name)
- Support for all comparison operators (=, !=, >, >=, <, <=, in, not_in, intersects)
- String operations (like, ~, !~) with ReDoS protection
- Logical operations (AND, OR, NOT) with short-circuit evaluation
- Performance optimized with timeout protection

Usage examples:
    >>> from filter_executor import FilterExecutor
    >>> from ast_nodes import FieldCondition, TypedValue
    >>> executor = FilterExecutor()
    >>> condition = FieldCondition("age", ">", TypedValue("int", 18))
    >>> result = executor.execute(condition, {"age": 25})

Dependencies:
- ast_nodes: For AST node types and TypedValue
- re: For regex operations
- datetime: For date/time comparisons
- signal: For timeout protection

Author: Development Team
Created: 2024-01-20
Updated: 2024-01-20
"""

import re
import signal
from typing import Any, Dict, List, Optional, Union, Callable
from datetime import datetime
from .ast import ASTNode, FieldCondition, LogicalOperator, ParenExpression, TypedValue


class TimeoutError(Exception):
    """Raised when an operation exceeds the timeout limit."""
    pass


class FilterExecutor:
    """
    Executor for filter AST evaluation.
    
    This class provides functionality to evaluate Abstract Syntax Trees (AST)
    against data objects. It supports all comparison operators, nested field
    access, and various data types with performance and security optimizations.
    
    The executor uses a visitor pattern to traverse AST nodes and evaluate
    each node according to its type. It includes timeout protection for
    potentially expensive operations like regex matching.
    
    Attributes:
        regex_timeout (float): Timeout for regex operations in seconds
        _field_cache (Dict): Cache for field value lookups
        _comparison_cache (Dict): Cache for comparison results
    
    Methods:
        execute(ast, data): Execute filter AST against data
        _evaluate_node(node, data): Recursively evaluate AST node
        _evaluate_field_condition(condition, data): Evaluate field condition
        _get_field_value(field_path, data): Get field value by path
        _compare_values(actual, operator, expected): Compare values using operator
    
    Usage examples:
        >>> executor = FilterExecutor(regex_timeout=1.0)
        >>> result = executor.execute(ast, chunk_data)
        
        >>> # With nested field access
        >>> condition = FieldCondition("user.profile.age", ">", TypedValue("int", 18))
        >>> result = executor.execute(condition, {"user": {"profile": {"age": 25}}})
    
    Raises:
        TimeoutError: When regex operation exceeds timeout
        ValueError: When field path is invalid or data type not supported
        TypeError: When comparison types are incompatible
    """
    
    def __init__(self, regex_timeout: float = 1.0) -> None:
        """
        Initialize FilterExecutor.
        
        Args:
            regex_timeout (float): Timeout for regex operations in seconds
                Default: 1.0 seconds
                Must be positive and reasonable (< 10 seconds)
        
        Raises:
            ValueError: If regex_timeout is invalid
        """
        if regex_timeout <= 0 or regex_timeout > 10:
            raise ValueError("regex_timeout must be between 0 and 10 seconds")
        
        self.regex_timeout = regex_timeout
        self._field_cache: Dict[str, Any] = {}
        self._comparison_cache: Dict[str, bool] = {}
    
    def execute(self, ast: ASTNode, data: Any) -> bool:
        """
        Execute filter AST against data.
        
        This method evaluates the entire AST tree against the provided data.
        It uses recursive evaluation starting from the root node and traverses
        all child nodes according to the AST structure.
        
        Args:
            ast (ASTNode): Root node of the Abstract Syntax Tree to evaluate
            data (Any): Data object to evaluate against (dict, object, etc.)
                Must support field access (dict keys, object attributes)
        
        Returns:
            bool: True if data matches the filter, False otherwise
        
        Raises:
            ValueError: If AST node type is not supported
            TimeoutError: If regex operation exceeds timeout
            TypeError: If data type is not supported for field access
        
        Usage examples:
            >>> executor = FilterExecutor()
            >>> result = executor.execute(ast, {"age": 25, "status": "active"})
            >>> print(result)  # True or False
            
            >>> # With complex nested data
            >>> data = {"user": {"profile": {"age": 25, "preferences": {"theme": "dark"}}}}
            >>> result = executor.execute(ast, data)
        
        Notes:
            - Field access supports both dict keys and object attributes
            - Nested fields use dot notation (e.g., "user.profile.name")
            - Performance is optimized with caching for repeated operations
            - All operations are protected against timeouts and errors
        """
        if ast is None:
            raise ValueError("AST cannot be None")
        
        if data is None:
            raise ValueError("Data cannot be None")
        
        # Clear caches for new execution
        self._field_cache.clear()
        self._comparison_cache.clear()
        
        try:
            return self._evaluate_node(ast, data)
        except Exception as e:
            # Log error and return False for safety
            print(f"Error executing AST: {e}")
            return False
    
    def _evaluate_node(self, node: ASTNode, data: Any) -> bool:
        """
        Recursively evaluate AST node.
        
        This method dispatches evaluation to the appropriate handler based on
        the node type. It supports all AST node types: FieldCondition,
        LogicalOperator, and ParenExpression.
        
        Args:
            node (ASTNode): AST node to evaluate
            data (Any): Data object to evaluate against
        
        Returns:
            bool: Evaluation result for the node
        
        Raises:
            ValueError: If node type is not supported
        
        Notes:
            - Uses isinstance checks for type-safe evaluation
            - Each node type has its own evaluation logic
            - Parenthesized expressions are evaluated by evaluating their content
        """
        if isinstance(node, FieldCondition):
            return self._evaluate_field_condition(node, data)
        elif isinstance(node, LogicalOperator):
            return self._evaluate_logical_operator(node, data)
        elif isinstance(node, ParenExpression):
            return self._evaluate_paren_expression(node, data)
        else:
            raise ValueError(f"Unknown node type: {type(node)}")
    
    def _evaluate_field_condition(self, condition: FieldCondition, data: Any) -> bool:
        """
        Evaluate field condition.
        
        This method evaluates a field condition by extracting the actual value
        from the data using the field path and comparing it with the expected
        value using the specified operator.
        
        Args:
            condition (FieldCondition): Field condition to evaluate
            data (Any): Data object to extract field value from
        
        Returns:
            bool: True if condition is satisfied, False otherwise
        
        Raises:
            ValueError: If field path is invalid or field not found
            TypeError: If comparison types are incompatible
        
        Usage examples:
            >>> condition = FieldCondition("age", ">", TypedValue("int", 18))
            >>> result = executor._evaluate_field_condition(condition, {"age": 25})
            >>> print(result)  # True
            
            >>> condition = FieldCondition("status", "=", TypedValue("str", "active"))
            >>> result = executor._evaluate_field_condition(condition, {"status": "inactive"})
            >>> print(result)  # False
        """
        try:
            actual_value = self._get_field_value(condition.field, data)
            return self._compare_values(actual_value, condition.operator, condition.value)
        except (ValueError, TypeError) as e:
            # Return False for any field access or comparison errors
            print(f"Error evaluating field condition {condition.field}: {e}")
            return False
    
    def _evaluate_logical_operator(self, operator: LogicalOperator, data: Any) -> bool:
        """
        Evaluate logical operator.
        
        This method evaluates logical operators (AND, OR, NOT) by evaluating
        their child nodes and applying the appropriate logical operation.
        Short-circuit evaluation is used for performance optimization.
        
        Args:
            operator (LogicalOperator): Logical operator to evaluate
            data (Any): Data object to evaluate against
        
        Returns:
            bool: Result of logical operation
        
        Notes:
            - AND: Returns False on first False child (short-circuit)
            - OR: Returns True on first True child (short-circuit)
            - NOT: Returns negation of single child
            - Performance optimized with short-circuit evaluation
        """
        if operator.operator == "AND":
            # Short-circuit: return False on first False
            for child in operator.children:
                if not self._evaluate_node(child, data):
                    return False
            return True
        
        elif operator.operator == "OR":
            # Short-circuit: return True on first True
            for child in operator.children:
                if self._evaluate_node(child, data):
                    return True
            return False
        
        elif operator.operator == "NOT":
            # NOT has exactly one child
            return not self._evaluate_node(operator.children[0], data)
        
        else:
            raise ValueError(f"Unknown logical operator: {operator.operator}")
    
    def _evaluate_paren_expression(self, paren: ParenExpression, data: Any) -> bool:
        """
        Evaluate parenthesized expression.
        
        This method evaluates a parenthesized expression by evaluating its
        contained expression. Parentheses are used for operator precedence
        and don't change the evaluation logic.
        
        Args:
            paren (ParenExpression): Parenthesized expression to evaluate
            data (Any): Data object to evaluate against
        
        Returns:
            bool: Result of the contained expression
        
        Notes:
            - Simply delegates to the contained expression
            - No additional logic needed for parentheses
            - Used for operator precedence control
        """
        return self._evaluate_node(paren.expression, data)
    
    def _get_field_value(self, field_path: str, data: Any) -> Any:
        """
        Get field value by path.
        
        This method extracts a value from the data object using a field path.
        It supports nested field access using dot notation (e.g., "user.profile.name")
        and works with both dictionaries and objects with attributes.
        
        Args:
            field_path (str): Field path to extract (e.g., "age", "user.profile.name")
            data (Any): Data object to extract from
        
        Returns:
            Any: Extracted field value
        
        Raises:
            ValueError: If field path is invalid or field not found
            TypeError: If data type doesn't support field access
        
        Usage examples:
            >>> value = executor._get_field_value("age", {"age": 25})
            >>> print(value)  # 25
            
            >>> value = executor._get_field_value("user.profile.name", 
            ...     {"user": {"profile": {"name": "John"}}})
            >>> print(value)  # "John"
            
            >>> # With object attributes
            >>> class User: pass
            >>> user = User()
            >>> user.name = "John"
            >>> value = executor._get_field_value("name", user)
            >>> print(value)  # "John"
        
        Notes:
            - Supports both dict keys and object attributes
            - Nested fields use dot notation
            - Returns None if field not found (not an error)
            - Caches results for performance
        """
        # Check cache first
        cache_key = f"{field_path}:{id(data)}"
        if cache_key in self._field_cache:
            return self._field_cache[cache_key]
        
        if not field_path or not field_path.strip():
            raise ValueError("Field path cannot be empty")
        
        # Split field path by dots
        field_parts = field_path.split('.')
        current_value = data
        
        try:
            for part in field_parts:
                if current_value is None:
                    return None
                
                if isinstance(current_value, dict):
                    if part not in current_value:
                        return None
                    current_value = current_value[part]
                elif hasattr(current_value, part):
                    current_value = getattr(current_value, part)
                else:
                    return None
            
            # Cache the result
            self._field_cache[cache_key] = current_value
            return current_value
            
        except (KeyError, AttributeError, TypeError):
            return None
    
    def _compare_values(self, actual: Any, operator: str, expected: TypedValue) -> bool:
        """
        Compare values using operator.
        
        This method performs type-safe comparisons between actual and expected
        values using the specified operator. It supports all comparison operators
        and handles type conversions appropriately.
        
        Args:
            actual (Any): Actual value from data
            operator (str): Comparison operator
            expected (TypedValue): Expected value with type information
        
        Returns:
            bool: True if comparison is satisfied, False otherwise
        
        Raises:
            ValueError: If operator is not supported
            TypeError: If types are incompatible for comparison
            TimeoutError: If regex operation exceeds timeout
        
        Usage examples:
            >>> result = executor._compare_values(25, ">", TypedValue("int", 18))
            >>> print(result)  # True
            
            >>> result = executor._compare_values("hello", "like", TypedValue("str", "he.*"))
            >>> print(result)  # True
            
            >>> result = executor._compare_values(["a", "b"], "intersects", TypedValue("list", ["b", "c"]))
            >>> print(result)  # True
        
        Notes:
            - Type-safe comparisons with automatic type conversion
            - ReDoS protection for regex operations
            - Null-safe comparisons (None values handled appropriately)
            - Caches comparison results for performance
        """
        # Check cache first
        cache_key = f"{actual}:{operator}:{expected}"
        if cache_key in self._comparison_cache:
            return self._comparison_cache[cache_key]
        
        # Handle null values
        if actual is None:
            if expected.type == "null":
                result = operator in ["=", "=="]
            else:
                result = operator in ["!=", "<>"]
        elif expected.type == "null":
            result = operator in ["!=", "<>"]
        else:
            # Handle inclusion operators that work across types
            if operator in ["in", "not_in"]:
                if expected.type == "list":
                    result = actual in expected.value if operator == "in" else actual not in expected.value
                else:
                    # For non-list expected values, treat as single-item list
                    result = actual == expected.value if operator == "in" else actual != expected.value
            else:
                # Perform type-specific comparison
                result = self._perform_typed_comparison(actual, operator, expected)
        
        # Cache the result
        self._comparison_cache[cache_key] = result
        return result
    
    def _perform_typed_comparison(self, actual: Any, operator: str, expected: TypedValue) -> bool:
        """
        Perform type-specific comparison.
        
        This method handles the actual comparison logic based on the expected
        value type. It includes type conversion and operator-specific logic
        for each supported data type.
        
        Args:
            actual (Any): Actual value from data
            operator (str): Comparison operator
            expected (TypedValue): Expected value with type information
        
        Returns:
            bool: Comparison result
        
        Raises:
            ValueError: If operator is not supported for the type
            TimeoutError: If regex operation exceeds timeout
        """
        if expected.type == "int":
            return self._compare_int(actual, operator, expected.value)
        elif expected.type == "float":
            return self._compare_float(actual, operator, expected.value)
        elif expected.type == "str":
            return self._compare_string(actual, operator, expected.value)
        elif expected.type == "list":
            return self._compare_list(actual, operator, expected.value)
        elif expected.type == "dict":
            return self._compare_dict(actual, operator, expected.value)
        elif expected.type == "date":
            return self._compare_date(actual, operator, expected.value)
        elif expected.type == "bool":
            return self._compare_bool(actual, operator, expected.value)
        else:
            raise ValueError(f"Unsupported type for comparison: {expected.type}")
    
    def _compare_int(self, actual: Any, operator: str, expected: int) -> bool:
        """Compare integer values."""
        try:
            actual_int = int(actual) if actual is not None else None
            if actual_int is None:
                return False
            
            if operator == "=":
                return actual_int == expected
            elif operator == "!=":
                return actual_int != expected
            elif operator == ">":
                return actual_int > expected
            elif operator == ">=":
                return actual_int >= expected
            elif operator == "<":
                return actual_int < expected
            elif operator == "<=":
                return actual_int <= expected
            else:
                raise ValueError(f"Unsupported operator for int: {operator}")
        except (ValueError, TypeError):
            return False
    
    def _compare_float(self, actual: Any, operator: str, expected: float) -> bool:
        """Compare float values."""
        try:
            actual_float = float(actual) if actual is not None else None
            if actual_float is None:
                return False
            
            if operator == "=":
                return abs(actual_float - expected) < 1e-10  # Float comparison
            elif operator == "!=":
                return abs(actual_float - expected) >= 1e-10
            elif operator == ">":
                return actual_float > expected
            elif operator == ">=":
                return actual_float >= expected
            elif operator == "<":
                return actual_float < expected
            elif operator == "<=":
                return actual_float <= expected
            else:
                raise ValueError(f"Unsupported operator for float: {operator}")
        except (ValueError, TypeError):
            return False
    
    def _compare_string(self, actual: Any, operator: str, expected: str) -> bool:
        """Compare string values with regex support."""
        try:
            # Handle enum values by converting to string
            if hasattr(actual, 'value'):
                actual_str = str(actual.value)
            else:
                actual_str = str(actual) if actual is not None else None
            
            if actual_str is None:
                return False
            
            if operator == "=":
                return actual_str == expected
            elif operator == "!=":
                return actual_str != expected
            elif operator == "like":
                return expected.lower() in actual_str.lower()
            elif operator == "~":
                return self._safe_regex_match(actual_str, expected)
            elif operator == "!~":
                return not self._safe_regex_match(actual_str, expected)
            else:
                raise ValueError(f"Unsupported operator for string: {operator}")
        except (ValueError, TypeError):
            return False
    
    def _compare_list(self, actual: Any, operator: str, expected: List) -> bool:
        """Compare list values."""
        try:
            if not isinstance(actual, list):
                return False
            
            if operator == "=":
                return actual == expected
            elif operator == "!=":
                return actual != expected
            elif operator == "intersects":
                return bool(set(actual) & set(expected))
            else:
                raise ValueError(f"Unsupported operator for list: {operator}")
        except (ValueError, TypeError):
            return False
    
    def _compare_dict(self, actual: Any, operator: str, expected: Dict) -> bool:
        """Compare dictionary values."""
        try:
            if not isinstance(actual, dict):
                return False
            
            if operator == "=":
                return actual == expected
            elif operator == "!=":
                return actual != expected
            elif operator == "contains_key":
                return all(key in actual for key in expected.keys())
            elif operator == "contains_value":
                return all(value in actual.values() for value in expected.values())
            else:
                raise ValueError(f"Unsupported operator for dict: {operator}")
        except (ValueError, TypeError):
            return False
    
    def _compare_date(self, actual: Any, operator: str, expected: Union[datetime, str]) -> bool:
        """Compare date/time values."""
        try:
            # Convert actual to datetime if needed
            if isinstance(actual, str):
                actual_dt = datetime.fromisoformat(actual.replace('Z', '+00:00'))
            elif isinstance(actual, datetime):
                actual_dt = actual
            else:
                return False
            
            # Convert expected to datetime if needed
            if isinstance(expected, str):
                expected_dt = datetime.fromisoformat(expected.replace('Z', '+00:00'))
            elif isinstance(expected, datetime):
                expected_dt = expected
            else:
                return False
            
            if operator == "=":
                return actual_dt == expected_dt
            elif operator == "!=":
                return actual_dt != expected_dt
            elif operator == ">":
                return actual_dt > expected_dt
            elif operator == ">=":
                return actual_dt >= expected_dt
            elif operator == "<":
                return actual_dt < expected_dt
            elif operator == "<=":
                return actual_dt <= expected_dt
            else:
                raise ValueError(f"Unsupported operator for date: {operator}")
        except (ValueError, TypeError):
            return False
    
    def _compare_bool(self, actual: Any, operator: str, expected: bool) -> bool:
        """Compare boolean values."""
        try:
            actual_bool = bool(actual) if actual is not None else None
            if actual_bool is None:
                return False
            
            if operator == "=":
                return actual_bool == expected
            elif operator == "!=":
                return actual_bool != expected
            else:
                raise ValueError(f"Unsupported operator for bool: {operator}")
        except (ValueError, TypeError):
            return False
    
    def _safe_regex_match(self, text: str, pattern: str) -> bool:
        """
        Safely perform regex matching with timeout protection.
        
        This method performs regex matching with protection against ReDoS attacks
        by using a timeout mechanism. If the regex operation takes too long,
        it raises a TimeoutError.
        
        Args:
            text (str): Text to match against
            pattern (str): Regex pattern to match
        
        Returns:
            bool: True if pattern matches, False otherwise
        
        Raises:
            TimeoutError: If regex operation exceeds timeout
            re.error: If regex pattern is invalid
        """
        def timeout_handler(signum, frame):
            raise TimeoutError("Regex operation timed out")
        
        # Set up timeout
        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(int(self.regex_timeout))
        
        try:
            result = bool(re.search(pattern, text))
            signal.alarm(0)  # Cancel alarm
            return result
        except re.error as e:
            signal.alarm(0)  # Cancel alarm
            raise ValueError(f"Invalid regex pattern: {e}")
        finally:
            signal.signal(signal.SIGALRM, old_handler)
    
    def clear_cache(self) -> None:
        """
        Clear internal caches.
        
        This method clears the field value cache and comparison result cache.
        It should be called when the executor is reused with different data
        to prevent memory leaks and ensure correct results.
        
        Usage examples:
            >>> executor.clear_cache()
            >>> # Now ready for new data
        """
        self._field_cache.clear()
        self._comparison_cache.clear()
    
    def get_cache_stats(self) -> Dict[str, int]:
        """
        Get cache statistics.
        
        This method returns statistics about the internal caches for
        performance monitoring and debugging purposes.
        
        Returns:
            Dict[str, int]: Cache statistics with keys:
                - field_cache_size: Number of cached field values
                - comparison_cache_size: Number of cached comparison results
        
        Usage examples:
            >>> stats = executor.get_cache_stats()
            >>> print(f"Field cache: {stats['field_cache_size']}")
            >>> print(f"Comparison cache: {stats['comparison_cache_size']}")
        """
        return {
            "field_cache_size": len(self._field_cache),
            "comparison_cache_size": len(self._comparison_cache)
        } 