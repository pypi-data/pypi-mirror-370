"""
Tests for ast.py module coverage.

This module tests the ast.py module to achieve 90%+ coverage
by testing all imports, exports, and functionality.
"""

import pytest
from chunk_metadata_adapter.ast import (
    # Core AST classes
    ASTNode, FieldCondition, LogicalOperator, ParenExpression, TypedValue,
    
    # Visitor pattern
    ASTVisitor, ASTPrinter, ASTValidator, ASTAnalyzer, ASTOptimizer,
    
    # Factory
    ASTNodeFactory,
    
    # JSON serialization
    ast_to_json, ast_from_json, ast_to_json_string, ast_from_json_string,
    
    # Parameterization and caching
    ParameterValue, ParameterizedAST, ASTParameterizer, ASTInstantiator, QueryCache
)


class TestASTModuleImports:
    """Tests for ast.py module imports and exports."""
    
    def test_all_classes_imported(self):
        """Test that all classes can be imported from ast module."""
        # Test core AST classes
        assert ASTNode is not None
        assert FieldCondition is not None
        assert LogicalOperator is not None
        assert ParenExpression is not None
        assert TypedValue is not None
        
        # Test visitor classes
        assert ASTVisitor is not None
        assert ASTPrinter is not None
        assert ASTValidator is not None
        assert ASTAnalyzer is not None
        assert ASTOptimizer is not None
        
        # Test factory
        assert ASTNodeFactory is not None
        
        # Test parameterization classes
        assert ParameterValue is not None
        assert ParameterizedAST is not None
        assert ASTParameterizer is not None
        assert ASTInstantiator is not None
        assert QueryCache is not None
    
    def test_all_functions_imported(self):
        """Test that all functions can be imported from ast module."""
        # Test JSON serialization functions
        assert ast_to_json is not None
        assert ast_from_json is not None
        assert ast_to_json_string is not None
        assert ast_from_json_string is not None
    
    def test_module_attributes(self):
        """Test that module has expected attributes."""
        import chunk_metadata_adapter.ast as ast_module
        
        # Check __all__ attribute
        assert hasattr(ast_module, '__all__')
        assert isinstance(ast_module.__all__, list)
        
        # Check that all exported items are in __all__
        expected_exports = [
            "ASTNode", "FieldCondition", "LogicalOperator", "ParenExpression", "TypedValue",
            "ASTVisitor", "ASTPrinter", "ASTValidator", "ASTAnalyzer", "ASTOptimizer",
            "ASTNodeFactory",
            "ast_to_json", "ast_from_json", "ast_to_json_string", "ast_from_json_string",
            "ParameterValue", "ParameterizedAST", "ASTParameterizer", "ASTInstantiator", "QueryCache"
        ]
        
        for export in expected_exports:
            assert export in ast_module.__all__
    
    def test_import_from_ast_submodule(self):
        """Test that classes are properly re-exported from ast submodule."""
        # Test that classes are the same as from submodule
        from chunk_metadata_adapter.ast.nodes import (
            ASTNode as ASTNodeSub, FieldCondition as FieldConditionSub,
            LogicalOperator as LogicalOperatorSub, ParenExpression as ParenExpressionSub,
            TypedValue as TypedValueSub
        )
        
        assert ASTNode is ASTNodeSub
        assert FieldCondition is FieldConditionSub
        assert LogicalOperator is LogicalOperatorSub
        assert ParenExpression is ParenExpressionSub
        assert TypedValue is TypedValueSub
    
    def test_visitor_imports(self):
        """Test that visitor classes are properly imported."""
        from chunk_metadata_adapter.ast.visitors import (
            ASTVisitor as ASTVisitorSub, ASTPrinter as ASTPrinterSub,
            ASTValidator as ASTValidatorSub, ASTAnalyzer as ASTAnalyzerSub,
            ASTOptimizer as ASTOptimizerSub
        )
        
        assert ASTVisitor is ASTVisitorSub
        assert ASTPrinter is ASTPrinterSub
        assert ASTValidator is ASTValidatorSub
        assert ASTAnalyzer is ASTAnalyzerSub
        assert ASTOptimizer is ASTOptimizerSub
    
    def test_factory_import(self):
        """Test that factory class is properly imported."""
        from chunk_metadata_adapter.ast.factory import ASTNodeFactory as ASTNodeFactorySub
        assert ASTNodeFactory is ASTNodeFactorySub
    
    def test_serialization_imports(self):
        """Test that serialization functions are properly imported."""
        from chunk_metadata_adapter.ast.serialization import (
            ast_to_json as ast_to_json_sub,
            ast_from_json as ast_from_json_sub,
            ast_to_json_string as ast_to_json_string_sub,
            ast_from_json_string as ast_from_json_string_sub
        )
        
        assert ast_to_json is ast_to_json_sub
        assert ast_from_json is ast_from_json_sub
        assert ast_to_json_string is ast_to_json_string_sub
        assert ast_from_json_string is ast_from_json_string_sub
    
    def test_parameterization_imports(self):
        """Test that parameterization classes are properly imported."""
        from chunk_metadata_adapter.ast.parameterization import (
            ParameterValue as ParameterValueSub,
            ParameterizedAST as ParameterizedASTSub,
            ASTParameterizer as ASTParameterizerSub,
            ASTInstantiator as ASTInstantiatorSub,
            QueryCache as QueryCacheSub
        )
        
        assert ParameterValue is ParameterValueSub
        assert ParameterizedAST is ParameterizedASTSub
        assert ASTParameterizer is ASTParameterizerSub
        assert ASTInstantiator is ASTInstantiatorSub
        assert QueryCache is QueryCacheSub


