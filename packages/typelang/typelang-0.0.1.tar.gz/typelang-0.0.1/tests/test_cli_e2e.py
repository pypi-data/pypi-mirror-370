"""E2E tests for the Typelang CLI."""

import json
import os
import subprocess
import tempfile
from pathlib import Path
import pytest

# Test fixtures
SIMPLE_SCHEMA = """type User = {
  id: string
  name: string
  age?: int
  email: string
}"""

COMPLEX_SCHEMA = """/** Product catalog item */
@table("products")
type Product = {
  /** Unique product identifier */
  @primary
  id: string
  
  /** Product display name */
  name: string
  
  /** Product description */
  description?: string
  
  /** Price in cents */
  price: int
  
  /** Available stock */
  stock: int
  
  /** Product categories */
  categories: string[]
  
  /** Product metadata */
  metadata: Dict<string, any>
  
  /** Product status */
  status: "draft" | "published" | "archived"
}

/** Order information */
type Order = {
  id: string
  userId: string
  products: Product[]
  total: float
  status: "pending" | "processing" | "shipped" | "delivered" | "cancelled"
  createdAt: string
  updatedAt?: string
}"""

GENERIC_SCHEMA = """type Container<T> = {
  value: T
  metadata: Dict<string, string>
}

type Response<T, E> = {
  success: bool
  data?: T
  error?: E
  timestamp: string
}"""


