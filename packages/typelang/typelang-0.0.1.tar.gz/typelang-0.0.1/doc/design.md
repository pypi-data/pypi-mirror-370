# Typelang v0.1 — Syntax, AST, IR & Multitarget Codegen Design

**Status:** Draft • **Owner:** You • **Last updated:** 2025‑08‑19

---

## 1) Summary

Typelang is a small, TypeScript‑flavored typing language for defining data models that can be code‑generated into multiple targets (TypeScript, Python, JSON Schema, Java, Rust). This document specifies:

* The surface syntax (subset of TypeScript) and constraints
* The **AST** (syntax‑preserving) and **IR** (canonical, target‑agnostic)
* Transformation pipeline (Parse → Resolve → Desugar → Canonicalize → Validate → Generate)
* Codegen mapping rules per target
* Diagnostics, testing, performance, and a roadmap

---

## 2) Goals & Non‑Goals

### Goals

* **Ergonomic syntax:** close to TypeScript for familiarity.
* **Stable IR:** canonical, sugar‑free, suitable for multiple codegens.
* **Deterministic generation:** stable ordering & naming.
* **Extensibility:** annotations and constraints travel from AST to IR to generators.
* **Clarity on optional vs nullable:** consistent across targets.

### Non‑Goals (v0.1)

* Full TS features (no conditional/mapped/intersection types beyond object fields).
* Runtime validation framework (we output types/schemas; runtime validation is target‑specific).
* Cross‑module import semantics (single module/file; imports are a v0.2 topic).
* Complex enums (numeric, heterogeneous, or mixed literal unions).

---

## 3) Language Spec (Surface Syntax)

### 3.1 Declarations

* **Type alias** with optional **type parameters**:

  ```ts
  type Name<T, U = string> = { /* fields */ }
  ```
* Optional **JSDoc** docstrings and **@attrs** are allowed ahead of declarations and fields:

  ```ts
  /** user record */
  @db.table("users")
  type User = { id: string }
  ```

### 3.2 Type Expressions

Supported forms:

* **Primitives:** `int`, `float`, `string`, `bool`, `any`, `list`, `dict`
* **References:** `Name`, `T` (type parameter)
* **Arrays:** `T[]`
* **Maps:** `Dict<K, V>`
* **Tuples:** `Tuple<A, B, ...>` (optional `rest` TBD)
* **Unions:** `A | B`
* **Inline objects:** `{ field: T, other?: U }`
* **String literal unions:** `'a' | 'b' | 'c'`

> **Recommendation:** Constrain `Dict<K,V>` to `K = string` for seamless multi‑target support. v0.1 warns on non‑string keys.

### 3.3 Objects & Fields

* `field: T` — required field (key must be present)
* `field?: T` — optional field (key may be absent)
* `readonly` prefix allowed (advisory; impacts some targets’ generation)
* Default values may be annotated in comments or attrs (e.g., `@default(42)`).

### 3.4 Optional vs Nullable

* **Optional**: property may be **absent** (`x?: T`).
* **Nullable**: value may be **null** (`x: T | null`).

---

## 4) Architecture Overview

```
 .typelang source
       │
       ▼
   Parser → AST (syntax‑preserving)
       │  (spans, comments, attrs)
       ▼
   Resolver (symbols, generics)
       │
       ▼
   Desugar (arrays, dict/list, tuples, inline objs)
       │
       ▼
   Canonicalize (flatten unions, enum‑string detect)
       │
       ▼
   Validate (keys, arity, cycles, constraints)
       │
       ▼
      IR  (canonical)
       │
   ┌────┴───────────────┬───────────────┬───────────────┬───────────────┐
   ▼                    ▼               ▼               ▼               ▼
 TypeScript         Python         JSON Schema          Java            Rust
 generator          generator      generator            generator       generator
```

---

## 5) AST (Concrete Syntax)

The AST mirrors the written syntax and preserves **source spans**, **docstrings**, and **attrs** for precise diagnostics and pretty‑printing.

