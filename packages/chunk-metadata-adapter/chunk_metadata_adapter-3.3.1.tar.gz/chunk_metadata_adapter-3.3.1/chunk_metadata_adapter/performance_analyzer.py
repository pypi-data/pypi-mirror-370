"""
Performance analyzer for query expressions.

This module provides functionality to analyze query performance characteristics,
including complexity assessment, optimization suggestions, and performance warnings.
"""

from typing import Dict, Any, List
from .ast import ASTNode
from .complexity_analyzer import analyze_complexity


class PerformanceAnalyzer:
    """
    Analyzer for query performance characteristics.
    
    This class analyzes query performance and provides optimization suggestions
    based on complexity metrics and query characteristics.
    """
    
    def __init__(self):
        """Initialize PerformanceAnalyzer."""
        self.analysis_cache = {}
        self.warning_thresholds = {
            "query_length": 1000,
            "max_depth": 5,
            "total_conditions": 20
        }
    
    def analyze(self, query: str, ast: ASTNode) -> Dict[str, Any]:
        """
        Analyze query performance characteristics.
        
        Args:
            query: Original query string
            ast: Parsed AST node
            
        Returns:
            Dict with performance analysis
        """
        warnings = []
        details = {
            "estimated_complexity": "low",
            "potential_issues": [],
            "optimization_suggestions": []
        }
        
        # Analyze query characteristics
        query_length = len(query)
        if query_length > 1000:
            details["estimated_complexity"] = "high"
            warnings.append("Query is very long - consider breaking it down")
        
        # Analyze AST complexity
        try:
            complexity = analyze_complexity(ast)
            
            max_depth = complexity.get("max_depth", 0)
            total_conditions = complexity.get("total_conditions", 0)
            
            if max_depth > 5:
                details["estimated_complexity"] = "medium"
                warnings.append("Deep nesting detected - may impact performance")
            
            if total_conditions > 20:
                details["estimated_complexity"] = "medium"
                warnings.append("Many conditions detected - consider optimization")
                
        except Exception as e:
            warnings.append(f"Complexity analysis failed: {str(e)}")
        
        # Check for regex operations
        if self._has_regex_operations(query):
            details["potential_issues"].append("Regex operations may be slow")
            details["optimization_suggestions"].append("Consider using exact matches instead of regex")
        
        # Check for list operations
        if "in" in query.lower() or "intersects" in query.lower():
            details["potential_issues"].append("List operations may be expensive")
            details["optimization_suggestions"].append("Consider indexing for list operations")
        
        # Check for nested field access
        if "." in query and "=" in query:
            details["potential_issues"].append("Nested field access may be slow")
            details["optimization_suggestions"].append("Consider flattening nested structures")
        
        return {
            "warnings": warnings,
            "details": details
        }
    
    def _has_regex_operations(self, query: str) -> bool:
        """Check if query contains regex operations."""
        regex_indicators = ["~", "!~", "like", "regex", "pattern"]
        return any(indicator in query.lower() for indicator in regex_indicators) 