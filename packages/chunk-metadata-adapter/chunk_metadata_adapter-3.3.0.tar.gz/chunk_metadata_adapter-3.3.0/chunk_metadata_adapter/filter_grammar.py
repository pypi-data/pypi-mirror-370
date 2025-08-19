"""
Lark grammar for SQL-like WHERE expressions (расширено: dict-литералы).

This module provides a standard SQL WHERE grammar for filter expressions,
с поддержкой строк в одинарных/двойных кавычках, булевых, null/None, списков, кастомных операторов и dict-литералов.
"""

from lark import Lark
from typing import List, Optional, Dict, Any

# Global parser cache for better performance
_GLOBAL_PARSER_CACHE: Optional[Lark] = None

FILTER_GRAMMAR = """
%import common.WS
%import common.CNAME
%import common.NUMBER
%import common.ESCAPED_STRING -> STRING
%import common.SIGNED_NUMBER
%ignore WS

RAW_STRING: /'[^']*'/

TRUE: "TRUE"i
FALSE: "FALSE"i
NULL: "NULL"i
NONE: "NONE"i | "None"i
INTERSECTS: "intersects"i
CONTAINS_KEY: "contains_key"i
CONTAINS_VALUE: "contains_value"i

// Операторы сравнения как отдельные токены
EQUAL: "="
NOTEQUAL: "!=" | "<>"
MORETHAN: ">"
MOREEQUAL: ">="
LESSTHAN: "<"
LESSEQUAL: "<="
LIKE: "LIKE"i
TILDE: "~"
NOT_TILDE: "!~"

?start: expr

?expr: expr XOR term   -> xor
     | expr OR term   -> or
     | term

?term: term AND factor -> and
     | factor

?factor: NOT factor   -> not
       | comparison
       | "(" expr ")"

?comparison: field_name comparator value
           | field_name IS NULL      -> is_null
           | field_name IS NOT NULL  -> is_not_null
           | field_name IN "(" value_list ")" -> in_list
           | field_name IN array -> in_array
           | field_name INTERSECTS value -> intersects
           | field_name CONTAINS_KEY value -> contains_key
           | field_name CONTAINS_VALUE value -> contains_value
           | NOT field_name          -> not_field

comparator: EQUAL | NOTEQUAL | MORETHAN | MOREEQUAL | LESSTHAN | LESSEQUAL | LIKE | TILDE | NOT_TILDE

value_list: value ("," value)*

?value: NUMBER | STRING | RAW_STRING | TRUE | FALSE | NULL | NONE | array | dict

?array: "[" [value ("," value)*] "]"

?dict: "{" [pair ("," pair)*] "}"
?pair: dict_key ":" value
?dict_key: STRING | RAW_STRING | CNAME

field_name: CNAME ("." CNAME)*

AND: "AND"i
OR: "OR"i
XOR: "XOR"i
NOT: "NOT"i
IS: "IS"i
IN: "IN"i
"""


class FilterGrammarValidator:
    """
    Validator for filter grammar syntax and semantics.
    
    This class provides methods to validate filter expressions
    against the grammar and check for common errors.
    
    Attributes:
        parser (Lark): Cached Lark parser instance
        max_query_length (int): Maximum allowed query length
        
    Methods:
        validate_syntax(query): Validate query syntax
        validate_semantics(query): Validate query semantics
        get_errors(query): Get detailed error information
    """
    
    def __init__(self, max_query_length: int = 10000) -> None:
        """
        Initialize FilterGrammarValidator.
        
        Args:
            max_query_length: Maximum allowed query length in characters
        """
        self.max_query_length = max_query_length
    
    @property
    def parser(self) -> Lark:
        """Get or create cached Lark parser instance."""
        global _GLOBAL_PARSER_CACHE
        if _GLOBAL_PARSER_CACHE is None:
            _GLOBAL_PARSER_CACHE = Lark(FILTER_GRAMMAR, start='start', parser='lalr')
        return _GLOBAL_PARSER_CACHE
    
    def validate_syntax(self, query: str) -> bool:
        """
        Validate query syntax.
        
        Args:
            query: Filter expression string to validate
            
        Returns:
            bool: True if syntax is valid, False otherwise
        """
        if not query or not query.strip():
            return False
        
        if len(query) > self.max_query_length:
            return False
        
        try:
            self.parser.parse(query)
            return True
        except Exception:
            return False
    
    def validate_semantics(self, query: str) -> List[str]:
        """
        Validate query semantics and return warnings.
        
        Args:
            query: Filter expression string to validate
            
        Returns:
            List[str]: List of semantic warnings
        """
        warnings = []
        
        # Check for common semantic issues
        if "like" in query.lower() and "~" in query:
            warnings.append("Mixing 'like' and regex operators may cause confusion")
        
        if query.count("(") != query.count(")"):
            warnings.append("Unmatched parentheses detected")
        
        if "null" in query.lower() and "=" in query:
            warnings.append("Consider using 'IS NULL' or 'IS NOT NULL' for null comparisons")
        
        return warnings
    
    def get_errors(self, query: str) -> Dict[str, Any]:
        """
        Get detailed error information for invalid query.
        
        Args:
            query: Filter expression string to analyze
            
        Returns:
            Dict[str, Any]: Error information including type, message, and position
        """
        errors = {
            "syntax_valid": False,
            "semantic_warnings": [],
            "error_type": None,
            "error_message": None,
            "error_position": None
        }
        
        try:
            # Try to parse
            self.parser.parse(query)
            errors["syntax_valid"] = True
        except Exception as e:
            errors["error_type"] = type(e).__name__
            errors["error_message"] = str(e)
            # Try to extract position information
            if hasattr(e, 'pos_in_stream'):
                errors["error_position"] = e.pos_in_stream
        
        # Get semantic warnings
        errors["semantic_warnings"] = self.validate_semantics(query)
        
        return errors


