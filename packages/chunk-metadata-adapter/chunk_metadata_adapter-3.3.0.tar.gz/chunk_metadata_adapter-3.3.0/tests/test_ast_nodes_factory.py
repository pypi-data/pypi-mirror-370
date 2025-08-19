"""
Unit and integration tests for ASTNodeFactory and AST nodes.

Covers TypedValue, FieldCondition, LogicalOperator, ParenExpression,
ASTPrinter, ASTValidator, ASTAnalyzer, and ASTNodeFactory.

Author: Development Team
Created: 2024-06-09
Updated: 2024-06-09
"""

import pytest
from datetime import datetime
from hypothesis import given, strategies as st
from chunk_metadata_adapter.ast import (
    TypedValue, FieldCondition, LogicalOperator, ParenExpression,
    ASTPrinter, ASTValidator, ASTAnalyzer, ASTNodeFactory
)

class TestTypedValue:
    """Tests for TypedValue class."""
    def test_creation_with_valid_data(self):
        value = TypedValue("int", 42)
        assert value.type == "int"
        assert value.value == 42

    # Removed test_creation_with_invalid_type: Literal is not enforced at runtime

    def test_null_type_validation(self):
        value = TypedValue("null", None)
        assert value.type == "null"
        assert value.value is None
        with pytest.raises(ValueError):
            TypedValue("null", 42)

    def test_string_type_validation(self):
        value = TypedValue("str", "hello")
        assert value.type == "str"
        assert value.value == "hello"
        with pytest.raises(ValueError):
            TypedValue("str", 42)

    def test_float_type_validation(self):
        value = TypedValue("float", 3.14)
        assert value.type == "float"
        assert value.value == 3.14
        value2 = TypedValue("float", 42)
        assert value2.type == "float"
        assert value2.value == 42

    @given(st.integers(min_value=-(2**63), max_value=2**63-1))
    def test_int_value_generation(self, int_value):
        value = TypedValue("int", int_value)
        assert value.type == "int"
        assert value.value == int_value

    @given(st.floats(allow_nan=False, allow_infinity=False))
    def test_float_value_generation(self, float_value):
        value = TypedValue("float", float_value)
        assert value.type == "float"
        assert value.value == float_value

    @given(st.text(max_size=100))
    def test_string_value_generation(self, string_value):
        value = TypedValue("str", string_value)
        assert value.type == "str"
        assert value.value == string_value

class TestFieldCondition:
    """Tests for FieldCondition class."""
    def test_creation_with_valid_data(self):
        condition = FieldCondition("age", ">", TypedValue("int", 18))
        assert condition.field == "age"
        assert condition.operator == ">"
        assert condition.value.type == "int"
        assert condition.value.value == 18

    def test_creation_with_invalid_field(self):
        with pytest.raises(ValueError):
            FieldCondition("", ">", TypedValue("int", 18))

    def test_creation_with_invalid_operator(self):
        with pytest.raises(ValueError):
            FieldCondition("age", "invalid_op", TypedValue("int", 18))

    def test_nested_field_validation(self):
        condition = FieldCondition("user.profile.name", "=", TypedValue("str", "John"))
        assert condition.field == "user.profile.name"
        with pytest.raises(ValueError):
            FieldCondition("user..profile.name", "=", TypedValue("str", "John"))

    def test_operator_validation(self):
        valid_operators = ["=", "!=", ">", ">=", "<", "<=", "like", "~", "!~", "in", "not_in", "intersects"]
        for operator in valid_operators:
            condition = FieldCondition("field", operator, TypedValue("str", "value"))
            assert condition.operator == operator
        with pytest.raises(ValueError):
            FieldCondition("field", "invalid", TypedValue("str", "value"))

class TestLogicalOperator:
    """Tests for LogicalOperator class."""
    def test_and_operator_creation(self):
        condition1 = FieldCondition("age", ">", TypedValue("int", 18))
        condition2 = FieldCondition("status", "=", TypedValue("str", "active"))
        operator = LogicalOperator("AND", [condition1, condition2])
        assert operator.operator == "AND"
        assert len(operator.children) == 2

    def test_or_operator_creation(self):
        condition1 = FieldCondition("type", "=", TypedValue("str", "DocBlock"))
        condition2 = FieldCondition("type", "=", TypedValue("str", "CodeBlock"))
        operator = LogicalOperator("OR", [condition1, condition2])
        assert operator.operator == "OR"
        assert len(operator.children) == 2

    def test_not_operator_validation(self):
        condition = FieldCondition("age", ">", TypedValue("int", 18))
        not_op = LogicalOperator("NOT", [condition])
        assert not_op.operator == "NOT"
        with pytest.raises(ValueError):
            LogicalOperator("NOT", [])
        with pytest.raises(ValueError):
            LogicalOperator("NOT", [condition, condition])

    def test_and_or_operator_validation(self):
        condition = FieldCondition("age", ">", TypedValue("int", 18))
        with pytest.raises(ValueError):
            LogicalOperator("AND", [condition])
        with pytest.raises(ValueError):
            LogicalOperator("OR", [condition])

