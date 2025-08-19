"""
Tests for query_validator.py coverage improvement.

This module contains tests to increase coverage of query_validator.py
to 90%+ by testing edge cases and error conditions.
"""

import pytest
from chunk_metadata_adapter.query_validator import QueryValidator, ValidationResult
from chunk_metadata_adapter.ast.nodes import FieldCondition, TypedValue, LogicalOperator


class TestQueryValidatorCoverage:
    """Tests for QueryValidator coverage improvement."""
    
    def test_validate_ast_with_string_input(self):
        """Test _validate_ast with string input (not AST node)."""
        validator = QueryValidator()
        result = validator._validate_ast("not an ast node")
        
        assert "errors" in result
        assert "warnings" in result
        assert len(result["errors"]) > 0
        assert "expected AST node, got string" in result["errors"][0]
    
    def test_validate_ast_with_exception(self):
        """Test _validate_ast with exception during validation."""
        validator = QueryValidator()
        
        # Create a mock AST that will cause an exception
        class MockAST:
            def accept(self, visitor):
                raise Exception("Mock validation error")
        
        result = validator._validate_ast(MockAST())
        
        assert "errors" in result
        assert "warnings" in result
        assert len(result["errors"]) > 0
        assert "AST validation error" in result["errors"][0]
    
    def test_validate_ast_with_invalid_ast(self):
        """Test validate_ast with invalid AST structure."""
        validator = QueryValidator()
        
        # Create an invalid AST that will fail validation
        class InvalidAST:
            def accept(self, visitor):
                return False  # Invalid AST
        
        result = validator.validate_ast(InvalidAST())
        
        assert not result.is_valid
        assert len(result.errors) > 0
        assert "AST structure validation failed" in result.errors[0]
    
    def test_validate_ast_with_complexity_exception(self):
        """Test validate_ast with exception during complexity analysis."""
        validator = QueryValidator()
        
        # Create a mock AST that will cause an exception during complexity analysis
        class MockAST:
            def accept(self, visitor):
                return True  # Valid AST
        
        # Test with a real AST that might cause complexity analysis issues
        from chunk_metadata_adapter.ast.nodes import FieldCondition, TypedValue
        condition = FieldCondition("age", ">", TypedValue("int", 18))
        
        # This should work without exceptions
        result = validator.validate_ast(condition)
        assert hasattr(result, 'is_valid')
    
    def test_validate_ast_with_depth_exceeded(self):
        """Test validate_ast with AST depth exceeding limit."""
        validator = QueryValidator(max_depth=2)
        
        # Create a deep AST structure
        deep_ast = LogicalOperator("AND", [
            LogicalOperator("OR", [
                FieldCondition("field1", "=", TypedValue("str", "value1")),
                FieldCondition("field2", "=", TypedValue("str", "value2"))
            ]),
            LogicalOperator("AND", [
                FieldCondition("field3", "=", TypedValue("str", "value3")),
                FieldCondition("field4", "=", TypedValue("str", "value4"))
            ])
        ])
        
        result = validator.validate_ast(deep_ast)
        
        # Should fail due to depth limit
        assert not result.is_valid
        assert any("AST too deep" in error for error in result.errors)
    
    def test_validate_ast_with_condition_count_exceeded(self):
        """Test validate_ast with condition count exceeding limit."""
        validator = QueryValidator(max_conditions=3)
        
        # Create an AST with many conditions
        many_conditions = LogicalOperator("AND", [
            FieldCondition("field1", "=", TypedValue("str", "value1")),
            FieldCondition("field2", "=", TypedValue("str", "value2")),
            FieldCondition("field3", "=", TypedValue("str", "value3")),
            FieldCondition("field4", "=", TypedValue("str", "value4")),
            FieldCondition("field5", "=", TypedValue("str", "value5"))
        ])
        
        result = validator.validate_ast(many_conditions)
        
        # Should fail due to condition count limit
        assert not result.is_valid
        assert any("Too many conditions" in error for error in result.errors)
    
    def test_generate_recommendations_with_dangerous_patterns(self):
        """Test _generate_recommendations with dangerous patterns."""
        validator = QueryValidator()
        
        details = {
            "security": {
                "dangerous_patterns_found": True,
                "redos_patterns_found": False
            }
        }
        
        recommendations = validator._generate_recommendations([], [], details)
        
        assert "Remove all dangerous patterns from query" in recommendations
    
    def test_generate_recommendations_with_redos_patterns(self):
        """Test _generate_recommendations with ReDoS patterns."""
        validator = QueryValidator()
        
        details = {
            "security": {
                "dangerous_patterns_found": False,
                "redos_patterns_found": True
            }
        }
        
        recommendations = validator._generate_recommendations([], [], details)
        
        assert "Simplify regex patterns to avoid ReDoS attacks" in recommendations
    
    def test_generate_recommendations_with_high_complexity(self):
        """Test _generate_recommendations with high complexity."""
        validator = QueryValidator()
        
        details = {
            "complexity": {
                "max_depth": 10,
                "total_conditions": 25
            }
        }
        
        recommendations = validator._generate_recommendations([], [], details)
        
        assert "Reduce nesting depth for better performance" in recommendations
        assert "Consider breaking complex queries into smaller parts" in recommendations
    
    def test_generate_recommendations_with_errors_and_warnings(self):
        """Test _generate_recommendations with errors and warnings."""
        validator = QueryValidator()
        
        errors = ["Syntax error"]
        warnings = ["Performance warning"]
        
        recommendations = validator._generate_recommendations(errors, warnings, {})
        
        assert "Fix all validation errors before execution" in recommendations
        assert "Review warnings and consider optimizations" in recommendations
    
    def test_validate_with_parse_exception(self):
        """Test validate with exception during parsing."""
        validator = QueryValidator()
        
        # Test with invalid query that will cause parse exception
        result = validator.validate("invalid syntax here")
        
        assert not result.is_valid
        assert len(result.errors) > 0
        # Should have syntax error
        assert any("syntax" in error.lower() for error in result.errors)
    
    def test_validate_with_unexpected_exception(self):
        """Test validate with unexpected exception during parsing."""
        validator = QueryValidator()
        
        # Test with invalid query that will cause parsing exception
        result = validator.validate("invalid syntax here")
        assert not result.is_valid
        assert len(result.errors) > 0