class TestCLIE2E:
    """Test the CLI end-to-end."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    def run_cli(self, *args, cwd=None):
        """Run the CLI with given arguments."""
        cmd = ["uv", "run", "typelang"] + list(args)
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=cwd or os.path.dirname(os.path.dirname(__file__))
        )
        if result.returncode != 0:
            raise RuntimeError(f"CLI failed: {result.stderr}")
        return result.stdout
    
    def test_typescript_target_stdout(self, temp_dir):
        """Test TypeScript generation to stdout."""
        schema_file = temp_dir / "schema.tl"
        schema_file.write_text(SIMPLE_SCHEMA)
        
        output = self.run_cli(str(schema_file), "-t", "ts")
        
        assert "export type User" in output
        assert "id: string" in output
        assert "name: string" in output
        assert "age?: number" in output
        assert "email: string" in output
    
    def test_typescript_target_file(self, temp_dir):
        """Test TypeScript generation to file."""
        schema_file = temp_dir / "schema.tl"
        schema_file.write_text(SIMPLE_SCHEMA)
        output_file = temp_dir / "output.ts"
        
        self.run_cli(str(schema_file), "-t", "ts", "-o", str(output_file))
        
        content = output_file.read_text()
        assert "export type User" in content
        assert "age?: number" in content
    
    def test_python_pydantic_stdout(self, temp_dir):
        """Test Python Pydantic generation to stdout."""
        schema_file = temp_dir / "schema.tl"
        schema_file.write_text(SIMPLE_SCHEMA)
        
        output = self.run_cli(str(schema_file), "-t", "py-pydantic")
        
        assert "from pydantic import BaseModel" in output
        assert "class User(BaseModel)" in output
        assert "id: str" in output
        assert "name: str" in output
        assert "age: Optional[int]" in output
        assert "email: str" in output
    
    def test_python_pydantic_file(self, temp_dir):
        """Test Python Pydantic generation to file."""
        schema_file = temp_dir / "schema.tl"
        schema_file.write_text(SIMPLE_SCHEMA)
        output_file = temp_dir / "output.py"
        
        self.run_cli(str(schema_file), "-t", "py-pydantic", "-o", str(output_file))
        
        content = output_file.read_text()
        assert "class User(BaseModel)" in content
        assert "Optional[int]" in content
    
    def test_python_dataclass_stdout(self, temp_dir):
        """Test Python dataclass generation to stdout."""
        schema_file = temp_dir / "schema.tl"
        schema_file.write_text(SIMPLE_SCHEMA)
        
        output = self.run_cli(str(schema_file), "-t", "py-dataclass")
        
        assert "from dataclasses import dataclass" in output
        assert "@dataclass" in output
        assert "class User:" in output
        assert "id: str" in output
        assert "age: Optional[int]" in output
    
    def test_python_dataclass_file(self, temp_dir):
        """Test Python dataclass generation to file."""
        schema_file = temp_dir / "schema.tl"
        schema_file.write_text(SIMPLE_SCHEMA)
        output_file = temp_dir / "output.py"
        
        self.run_cli(str(schema_file), "-t", "py-dataclass", "-o", str(output_file))
        
        content = output_file.read_text()
        assert "@dataclass" in content
        assert "class User:" in content
    
    def test_jsonschema_stdout(self, temp_dir):
        """Test JSON Schema generation to stdout."""
        schema_file = temp_dir / "schema.tl"
        schema_file.write_text(SIMPLE_SCHEMA)
        
        output = self.run_cli(str(schema_file), "-t", "jsonschema")
        schema = json.loads(output)
        
        assert "$schema" in schema
        assert schema["type"] == "object"
        assert "id" in schema["properties"]
        assert "name" in schema["properties"]
        assert "age" in schema["properties"]
        assert "email" in schema["properties"]
        assert "id" in schema["required"]
        assert "name" in schema["required"]
        assert "email" in schema["required"]
        assert "age" not in schema["required"]
    
    def test_jsonschema_file(self, temp_dir):
        """Test JSON Schema generation to file."""
        schema_file = temp_dir / "schema.tl"
        schema_file.write_text(SIMPLE_SCHEMA)
        output_file = temp_dir / "output.json"
        
        self.run_cli(str(schema_file), "-t", "jsonschema", "-o", str(output_file))
        
        content = output_file.read_text()
        schema = json.loads(content)
        assert "$schema" in schema
        assert "id" in schema["properties"]
    
    def test_ir_stdout(self, temp_dir):
        """Test IR generation to stdout."""
        schema_file = temp_dir / "schema.tl"
        schema_file.write_text(SIMPLE_SCHEMA)
        
        output = self.run_cli(str(schema_file), "-t", "ir")
        ir = json.loads(output)
        
        assert "types" in ir
        assert len(ir["types"]) == 1
        assert ir["types"][0]["name"] == "User"
        assert ir["types"][0]["body"]["kind"] == "Struct"
        assert len(ir["types"][0]["body"]["fields"]) == 4
    
    def test_ir_file(self, temp_dir):
        """Test IR generation to file."""
        schema_file = temp_dir / "schema.tl"
        schema_file.write_text(SIMPLE_SCHEMA)
        output_file = temp_dir / "output.json"
        
        self.run_cli(str(schema_file), "-t", "ir", "-o", str(output_file))
        
        content = output_file.read_text()
        ir = json.loads(content)
        assert ir["types"][0]["name"] == "User"
    
    def test_complex_schema_typescript(self, temp_dir):
        """Test complex schema with TypeScript."""
        schema_file = temp_dir / "schema.tl"
        schema_file.write_text(COMPLEX_SCHEMA)
        
        output = self.run_cli(str(schema_file), "-t", "ts")
        
        assert "export type Product" in output
        assert "export type Order" in output
        assert "/** Product catalog item */" in output
        assert '@table("products")' in output
        assert "categories: string[]" in output
        assert "metadata: Record<string, any>" in output
        assert "'draft' | 'published' | 'archived'" in output
    
    def test_complex_schema_pydantic(self, temp_dir):
        """Test complex schema with Pydantic."""
        schema_file = temp_dir / "schema.tl"
        schema_file.write_text(COMPLEX_SCHEMA)
        
        output = self.run_cli(str(schema_file), "-t", "py-pydantic")
        
        assert "class Product(BaseModel)" in output
        assert "class Order(BaseModel)" in output
        assert "List[str]" in output
        assert "Dict[str, Any]" in output
        assert "Literal['draft']" in output
        assert "List['Product']" in output
    
    def test_complex_schema_jsonschema(self, temp_dir):
        """Test complex schema with JSON Schema."""
        schema_file = temp_dir / "schema.tl"
        schema_file.write_text(COMPLEX_SCHEMA)
        
        output = self.run_cli(str(schema_file), "-t", "jsonschema")
        schema = json.loads(output)
        
        assert "Product" in schema["definitions"]
        assert "Order" in schema["definitions"]
        assert schema["definitions"]["Product"]["properties"]["categories"]["type"] == "array"
        assert "draft" in schema["definitions"]["Product"]["properties"]["status"]["enum"]
        assert "published" in schema["definitions"]["Product"]["properties"]["status"]["enum"]
    
    def test_generic_schema(self, temp_dir):
        """Test generic types."""
        schema_file = temp_dir / "schema.tl"
        schema_file.write_text(GENERIC_SCHEMA)
        
        # TypeScript
        ts_output = self.run_cli(str(schema_file), "-t", "ts")
        assert "Container<T>" in ts_output
        assert "Response<T, E>" in ts_output
        assert "value: T" in ts_output
        assert "data?: T" in ts_output
        assert "error?: E" in ts_output
        
        # Python (generics have limited support)
        py_output = self.run_cli(str(schema_file), "-t", "py-pydantic")
        assert "class Container" in py_output
        assert "class Response" in py_output
    
    def test_default_target(self, temp_dir):
        """Test default target is TypeScript."""
        schema_file = temp_dir / "schema.tl"
        schema_file.write_text(SIMPLE_SCHEMA)
        
        # No target specified
        output = self.run_cli(str(schema_file))
        
        assert "export type User" in output
        assert "id: string" in output
    
    def test_auto_extension(self, temp_dir):
        """Test automatic extension addition."""
        schema_file = temp_dir / "schema.tl"
        schema_file.write_text(SIMPLE_SCHEMA)
        
        # TypeScript
        output_base = temp_dir / "output"
        self.run_cli(str(schema_file), "-t", "ts", "-o", str(output_base))
        assert (temp_dir / "output.ts").exists()
        
        # Python
        output_base = temp_dir / "output2"
        self.run_cli(str(schema_file), "-t", "py-pydantic", "-o", str(output_base))
        assert (temp_dir / "output2.py").exists()
        
        # JSON Schema
        output_base = temp_dir / "output3"
        self.run_cli(str(schema_file), "-t", "jsonschema", "-o", str(output_base))
        assert (temp_dir / "output3.json").exists()
    
    def test_markdown_input(self, temp_dir):
        """Test extracting schema from markdown."""
        md_file = temp_dir / "schema.md"
        md_content = f"""# Schema Documentation
        