class TestASTModuleFunctionality:
    """Tests for ast.py module functionality."""
    
    def test_typed_value_creation(self):
        """Test TypedValue creation and validation."""
        # Test valid TypedValue creation
        value = TypedValue("int", 42)
        assert value.type == "int"
        assert value.value == 42
        
        # Test string TypedValue
        str_value = TypedValue("str", "test")
        assert str_value.type == "str"
        assert str_value.value == "test"
        
        # Test float TypedValue
        float_value = TypedValue("float", 3.14)
        assert float_value.type == "float"
        assert float_value.value == 3.14
    
    def test_field_condition_creation(self):
        """Test FieldCondition creation."""
        value = TypedValue("int", 18)
        condition = FieldCondition("age", ">", value)
        
        assert condition.field == "age"
        assert condition.operator == ">"
        assert condition.value == value
        assert condition.node_type == "field_condition"
    
    def test_logical_operator_creation(self):
        """Test LogicalOperator creation."""
        value1 = TypedValue("int", 18)
        value2 = TypedValue("int", 25)
        condition1 = FieldCondition("age", ">", value1)
        condition2 = FieldCondition("age", "<", value2)
        
        operator = LogicalOperator("AND", [condition1, condition2])
        
        assert operator.operator == "AND"
        assert len(operator.children) == 2
        assert operator.node_type == "logical_operator"
    
    def test_paren_expression_creation(self):
        """Test ParenExpression creation."""
        value = TypedValue("int", 18)
        condition = FieldCondition("age", ">", value)
        
        paren_expr = ParenExpression(condition)
        
        assert paren_expr.expression == condition
        assert paren_expr.node_type == "paren_expression"
    
    def test_ast_visitor_usage(self):
        """Test ASTVisitor usage."""
        # Create a simple AST
        value = TypedValue("int", 18)
        condition = FieldCondition("age", ">", value)
        
        # Test that visitor can be instantiated (abstract class)
        with pytest.raises(TypeError):
            ASTVisitor()
    
    def test_ast_printer_usage(self):
        """Test ASTPrinter usage."""
        from chunk_metadata_adapter.ast import ASTPrinter
        
        # Create a simple AST
        value = TypedValue("int", 18)
        condition = FieldCondition("age", ">", value)
        
        # Test printer
        printer = ASTPrinter()
        result = printer.visit(condition)
        assert isinstance(result, str)
        assert "age" in result
        assert ">" in result
    
    def test_ast_node_factory_usage(self):
        """Test ASTNodeFactory usage."""
        factory = ASTNodeFactory()
        
        # Test creating TypedValue
        value = factory.create_typed_value("int", 42)
        assert isinstance(value, TypedValue)
        assert value.type == "int"
        assert value.value == 42
        
        # Test creating FieldCondition
        condition = factory.create_field_condition("age", ">", value)
        assert isinstance(condition, FieldCondition)
        assert condition.field == "age"
        assert condition.operator == ">"
        assert condition.value == value
    
    def test_json_serialization_functions(self):
        """Test JSON serialization functions."""
        # Create a simple AST
        value = TypedValue("int", 18)
        condition = FieldCondition("age", ">", value)
        
        # Test ast_to_json
        json_data = ast_to_json(condition)
        assert isinstance(json_data, dict)
        assert json_data["node_type"] == "field_condition"
        assert json_data["field"] == "age"
        assert json_data["operator"] == ">"
        
        # Test ast_from_json
        restored_condition = ast_from_json(json_data)
        assert isinstance(restored_condition, FieldCondition)
        assert restored_condition.field == "age"
        assert restored_condition.operator == ">"
        
        # Test ast_to_json_string
        json_string = ast_to_json_string(condition)
        assert isinstance(json_string, str)
        assert "age" in json_string
        assert ">" in json_string
        
        # Test ast_from_json_string
        restored_from_string = ast_from_json_string(json_string)
        assert isinstance(restored_from_string, FieldCondition)
        assert restored_from_string.field == "age"
        assert restored_from_string.operator == ">"
    
    def test_parameterization_classes(self):
        """Test parameterization classes."""
        # Test ParameterValue
        param_value = ParameterValue("param_1", "int", "age threshold")
        assert param_value.param_id == "param_1"
        assert param_value.param_type == "int"
        assert param_value.description == "age threshold"
        
        # Test ParameterizedAST
        value = TypedValue("int", 18)
        condition = FieldCondition("age", ">", value)
        param_ast = ParameterizedAST(condition, {"param_1": param_value}, "template_hash_123")
        assert param_ast.ast == condition
        assert "param_1" in param_ast.parameters
        assert param_ast.template_hash == "template_hash_123"
        
        # Test ASTParameterizer
        parameterizer = ASTParameterizer()
        assert parameterizer is not None
        
        # Test ASTInstantiator
        instantiator = ASTInstantiator()
        assert instantiator is not None
        
        # Test QueryCache
        cache = QueryCache()
        assert cache is not None


