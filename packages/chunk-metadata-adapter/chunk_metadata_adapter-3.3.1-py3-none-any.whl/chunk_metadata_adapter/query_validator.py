"""
Query validator for security and correctness checking.

This module provides the QueryValidator class, which validates filter expressions
for security threats, structural correctness, and performance characteristics.
It uses AST analysis and pattern matching to detect various types of issues.

Key features:
- Security validation (ReDoS, injection attacks, dangerous patterns)
- Structural correctness validation using AST analysis
- Performance analysis and complexity assessment
- Detailed error reporting with recommendations
- Integration with existing AST structures and visitors

Usage examples:
    >>> validator = QueryValidator()
    >>> result = validator.validate("age > 18 AND status = 'active'")
    >>> print(f"Valid: {result.is_valid}")
    >>> print(f"Errors: {result.errors}")

Dependencies:
- ast_nodes: For AST structures and visitors
- filter_parser: For parsing queries into AST
- complexity_analyzer: For complexity analysis
- security_validator: For security validation
- performance_analyzer: For performance analysis

Author: Development Team
Created: 2024-06-13
Updated: 2024-06-13
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from .ast import ASTNode, ASTValidator
from .filter_parser import FilterParser, FilterParseError
from .complexity_analyzer import analyze_complexity
from .security_validator import SecurityValidator
from .performance_analyzer import PerformanceAnalyzer


@dataclass
class ValidationResult:
    """
    Result of query validation with detailed information.
    
    This class provides comprehensive validation results including
    success status, errors, warnings, and detailed analysis information.
    
    Attributes:
        is_valid (bool): Whether the query passed all validations
        errors (List[str]): List of validation errors that prevent execution
        warnings (List[str]): List of warnings that don't prevent execution
        details (Optional[Dict[str, Any]]): Detailed analysis information
            - complexity: Query complexity metrics
            - security: Security analysis results
            - performance: Performance impact assessment
            - recommendations: Optimization suggestions
    """
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    details: Optional[Dict[str, Any]] = None
    
    def __post_init__(self) -> None:
        """Initialize default details if not provided."""
        if self.details is None:
            self.details = {
                "complexity": {},
                "security": {},
                "performance": {},
                "recommendations": []
            }


class QueryValidator:
    """
    Validator for query safety and correctness.
    
    This class provides comprehensive validation of filter expressions
    including security checks, structural validation, and performance analysis.
    It uses AST-based analysis and pattern matching to detect issues.
    
    Attributes:
        max_depth (int): Maximum allowed AST depth (default: 10)
        max_conditions (int): Maximum allowed conditions (default: 100)
        regex_timeout (float): Timeout for regex operations in seconds (default: 1.0)
        max_query_length (int): Maximum query length in characters (default: 10000)
    
    Methods:
        validate(query): Validate query string for safety and correctness
        validate_ast(ast): Validate parsed AST structure
        analyze_complexity(query): Analyze query complexity metrics
        check_security(query): Perform security validation checks
    
    Usage examples:
        >>> validator = QueryValidator()
        >>> result = validator.validate("age > 18 AND status = 'active'")
        >>> if result.is_valid:
        ...     print("Query is safe to execute")
        ... else:
        ...     print(f"Validation errors: {result.errors}")
    
    Raises:
        ValueError: When validation parameters are invalid
    """
    
    def __init__(self, 
                 max_depth: int = 10,
                 max_conditions: int = 100,
                 regex_timeout: float = 1.0,
                 max_query_length: int = 10000) -> None:
        """
        Initialize QueryValidator with validation parameters.
        
        Args:
            max_depth: Maximum allowed AST depth
            max_conditions: Maximum allowed conditions in query
            regex_timeout: Timeout for regex operations in seconds
            max_query_length: Maximum query length in characters
        
        Raises:
            ValueError: When parameters are invalid
        """
        if max_depth < 1:
            raise ValueError("max_depth must be at least 1")
        if max_conditions < 1:
            raise ValueError("max_conditions must be at least 1")
        if regex_timeout <= 0:
            raise ValueError("regex_timeout must be positive")
        if max_query_length < 1:
            raise ValueError("max_query_length must be at least 1")
        
        self.max_depth = max_depth
        self.max_conditions = max_conditions
        self.regex_timeout = regex_timeout
        self.max_query_length = max_query_length
        
        # Initialize specialized validators
        self.security_validator = SecurityValidator(regex_timeout)
        self.performance_analyzer = PerformanceAnalyzer()
    
    def validate(self, query: str) -> ValidationResult:
        """
        Validate query string for safety and correctness.
        
        This method performs comprehensive validation including security checks,
        structural validation, and performance analysis. It returns detailed
        results with errors, warnings, and recommendations.
        
        Args:
            query: Filter expression string to validate
            
        Returns:
            ValidationResult: Comprehensive validation results
            
        Raises:
            ValueError: When query is None or empty
        """
        if query is None:
            raise ValueError("Query cannot be None")
        
        if not isinstance(query, str):
            raise ValueError("Query must be a string")
        
        # Initialize result
        errors = []
        warnings = []
        details = {
            "complexity": {},
            "security": {},
            "performance": {},
            "recommendations": []
        }
        
        # Basic validation
        if not query.strip():
            errors.append("Query cannot be empty")
            return ValidationResult(False, errors, warnings, details)
        
        # Length validation
        if len(query) > self.max_query_length:
            errors.append(f"Query too long: {len(query)} > {self.max_query_length} characters")
        
        # Security validation
        security_result = self.security_validator.validate(query)
        errors.extend(security_result["errors"])
        warnings.extend(security_result["warnings"])
        details["security"] = security_result["details"]
        
        # Try to parse and validate AST structure
        try:
            parser = FilterParser()
            ast = parser.parse(query)
            
            # AST-based validation
            ast_result = self._validate_ast(ast)
            errors.extend(ast_result["errors"])
            warnings.extend(ast_result["warnings"])
            
            # Complexity analysis
            complexity_result = analyze_complexity(ast)
            details["complexity"] = complexity_result
            
            # Check complexity constraints
            max_depth = complexity_result.get("max_depth", 0)
            total_conditions = complexity_result.get("total_conditions", 0)
            
            if max_depth > self.max_depth:
                errors.append(f"AST too deep: {max_depth} > {self.max_depth}")
            
            if total_conditions > self.max_conditions:
                errors.append(f"Too many conditions: {total_conditions} > {self.max_conditions}")
            
            # Performance analysis
            performance_result = self.performance_analyzer.analyze(query, ast)
            details["performance"] = performance_result["details"]
            warnings.extend(performance_result["warnings"])
            
        except FilterParseError as e:
            errors.append(f"Syntax error: {e.message}")
        except Exception as e:
            errors.append(f"Unexpected error during parsing: {str(e)}")
        
        # Generate recommendations
        details["recommendations"] = self._generate_recommendations(
            errors, warnings, details
        )
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            details=details
        )
    
    def validate_ast(self, ast: ASTNode) -> ValidationResult:
        """
        Validate parsed AST structure.
        
        This method validates an already parsed AST for structural correctness
        and complexity constraints.
        
        Args:
            ast: Parsed AST node to validate
            
        Returns:
            ValidationResult: Validation results for AST structure
        """
        errors = []
        warnings = []
        details = {
            "complexity": {},
            "security": {},
            "performance": {},
            "recommendations": []
        }
        
        # Use ASTValidator for structural validation
        try:
            validator = ASTValidator()
            is_valid = ast.accept(validator)
            if not is_valid:
                errors.append("AST structure validation failed")
        except Exception as e:
            errors.append(f"AST validation error: {str(e)}")
        
        # Complexity analysis
        try:
            complexity_result = analyze_complexity(ast)
            details["complexity"] = complexity_result
            
            # Check depth constraints
            max_depth = complexity_result.get("max_depth", 0)
            if max_depth > self.max_depth:
                errors.append(f"AST too deep: {max_depth} > {self.max_depth}")
            
            # Check condition count
            total_conditions = complexity_result.get("total_conditions", 0)
            if total_conditions > self.max_conditions:
                errors.append(f"Too many conditions: {total_conditions} > {self.max_conditions}")
            
        except Exception as e:
            errors.append(f"Complexity analysis error: {str(e)}")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            details=details
        )
    
    def _validate_ast(self, ast: ASTNode) -> Dict[str, Any]:
        """
        Validate AST structure using ASTValidator.
        
        Args:
            ast: AST node to validate
            
        Returns:
            Dict with validation results
        """
        errors = []
        warnings = []
        
        try:
            validator = ASTValidator()
            is_valid = ast.accept(validator)
            if not is_valid:
                errors.append("AST structure validation failed")
        except Exception as e:
            # Check if it's a string (not an AST node)
            if isinstance(ast, str):
                errors.append("AST validation failed: expected AST node, got string")
            else:
                errors.append(f"AST validation error: {str(e)}")
        
        return {
            "errors": errors,
            "warnings": warnings
        }
    
    def _generate_recommendations(self, errors: List[str], warnings: List[str], 
                                 details: Dict[str, Any]) -> List[str]:
        """
        Generate optimization and security recommendations.
        
        Args:
            errors: List of validation errors
            warnings: List of validation warnings
            details: Detailed analysis information
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        # Security recommendations
        if details.get("security", {}).get("dangerous_patterns_found"):
            recommendations.append("Remove all dangerous patterns from query")
        
        if details.get("security", {}).get("redos_patterns_found"):
            recommendations.append("Simplify regex patterns to avoid ReDoS attacks")
        
        # Performance recommendations
        complexity = details.get("complexity", {})
        if complexity.get("max_depth", 0) > 5:
            recommendations.append("Reduce nesting depth for better performance")
        
        if complexity.get("total_conditions", 0) > 20:
            recommendations.append("Consider breaking complex queries into smaller parts")
        
        # General recommendations
        if len(errors) > 0:
            recommendations.append("Fix all validation errors before execution")
        
        if len(warnings) > 0:
            recommendations.append("Review warnings and consider optimizations")
        
        return recommendations 