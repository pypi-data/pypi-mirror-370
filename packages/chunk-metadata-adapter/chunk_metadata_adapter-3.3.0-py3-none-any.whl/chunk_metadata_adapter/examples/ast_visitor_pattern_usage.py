"""
AST Visitor pattern usage example.

This example demonstrates how to use the Visitor pattern with AST nodes
for printing, validation, analysis, and optimization.

Author: Development Team
Created: 2024-01-15
Updated: 2024-01-20
"""

from chunk_metadata_adapter.ast import (
    TypedValue,
    FieldCondition,
    LogicalOperator,
    ParenExpression,
    ASTPrinter,
    ASTValidator,
    ASTAnalyzer,
    ASTOptimizer
)


def main():
    """Demonstrate AST Visitor pattern usage."""
    print("=== AST Visitor Pattern Usage Example ===\n")
    
    # 1. Create a complex AST for demonstration
    print("1. Creating complex AST:")
    print("   (age > 18 AND status = 'active') OR (type = 'DocBlock' AND quality_score >= 0.8)")
    print()
    
    # Left side: age > 18 AND status = 'active'
    age_condition = FieldCondition("age", ">", TypedValue("int", 18))
    status_condition = FieldCondition("status", "=", TypedValue("str", "active"))
    left_and = LogicalOperator("AND", [age_condition, status_condition])
    left_paren = ParenExpression(left_and)
    
    # Right side: type = 'DocBlock' AND quality_score >= 0.8
    type_condition = FieldCondition("type", "=", TypedValue("str", "DocBlock"))
    quality_condition = FieldCondition("quality_score", ">=", TypedValue("float", 0.8))
    right_and = LogicalOperator("AND", [type_condition, quality_condition])
    
    # Root: OR
    root_or = LogicalOperator("OR", [left_paren, right_and])
    
    # 2. Use ASTPrinter to visualize the structure
    print("2. AST Structure (using ASTPrinter):")
    printer = ASTPrinter()
    print_result = root_or.accept(printer)
    print(print_result)
    print()
    
    # 3. Use ASTValidator to validate the structure
    print("3. AST Validation (using ASTValidator):")
    validator = ASTValidator()
    is_valid = root_or.accept(validator)
    
    if is_valid:
        print("   ✅ AST is valid")
        print(f"   No errors found")
    else:
        print("   ❌ AST has errors:")
        for error in validator.errors:
            print(f"   - {error}")
    print()
    
    # 4. Use ASTAnalyzer to analyze complexity
    print("4. AST Analysis (using ASTAnalyzer):")
    analyzer = ASTAnalyzer()
    analyzer.visit(root_or)
    analysis = analyzer.get_analysis()
    
    print(f"   Field conditions: {analysis['field_count']}")
    print(f"   Logical operators: {analysis['operator_count']}")
    print(f"   Maximum depth: {analysis['max_depth']}")
    print(f"   Fields used: {', '.join(analysis['fields_used'])}")
    print(f"   Operators used: {', '.join(analysis['operators_used'])}")
    print(f"   Complexity score: {analysis['complexity_score']}")
    print()
    
    # 5. Use ASTOptimizer to optimize the structure
    print("5. AST Optimization (using ASTOptimizer):")
    optimizer = ASTOptimizer()
    optimized = optimizer.visit(root_or)
    
    print("   Original AST:")
    print(print_result)
    print()
    
    print("   Optimized AST:")
    optimized_printer = ASTPrinter()
    optimized_result = optimized.accept(optimized_printer)
    print(optimized_result)
    print()
    
    # 6. Demonstrate with real-world SemanticChunk fields
    print("6. Real-world SemanticChunk filter analysis:")
    
    # Create a realistic filter
    real_world_conditions = [
        FieldCondition("type", "=", TypedValue("str", "DocBlock")),
        FieldCondition("quality_score", ">=", TypedValue("float", 0.8)),
        FieldCondition("year", ">=", TypedValue("int", 2020)),
        FieldCondition("is_public", "=", TypedValue("bool", True)),
        FieldCondition("tags", "intersects", TypedValue("list", ["ai", "ml"])),
        FieldCondition("block_meta.version", "=", TypedValue("str", "1.0")),
    ]
    
    real_world_and = LogicalOperator("AND", real_world_conditions)
    
    # Analyze real-world filter
    real_analyzer = ASTAnalyzer()
    real_analyzer.visit(real_world_and)
    real_analysis = real_analyzer.get_analysis()
    
    print(f"   Real-world filter analysis:")
    print(f"   - Total conditions: {real_analysis['field_count']}")
    print(f"   - Logical operators: {real_analysis['operator_count']}")
    print(f"   - Fields: {', '.join(real_analysis['fields_used'])}")
    print(f"   - Complexity: {real_analysis['complexity_score']}")
    print()
    
    # 7. Demonstrate error handling
    print("7. Error handling demonstration:")
    
    try:
        # Try to create invalid AST (will be caught by validation)
        invalid_condition = FieldCondition("123field", ">", TypedValue("int", 18))
        print("   ❌ Should not reach here")
    except ValueError as e:
        print(f"   ✅ Caught validation error: {e}")
    
    try:
        # Try to create invalid logical operator
        child = FieldCondition("age", ">", TypedValue("int", 18))
        invalid_op = LogicalOperator("NOT", [child, child])  # NOT should have only one child
        print("   ❌ Should not reach here")
    except ValueError as e:
        print(f"   ✅ Caught validation error: {e}")
    
    print()
    print("=== Example completed successfully! ===")


if __name__ == "__main__":
    main() 