class FilterGrammarExamples:
    """
    Examples of valid filter expressions for testing and documentation.
    
    This class provides comprehensive examples of filter expressions
    that can be parsed by the grammar, organized by complexity and type.
    """
    
    @staticmethod
    def get_simple_examples() -> List[str]:
        """Get simple filter expression examples."""
        return [
            # Numeric comparisons
            "age > 18",
            "quality_score >= 0.8",
            "feedback_accepted != 0",
            "year = 2024",
            
            # String comparisons
            "title = 'Python Tutorial'",
            "description like 'AI'",
            "author ~ 'John.*Doe'",
            
            # Boolean values
            "is_public = true",
            "used_in_generation != false",
            
            # Null values
            "summary = null",
            "year != null"
        ]
    
    @staticmethod
    def get_complex_examples() -> List[str]:
        """Get complex filter expression examples."""
        return [
            # Logical operators
            "age > 18 AND status = 'active'",
            "type = 'DocBlock' OR type = 'CodeBlock'",
            "NOT is_deleted = true",
            
            # Parentheses for precedence
            "(age > 18 OR vip = true) AND status = 'active'",
            "NOT (is_deleted = true OR is_archived = true)",
            
            # Nested fields
            "user.profile.name = 'John'",
            "block_meta.version = '1.0'",
            "metrics.quality.score > 0.8"
        ]
    
    @staticmethod
    def get_list_examples() -> List[str]:
        """Get list operation examples."""
        return [
            # Inclusion operators
            "tags intersects ['ai', 'ml']",
            "categories intersects ['tutorial', 'guide']",
            "years intersects [2020, 2021, 2022]",
            
            # Exact list matching
            "tags = ['python', 'ai', 'tutorial']",
            "years = [2020, 2021, 2022]"
        ]
    
    @staticmethod
    def get_dict_examples() -> List[str]:
        """Get dictionary operation examples."""
        return [
            # Dictionary operations
            "block_meta contains_key 'version'",
            "metadata contains_value 'John'",
            
            # Exact dictionary matching
            "block_meta = {'version': '1.0', 'author': 'John'}",
            
            # Total chunks metadata examples
            "block_meta.total_chunks_in_source = 5",
            "block_meta.is_last_chunk = true",
            "block_meta.is_first_chunk = true",
            "block_meta.chunk_percentage > 50"
        ]
    
    @staticmethod
    def get_date_examples() -> List[str]:
        """Get date comparison examples."""
        return [
            # Date comparisons
            "created_at > '2024-01-01'",
            "updated_at >= '2024-01-01T12:00:00Z'",
            "published_at < '2024-12-31'"
        ]
    
    @staticmethod
    def get_business_examples() -> List[str]:
        """Get business scenario examples."""
        return [
            # Content management
            """
            type = 'DocBlock' AND
            quality_score >= 0.8 AND
            status = 'verified' AND
            (tags intersects ['documentation', 'guide'] OR 
             tags intersects ['tutorial', 'example']) AND
            year >= 2020 AND
            is_public = true AND
            NOT is_deleted = true
            """,
            
            # Analytics and reporting
            """
            (type = 'DocBlock' OR type = 'CodeBlock') AND
            feedback_accepted >= 5 AND
            used_in_generation = true AND
            (language = 'en' OR language = 'ru') AND
            created_at >= '2024-01-01T00:00:00Z' AND
            quality_score >= 0.7
            """,
            
            # Search and discovery
            """
            (title like 'Python' OR 
             summary like 'machine learning' OR
             tags intersects ['python', 'ai', 'ml']) AND
            (type = 'DocBlock' OR type = 'CodeBlock') AND
            quality_score >= 0.6 AND
            year >= 2020 AND
            is_public = true
            """,
            
            # Chunk position and source metadata
            """
            block_meta.total_chunks_in_source >= 10 AND
            block_meta.is_last_chunk = true AND
            quality_score >= 0.8 AND
            type = 'DocBlock'
            """,
            
            # First chunk with specific criteria
            """
            ordinal = 0 AND
            block_meta.is_first_chunk = true AND
            language = 'en' AND
            type = 'DocBlock'
            """
        ]
    
    @staticmethod
    def get_invalid_examples() -> List[str]:
        """Get invalid filter expression examples for testing error handling."""
        return [
            # Syntax errors
            "age >>>> 18",  # Invalid operator
            "(age > 18",    # Unclosed parentheses
            "title = 'unclosed",  # Unclosed quotes
            "age > AND status = 'active'",  # Invalid syntax
            
            # Semantic errors
            "field..nested = 'value'",  # Invalid field name
            "field name = 'value'",  # Invalid field name with space
            "field-name = 'value'",  # Invalid field name with dash
            "123field = 'value'",  # Invalid field name starting with number
            "field = 'value' AND"  # Incomplete expression
        ]


# Export the grammar and validator
__all__ = [
    "FILTER_GRAMMAR",
    "FilterGrammarValidator", 
    "FilterGrammarExamples"
] 