class TestASTModuleEdgeCases:
    """Tests for ast.py module edge cases."""
    
    def test_typed_value_edge_cases(self):
        """Test TypedValue edge cases."""
        # Test null type
        null_value = TypedValue("null", None)
        assert null_value.type == "null"
        assert null_value.value is None
        
        # Test list type
        list_value = TypedValue("list", [1, 2, 3])
        assert list_value.type == "list"
        assert list_value.value == [1, 2, 3]
        
        # Test dict type
        dict_value = TypedValue("dict", {"key": "value"})
        assert dict_value.type == "dict"
        assert dict_value.value == {"key": "value"}
    
    def test_field_condition_edge_cases(self):
        """Test FieldCondition edge cases."""
        # Test with different operators
        operators = ["=", "!=", ">", ">=", "<", "<=", "in", "not_in", "like", "~", "!~"]
        value = TypedValue("int", 18)
        
        for operator in operators:
            condition = FieldCondition("field", operator, value)
            assert condition.operator == operator
            assert condition.field == "field"
            assert condition.value == value
    
    def test_logical_operator_edge_cases(self):
        """Test LogicalOperator edge cases."""
        value = TypedValue("int", 18)
        condition = FieldCondition("age", ">", value)
        
        # Test NOT operator (single child)
        not_op = LogicalOperator("NOT", [condition])
        assert not_op.operator == "NOT"
        assert len(not_op.children) == 1
        
        # Test multiple children
        condition2 = FieldCondition("age", "<", TypedValue("int", 25))
        and_op = LogicalOperator("AND", [condition, condition2])
        assert and_op.operator == "AND"
        assert len(and_op.children) == 2
    
    def test_json_serialization_edge_cases(self):
        """Test JSON serialization edge cases."""
        # Test with complex AST
        value1 = TypedValue("int", 18)
        value2 = TypedValue("int", 25)
        condition1 = FieldCondition("age", ">", value1)
        condition2 = FieldCondition("age", "<", value2)
        operator = LogicalOperator("AND", [condition1, condition2])
        
        # Serialize and deserialize
        json_data = ast_to_json(operator)
        restored = ast_from_json(json_data)
        
        assert isinstance(restored, LogicalOperator)
        assert restored.operator == "AND"
        assert len(restored.children) == 2
        assert isinstance(restored.children[0], FieldCondition)
        assert isinstance(restored.children[1], FieldCondition)
    
    def test_factory_edge_cases(self):
        """Test ASTNodeFactory edge cases."""
        factory = ASTNodeFactory()
        
        # Test creating different types of values
        types_and_values = [
            ("int", 42),
            ("float", 3.14),
            ("str", "test"),
            ("bool", True),
            ("list", [1, 2, 3]),
            ("dict", {"key": "value"}),
            ("null", None)
        ]
        
        for type_name, value in types_and_values:
            typed_value = factory.create_typed_value(type_name, value)
            assert typed_value.type == type_name
            assert typed_value.value == value
        
        # Test creating logical operators
        value = TypedValue("int", 18)
        condition = FieldCondition("age", ">", value)
        
        and_op = factory.create_logical_operator("AND", [condition, condition])
        assert isinstance(and_op, LogicalOperator)
        assert and_op.operator == "AND"
        assert len(and_op.children) == 2
        
        not_op = factory.create_logical_operator("NOT", [condition])
        assert isinstance(not_op, LogicalOperator)
        assert not_op.operator == "NOT"
        assert len(not_op.children) == 1
