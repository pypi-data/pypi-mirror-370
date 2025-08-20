"""AST (Abstract Syntax Tree) types for Typelang."""

from dataclasses import dataclass, field
from typing import Any, Optional, Union, List
from enum import Enum


@dataclass
class Span:
    """Source location information."""
    start: int
    end: int
    line: int
    col: int


@dataclass
class Doc:
    """JSDoc documentation."""
    js_doc: Optional[str] = None


@dataclass
class Attr:
    """Attribute metadata."""
    key: str
    value: Optional[Union[str, int, float, bool]] = None


@dataclass
class NodeBase:
    """Base class for all AST nodes."""
    span: Optional[Span] = None
    doc: Optional[Doc] = None
    attrs: Optional[List[Attr]] = None


@dataclass
class Module(NodeBase):
    """Root module containing type declarations."""
    kind: str = "Module"
    body: List['TypeDecl'] = field(default_factory=list)


@dataclass
class TypeDecl(NodeBase):
    """Type declaration."""
    kind: str = "TypeDecl"
    name: 'Identifier' = None
    type_params: Optional[List['TypeParam']] = None
    type: 'TypeExpr' = None
    alias_kind: Optional[str] = "alias"  # 'alias' or 'newtype'


@dataclass
class TypeParam(NodeBase):
    """Type parameter for generic types."""
    kind: str = "TypeParam"
    name: 'Identifier' = None
    constraint: Optional['TypeExpr'] = None
    default_type: Optional['TypeExpr'] = None


@dataclass
class Identifier(NodeBase):
    """Identifier node."""
    kind: str = "Identifier"
    name: str = ""


# Type expressions

@dataclass
class TSPrimitive(NodeBase):
    """Primitive type."""
    kind: str = "TSPrimitive"
    name: str = ""  # 'int', 'float', 'string', 'bool', 'list', 'dict'


@dataclass
class TSAny(NodeBase):
    """Any type."""
    kind: str = "TSAny"


@dataclass
class TSUnknown(NodeBase):
    """Unknown type."""
    kind: str = "TSUnknown"


@dataclass
class TSNever(NodeBase):
    """Never type."""
    kind: str = "TSNever"


@dataclass
class TSArray(NodeBase):
    """Array type."""
    kind: str = "TSArray"
    element: 'TypeExpr' = None


@dataclass
class TSMap(NodeBase):
    """Map/Dictionary type."""
    kind: str = "TSMap"
    key: 'TypeExpr' = None
    value: 'TypeExpr' = None


@dataclass
class TSTuple(NodeBase):
    """Tuple type."""
    kind: str = "TSTuple"
    elements: List['TypeExpr'] = field(default_factory=list)
    rest: Optional['TypeExpr'] = None


@dataclass
class TSUnion(NodeBase):
    """Union type."""
    kind: str = "TSUnion"
    variants: List['TypeExpr'] = field(default_factory=list)


@dataclass
class TSObject(NodeBase):
    """Object type."""
    kind: str = "TSObject"
    fields: List['ObjectField'] = field(default_factory=list)
    closed: bool = True
    index_signature: Optional[dict] = None  # {'key': TypeExpr, 'value': TypeExpr}


@dataclass
class ObjectField(NodeBase):
    """Object field."""
    kind: str = "ObjectField"
    name: str = ""
    type: 'TypeExpr' = None
    optional: bool = False
    readonly: bool = False
    default_value: Optional['LiteralValue'] = None


@dataclass
class TSLiteral(NodeBase):
    """Literal type."""
    kind: str = "TSLiteral"
    value: 'LiteralValue' = None


@dataclass
class TSRef(NodeBase):
    """Type reference."""
    kind: str = "TSRef"
    name: str = ""


@dataclass
class TSGenericApp(NodeBase):
    """Generic type application."""
    kind: str = "TSGenericApp"
    callee: TSRef = None
    args: List['TypeExpr'] = field(default_factory=list)


@dataclass
class TSNullable(NodeBase):
    """Nullable type."""
    kind: str = "TSNullable"
    inner: 'TypeExpr' = None


# Literal values

@dataclass
class StringLit:
    """String literal value."""
    kind: str = "StringLit"
    value: str = ""


@dataclass
class NumLit:
    """Number literal value."""
    kind: str = "NumLit"
    value: float = 0


@dataclass
class BoolLit:
    """Boolean literal value."""
    kind: str = "BoolLit"
    value: bool = False


@dataclass
class NullLit:
    """Null literal value."""
    kind: str = "NullLit"


# Type aliases for unions
TypeExpr = Union[
    TSPrimitive, TSAny, TSUnknown, TSNever,
    TSArray, TSMap, TSTuple, TSUnion, TSObject,
    TSLiteral, TSRef, TSGenericApp, TSNullable
]

LiteralValue = Union[StringLit, NumLit, BoolLit, NullLit]