```ts
export interface Span { start: number; end: number; line: number; col: number }
export interface Doc { jsDoc?: string }
export interface Attr { key: string; value?: string | number | boolean }
export interface NodeBase { span?: Span; doc?: Doc; attrs?: Attr[] }

export interface Module extends NodeBase {
  kind: 'Module'
  body: TypeDecl[]
}

export interface TypeDecl extends NodeBase {
  kind: 'TypeDecl'
  name: Identifier
  typeParams?: TypeParam[]
  type: TypeExpr
  aliasKind?: 'alias' | 'newtype'
}

export interface TypeParam extends NodeBase {
  kind: 'TypeParam'
  name: Identifier
  constraint?: TypeExpr
  defaultType?: TypeExpr
}

export interface Identifier extends NodeBase { kind: 'Identifier'; name: string }

export type TypeExpr =
  | TSPrimitive | TSAny | TSUnknown | TSNever
  | TSArray | TSMap | TSTuple | TSUnion | TSObject
  | TSLiteral | TSRef | TSGenericApp | TSNullable

export interface TSPrimitive extends NodeBase {
  kind: 'TSPrimitive'
  name: 'int' | 'float' | 'string' | 'bool' | 'list' | 'dict'
}
export interface TSAny extends NodeBase { kind: 'TSAny' }
export interface TSUnknown extends NodeBase { kind: 'TSUnknown' }
export interface TSNever extends NodeBase { kind: 'TSNever' }

export interface TSArray extends NodeBase { kind: 'TSArray'; element: TypeExpr }
export interface TSMap extends NodeBase { kind: 'TSMap'; key: TypeExpr; value: TypeExpr }
export interface TSTuple extends NodeBase { kind: 'TSTuple'; elements: TypeExpr[]; rest?: TypeExpr }
export interface TSUnion extends NodeBase { kind: 'TSUnion'; variants: TypeExpr[] }

export interface TSObject extends NodeBase {
  kind: 'TSObject'
  fields: ObjectField[]
  closed?: boolean
  indexSignature?: { key: TypeExpr; value: TypeExpr }
}

export interface ObjectField extends NodeBase {
  kind: 'ObjectField'
  name: string
  type: TypeExpr
  optional?: boolean
  readonly?: boolean
  defaultValue?: LiteralValue
}

export type LiteralValue =
  | { kind: 'StringLit'; value: string }
  | { kind: 'NumLit'; value: number }
  | { kind: 'BoolLit'; value: boolean }
  | { kind: 'NullLit' }

export interface TSLiteral extends NodeBase { kind: 'TSLiteral'; value: LiteralValue }
export interface TSRef extends NodeBase { kind: 'TSRef'; name: string }
export interface TSGenericApp extends NodeBase { kind: 'TSGenericApp'; callee: TSRef; args: TypeExpr[] }
export interface TSNullable extends NodeBase { kind: 'TSNullable'; inner: TypeExpr }
```

> The AST accepts `list` and `dict` as primitives; the IR normalizes them to containers.

---

## 6) IR (Canonical Core Types)

The IR removes syntactic sugar and resolves all names. It is **target‑agnostic** and stable for codegen.

