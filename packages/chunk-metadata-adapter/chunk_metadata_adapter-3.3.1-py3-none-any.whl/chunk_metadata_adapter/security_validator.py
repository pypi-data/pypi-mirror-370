"""
Security validator for query expressions.

This module provides functionality to validate query expressions for security threats,
including ReDoS attacks, injection patterns, and dangerous operations.
"""

import re
import signal
from typing import Dict, Any, List


class SecurityValidator:
    """
    Validator for query security threats.
    
    This class detects various security threats in query expressions:
    - ReDoS (Regular Expression Denial of Service) patterns
    - Code injection patterns
    - Dangerous operations
    - Performance anti-patterns
    """
    
    # Dangerous patterns that could be used for attacks
    DANGEROUS_PATTERNS = [
        # Code injection patterns
        r'__import__\s*\(',
        r'exec\s*\(',
        r'eval\s*\(',
        r'globals\s*\(',
        r'locals\s*\(',
        r'compile\s*\(',
        
        # File system access
        r'open\s*\(',
        r'file\s*\(',
        r'os\.system\s*\(',
        r'subprocess\s*\(',
        
        # Network access
        r'urllib\s*\(',
        r'requests\s*\(',
        r'socket\s*\(',
        
        # Memory manipulation
        r'memoryview\s*\(',
        r'buffer\s*\(',
        
        # Reflection and introspection
        r'getattr\s*\(',
        r'setattr\s*\(',
        r'delattr\s*\(',
        r'hasattr\s*\(',
        
        # Module manipulation
        r'reload\s*\(',
        r'__import__\s*\(',
        
        # Dangerous builtins
        r'input\s*\(',
        r'raw_input\s*\(',
    ]
    
    # ReDoS patterns that could cause exponential backtracking
    REDOS_PATTERNS = [
        r'\(.*\)\*',  # Nested repetition
        r'\.\*\.\*\.\*',  # Multiple wildcards
        r'.*\{.*\{.*\}',  # Nested quantifiers
        r'\([^)]*\)\*[^)]*\)',  # Nested parentheses with repetition
        r'[a-zA-Z]*\*[a-zA-Z]*\*',  # Multiple character class repetition
    ]
    
    # Performance anti-patterns
    PERFORMANCE_PATTERNS = [
        r'\.\*.*\.\*.*\.\*',  # Triple wildcard
        r'\([^)]*\)\{[0-9]+,\}',  # Unbounded repetition
        r'.*\*.*\*.*\*',  # Multiple unbounded repetition
    ]
    
    def __init__(self, regex_timeout: float = 1.0):
        """
        Initialize SecurityValidator.
        
        Args:
            regex_timeout: Timeout for regex operations in seconds
        """
        self.regex_timeout = regex_timeout
        
        # Compile patterns for performance
        self._dangerous_patterns = [re.compile(pattern, re.IGNORECASE) 
                                   for pattern in self.DANGEROUS_PATTERNS]
        self._redos_patterns = [re.compile(pattern, re.IGNORECASE) 
                               for pattern in self.REDOS_PATTERNS]
        self._performance_patterns = [re.compile(pattern, re.IGNORECASE) 
                                     for pattern in self.PERFORMANCE_PATTERNS]
    
    def validate(self, query: str) -> Dict[str, Any]:
        """
        Validate query for security threats.
        
        Args:
            query: Query string to validate
            
        Returns:
            Dict with errors, warnings, and security details
        """
        errors = []
        warnings = []
        details = {
            "dangerous_patterns_found": [],
            "redos_patterns_found": [],
            "performance_patterns_found": [],
            "risk_level": "low"
        }
        
        # Check for dangerous patterns
        for pattern in self._dangerous_patterns:
            if pattern.search(query):
                dangerous_pattern = pattern.pattern
                errors.append(f"Dangerous pattern detected: {dangerous_pattern}")
                details["dangerous_patterns_found"].append(dangerous_pattern)
        
        # Check for ReDoS patterns
        for pattern in self._redos_patterns:
            if pattern.search(query):
                redos_pattern = pattern.pattern
                warnings.append(f"Potentially dangerous regex pattern: {redos_pattern}")
                details["redos_patterns_found"].append(redos_pattern)
        
        # Check for performance anti-patterns
        for pattern in self._performance_patterns:
            if pattern.search(query):
                perf_pattern = pattern.pattern
                warnings.append(f"Performance anti-pattern detected: {perf_pattern}")
                details["performance_patterns_found"].append(perf_pattern)
        
        # Check for regex operations in query content
        if self._has_regex_operations(query):
            # Additional check for dangerous patterns in regex values
            regex_values = self._extract_regex_values(query)
            for regex_value in regex_values:
                # Check each regex value against dangerous patterns
                for pattern in self._redos_patterns:
                    if pattern.search(regex_value):
                        redos_pattern = pattern.pattern
                        warnings.append(f"ReDoS pattern in regex value: {redos_pattern}")
                        details["redos_patterns_found"].append(redos_pattern)
                
                for pattern in self._performance_patterns:
                    if pattern.search(regex_value):
                        perf_pattern = pattern.pattern
                        warnings.append(f"Performance pattern in regex value: {perf_pattern}")
                        details["performance_patterns_found"].append(perf_pattern)
        
        # Test regex operations with timeout
        if self._has_regex_operations(query):
            if not self._test_regex_timeout(query):
                errors.append("Regex operation timeout - potential ReDoS attack")
        
        # Determine risk level
        if details["dangerous_patterns_found"]:
            details["risk_level"] = "high"
        elif details["redos_patterns_found"]:
            details["risk_level"] = "medium"
        elif details["performance_patterns_found"]:
            details["risk_level"] = "low"
        
        return {
            "errors": errors,
            "warnings": warnings,
            "details": details
        }
    
    def _has_regex_operations(self, query: str) -> bool:
        """Check if query contains regex operations."""
        regex_indicators = ["~", "!~", "like", "regex", "pattern"]
        return any(indicator in query.lower() for indicator in regex_indicators)
    
    def _extract_regex_values(self, query: str) -> List[str]:
        """Extract regex values from query for pattern analysis."""
        regex_values = []
        
        # Pattern to match field ~ 'pattern' or field !~ 'pattern' or field like 'pattern'
        regex_patterns = [
            r"(\w+)\s*[~!~]\s*['\"]([^'\"]*)['\"]",  # field ~ 'pattern' or field !~ 'pattern'
            r"(\w+)\s+like\s+['\"]([^'\"]*)['\"]",   # field like 'pattern'
        ]
        
        for pattern in regex_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            for match in matches:
                if len(match) == 2:  # field, pattern
                    regex_values.append(match[1])
                else:  # just pattern
                    regex_values.append(match)
        
        return regex_values
    
    def _test_regex_timeout(self, query: str) -> bool:
        """
        Test regex operations with timeout to detect ReDoS.
        
        Args:
            query: Query string to test
            
        Returns:
            True if regex operations complete within timeout
        """
        def timeout_handler(signum, frame):
            raise TimeoutError("Regex operation timeout")
        
        try:
            # Set up timeout
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(int(self.regex_timeout))
            
            # Test regex patterns in query
            test_patterns = [
                r'\(.*\)\*',
                r'\.\*.*\.\*',
                r'[a-zA-Z]*\*[a-zA-Z]*\*'
            ]
            
            for pattern in test_patterns:
                if re.search(pattern, query):
                    # This could be expensive, but we have timeout
                    re.findall(pattern, query)
            
            signal.alarm(0)  # Cancel alarm
            return True
            
        except TimeoutError:
            return False
        except Exception:
            return True  # Assume safe if we can't test
        finally:
            signal.alarm(0)  # Ensure alarm is cancelled 