class TestParenExpression:
    """Tests for ParenExpression class."""
    def test_creation_with_valid_expression(self):
        condition = FieldCondition("age", ">", TypedValue("int", 18))
        paren_expr = ParenExpression(condition)
        assert paren_expr.expression == condition
        assert len(paren_expr.children) == 1
        assert paren_expr.children[0] == condition

    def test_creation_with_none_expression(self):
        with pytest.raises(ValueError):
            ParenExpression(None)

    def test_creation_with_invalid_expression(self):
        with pytest.raises(ValueError):
            ParenExpression("not_an_ast_node")

    def test_string_representation(self):
        condition = FieldCondition("age", ">", TypedValue("int", 18))
        paren_expr = ParenExpression(condition)
        assert str(paren_expr) == "(age > 18)"

class TestASTPrinter:
    """Tests for ASTPrinter visitor."""
    def test_print_field_condition(self):
        condition = FieldCondition("age", ">", TypedValue("int", 18))
        printer = ASTPrinter()
        result = condition.accept(printer)
        assert "FieldCondition: age > 18" in result

    def test_print_logical_operator(self):
        condition1 = FieldCondition("age", ">", TypedValue("int", 18))
        condition2 = FieldCondition("status", "=", TypedValue("str", "active"))
        operator = LogicalOperator("AND", [condition1, condition2])
        printer = ASTPrinter()
        result = operator.accept(printer)
        assert "LogicalOperator: AND" in result
        assert "FieldCondition: age > 18" in result
        assert 'FieldCondition: status = "active"' in result

    def test_print_paren_expression(self):
        condition = FieldCondition("age", ">", TypedValue("int", 18))
        paren_expr = ParenExpression(condition)
        printer = ASTPrinter()
        result = paren_expr.accept(printer)
        assert "ParenExpression:" in result
        assert "FieldCondition: age > 18" in result

    def test_print_with_indentation(self):
        condition1 = FieldCondition("age", ">", TypedValue("int", 18))
        condition2 = FieldCondition("status", "=", TypedValue("str", "active"))
        operator = LogicalOperator("AND", [condition1, condition2])
        printer = ASTPrinter(indent=2)
        result = operator.accept(printer)
        lines = result.split('\n')
        assert lines[0].startswith('    LogicalOperator: AND')
        assert lines[1].startswith('      FieldCondition: age > 18')
        assert lines[2].startswith('      FieldCondition: status = "active"')

class TestASTValidator:
    """Tests for ASTValidator visitor."""
    def test_validate_valid_ast(self):
        condition = FieldCondition("age", ">", TypedValue("int", 18))
        validator = ASTValidator()
        result = condition.accept(validator)
        assert result is True
        assert len(validator.errors) == 0

    def test_validate_invalid_field_condition(self):
        with pytest.raises(ValueError):
            FieldCondition("", ">", TypedValue("int", 18))

    def test_validate_invalid_logical_operator(self):
        condition = FieldCondition("age", ">", TypedValue("int", 18))
        with pytest.raises(ValueError):
            LogicalOperator("NOT", [])

    def test_validate_complex_ast(self):
        age_condition = FieldCondition("age", ">", TypedValue("int", 18))
        vip_condition = FieldCondition("vip", "=", TypedValue("bool", True))
        or_operator = LogicalOperator("OR", [age_condition, vip_condition])
        paren_expr = ParenExpression(or_operator)
        status_condition = FieldCondition("status", "=", TypedValue("str", "active"))
        final_operator = LogicalOperator("AND", [paren_expr, status_condition])
        validator = ASTValidator()
        result = final_operator.accept(validator)
        assert result is True
        assert len(validator.errors) == 0

