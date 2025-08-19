"""
Unit tests for QueryValidator and validation functionality.

This module tests the QueryValidator class, which provides comprehensive
validation of filter expressions for security, correctness, and performance.
It covers security validation, structural validation, and complexity analysis.

Author: Development Team
Created: 2024-06-13
Updated: 2024-06-13
"""

import pytest
from chunk_metadata_adapter.query_validator import QueryValidator, ValidationResult
from chunk_metadata_adapter.ast import FieldCondition, LogicalOperator, ParenExpression, TypedValue


class TestQueryValidator:
    """
    Tests for QueryValidator functionality.
    """
    
    def setup_method(self):
        """Set up validator for each test."""
        self.validator = QueryValidator()
    
    def test_validate_safe_query(self):
        """Test validation of safe query."""
        result = self.validator.validate("age > 18 AND status = 'active'")
        assert result.is_valid == True
        assert len(result.errors) == 0
        assert len(result.warnings) == 0
    
    def test_validate_empty_query(self):
        """Test validation of empty query."""
        result = self.validator.validate("")
        assert result.is_valid == False
        assert len(result.errors) == 1
        assert "empty" in result.errors[0].lower()
    
    def test_validate_none_query(self):
        """Test validation of None query."""
        with pytest.raises(ValueError, match="cannot be None"):
            self.validator.validate(None)
    
    def test_validate_non_string_query(self):
        """Test validation of non-string query."""
        with pytest.raises(ValueError, match="must be a string"):
            self.validator.validate(123)
    
    def test_validate_query_too_long(self):
        """Test validation of query that exceeds length limit."""
        long_query = "age > 18 AND " * 1000  # Very long query
        result = self.validator.validate(long_query)
        assert result.is_valid == False
        assert len(result.errors) >= 1  # May have multiple errors
        assert any("too long" in error.lower() for error in result.errors)
    
    def test_validate_dangerous_patterns(self):
        """Test validation detects dangerous patterns."""
        dangerous_queries = [
            "age > 18 AND __import__('os')",
            "status = 'active' AND exec('print(1)')",
            "name = 'test' AND eval('1+1')",
            "type = 'user' AND open('file.txt')",
            "id = 123 AND os.system('ls')",
        ]
        
        for query in dangerous_queries:
            result = self.validator.validate(query)
            assert result.is_valid == False
            assert len(result.errors) >= 1
            assert any("dangerous" in error.lower() for error in result.errors)
    
    def test_validate_redos_patterns(self):
        """Test validation detects ReDoS patterns."""
        redos_queries = [
            "name ~ '(.*)*'",  # Nested repetition
            "title ~ '.*.*.*'",  # Multiple wildcards
            "content ~ '[^}]*{[^}]*{[^}]*}'",  # Nested quantifiers
        ]
        
        for query in redos_queries:
            result = self.validator.validate(query)
            # ReDoS patterns should generate warnings, not errors
            assert len(result.warnings) >= 1
    
    def test_validate_performance_patterns(self):
        """Test validation detects performance anti-patterns."""
        performance_queries = [
            "name ~ '.*.*.*.*'",  # Multiple wildcards
            "title ~ '(.*){10,}'",  # Unbounded repetition
            "content ~ '[a-z]*[a-z]*[a-z]*'",  # Multiple unbounded repetition
        ]
        
        for query in performance_queries:
            result = self.validator.validate(query)
            # Performance patterns should generate warnings, not errors
            assert len(result.warnings) >= 1
    
    def test_validate_complex_query(self):
        """Test validation of complex but safe query."""
        complex_query = "(age > 18 OR vip = true) AND (status = 'active' OR status = 'verified') AND (type = 'user' OR type = 'admin') AND NOT is_deleted AND quality_score >= 0.8"
        result = self.validator.validate(complex_query)
        assert result.is_valid == True
        assert len(result.errors) == 0
    
    def test_validate_ast_structure(self):
        """Test AST structure validation."""
        # Create a valid AST
        condition1 = FieldCondition("age", ">", TypedValue("int", 18))
        condition2 = FieldCondition("status", "=", TypedValue("str", "active"))
        ast = LogicalOperator("AND", [condition1, condition2])
        
        result = self.validator.validate_ast(ast)
        assert result.is_valid == True
        assert len(result.errors) == 0
    
    def test_validate_ast_complexity(self):
        """Test AST complexity analysis."""
        # Create a complex AST
        conditions = []
        for i in range(25):  # More than max_conditions (20)
            condition = FieldCondition(f"field{i}", "=", TypedValue("int", i))
            conditions.append(condition)
        
        ast = LogicalOperator("AND", conditions)
        result = self.validator.validate_ast(ast)
        
        # Should be valid but with complexity details
        assert result.is_valid == True
        assert "complexity" in result.details
        complexity = result.details["complexity"]
        assert "total_conditions" in complexity
        assert complexity["total_conditions"] >= 25
    
    def test_validate_nested_ast(self):
        """Test validation of deeply nested AST."""
        # Create a deeply nested expression that exceeds max_depth
        nested_query = "(((a = 1 AND b = 2) AND (c = 3 AND d = 4)) AND ((e = 5 AND f = 6) AND (g = 7 AND h = 8)))"
        
        # Create validator with very small depth limit
        validator = QueryValidator(max_depth=3)
        result = validator.validate(nested_query)
        
        # Should fail due to excessive depth
        assert result.is_valid == False
        assert any("too deep" in error.lower() for error in result.errors)
        
        # Check complexity details
        complexity = result.details["complexity"]
        assert "max_depth" in complexity
        assert complexity["max_depth"] > 3  # Should be 4
    
    def test_validation_details(self):
        """Test that validation provides detailed information."""
        result = self.validator.validate("age > 18 AND status = 'active'")
        
        assert result.details is not None
        assert "complexity" in result.details
        assert "security" in result.details
        assert "performance" in result.details
        assert "recommendations" in result.details
        
        # Check complexity details
        complexity = result.details["complexity"]
        # These fields may not be present in all cases, so we check if they exist
        if "max_depth" in complexity:
            assert isinstance(complexity["max_depth"], (int, type(None)))
        if "total_conditions" in complexity:
            assert isinstance(complexity["total_conditions"], (int, type(None)))
        if "operator_distribution" in complexity:
            assert isinstance(complexity["operator_distribution"], dict)
        if "field_distribution" in complexity:
            assert isinstance(complexity["field_distribution"], dict)
    
    def test_security_analysis(self):
        """Test security analysis provides detailed information."""
        result = self.validator.validate("age > 18 AND __import__('os')")
        
        security = result.details["security"]
        assert "dangerous_patterns_found" in security
        assert "redos_patterns_found" in security
        assert "performance_patterns_found" in security
        assert "risk_level" in security
        
        assert len(security["dangerous_patterns_found"]) > 0
        assert security["risk_level"] == "high"
    
    def test_performance_analysis(self):
        """Test performance analysis functionality."""
        query = "age > 18 AND status = 'active'"
        result = self.validator.validate(query)
        
        performance = result.details["performance"]
        assert "estimated_complexity" in performance
        assert "potential_issues" in performance
        assert "optimization_suggestions" in performance
        
        # Should be valid query
        assert result.is_valid == True
    
    def test_recommendations_generation(self):
        """Test that recommendations are generated appropriately."""
        # Test with dangerous query
        result = self.validator.validate("age > 18 AND __import__('os')")
        recommendations = result.details["recommendations"]
        
        assert len(recommendations) > 0
        assert any("dangerous" in rec.lower() for rec in recommendations)
        assert any("fix" in rec.lower() for rec in recommendations)
    
    def test_custom_validation_parameters(self):
        """Test validation with custom parameters."""
        # Create validator with very restrictive limits
        strict_validator = QueryValidator(
            max_depth=5,
            max_conditions=5,
            regex_timeout=0.5,
            max_query_length=100
        )
        
        # This query should exceed the condition limit
        complex_query = "age > 18 AND status = 'active' AND type = 'user'"
        result = strict_validator.validate(complex_query)
        
        # Should fail due to too many conditions (6 > 5)
        assert result.is_valid == False
        assert any("too many conditions" in error.lower() for error in result.errors)
    
    def test_invalid_validation_parameters(self):
        """Test that invalid parameters raise appropriate errors."""
        with pytest.raises(ValueError, match="max_depth must be at least 1"):
            QueryValidator(max_depth=0)
        
        with pytest.raises(ValueError, match="max_conditions must be at least 1"):
            QueryValidator(max_conditions=0)
        
        with pytest.raises(ValueError, match="regex_timeout must be positive"):
            QueryValidator(regex_timeout=0)
        
        with pytest.raises(ValueError, match="max_query_length must be at least 1"):
            QueryValidator(max_query_length=0)
    
    def test_regex_operations_detection(self):
        """Test detection of regex operations."""
        regex_queries = [
            "name ~ 'pattern'",
            "title !~ 'pattern'",
            "content like 'pattern'",
        ]
        
        for query in regex_queries:
            result = self.validator.validate(query)
            performance = result.details["performance"]
            assert "potential_issues" in performance
            assert any("regex" in issue.lower() for issue in performance["potential_issues"])
    
    def test_list_operations_detection(self):
        """Test detection of list operations."""
        list_queries = [
            "tags in ['ai', 'ml']",
        ]
        
        for query in list_queries:
            result = self.validator.validate(query)
            performance = result.details["performance"]
            assert "potential_issues" in performance
            assert any("list" in issue.lower() for issue in performance["potential_issues"])


