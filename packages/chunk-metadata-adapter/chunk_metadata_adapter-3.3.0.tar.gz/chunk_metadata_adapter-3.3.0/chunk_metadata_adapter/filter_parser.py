"""
Filter parser using Lark grammar for expression parsing.

This module provides the FilterParser class, which parses filter expressions
into Abstract Syntax Trees (AST) using the Lark grammar and AST node classes.
It includes a FilterTransformer for converting Lark parse trees to AST nodes.

Key features:
- Parses filter strings into AST (FieldCondition, LogicalOperator, ParenExpression)
- Supports all operators and data types from filter_grammar.py
- Caches Lark parser for performance
- Handles syntax and validation errors with detailed messages
- Full date support with ISO formats and validation

Usage examples:
    >>> parser = FilterParser()
    >>> ast = parser.parse("age > 18 AND status = 'active'")
    >>> print(ast)

Dependencies:
- lark: For parsing and tree transformation
- ast_nodes: For AST node classes
- datetime: For date parsing and validation

Author: Development Team
Created: 2024-06-13
Updated: 2024-06-13
"""

from typing import Optional, List, Any
from datetime import datetime, date
import re
from lark import Lark, Transformer, Tree, Token, exceptions
from .ast import ASTNode, FieldCondition, LogicalOperator, ParenExpression, TypedValue
from .filter_grammar import FILTER_GRAMMAR

class FilterParseError(ValueError):
    """
    Raised when filter parsing fails.

    This exception is raised when the FilterParser encounters an invalid
    filter expression that cannot be parsed into a valid AST. Common causes
    include syntax errors, invalid operators, or malformed expressions.

    Attributes:
        message (str): Human-readable error message describing the parse error
        query (str): The original query string that failed to parse
        position (int): Character position where the error occurred

    Usage examples:
        >>> try:
        ...     parser.parse("age > AND status = 'active'")
        ... except FilterParseError as e:
        ...     print(f"Parse error at position {e.position}: {e.message}")

    Notes:
        - Position is 0-indexed
        - Query is preserved for debugging purposes
        - Expected value may be None if not determinable
    """
    def __init__(self, message: str, query: str, position: Optional[int] = None):
        self.message = message
        self.query = query
        self.position = position
        super().__init__(f"Parse error: {message}")