Here's our schema:

```ts
{SIMPLE_SCHEMA}
```

More documentation here.
"""
        md_file.write_text(md_content)
        
        output = self.run_cli(str(md_file), "-t", "ts")
        
        assert "export type User" in output
        assert "id: string" in output
    
    def test_error_handling(self, temp_dir):
        """Test error handling for invalid schemas."""
        schema_file = temp_dir / "schema.tl"
        
        # Syntax error
        schema_file.write_text("type User = {")
        with pytest.raises(RuntimeError):
            self.run_cli(str(schema_file), "-t", "ts")
        
        # Missing type reference (should recover with 'any')
        schema_file.write_text("""type User = {
            profile: MissingType
        }""")
        output = self.run_cli(str(schema_file), "-t", "ts")
        assert "any" in output  # Should fallback to any
    
    def test_preserve_metadata_in_ir(self, temp_dir):
        """Test that IR preserves all metadata."""
        schema_file = temp_dir / "schema.tl"
        schema_file.write_text(COMPLEX_SCHEMA)
        
        output = self.run_cli(str(schema_file), "-t", "ir")
        ir = json.loads(output)
        
        assert len(ir["types"]) == 2
        product = next(t for t in ir["types"] if t["name"] == "Product")
        assert product["doc"] is not None
        assert product["attrs"] is not None
        
        id_field = next(f for f in product["body"]["fields"] if f["name"] == "id")
        assert id_field["doc"] is not None