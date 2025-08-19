"""
Basic usage example for AST nodes.

This example demonstrates how to create and work with AST nodes
for filter expressions.

Author: Development Team
Created: 2024-01-15
Updated: 2024-01-20
"""

from chunk_metadata_adapter.ast import (
    TypedValue,
    FieldCondition,
    LogicalOperator,
    ParenExpression
)


def main():
    """Demonstrate basic AST usage."""
    print("=== AST Basic Usage Example ===\n")
    
    # 1. Create simple field conditions
    print("1. Creating simple field conditions:")
    age_condition = FieldCondition("age", ">", TypedValue("int", 18))
    status_condition = FieldCondition("status", "=", TypedValue("str", "active"))
    type_condition = FieldCondition("type", "=", TypedValue("str", "DocBlock"))
    
    print(f"   {age_condition}")
    print(f"   {status_condition}")
    print(f"   {type_condition}")
    print()
    
    # 2. Create logical operators
    print("2. Creating logical operators:")
    and_condition = LogicalOperator("AND", [age_condition, status_condition])
    or_condition = LogicalOperator("OR", [type_condition, FieldCondition("type", "=", TypedValue("str", "CodeBlock"))])
    
    print(f"   {and_condition}")
    print(f"   {or_condition}")
    print()
    
    # 3. Create complex expression with parentheses
    print("3. Creating complex expression:")
    # (age > 18 AND status = 'active') OR (type = 'DocBlock')
    left_paren = ParenExpression(and_condition)
    complex_expr = LogicalOperator("OR", [left_paren, type_condition])
    
    print(f"   {complex_expr}")
    print(f"   Depth: {complex_expr.depth}")
    print(f"   Is leaf: {complex_expr.is_leaf}")
    print()
    
    # 4. Demonstrate nested field access
    print("4. Nested field access:")
    nested_condition = FieldCondition("block_meta.version", "=", TypedValue("str", "1.0"))
    print(f"   {nested_condition}")
    print()
    
    # 5. Demonstrate different value types
    print("5. Different value types:")
    float_condition = FieldCondition("quality_score", ">=", TypedValue("float", 0.8))
    bool_condition = FieldCondition("is_public", "=", TypedValue("bool", True))
    list_condition = FieldCondition("tags", "intersects", TypedValue("list", ["ai", "ml"]))
    null_condition = FieldCondition("deleted_at", "=", TypedValue("null", None))
    
    print(f"   {float_condition}")
    print(f"   {bool_condition}")
    print(f"   {list_condition}")
    print(f"   {null_condition}")
    print()
    
    # 6. Demonstrate validation
    print("6. Validation examples:")
    try:
        invalid_field = FieldCondition("123field", ">", TypedValue("int", 18))
    except ValueError as e:
        print(f"   Invalid field name: {e}")
    
    try:
        invalid_operator = FieldCondition("age", "invalid_op", TypedValue("int", 18))
    except ValueError as e:
        print(f"   Invalid operator: {e}")
    
    try:
        invalid_type = TypedValue("int", "not an int")
    except ValueError as e:
        print(f"   Invalid type: {e}")
    
    print()
    print("=== Example completed successfully! ===")


if __name__ == "__main__":
    main() 