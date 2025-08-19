"""
Tests for AST compatibility modules.

This module tests the backward compatibility modules ast.py and ast_nodes.py
to ensure they properly re-export all necessary classes and functions.
"""

import pytest
from chunk_metadata_adapter import ast
from chunk_metadata_adapter import ast_nodes


class TestASTCompatibility:
    """Tests for AST compatibility modules."""
    
    def test_ast_module_imports(self):
        """Test that ast.py properly re-exports all classes."""
        # Test core AST classes
        assert hasattr(ast, 'ASTNode')
        assert hasattr(ast, 'FieldCondition')
        assert hasattr(ast, 'LogicalOperator')
        assert hasattr(ast, 'ParenExpression')
        assert hasattr(ast, 'TypedValue')
        
        # Test visitor pattern
        assert hasattr(ast, 'ASTVisitor')
        assert hasattr(ast, 'ASTPrinter')
        assert hasattr(ast, 'ASTValidator')
        assert hasattr(ast, 'ASTAnalyzer')
        assert hasattr(ast, 'ASTOptimizer')
        
        # Test factory
        assert hasattr(ast, 'ASTNodeFactory')
        
        # Test JSON serialization
        assert hasattr(ast, 'ast_to_json')
        assert hasattr(ast, 'ast_from_json')
        assert hasattr(ast, 'ast_to_json_string')
        assert hasattr(ast, 'ast_from_json_string')
        
        # Test parameterization and caching
        assert hasattr(ast, 'ParameterValue')
        assert hasattr(ast, 'ParameterizedAST')
        assert hasattr(ast, 'ASTParameterizer')
        assert hasattr(ast, 'ASTInstantiator')
        assert hasattr(ast, 'QueryCache')
    
    def test_ast_nodes_module_imports(self):
        """Test that ast_nodes.py properly re-exports all classes."""
        # Test core AST classes
        assert hasattr(ast_nodes, 'ASTNode')
        assert hasattr(ast_nodes, 'FieldCondition')
        assert hasattr(ast_nodes, 'LogicalOperator')
        assert hasattr(ast_nodes, 'ParenExpression')
        assert hasattr(ast_nodes, 'TypedValue')
        
        # Test factory
        assert hasattr(ast_nodes, 'ASTNodeFactory')
    
    def test_ast_module_functionality(self):
        """Test that imported classes from ast.py work correctly."""
        from chunk_metadata_adapter.ast import FieldCondition, TypedValue, LogicalOperator
        
        # Test TypedValue creation
        value = TypedValue("int", 42)
        assert value.type == "int"
        assert value.value == 42
        
        # Test FieldCondition creation
        condition = FieldCondition("age", ">", value)
        assert condition.field == "age"
        assert condition.operator == ">"
        assert condition.value == value
        
        # Test LogicalOperator creation with two children
        condition2 = FieldCondition("status", "=", TypedValue("str", "active"))
        operator = LogicalOperator("AND", [condition, condition2])
        assert operator.operator == "AND"
        assert len(operator.children) == 2
        assert operator.children[0] == condition
        assert operator.children[1] == condition2
    
    def test_ast_nodes_module_functionality(self):
        """Test that imported classes from ast_nodes.py work correctly."""
        from chunk_metadata_adapter.ast_nodes import FieldCondition, TypedValue, ASTNodeFactory
        
        # Test TypedValue creation
        value = TypedValue("str", "test")
        assert value.type == "str"
        assert value.value == "test"
        
        # Test FieldCondition creation
        condition = FieldCondition("name", "=", value)
        assert condition.field == "name"
        assert condition.operator == "="
        assert condition.value == value
        
        # Test ASTNodeFactory
        factory = ASTNodeFactory()
        assert factory is not None
    
    def test_ast_module_all_attribute(self):
        """Test that ast.py has correct __all__ attribute."""
        expected_exports = [
            "ASTNode", "FieldCondition", "LogicalOperator", "ParenExpression", "TypedValue",
            "ASTVisitor", "ASTPrinter", "ASTValidator", "ASTAnalyzer", "ASTOptimizer",
            "ASTNodeFactory",
            "ast_to_json", "ast_from_json", "ast_to_json_string", "ast_from_json_string",
            "ParameterValue", "ParameterizedAST", "ASTParameterizer", "ASTInstantiator", "QueryCache"
        ]
        
        for export in expected_exports:
            assert export in ast.__all__
    
    def test_ast_nodes_module_all_attribute(self):
        """Test that ast_nodes.py has correct __all__ attribute."""
        expected_exports = [
            "ASTNode", "FieldCondition", "LogicalOperator", "ParenExpression", "TypedValue",
            "ASTNodeFactory"
        ]
        
        for export in expected_exports:
            assert export in ast_nodes.__all__
    
    def test_ast_module_serialization_functions(self):
        """Test that serialization functions from ast.py work correctly."""
        from chunk_metadata_adapter.ast import FieldCondition, TypedValue, ast_to_json, ast_from_json
        
        # Create a simple AST
        condition = FieldCondition("age", ">", TypedValue("int", 18))
        
        # Test JSON serialization
        json_data = ast_to_json(condition)
        assert isinstance(json_data, dict)
        assert json_data["node_type"] == "field_condition"
        assert json_data["field"] == "age"
        assert json_data["operator"] == ">"
        
        # Test JSON deserialization
        restored_condition = ast_from_json(json_data)
        assert isinstance(restored_condition, FieldCondition)
        assert restored_condition.field == "age"
        assert restored_condition.operator == ">"
        assert restored_condition.value.type == "int"
        assert restored_condition.value.value == 18
    
    def test_ast_module_visitor_pattern(self):
        """Test that visitor pattern classes from ast.py work correctly."""
        from chunk_metadata_adapter.ast import FieldCondition, TypedValue, ASTPrinter, ASTValidator
        
        # Create a simple AST
        condition = FieldCondition("age", ">", TypedValue("int", 18))
        
        # Test ASTPrinter
        printer = ASTPrinter()
        result = condition.accept(printer)
        assert isinstance(result, str)
        assert "age" in result
        assert ">" in result
        
        # Test ASTValidator
        validator = ASTValidator()
        result = condition.accept(validator)
        assert isinstance(result, bool)
        assert result == True  # Valid condition should pass validation