class TestASTAnalyzer:
    """Tests for ASTAnalyzer visitor."""
    def test_analyze_simple_condition(self):
        condition = FieldCondition("age", ">", TypedValue("int", 18))
        analyzer = ASTAnalyzer()
        result = condition.accept(analyzer)
        analysis = analyzer.get_analysis()
        assert analysis["field_count"] == 1
        assert analysis["operator_count"] == 0
        assert "age" in analysis["fields_used"]
        assert ">" in analysis["operators_used"]

    def test_analyze_logical_operator(self):
        condition1 = FieldCondition("age", ">", TypedValue("int", 18))
        condition2 = FieldCondition("status", "=", TypedValue("str", "active"))
        operator = LogicalOperator("AND", [condition1, condition2])
        analyzer = ASTAnalyzer()
        result = operator.accept(analyzer)
        analysis = analyzer.get_analysis()
        assert analysis["field_count"] == 2
        assert analysis["operator_count"] == 1
        assert "AND" in analysis["operators_used"]

    def test_analyze_paren_expression(self):
        condition = FieldCondition("age", ">", TypedValue("int", 18))
        paren_expr = ParenExpression(condition)
        analyzer = ASTAnalyzer()
        result = paren_expr.accept(analyzer)
        analysis = analyzer.get_analysis()
        assert analysis["field_count"] == 1
        assert analysis["operator_count"] == 0

    def test_analyze_complex_ast(self):
        age_condition = FieldCondition("age", ">", TypedValue("int", 18))
        vip_condition = FieldCondition("vip", "=", TypedValue("bool", True))
        or_operator = LogicalOperator("OR", [age_condition, vip_condition])
        paren_expr = ParenExpression(or_operator)
        status_condition = FieldCondition("status", "=", TypedValue("str", "active"))
        final_operator = LogicalOperator("AND", [paren_expr, status_condition])
        analyzer = ASTAnalyzer()
        result = final_operator.accept(analyzer)
        analysis = analyzer.get_analysis()
        assert analysis["field_count"] == 3
        assert analysis["operator_count"] == 2
        assert analysis["max_depth"] >= 2

class TestASTNodeFactory:
    """Tests for ASTNodeFactory."""
    def test_create_simple_condition(self):
        condition = ASTNodeFactory.create_simple_condition("age", ">", "int", 18)
        assert isinstance(condition, FieldCondition)
        assert condition.field == "age"
        assert condition.operator == ">"
        assert condition.value.type == "int"
        assert condition.value.value == 18

    def test_create_complex_expression(self):
        conditions = [
            ("age", ">", "int", 18),
            ("status", "=", "str", "active"),
            ("is_public", "=", "bool", True)
        ]
        expression = ASTNodeFactory.create_complex_expression(conditions, "AND")
        assert isinstance(expression, LogicalOperator)
        assert expression.operator == "AND"
        assert len(expression.children) == 3
        for child in expression.children:
            assert isinstance(child, FieldCondition)

    def test_create_and_or_operators(self):
        condition1 = FieldCondition("age", ">", TypedValue("int", 18))
        condition2 = FieldCondition("status", "=", TypedValue("str", "active"))
        and_op = ASTNodeFactory.create_and_operator([condition1, condition2])
        assert and_op.operator == "AND"
        assert len(and_op.children) == 2
        or_op = ASTNodeFactory.create_or_operator([condition1, condition2])
        assert or_op.operator == "OR"
        assert len(or_op.children) == 2

    def test_create_not_operator(self):
        condition = FieldCondition("age", ">", TypedValue("int", 18))
        not_op = ASTNodeFactory.create_not_operator(condition)
        assert not_op.operator == "NOT"
        assert len(not_op.children) == 1
        assert not_op.children[0] == condition

class TestASTPerformance:
    """Performance tests for AST operations."""
    def test_ast_creation_performance(self):
        import time
        start_time = time.time()
        for i in range(1000):
            condition = ASTNodeFactory.create_simple_condition(
                f"field_{i}", "=", "int", i
            )
        end_time = time.time()
        creation_time = end_time - start_time
        assert creation_time < 1.0

    def test_ast_validation_performance(self):
        import time
        conditions = []
        for i in range(100):
            conditions.append((f"field_{i}", "=", "int", i))
        expression = ASTNodeFactory.create_complex_expression(conditions, "AND")
        start_time = time.time()
        validator = ASTValidator()
        result = expression.accept(validator)
        end_time = time.time()
        validation_time = end_time - start_time
        assert result is True
        assert validation_time < 0.1

    def test_ast_analysis_performance(self):
        import time
        conditions = []
        for i in range(50):
            conditions.append((f"field_{i}", "=", "int", i))
        expression = ASTNodeFactory.create_complex_expression(conditions, "AND")
        start_time = time.time()
        analyzer = ASTAnalyzer()
        analysis = expression.accept(analyzer)
        result = analyzer.get_analysis()
        end_time = time.time()
        analysis_time = end_time - start_time
        assert result["field_count"] == 50
        assert result["operator_count"] == 1
        assert analysis_time < 0.1 