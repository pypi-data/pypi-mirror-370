"""IR (Intermediate Representation) types for Typelang."""

from dataclasses import dataclass, field
from typing import Any, Optional, Union, List, Dict
from .ast_types import Doc, Attr, LiteralValue

# Type ID for referencing types
TypeId = int


@dataclass
class ResolvedRef:
    """Resolved type reference."""
    target: TypeId
    type_args: Optional[List['TypeRef']] = None


@dataclass
class IRProgram:
    """Root IR program containing all type definitions."""
    types: List['IRTypeDef'] = field(default_factory=list)


@dataclass
class IRTypeDef:
    """IR type definition."""
    id: TypeId
    name: str
    kind: str  # 'alias' or 'newtype'
    type_params: List['IRTypeParam'] = field(default_factory=list)
    body: 'CoreType' = None
    doc: Optional[Doc] = None
    attrs: Optional[List[Attr]] = None


@dataclass
class IRTypeParam:
    """IR type parameter."""
    name: str
    constraint: Optional['TypeRef'] = None
    default_type: Optional['TypeRef'] = None


@dataclass
class TypeRef:
    """Type reference wrapper."""
    type: 'CoreType'


# Core types

@dataclass
class CTAny:
    """Any type."""
    kind: str = "Any"


@dataclass
class CTUnknown:
    """Unknown type."""
    kind: str = "Unknown"


@dataclass
class CTNever:
    """Never type."""
    kind: str = "Never"


@dataclass
class CTPrimitive:
    """Primitive type."""
    kind: str = "Primitive"
    name: str = ""  # 'int', 'float', 'string', 'bool', 'bytes'


@dataclass
class CTList:
    """List type."""
    kind: str = "List"
    element: TypeRef = None


@dataclass
class CTMap:
    """Map type."""
    kind: str = "Map"
    key: TypeRef = None
    value: TypeRef = None
    string_keyed_only: bool = False


@dataclass
class CTTuple:
    """Tuple type."""
    kind: str = "Tuple"
    elements: List[TypeRef] = field(default_factory=list)
    rest: Optional[TypeRef] = None


@dataclass
class CTUnion:
    """Union type."""
    kind: str = "Union"
    variants: List[TypeRef] = field(default_factory=list)


@dataclass
class CTEnumString:
    """String enum type."""
    kind: str = "EnumString"
    variants: List[Dict[str, Any]] = field(default_factory=list)  # [{'name': str, 'value': str}]


@dataclass
class CTStruct:
    """Struct type."""
    kind: str = "Struct"
    fields: List['IRField'] = field(default_factory=list)
    closed: bool = True
    additional_props_type: Optional[TypeRef] = None


@dataclass
class IRField:
    """Struct field."""
    name: str
    type: TypeRef
    optional: bool = False
    readonly: bool = False
    default_value: Optional[LiteralValue] = None
    doc: Optional[Doc] = None
    attrs: Optional[List[Attr]] = None


@dataclass
class CTRef:
    """Type reference."""
    kind: str = "Ref"
    ref: Dict[str, Any] = field(default_factory=dict)  # {'type_param': str} or {'def_id': TypeId}
    type_args: Optional[List[TypeRef]] = None


@dataclass
class CTNullable:
    """Nullable type."""
    kind: str = "Nullable"
    inner: TypeRef = None


# Type alias for core types union
CoreType = Union[
    CTAny, CTUnknown, CTNever, CTPrimitive,
    CTList, CTMap, CTTuple, CTUnion,
    CTEnumString, CTStruct, CTRef, CTNullable
]