"""
AST JSON Serialization Demo

This example demonstrates how to serialize and deserialize AST nodes
to and from JSON format for client-server communication.

Key features demonstrated:
- Serializing AST nodes to JSON
- Deserializing JSON back to AST nodes
- Round-trip serialization validation
- Complex AST structures with nested operators
- Error handling for invalid JSON

Usage:
    python -m chunk_metadata_adapter.examples.ast_json_serialization_demo

Author: Development Team
Created: 2024-01-20
"""

import json
from datetime import datetime
from chunk_metadata_adapter.ast import (
    TypedValue, FieldCondition, LogicalOperator, ParenExpression,
    ast_to_json, ast_from_json, ast_to_json_string, ast_from_json_string
)


def demo_basic_serialization():
    """Demonstrate basic AST node serialization."""
    print("=== Basic AST Node Serialization ===")
    
    # Create a simple field condition
    condition = FieldCondition("age", ">", TypedValue("int", 18))
    
    # Serialize to JSON dictionary
    json_data = ast_to_json(condition)
    print(f"Serialized to JSON: {json.dumps(json_data, indent=2)}")
    
    # Deserialize back to AST
    reconstructed = ast_from_json(json_data)
    print(f"Deserialized AST: {reconstructed}")
    print(f"Type: {type(reconstructed)}")
    print(f"Field: {reconstructed.field}")
    print(f"Operator: {reconstructed.operator}")
    print(f"Value: {reconstructed.value}")
    print()


def demo_complex_ast_serialization():
    """Demonstrate complex AST serialization with nested operators."""
    print("=== Complex AST Serialization ===")
    
    # Create complex AST: (age > 18 AND status = 'active') OR (vip = true)
    age_condition = FieldCondition("age", ">", TypedValue("int", 18))
    status_condition = FieldCondition("status", "=", TypedValue("str", "active"))
    vip_condition = FieldCondition("vip", "=", TypedValue("bool", True))
    
    and_operator = LogicalOperator("AND", [age_condition, status_condition])
    paren_expression = ParenExpression(and_operator)
    or_operator = LogicalOperator("OR", [paren_expression, vip_condition])
    
    # Serialize to JSON string with indentation
    json_str = ast_to_json_string(or_operator, indent=2)
    print("Complex AST serialized to JSON string:")
    print(json_str)
    print()
    
    # Deserialize from JSON string
    reconstructed = ast_from_json_string(json_str)
    print(f"Deserialized complex AST: {reconstructed}")
    print(f"Type: {type(reconstructed)}")
    print(f"Operator: {reconstructed.operator}")
    print(f"Number of children: {len(reconstructed.children)}")
    print()


def demo_different_value_types():
    """Demonstrate serialization of different TypedValue types."""
    print("=== Different Value Types Serialization ===")
    
    # Create various typed values
    values = [
        TypedValue("int", 42),
        TypedValue("float", 3.14),
        TypedValue("str", "hello world"),
        TypedValue("bool", True),
        TypedValue("null", None),
        TypedValue("list", [1, 2, 3, "test"]),
        TypedValue("dict", {"key": "value", "nested": {"data": 123}}),
        TypedValue("date", datetime(2024, 1, 15, 12, 30, 45))
    ]
    
    for value in values:
        json_data = value.to_json()
        reconstructed = TypedValue.from_json(json_data)
        
        print(f"Original: {value}")
        print(f"JSON: {json.dumps(json_data, indent=2)}")
        print(f"Reconstructed: {reconstructed}")
        print(f"Match: {value == reconstructed}")
        print()


def demo_round_trip_validation():
    """Demonstrate round-trip serialization validation."""
    print("=== Round-trip Serialization Validation ===")
    
    # Create a complex query: age > 18 AND (status = 'active' OR role = 'admin')
    age_condition = FieldCondition("age", ">", TypedValue("int", 18))
    status_condition = FieldCondition("status", "=", TypedValue("str", "active"))
    role_condition = FieldCondition("role", "=", TypedValue("str", "admin"))
    
    or_operator = LogicalOperator("OR", [status_condition, role_condition])
    paren_expression = ParenExpression(or_operator)
    and_operator = LogicalOperator("AND", [age_condition, paren_expression])
    
    print(f"Original AST: {and_operator}")
    print(f"Original string representation: {str(and_operator)}")
    print()
    
    # Round trip: AST -> JSON -> AST
    json_data = ast_to_json(and_operator)
    reconstructed = ast_from_json(json_data)
    
    print(f"Reconstructed AST: {reconstructed}")
    print(f"Reconstructed string representation: {str(reconstructed)}")
    print(f"Round-trip successful: {str(and_operator) == str(reconstructed)}")
    print()


def demo_error_handling():
    """Demonstrate error handling for invalid JSON."""
    print("=== Error Handling ===")
    
    # Test invalid JSON data
    invalid_cases = [
        ("Not a dict", "not a dict"),
        ("Missing node_type", {"field": "age"}),
        ("Invalid node_type", {"node_type": "invalid_type", "field": "age"}),
        ("Missing required fields", {"node_type": "field_condition", "field": "age"}),
    ]
    
    for case_name, invalid_data in invalid_cases:
        try:
            if isinstance(invalid_data, str):
                ast_from_json_string(invalid_data)
            else:
                ast_from_json(invalid_data)
            print(f"❌ {case_name}: Should have raised an error")
        except Exception as e:
            print(f"✅ {case_name}: {type(e).__name__}: {e}")
    
    print()


def demo_client_server_scenario():
    """Demonstrate client-server communication scenario."""
    print("=== Client-Server Communication Scenario ===")
    
    # Client side: Build AST locally
    print("Client: Building AST locally...")
    client_ast = LogicalOperator("AND", [
        FieldCondition("age", ">=", TypedValue("int", 21)),
        FieldCondition("verified", "=", TypedValue("bool", True)),
        LogicalOperator("OR", [
            FieldCondition("country", "=", TypedValue("str", "US")),
            FieldCondition("country", "=", TypedValue("str", "CA"))
        ])
    ])
    
    print(f"Client AST: {client_ast}")
    
    # Client side: Serialize to JSON for transmission
    print("\nClient: Serializing to JSON for transmission...")
    json_data = ast_to_json(client_ast)
    json_str = json.dumps(json_data, indent=2)
    print(f"JSON payload: {json_str}")
    
    # Network transmission (simulated)
    print("\nNetwork: Transmitting JSON payload...")
    
    # Server side: Receive and deserialize
    print("\nServer: Receiving and deserializing JSON...")
    received_data = json.loads(json_str)
    server_ast = ast_from_json(received_data)
    
    print(f"Server AST: {server_ast}")
    print(f"Server string representation: {str(server_ast)}")
    
    # Server side: Process the AST
    print("\nServer: Processing AST...")
    print("✅ AST successfully reconstructed and ready for execution")
    print()


def main():
    """Run all serialization demos."""
    print("AST JSON Serialization Demo")
    print("=" * 50)
    print()
    
    try:
        demo_basic_serialization()
        demo_complex_ast_serialization()
        demo_different_value_types()
        demo_round_trip_validation()
        demo_error_handling()
        demo_client_server_scenario()
        
        print("🎉 All demos completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 