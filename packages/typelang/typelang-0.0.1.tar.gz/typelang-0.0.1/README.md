# Typelang Python

Python implementation of Typelang - A TypeScript-flavored schema definition language for cross-platform type generation.

## Features

- **TypeScript-like syntax** - Familiar and easy to learn
- **Multiple targets** - Generate TypeScript, Python (dataclass/Pydantic), and JSON Schema
- **CLI and API** - Use as a command-line tool or programmatic library
- **Rich metadata** - Support for JSDoc comments and custom attributes
- **Generic types** - Support for generic type parameters
- **Pure Python** - No external dependencies for core functionality

## Installation

### Using pip

```bash
pip install typelang
```

### Using uv (recommended)

```bash
uv add typelang
```

### From source

```bash
git clone https://github.com/dataset-sh/typelang-py
cd typelang-py
uv sync
```

## Quick Start

### CLI Usage

```bash
# Generate TypeScript types
typelang schema.tl -o types.ts

# Generate Python Pydantic models
typelang schema.tl -t py-pydantic -o models.py

# Generate Python dataclasses
typelang schema.tl -t py-dataclass -o models.py

# Generate JSON Schema
typelang schema.tl -t jsonschema -o schema.json

# Output to stdout
typelang schema.tl -t ts

# View intermediate representation
typelang schema.tl -t ir
```

### Programmatic API

```python
from typelang import Compiler

source = """
type User = {
  id: string
  name: string
  email?: string
  age: int
}
"""

compiler = Compiler()

# Generate TypeScript
typescript = compiler.compile(source, target="typescript")
print(typescript)

# Generate Python Pydantic
pydantic = compiler.compile(source, target="python-pydantic")
print(pydantic)

# Generate JSON Schema
jsonschema = compiler.compile(source, target="jsonschema")
print(jsonschema)
```

## Schema Language

### Basic Types

```typescript
type User = {
  // Primitive types
  id: string
  age: int
  score: float
  active: bool
  
  // Optional fields
  email?: string
  phone?: string
  
  // Arrays
  tags: string[]
  scores: float[]
  
  // Maps/Dictionaries
  metadata: Dict<string, any>
  settings: Dict<string, bool>
}
```

### Generic Types

```typescript
// Generic type parameters
type Container<T> = {
  value: T
  timestamp: string
}

type Result<T, E> = {
  success: bool
  data?: T
  error?: E
}

// Using generic types
type UserContainer = Container<User>
```

### Union Types

```typescript
// String literal unions (enums)
type Status = "draft" | "published" | "archived"

// Mixed unions
type StringOrNumber = string | int

// Complex unions
type Response = 
  | { success: true, data: User }
  | { success: false, error: string }
```

### Nested Objects

```typescript
type Address = {
  street: string
  city: string
  country: string
}

type User = {
  name: string
  address: Address  // Nested type reference
  
  // Inline nested object
  contact: {
    email: string
    phone?: string
  }
}
```

### Metadata and Attributes

```typescript
/** User model for the application */
@table("users")
@index(["email", "username"])
type User = {
  /** Unique identifier */
  @primary
  @generated("uuid")
  id: string
  
  /** User's email address */
  @unique
  @validate("email")
  email: string
  
  /** User's display name */
  @minLength(3)
  @maxLength(50)
  name: string
}
```

## CLI Options

```
Usage: typelang [-h] [-o OUTPUT] [-t TARGET] input

Typelang compiler - compile schema definitions to various target languages

positional arguments:
  input                Input Typelang file (.tl or .md)

options:
  -h, --help           show this help message and exit
  -o, --output OUTPUT  Output file path (optional, defaults to stdout)
  -t, --target TARGET  Target format (default: ts). Available: ts, py-dataclass, py-pydantic, jsonschema, ir

Examples:
  typelang schema.tl -o types.ts
  typelang schema.tl -t py-pydantic -o models.py
  typelang schema.tl -t jsonschema
  typelang schema.tl -t ir -o schema.ir.json
```

## API Reference

### `Compiler` class

The main compiler class for transforming Typelang source to various targets.

```python
from typelang import Compiler

compiler = Compiler()
```

### `compile(source: str, target: str = "typescript") -> Optional[str]`

Compiles Typelang source code to the specified target format.

**Parameters:**
- `source`: Typelang source code string
- `target`: Target format - one of:
  - `"typescript"` or `"ts"` - TypeScript type definitions
  - `"python-dataclass"` or `"py-dataclass"` - Python dataclasses
  - `"python-pydantic"` or `"py-pydantic"` - Python Pydantic models
  - `"jsonschema"` - JSON Schema
  - `"ir"` - Intermediate Representation (JSON)