class FilterTransformer(Transformer):
    """
    Transformer for converting Lark parse tree to AST nodes.

    This class transforms the Lark parse tree into the project's AST node
    classes (FieldCondition, LogicalOperator, ParenExpression, etc.).
    It handles all supported operators and value types including dates.
    """
    
    # Date parsing patterns
    DATE_PATTERNS = [
        # ISO 8601 with timezone
        r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z?$',
        # ISO 8601 without timezone
        r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?$',
        # Date only (YYYY-MM-DD)
        r'^\d{4}-\d{2}-\d{2}$',
        # Date with time (YYYY-MM-DD HH:MM:SS)
        r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$',
        # Date with time and milliseconds (YYYY-MM-DD HH:MM:SS.mmm)
        r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+$',
    ]
    
    def _is_date_string(self, value_str: str) -> bool:
        """Check if string represents a valid date format."""
        # Remove quotes if present
        if value_str.startswith('"') and value_str.endswith('"'):
            value_str = value_str[1:-1]
        elif value_str.startswith("'") and value_str.endswith("'"):
            value_str = value_str[1:-1]
        
        # Check against patterns
        for pattern in self.DATE_PATTERNS:
            if re.match(pattern, value_str):
                return True
        return False
    
    def _parse_date(self, value_str: str) -> str:
        """Parse date string and return ISO format."""
        # Remove quotes if present
        if value_str.startswith('"') and value_str.endswith('"'):
            value_str = value_str[1:-1]
        elif value_str.startswith("'") and value_str.endswith("'"):
            value_str = value_str[1:-1]
        
        try:
            # Try different date formats
            if 'T' in value_str:
                # ISO format with T
                if value_str.endswith('Z'):
                    dt = datetime.fromisoformat(value_str[:-1])
                else:
                    dt = datetime.fromisoformat(value_str)
            elif ' ' in value_str:
                # Date with space separator
                if '.' in value_str:
                    dt = datetime.strptime(value_str, '%Y-%m-%d %H:%M:%S.%f')
                else:
                    dt = datetime.strptime(value_str, '%Y-%m-%d %H:%M:%S')
            else:
                # Date only
                dt = datetime.strptime(value_str, '%Y-%m-%d')
            
            # Return ISO format
            return dt.isoformat()
        except ValueError:
            # If parsing fails, return original string
            return value_str

    def or_expr(self, args: List[Any]) -> ASTNode:
        """Transform OR expression."""
        print(f"LOG: or_expr args={args}")
        # Фильтруем токены операторов, оставляем только выражения
        filtered_children = []
        for arg in args:
            if isinstance(arg, Token) and arg.type == 'OR':
                continue
            filtered_children.append(arg)
        
        if len(filtered_children) == 1:
            return filtered_children[0]
        
        # Создаем LogicalOperator с правильными детьми
        return LogicalOperator(operator="OR", children=filtered_children)

    def xor_expr(self, args: List[Any]) -> ASTNode:
        print(f"LOG: xor_expr args={args}")
        filtered_children = [arg for arg in args if not (isinstance(arg, Token) and arg.type == 'XOR')]
        if len(filtered_children) == 1:
            return filtered_children[0]
        return LogicalOperator(operator="XOR", children=filtered_children)

    def and_expr(self, args: List[Any]) -> ASTNode:
        """Transform AND expression."""
        print(f"LOG: and_expr args={args}")
        # Фильтруем токены операторов, оставляем только выражения
        filtered_children = []
        for arg in args:
            if isinstance(arg, Token) and arg.type == 'AND':
                continue
            filtered_children.append(arg)
        
        if len(filtered_children) == 1:
            return filtered_children[0]
        
        # Создаем LogicalOperator с правильными детьми
        return LogicalOperator(operator="AND", children=filtered_children)

    def not_expr(self, args: List[Any]) -> ASTNode:
        """Transform NOT expression."""
        print(f"LOG: not_expr called, args={args}")
        if len(args) == 1:
            return args[0]
        
        # Если первый аргумент - токен NOT, создаем LogicalOperator
        if isinstance(args[0], Token) and args[0].type == "NOT":
            return LogicalOperator(operator="NOT", children=[args[1]])
        
        return args[0]

    def comparison(self, args: List[Any]) -> FieldCondition:
        """Transform comparison expression."""
        print(f"LOG: comparison called, args={args}")
        
        if len(args) == 3:
            field_name, operator, value = args
            
            # Если value - это кортеж от pair, преобразуем его в TypedValue
            if isinstance(value, tuple) and len(value) == 2:
                key, val = value
                # Если val это TypedValue, извлекаем его значение
                if isinstance(val, TypedValue):
                    dict_value = {key: val.value}
                else:
                    dict_value = {key: val}
                value = TypedValue(type="dict", value=dict_value)
            
            result = FieldCondition(field=field_name, operator=operator, value=value)
            print(f"LOG: AST result: {field_name} {operator} {value}")
            return result
        else:
            raise ValueError(f"Invalid comparison arguments: {args}")

    def not_field(self, args: List[Any]) -> FieldCondition:
        """Transform NOT field_name expression."""
        print(f"LOG: not_field called, args={args}")
        
        if len(args) == 2:
            not_token, field_name = args
            # Создаем условие field_name = false (эквивалент NOT field_name)
            result = FieldCondition(field=field_name, operator="=", value=TypedValue("bool", False))
            print(f"LOG: AST result: NOT {field_name}")
            return result
        else:
            raise ValueError(f"Invalid not_field arguments: {args}")

    def field_expr(self, args: List[Any]) -> FieldCondition:
        """Transform field expression (alias for comparison)."""
        print(f"LOG: field_expr called, args={args}")
        return self.comparison(args)
    
    def intersects(self, args: List[Any]) -> FieldCondition:
        """Transform intersects expression."""
        print(f"LOG: intersects called, args={args}")
        if len(args) == 3:
            field, operator, value = args
            return FieldCondition(field=field, operator="intersects", value=value)
        elif len(args) == 2:
            field, value = args
            return FieldCondition(field=field, operator="intersects", value=value)
        return args[0]

    def paren_expr(self, args: List[Any]) -> ParenExpression:
        """Transform parenthesized expression."""
        return ParenExpression(expression=args[0])

    def field_name(self, args: List[Any]) -> str:
        """Transform field name (dot notation)."""
        return ".".join(str(a) for a in args)

    # Операторы сравнения
    def comparison_op(self, args: List[Any]) -> str:
        """Transform comparison operator."""
        if not args:
            return "="  # fallback
        return str(args[0])

    # Операторы включения
    def inclusion_op(self, args: List[Any]) -> str:
        """Transform inclusion operator."""
        if not args:
            return "in"  # fallback
        return str(args[0])

    # Строковые операторы
    def string_op(self, args: List[Any]) -> str:
        """Transform string operator."""
        if not args:
            return "like"  # fallback
        return str(args[0])

    # Операторы словарей
    def dict_op(self, args: List[Any]) -> str:
        """Transform dict operator."""
        if not args:
            return "contains_key"  # fallback
        return str(args[0])

    # Методы для обработки операторов как токенов
    def __default__(self, data, children, meta):
        """Default transformer method."""
        print(f"LOG: __default__ called: data={data}, children={children}")
        
        # Обработка логических операторов
        if data == "or":
            # Фильтруем токены операторов, оставляем только выражения
            filtered_children = []
            for child in children:
                if isinstance(child, Token) and child.type == 'OR':
                    continue
                if isinstance(child, str) and child == 'OR':
                    continue
                filtered_children.append(child)
            
            if len(filtered_children) == 1:
                return filtered_children[0]
            
            return LogicalOperator(operator="OR", children=filtered_children)
        
        elif data == "and":
            # Фильтруем токены операторов, оставляем только выражения
            filtered_children = []
            for child in children:
                if isinstance(child, Token) and child.type == 'AND':
                    continue
                if isinstance(child, str) and child == 'AND':
                    continue
                filtered_children.append(child)
            
            if len(filtered_children) == 1:
                return filtered_children[0]
            
            return LogicalOperator(operator="AND", children=filtered_children)
        
        elif data == "not":
            if len(children) == 1:
                return children[0]
            
            # Если первый аргумент - токен NOT, создаем LogicalOperator
            if isinstance(children[0], Token) and children[0].type == "NOT":
                return LogicalOperator(operator="NOT", children=[children[1]])
            if isinstance(children[0], str) and children[0] == "NOT":
                return LogicalOperator(operator="NOT", children=[children[1]])
            
            return children[0]
        
        elif data == "xor":
            # Фильтруем токены операторов, оставляем только выражения
            filtered_children = []
            for child in children:
                if isinstance(child, Token) and child.type == 'XOR':
                    continue
                if isinstance(child, str) and child == 'XOR':
                    continue
                filtered_children.append(child)
            
            if len(filtered_children) == 1:
                return filtered_children[0]
            
            return LogicalOperator(operator="XOR", children=filtered_children)
        
        # Обработка операторов сравнения
        elif data in ['>', '<', '>=', '<=', '=', '!=']:
            return data
        
        # Обработка операторов включения
        elif data in ['in', 'not_in']:
            return data
        
        # Обработка строковых операторов
        elif data in ['like', '~', '!~']:
            return data
        
        # Обработка операторов словарей
        elif data in ['contains_key', 'contains_value']:
            return data
        
        # Обработка специальных конструкций
        elif data == "in_array":
            if len(children) == 3:
                field, operator, array_value = children
                return FieldCondition(field=field, operator="in", value=array_value)
            return children[0] if children else data
        
        elif data == "intersects":
            if len(children) == 3:
                field, operator, array_value = children
                # Если operator это строка "intersects", игнорируем его
                if operator == "intersects":
                    return FieldCondition(field=field, operator="intersects", value=array_value)
                else:
                    return FieldCondition(field=field, operator="intersects", value=array_value)
            elif len(children) == 2:
                field, second_arg = children
                # Если второй аргумент - TypedValue, создаем FieldCondition
                if isinstance(second_arg, TypedValue):
                    return FieldCondition(field=field, operator="intersects", value=second_arg)
                else:
                    # Иначе возвращаем первый аргумент
                    return field
            elif len(children) == 1:
                return children[0]
            return children[0] if children else data
        
        elif data == "array":
            # Собираем все элементы массива
            values = []
            for child in children:
                if isinstance(child, TypedValue):
                    values.append(child.value)
                else:
                    # Обработка строк в массиве
                    s = str(child)
                    if s.startswith("'") and s.endswith("'"):
                        s = s[1:-1]
                    elif s.startswith('"') and s.endswith('"'):
                        s = s[1:-1]
                    values.append(s)
            return TypedValue(type="list", value=values)
        
        elif data == "dict":
            # Собираем все пары в словарь
            d = {}
            for child in children:
                if isinstance(child, tuple) and len(child) == 2:
                    key, value = child
                    d[str(key)] = value.value if isinstance(value, TypedValue) else value
            return TypedValue(type="dict", value=d)
        
        elif data == "pair":
            # Создаем пару ключ-значение
            if len(children) == 2:
                key, value = children
                return (str(key), value.value if isinstance(value, TypedValue) else value)
            return children[0] if children else data
        
        # Возвращаем первый дочерний элемент или данные
        return children[0] if children else data

    # Методы для токенов операторов сравнения
    def EQUAL(self, token):
        return "="

    def NOTEQUAL(self, token):
        return "!="

    def MORETHAN(self, token):
        return ">"

    def MOREEQUAL(self, token):
        return ">="

    def LESSTHAN(self, token):
        return "<"

    def LESSEQUAL(self, token):
        return "<="

    # Методы для токенов строковых операторов
    def LIKE(self, token):
        return "like"

    def TILDE(self, token):
        return "~"

    def NOT_TILDE(self, token):
        return "!~"

    # Методы для токенов операторов включения
    def IN(self, token):
        return "in"

    def NOT_IN(self, token):
        return "not_in"

    def INTERSECTS(self, token):
        return "intersects"

    # Методы для токенов операторов словарей
    def CONTAINS_KEY(self, token):
        return "contains_key"

    def CONTAINS_VALUE(self, token):
        return "contains_value"

    # Logical operator tokens
    def NOT(self, token):
        return "NOT"
    
    def AND(self, token):
        return "AND"
    
    def OR(self, token):
        return "OR"
    
    def XOR(self, token):
        return "XOR"

    # Методы для обработки операторов как строк
    def comparator(self, args: List[Any]) -> str:
        """Transform comparator operator."""
        if not args:
            return "="  # fallback
        return str(args[0])

    def number(self, args: List[Any]) -> TypedValue:
        token = args[0]
        if "." in str(token):
            return TypedValue(type="float", value=float(token))
        return TypedValue(type="int", value=int(token))

    def string(self, args: List[Any]) -> TypedValue:
        token = args[0]
        s = str(token)
        if s.startswith("\"") and s.endswith("\""):
            s = s[1:-1]
        elif s.startswith("'") and s.endswith("'"):
            s = s[1:-1]
        return TypedValue(type="str", value=s)

    def boolean(self, args: List[Any]) -> TypedValue:
        val = str(args[0]).lower()
        return TypedValue(type="bool", value=(val == "true"))

    def null_value(self, args: List[Any]) -> TypedValue:
        return TypedValue(type="null", value=None)

    def array_value(self, args: List[Any]) -> TypedValue:
        values = []
        for v in args:
            if isinstance(v, TypedValue):
                values.append(v.value)
            else:
                # Обработка строк в массиве
                s = str(v)
                if s.startswith("'") and s.endswith("'"):
                    s = s[1:-1]
                elif s.startswith('"') and s.endswith('"'):
                    s = s[1:-1]
                values.append(s)
        return TypedValue(type="list", value=values)

    def dict_value(self, args: List[Any]) -> TypedValue:
        d = dict(args)
        return TypedValue(type="dict", value=d)

    def pair(self, args: List[Any]) -> tuple:
        key, value = args
        return (str(key), value.value if isinstance(value, TypedValue) else value)

    def date_value(self, args: List[Any]) -> TypedValue:
        # Улучшенная обработка дат
        s = str(args[0])
        if s.startswith('"') and s.endswith('"'):
            s = s[1:-1]
        elif s.startswith("'") and s.endswith("'"):
            s = s[1:-1]
        
        # Парсим и валидируем дату
        parsed_date = self._parse_date(s)
        return TypedValue(type="date", value=parsed_date)

    def primitive_value(self, args: List[Any]) -> TypedValue:
        return args[0]

    def value(self, args: List[Any]) -> Any:
        return args[0]

    def TRUE(self, token):
        return TypedValue(type="bool", value=True)

    def FALSE(self, token):
        return TypedValue(type="bool", value=False)

    def NULL(self, token):
        return TypedValue(type="null", value=None)

    def INT(self, token):
        return TypedValue(type="int", value=int(token))

    def FLOAT(self, token):
        return TypedValue(type="float", value=float(token))

    def STRING(self, token):
        s = str(token)
        if s.startswith('"') and s.endswith('"'):
            s = s[1:-1]
        
        # Проверяем, не является ли это датой
        if self._is_date_string(s):
            parsed_date = self._parse_date(s)
            return TypedValue(type="date", value=parsed_date)
        
        return TypedValue(type="str", value=s)

    def RAW_STRING(self, token):
        s = str(token)
        if s.startswith("'") and s.endswith("'"):
            s = s[1:-1]
        
        # Проверяем, не является ли это датой
        if self._is_date_string(s):
            parsed_date = self._parse_date(s)
            return TypedValue(type="date", value=parsed_date)
        
        return TypedValue(type="str", value=s)

    def DATE_ISO(self, token):
        s = str(token)
        if s.startswith('"') and s.endswith('"'):
            s = s[1:-1]
        
        # Парсим и валидируем дату
        parsed_date = self._parse_date(s)
        return TypedValue(type="date", value=parsed_date)

    def CNAME(self, token):
        return str(token)

    def NUMBER(self, token):
        """Transform NUMBER token to TypedValue."""
        s = str(token)
        if "." in s:
            return TypedValue(type="float", value=float(s))
        return TypedValue(type="int", value=int(s))