```ts
export type TypeId = number
export interface ResolvedRef { target: TypeId; typeArgs?: TypeRef[] }

export interface IRProgram { types: IRTypeDef[] }

export interface IRTypeDef {
  id: TypeId
  name: string
  kind: 'alias' | 'newtype'
  typeParams: IRTypeParam[]
  body: CoreType
  doc?: Doc
  attrs?: Attr[]
}

export interface IRTypeParam { name: string; constraint?: TypeRef; defaultType?: TypeRef }

export type CoreType =
  | CTAny | CTUnknown | CTNever
  | CTPrimitive | CTList | CTMap | CTTuple
  | CTUnion | CTEnumString | CTStruct | CTRef | CTNullable

export interface CTAny { kind: 'Any' }
export interface CTUnknown { kind: 'Unknown' }
export interface CTNever { kind: 'Never' }

export interface CTPrimitive {
  kind: 'Primitive'
  name: 'int' | 'float' | 'string' | 'bool' | 'bytes'
}

export interface CTList { kind: 'List'; element: TypeRef }

export interface CTMap {
  kind: 'Map'
  key: TypeRef
  value: TypeRef
  stringKeyedOnly?: boolean
}

export interface CTTuple { kind: 'Tuple'; elements: TypeRef[]; rest?: TypeRef }

export interface CTUnion { kind: 'Union'; variants: TypeRef[] }

export interface CTEnumString {
  kind: 'EnumString'
  variants: { name?: string; value: string }[]
}

export interface CTStruct {
  kind: 'Struct'
  fields: IRField[]
  closed: boolean
  additionalPropsType?: TypeRef
}

export interface IRField {
  name: string
  type: TypeRef
  optional: boolean
  readonly?: boolean
  defaultValue?: LiteralValue
  doc?: Doc
  attrs?: Attr[]
}

export interface CTRef { kind: 'Ref'; ref: { typeParam?: string; defId?: TypeId }; typeArgs?: TypeRef[] }
export interface CTNullable { kind: 'Nullable'; inner: TypeRef }
export interface TypeRef { type: CoreType }
```

**Why optional vs nullable?** Optional: key may be absent. Nullable: key present, value may be `null`. Targets treat these differently.

---

## 7) Transform Passes

1. **Parse → AST**

   * Tokenize and parse into AST preserving spans and docs.
   * Collect `@attrs` on declarations and fields.

2. **Resolve**

   * Build symbol table for type names and parameters.
   * Validate type argument arity and constraints.

3. **Desugar**

   * `T[]` → `CTList<T>`
   * `list` → `CTList<Any>`
   * `dict` → `CTMap<string, Any>`; set `stringKeyedOnly=true`
   * `Dict<K,V>` → `CTMap<K,V>`
   * `Tuple<A,B,...>` → `CTTuple`
   * Inline object → `CTStruct{closed:true}`
   * Index signature → `CTStruct{closed:false, additionalPropsType: ...}`

4. **Canonicalize**

   * Flatten unions; structural hash dedupe.
   * If union is all string literals → `CTEnumString`.
   * Normalize field order (lexical) for determinism.

5. **Validate**

   * Map key kind (warn on non‑string for v0.1).
   * Typeparam resolution & cycles (SCC detection).
   * Optional vs default consistency.

6. **Topo sort**

   * Order `IRTypeDef` deterministically; mark SCCs (recursive types).

7. **Codegen**

   * Targets use IR + attrs + docs. Provide exportable name maps.

---

## 8) Generics & Monomorphization

* **Keep generics in IR** via `IRTypeParam` + `CTRef` to type params.
* **TypeScript/Java/Rust**: preserve generics natively.
* **JSON Schema**: no native generics → **monomorphize** per use site or a pre‑declared set. Naming scheme:

  * `Name__of__String`, `Pair__of__String__and__Int`
  * Or hashed args: `Name__g_ab12cd` (stable hash of type args)
* **Python**: either generic `typing.Generic` or concrete monomorphized classes. v0.1: prefer concrete monomorphization for simplicity.

---

## 9) Target Mapping Rules

### 9.1 TypeScript

* `CTStruct` → `interface` (or `type`); optional fields get `?`.
* `CTEnumString` → union of string literals.
* `CTUnion` → `A | B` (consider tagged unions via `@tag("kind")`).
* `CTMap(string,V)` → `Record<string, V>`.
* `any` → `any`.

### 9.2 Python (typing + dataclasses or pydantic)

* `CTStruct` → `@dataclass` fields.
* Optional → `Optional[T] = None`.
* `CTEnumString` → `Enum` (or `Literal[...]`).
* `CTUnion` → `typing.Union`.
* `CTMap(string,V)` → `dict[str, V]`; `CTList` → `list[T]`.
* Pydantic optional: generate `BaseModel` classes when `--pydantic` flag set.

### 9.3 JSON Schema (2020‑12)

