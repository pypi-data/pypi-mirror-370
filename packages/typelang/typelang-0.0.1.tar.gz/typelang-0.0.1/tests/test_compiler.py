"""Tests for the Typelang compiler."""

import json
from typelang import Compiler


def test_simple_type():
    """Test compiling a simple type."""
    source = """
type User = {
    name: string
    age: int
}
"""
    
    compiler = Compiler()
    
    # Test TypeScript generation
    ts_result = compiler.compile(source, "typescript")
    assert ts_result is not None
    assert "type User" in ts_result
    assert "name: string" in ts_result
    assert "age: number" in ts_result
    
    # Test Python dataclass generation
    py_dataclass = compiler.compile(source, "python-dataclass")
    assert py_dataclass is not None
    assert "class User" in py_dataclass
    assert "name: str" in py_dataclass
    assert "age: int" in py_dataclass
    
    # Test Python Pydantic generation
    py_pydantic = compiler.compile(source, "python-pydantic")
    assert py_pydantic is not None
    assert "class User(BaseModel)" in py_pydantic
    assert "name: str" in py_pydantic
    assert "age: int" in py_pydantic
    
    # Test JSON Schema generation
    jsonschema = compiler.compile(source, "jsonschema")
    assert jsonschema is not None
    schema = json.loads(jsonschema)
    assert "title" in schema
    assert schema["title"] == "User"
    assert "properties" in schema
    assert "name" in schema["properties"]
    assert "age" in schema["properties"]


def test_optional_fields():
    """Test optional fields."""
    source = """
type Product = {
    id: string
    name: string
    description?: string
    price: float
}
"""
    
    compiler = Compiler()
    
    # Test TypeScript
    ts_result = compiler.compile(source, "typescript")
    assert "description?: string" in ts_result
    
    # Test Python dataclass
    py_dataclass = compiler.compile(source, "python-dataclass")
    assert "Optional[str]" in py_dataclass
    
    # Test JSON Schema
    jsonschema = compiler.compile(source, "jsonschema")
    schema = json.loads(jsonschema)
    assert "required" in schema
    assert "id" in schema["required"]
    assert "name" in schema["required"]
    assert "price" in schema["required"]
    assert "description" not in schema["required"]


def test_union_types():
    """Test union types."""
    source = """
type Status = "pending" | "approved" | "rejected"

type Response = {
    status: Status
    data: string | null
}
"""
    
    compiler = Compiler()
    
    # Test TypeScript
    ts_result = compiler.compile(source, "typescript")
    assert "'pending' | 'approved' | 'rejected'" in ts_result
    assert "string | null" in ts_result
    
    # Test Python
    py_pydantic = compiler.compile(source, "python-pydantic")
    assert "Literal['pending']" in py_pydantic or "Union[Literal['pending']" in py_pydantic
    
    # Test JSON Schema
    jsonschema = compiler.compile(source, "jsonschema")
    schema = json.loads(jsonschema)
    status_def = schema["definitions"]["Status"]
    assert "enum" in status_def
    assert "pending" in status_def["enum"]
    assert "approved" in status_def["enum"]
    assert "rejected" in status_def["enum"]


def test_generic_types():
    """Test generic types."""
    source = """
type Container<T> = {
    value: T
    metadata: Dict<string, string>
}
"""
    
    compiler = Compiler()
    
    # Test TypeScript
    ts_result = compiler.compile(source, "typescript")
    assert "Container<T>" in ts_result
    assert "value: T" in ts_result
    assert "Record<string, string>" in ts_result
    
    # Test Python (note: generics have limited support)
    py_dataclass = compiler.compile(source, "python-dataclass")
    assert py_dataclass is not None


def test_arrays():
    """Test array types."""
    source = """
type TodoList = {
    items: string[]
    tags: list
}
"""
    
    compiler = Compiler()
    
    # Test TypeScript
    ts_result = compiler.compile(source, "typescript")
    assert "string[]" in ts_result
    assert "any[]" in ts_result
    
    # Test Python
    py_dataclass = compiler.compile(source, "python-dataclass")
    assert "List[str]" in py_dataclass
    assert "List[Any]" in py_dataclass


def test_nested_objects():
    """Test nested object types."""
    source = """
type Address = {
    street: string
    city: string
    country: string
}

type Person = {
    name: string
    address: Address
}
"""
    
    compiler = Compiler()
    
    # Test TypeScript
    ts_result = compiler.compile(source, "typescript")
    assert "type Address" in ts_result
    assert "type Person" in ts_result
    assert "address: Address" in ts_result
    
    # Test Python
    py_pydantic = compiler.compile(source, "python-pydantic")
    assert "class Address(BaseModel)" in py_pydantic
    assert "class Person(BaseModel)" in py_pydantic
    assert "address: 'Address'" in py_pydantic
    
    # Test JSON Schema
    jsonschema = compiler.compile(source, "jsonschema")
    schema = json.loads(jsonschema)
    assert "Address" in schema["definitions"]
    assert "Person" in schema["definitions"]


def test_comments_and_attributes():
    """Test JSDoc comments and attributes."""
    source = """
/** User model for the application */
@table("users")
type User = {
    /** Unique identifier */
    @primary
    id: string
    
    /** User's display name */
    name: string
}
"""
    
    compiler = Compiler()
    
    # Test TypeScript
    ts_result = compiler.compile(source, "typescript")
    assert "/** User model for the application */" in ts_result
    assert "/** Unique identifier */" in ts_result
    assert "@table(\"users\")" in ts_result
    assert "@primary" in ts_result


def test_error_recovery():
    """Test error recovery for missing type references."""
    source = """
type User = {
    name: string
    profile: MissingType
}
"""
    
    compiler = Compiler()
    
    # Should compile with errors but still generate output
    ts_result = compiler.compile(source, "typescript")
    assert ts_result is not None
    assert "any" in ts_result  # Missing type should default to any
    
    errors = compiler.get_errors()
    assert len(errors) > 0
    assert "MissingType" in str(errors)