class FilterParser:
    """
    Parser for filter expressions using Lark grammar.

    This class parses filter query strings into Abstract Syntax Trees (AST)
    using the project's Lark grammar and AST node classes. It caches the parser
    for performance and provides detailed error messages on failure.

    Attributes:
        max_query_length (int): Maximum allowed query length (default: 10000)

    Methods:
        parse(query): Parse filter string into AST

    Usage examples:
        >>> parser = FilterParser()
        >>> ast = parser.parse("age > 18 AND status = 'active'")
        >>> print(type(ast))

    Raises:
        FilterParseError: When query is invalid or cannot be parsed
    """
    _parser_cache: Optional[Lark] = None

    def __init__(self, max_query_length: int = 10000) -> None:
        self.max_query_length = max_query_length

    @classmethod
    def _get_parser(cls) -> Lark:
        # Очищаем кэш для отладки
        cls._parser_cache = None
        if cls._parser_cache is None:
            from .filter_grammar import FILTER_GRAMMAR
            cls._parser_cache = Lark(FILTER_GRAMMAR, parser="lalr", propagate_positions=True)
        return cls._parser_cache

    def parse(self, query: str) -> ASTNode:
        print(f"LOG: parse called with query: {query}")
        self._validate_query(query)
        parser = self._get_parser()
        try:
            tree = parser.parse(query)
            print(f"LOG: Lark parse tree: {tree.pretty()}")
            transformer = FilterTransformer()
            result = transformer.transform(tree)
            print(f"LOG: AST result: {result}")
            return result
        except exceptions.LarkError as e:
            pos = getattr(e, 'pos_in_stream', None)
            raise FilterParseError(str(e), query, pos)
        except Exception as e:
            raise FilterParseError(str(e), query)

    def _validate_query(self, query: str) -> None:
        if not query or not query.strip():
            raise FilterParseError("Query cannot be empty", query)
        if len(query) > self.max_query_length:
            raise FilterParseError(f"Query too long: {len(query)} > {self.max_query_length}", query) 