**Returns:**
- Generated code as string, or `None` if compilation failed

**Example:**

```python
from typelang import Compiler

schema = """
/** Product in our catalog */
@table("products")
type Product = {
  /** Unique product ID */
  @primary
  id: string
  
  /** Product display name */
  name: string
  
  /** Price in cents */
  price: int
  
  /** Available stock */
  stock: int
  
  /** Product categories */
  categories: string[]
  
  /** Product status */
  status: "draft" | "published" | "out-of-stock"
}

/** Customer order */
type Order = {
  id: string
  customerId: string
  products: Product[]
  total: float
  status: "pending" | "paid" | "shipped" | "delivered"
  createdAt: string
}
"""

compiler = Compiler()

# Generate TypeScript
typescript = compiler.compile(schema, target="typescript")
if typescript:
    with open("types.ts", "w") as f:
        f.write(typescript)

# Generate Python Pydantic
pydantic = compiler.compile(schema, target="python-pydantic")
if pydantic:
    with open("models.py", "w") as f:
        f.write(pydantic)

# Generate JSON Schema
jsonschema = compiler.compile(schema, target="jsonschema")
if jsonschema:
    with open("schema.json", "w") as f:
        f.write(jsonschema)

# Check for errors
if compiler.get_errors():
    print("Compilation errors:")
    for error in compiler.get_errors():
        print(f"  - {error}")
```

### `get_errors() -> List[str]`

Returns a list of compilation errors encountered during the last compilation.

### `compile_file(input_path: str, output_path: Optional[str] = None, target: str = "typescript") -> bool`

Convenience function to compile a file directly.

**Parameters:**
- `input_path`: Path to input Typelang file
- `output_path`: Path to output file (optional, derives from input if not provided)
- `target`: Target format (same as `compile` method)

**Returns:**
- `True` if successful, `False` otherwise

**Example:**

```python
from typelang import compile_file

# Compile with automatic output path
success = compile_file("schema.tl", target="python-pydantic")
# Creates schema_pydantic.py

# Compile with specific output path
success = compile_file("schema.tl", "models.py", target="python-pydantic")
```

## Built-in Types

| Typelang | TypeScript | Python | JSON Schema |
|----------|------------|---------|-------------|
| `string` | `string` | `str` | `"type": "string"` |
| `int` | `number` | `int` | `"type": "integer"` |
| `float` | `number` | `float` | `"type": "number"` |
| `bool` | `boolean` | `bool` | `"type": "boolean"` |
| `any` | `any` | `Any` | `{}` |
| `T[]` | `T[]` | `List[T]` | `"type": "array"` |
| `Dict<K,V>` | `Record<K,V>` | `Dict[K,V]` | `"type": "object"` |
| `T?` | `T \| undefined` | `Optional[T]` | not required |

## Output Examples

### TypeScript Output

```typescript
export type User = {
  id: string
  name: string
  email?: string
  age: number
}
```

### Python Pydantic Output

```python
from pydantic import BaseModel, Field
from typing import Optional

class User(BaseModel):
    id: str
    name: str
    email: Optional[str] = Field(default=None)
    age: int
```

### Python Dataclass Output

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    id: str
    name: str
    age: int
    email: Optional[str] = None
```

### JSON Schema Output

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "id": {"type": "string"},
    "name": {"type": "string"},
    "email": {"type": "string"},
    "age": {"type": "integer"}
  },
  "required": ["id", "name", "age"]
}
```

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/dataset-sh/typelang-py
cd typelang-py

# Install with uv
uv sync

# Or install with pip
pip install -e .
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov

# Run specific test file
uv run pytest tests/test_compiler.py
```

### Project Structure

```
typelang-py/
   src/
      typelang_py/
          __init__.py          # Package exports
          __main__.py          # CLI entry point
          ast_types.py         # AST type definitions
          ir_types.py          # IR type definitions
          lexer.py             # Tokenizer
          parser.py            # Parser
          transformer.py       # AST to IR transformer
          compiler.py          # Main compiler
          codegen_typescript.py    # TypeScript generator
          codegen_python_dataclass.py  # Dataclass generator
          codegen_python_pydantic.py   # Pydantic generator
          codegen_jsonschema.py        # JSON Schema generator
   tests/
      test_compiler.py        # Compiler tests
      test_cli_e2e.py        # End-to-end CLI tests
   pyproject.toml              # Project configuration
   README.md                   # This file
```

## License

MIT � [Hao Wu](https://github.com/dataset-sh)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Related Projects

- [@dataset.sh/typelang](https://www.npmjs.com/package/@dataset.sh/typelang) - TypeScript/JavaScript implementation of Typelang
- [typelang-spec](https://github.com/dataset-sh/typelang-spec) - Language specification