class TestValidationResult:
    """
    Tests for ValidationResult class.
    """
    
    def test_validation_result_creation(self):
        """Test ValidationResult creation with default values."""
        result = ValidationResult(
            is_valid=True,
            errors=[],
            warnings=[]
        )
        
        assert result.is_valid == True
        assert result.errors == []
        assert result.warnings == []
        assert result.details is not None
        assert "complexity" in result.details
        assert "security" in result.details
        assert "performance" in result.details
        assert "recommendations" in result.details
    
    def test_validation_result_with_details(self):
        """Test ValidationResult creation with custom details."""
        custom_details = {
            "complexity": {"max_depth": 5},
            "security": {"risk_level": "low"},
            "performance": {"estimated_complexity": "medium"},
            "recommendations": ["Test recommendation"]
        }
        
        result = ValidationResult(
            is_valid=False,
            errors=["Test error"],
            warnings=["Test warning"],
            details=custom_details
        )
        
        assert result.is_valid == False
        assert result.errors == ["Test error"]
        assert result.warnings == ["Test warning"]
        assert result.details == custom_details


class TestQueryValidatorIntegration:
    """
    Integration tests for QueryValidator with real scenarios.
    """
    
    def test_real_world_safe_queries(self):
        """Test validation of real-world safe queries."""
        safe_queries = [
            "age > 18 AND status = 'active'",
            "(type = 'DocBlock' OR type = 'CodeBlock') AND quality_score >= 0.8",
            "NOT (is_deleted = true) AND (is_public = true OR user_role = 'admin')",
            "title like 'Python' AND language = 'en'",
            "created_at >= '2024-01-01' AND updated_at <= '2024-12-31'",
        ]
        
        validator = QueryValidator()
        for query in safe_queries:
            result = validator.validate(query)
            assert result.is_valid == True, f"Query failed validation: {query}"
            assert len(result.errors) == 0, f"Query has errors: {query}"
    
    def test_real_world_dangerous_queries(self):
        """Test validation of real-world dangerous queries."""
        dangerous_queries = [
            "age > 18 AND __import__('os').system('rm -rf /')",
            "status = 'active' AND eval('print(1)')",
            "type = 'user' AND exec('import os')",
            "name = 'test' AND open('/etc/passwd')",
        ]
        
        validator = QueryValidator()
        for query in dangerous_queries:
            result = validator.validate(query)
            assert result.is_valid == False, f"Dangerous query passed validation: {query}"
            assert len(result.errors) >= 1, f"Dangerous query has no errors: {query}"
            assert any("dangerous" in error.lower() for error in result.errors)
    
    def test_complex_business_scenarios(self):
        """Test validation of complex business scenarios."""
        complex_scenarios = [
            # Content management filter
            "type = 'DocBlock' AND quality_score >= 0.8 AND status = 'verified' AND year >= 2020 AND is_public = true AND NOT (is_deleted = true)",
            
            # Analytics filter
            "(type = 'DocBlock' OR type = 'CodeBlock') AND feedback_accepted >= 5 AND used_in_generation = true AND (language = 'en' OR language = 'ru') AND created_at >= '2024-01-01T00:00:00Z' AND quality_score >= 0.7",
            
            # Search and discovery filter
            "(title like 'Python' OR summary like 'machine learning') AND (type = 'DocBlock' OR type = 'CodeBlock') AND quality_score >= 0.6 AND year >= 2020 AND is_public = true"
        ]
        
        validator = QueryValidator()
        for scenario in complex_scenarios:
            result = validator.validate(scenario)
            assert result.is_valid == True, f"Complex scenario failed: {scenario[:100]}..."
            assert len(result.errors) == 0, f"Complex scenario has errors: {scenario[:100]}..." 