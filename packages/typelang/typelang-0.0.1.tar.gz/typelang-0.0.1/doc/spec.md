# Typelang Language Specification v0.1

## Table of Contents
1. [Introduction](#introduction)
2. [Lexical Structure](#lexical-structure)
3. [Grammar](#grammar)
4. [Type System](#type-system)
5. [Built-in Types](#built-in-types)
6. [Type Expressions](#type-expressions)
7. [Declarations](#declarations)
8. [Metadata](#metadata)
9. [Semantic Rules](#semantic-rules)
10. [Code Generation Guidelines](#code-generation-guidelines)

## Introduction

Typelang is a TypeScript-flavored schema definition language designed for cross-platform type generation. It provides a familiar syntax for defining data models that can be compiled to TypeScript, Python, JSON Schema, and other target languages.

### Design Principles
- **Familiar Syntax**: Subset of TypeScript for easy adoption
- **Platform Agnostic**: Clean separation between syntax and target semantics
- **Type Safety**: Strong typing with clear nullable/optional semantics
- **Extensible**: Metadata through JSDoc and attributes
- **Deterministic**: Stable, reproducible code generation

## Lexical Structure

### Character Set
- Unicode UTF-8 encoded source files
- Line terminators: LF (`\n`), CR (`\r`), CRLF (`\r\n`)
- Whitespace: space, tab, line terminators

### Comments
```
LineComment      ::= '//' [^\n]*
BlockComment     ::= '/*' .*? '*/'
JSDocComment     ::= '/**' .*? '*/'
```

### Identifiers
```
Identifier       ::= [a-zA-Z_$][a-zA-Z0-9_$]*
```

### Keywords
Reserved keywords that cannot be used as identifiers:
```
type any unknown never
int float string bool
list dict
readonly
true false null
```

### Literals
```
StringLiteral    ::= "'" ( [^'\\\n] | EscapeSequence )* "'"
                   | '"' ( [^"\\\n] | EscapeSequence )* '"'
NumberLiteral    ::= [0-9]+ ('.' [0-9]+)?
BooleanLiteral   ::= 'true' | 'false'
NullLiteral      ::= 'null'

EscapeSequence   ::= '\\' ['"\\nrt]
```

### Punctuation
```
{ } [ ] ( ) < >
= : ; , ? | &
. @
```

## Grammar

### EBNF Notation
```
Module           ::= Declaration*

Declaration      ::= Metadata? 'type' Identifier TypeParameters? '=' TypeExpression

TypeParameters   ::= '<' TypeParameter (',' TypeParameter)* '>'
TypeParameter    ::= Identifier ('=' TypeExpression)?

TypeExpression   ::= UnionType
UnionType        ::= IntersectionType ('|' IntersectionType)*
IntersectionType ::= PostfixType
PostfixType      ::= PrimaryType ArraySuffix*
ArraySuffix      ::= '[' ']'

PrimaryType      ::= Identifier                    # Type reference
                   | BuiltinType                    # Built-in type
                   | ObjectType                     # Inline object
                   | StringLiteral                  # String literal
                   | NumberLiteral                  # Number literal  
                   | BooleanLiteral                 # Boolean literal
                   | NullLiteral                    # Null literal
                   | GenericType                    # Generic application
                   | '(' TypeExpression ')'         # Parenthesized

BuiltinType      ::= 'int' | 'float' | 'string' | 'bool' 
                   | 'any' | 'unknown' | 'never'
                   | 'list' | 'dict'

GenericType      ::= Identifier '<' TypeArguments '>'
TypeArguments    ::= TypeExpression (',' TypeExpression)*

ObjectType       ::= '{' ObjectField* '}'
ObjectField      ::= Metadata? ReadonlyModifier? Identifier '?'? ':' TypeExpression
                     (',' | ';' | '\n')?
ReadonlyModifier ::= 'readonly'

Metadata         ::= (JSDocComment | Attribute)*
Attribute        ::= '@' AttributeKey ('(' AttributeValue ')')?
AttributeKey     ::= Identifier ('.' Identifier)*
AttributeValue   ::= StringLiteral | NumberLiteral | BooleanLiteral
```

## Type System

### Type Categories

1. **Primitive Types**: Basic scalar types
2. **Container Types**: Collections and compounds
3. **Literal Types**: Constant values
4. **Reference Types**: Named type references
5. **Union Types**: Choice between multiple types
6. **Object Types**: Structured records

### Type Equivalence

Two types are equivalent if they have the same structure after normalization:
- Type aliases are expanded
- Generic parameters are substituted
- Unions are flattened and deduplicated

## Built-in Types

### Primitive Types

| Typelang | Description | TypeScript | Python | JSON Schema |
|----------|-------------|------------|---------|-------------|
| `int` | Integer number | `number` | `int` | `{"type": "integer"}` |
| `float` | Floating point | `number` | `float` | `{"type": "number"}` |
| `string` | Text string | `string` | `str` | `{"type": "string"}` |
| `bool` | Boolean | `boolean` | `bool` | `{"type": "boolean"}` |
| `any` | Any type | `any` | `Any` | `{}` |
| `unknown` | Unknown type | `unknown` | `Any` | `{}` |
| `never` | Never type | `never` | `NoReturn` | `{"not": {}}` |

### Container Types

| Typelang | Description | TypeScript | Python | JSON Schema |
|----------|-------------|------------|---------|-------------|
| `list` | Untyped list | `any[]` | `List[Any]` | `{"type": "array"}` |
| `dict` | String-keyed dictionary | `Record<string, any>` | `Dict[str, Any]` | `{"type": "object"}` |
| `T[]` | Array of T | `T[]` | `List[T]` | `{"type": "array", "items": ...}` |
| `Dict<K, V>` | Map type | `Record<K, V>` or `Map<K, V>` | `Dict[K, V]` | varies |
| `Tuple<T...>` | Fixed tuple | `[T, ...]` | `Tuple[T, ...]` | `{"prefixItems": [...]}` |

### Special Generic Types

#### Dict<K, V>
- **Recommendation**: Use `Dict<string, V>` for maximum compatibility
- Non-string keys generate warnings in v0.1
- Maps to `Record<string, V>` in TypeScript when K is string
- Maps to object with additionalProperties in JSON Schema when K is string

#### Tuple<T1, T2, ...>
- Fixed-length tuple type
- Each position has a specific type
- No rest parameters in v0.1

## Type Expressions

### Arrays
```typelang
type Items = string[]           # Array of strings
type Matrix = int[][]           # 2D array of integers
```

### Unions
```typelang
type Status = 'pending' | 'active' | 'done'  # String literal union
type Mixed = string | int | bool             # Type union
type Nullable = string | null                # Nullable type
```

### Objects
```typelang
type User = {
  id: string                    # Required field
  name?: string                 # Optional field
  readonly age: int            # Readonly field
}
```

### Generic Types
```typelang
type Container<T> = {
  value: T
  items: T[]
}

type StringContainer = Container<string>     # Type application
```

### Type Parameters
```typelang
type Box<T = string> = {        # Default type parameter
  value: T
}
```

## Declarations

### Type Alias Declaration
```typelang
type Name = TypeExpression
```
Creates a type alias that can be referenced by name.

### Generic Type Declaration
```typelang
type Name<T, U = DefaultType> = TypeExpression
```
Declares a parameterized type with optional default values.

## Metadata

### JSDoc Comments
```typelang
/** 
 * User account information
 * @deprecated Use Account instead
 */
type User = {
  /** User's unique identifier */
  id: string
}
```

### Attributes
```typelang
@db.table("users")
@serializable
type User = {
  @db.primary
  @db.column("user_id")
  id: string
  
  @db.index
  email: string
}
```

Attributes are preserved through compilation and made available to code generators.

## Semantic Rules

### Field Modifiers

#### Optional (`?`)
- Field may be absent from the object
- In TypeScript: `field?: T`
- In Python: `Optional[T] = None`
- In JSON Schema: not in required array

#### Readonly
- Field should not be modified after initialization
- Advisory in most targets
- May affect Pydantic configuration

### Nullable vs Optional

| Pattern | Meaning | TypeScript | Python |
|---------|---------|------------|---------|
| `field: T` | Required, non-null | `field: T` | `field: T` |
| `field?: T` | Optional, non-null when present | `field?: T` | `field: Optional[T] = None` |
| `field: T \| null` | Required, nullable | `field: T \| null` | `field: Optional[T]` |
| `field?: T \| null` | Optional, nullable | `field?: T \| null` | `field: Optional[T] = None` |

### Type Resolution

1. Type parameters are resolved in the current scope
2. Type references are resolved in declaration order
3. Forward references are allowed
4. Circular references are allowed (with care in some targets)
5. Unknown type references generate errors but fall back to `any`

### String Literal Unions

When a union consists entirely of string literals, it's treated as an enum:
```typelang
type Status = 'pending' | 'active' | 'done'
```

Generates:
- TypeScript: `type Status = 'pending' | 'active' | 'done'`
- Python: `Literal['pending', 'active', 'done']`
- JSON Schema: `{"enum": ["pending", "active", "done"]}`

## Code Generation Guidelines

### General Principles

1. **Preserve Intent**: Maintain the semantic meaning across targets
2. **Idiomatic Output**: Generate natural code for each target
3. **Stable Ordering**: Fields and types in deterministic order
4. **Metadata Preservation**: Keep JSDoc and attributes where possible
5. **Error Recovery**: Generate best-effort output even with errors

### Target-Specific Mappings

#### TypeScript
- Preserve generic parameters
- Use interfaces or type aliases
- Keep readonly modifiers
- Map primitives to JS types (int/float → number)

#### Python (Dataclass)
- Use `@dataclass` decorator
- Import from `typing` module
- Generic types use `TypeVar` and `Generic`
- Forward references as string literals

#### Python (Pydantic)
- Inherit from `BaseModel`
- Use `Field()` for constraints
- Config class for additional settings
- Validation on assignment for readonly

#### JSON Schema
- Latest draft (2020-12) by default
- Monomorphize generic types
- String enums as enum constraint
- Attributes as x- extensions

### Generic Type Handling

#### Monomorphization
For targets without generics (JSON Schema), create concrete instances:
- Name pattern: `TypeName__of__ArgType`
- Or hash-based: `TypeName__g_abc123`

#### Type Parameter Preservation
For targets with generics (TypeScript, Python):
- Keep parameter declarations
- Forward type arguments correctly
- Handle variance appropriately

### Error Handling

When encountering errors, generators should:
1. Report clear error messages
2. Continue processing other types
3. Use fallback types (`any`/`Any`) for unknown references
4. Generate partial output when possible

## Examples

### Complete Example
```typelang
/** 
 * User account with profile information
 */
@api.model
type User<T = unknown> = {
  /** Unique identifier */
  @db.primary
  id: string
  
  /** User's email address */
  @validation.email
  email?: string
  
  /** Account status */
  status: 'active' | 'suspended' | 'deleted'
  
  /** User profile data */
  profile: {
    name: string
    age?: int
    tags: string[]
  }
  
  /** Additional metadata */
  metadata?: T
  
  /** Creation timestamp */
  readonly createdAt: float
}

/** User role enumeration */
type Role = 'admin' | 'user' | 'guest'

/** API Response wrapper */
type Response<T> = {
  success: bool
  data?: T
  error?: string
}
```

### Type Composition
```typelang
type Address = {
  street: string
  city: string
  country: string
}

type Person = {
  name: string
  addresses: Address[]
}

type Company = {
  name: string
  employees: Person[]
  headquarters: Address
}
```

## Version History

### v0.1 (Current)
- Initial specification
- Core type system
- Basic metadata support
- Multi-target code generation

### Future Considerations (v0.2+)
- Module system and imports
- Intersection types
- Conditional types
- Computed properties
- Numeric enums
- Rest parameters in tuples
- Type constraints on parameters