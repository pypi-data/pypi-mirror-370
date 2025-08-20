"""Transformer from AST to IR for Typelang."""

from typing import Dict, Set, List, Optional, Any
from dataclasses import dataclass
from .ast_types import *
from .ir_types import *


@dataclass
class Context:
    """Transformation context."""
    type_id_counter: int = 0
    type_map: Dict[str, IRTypeDef] = None
    type_params: Set[str] = None
    errors: List[str] = None
    
    def __post_init__(self):
        if self.type_map is None:
            self.type_map = {}
        if self.type_params is None:
            self.type_params = set()
        if self.errors is None:
            self.errors = []


class Transformer:
    """Transform AST to IR."""
    
    def __init__(self):
        """Initialize transformer."""
        self.context = Context()
    
    def transform(self, ast: Module) -> IRProgram:
        """Transform AST module to IR program."""
        # First pass: collect all type declarations
        for decl in ast.body:
            self.collect_type_decl(decl)
        
        # Second pass: transform type bodies
        types = []
        for decl in ast.body:
            ir_type = self.transform_type_decl(decl)
            if ir_type:
                types.append(ir_type)

        return IRProgram(types=types)
    
    def collect_type_decl(self, decl: TypeDecl):
        """Collect type declaration in first pass."""
        type_id = self.context.type_id_counter
        self.context.type_id_counter += 1
        
        ir_type = IRTypeDef(
            id=type_id,
            name=decl.name.name,
            kind=decl.alias_kind or 'alias',
            type_params=[],
            body=CTAny(),  # Placeholder
            doc=decl.doc,
            attrs=decl.attrs
        )
        self.context.type_map[decl.name.name] = ir_type
    
    def transform_type_decl(self, decl: TypeDecl) -> Optional[IRTypeDef]:
        """Transform type declaration."""
        existing = self.context.type_map.get(decl.name.name)
        if not existing:
            return None
        
        # Set up type parameters in context
        old_type_params = set(self.context.type_params)
        if decl.type_params:
            for param in decl.type_params:
                self.context.type_params.add(param.name.name)
        
        # Transform type parameters
        existing.type_params = [self.transform_type_param(p) for p in (decl.type_params or [])]
        
        # Transform body
        body = self.transform_type_expr(decl.type)
        if body:
            existing.body = body.type
        
        # Restore type parameters context
        self.context.type_params = old_type_params
        
        return existing
    
    def transform_type_param(self, param: TypeParam) -> IRTypeParam:
        """Transform type parameter."""
        return IRTypeParam(
            name=param.name.name,
            constraint=self.transform_type_expr(param.constraint) if param.constraint else None,
            default_type=self.transform_type_expr(param.default_type) if param.default_type else None
        )
    
    def transform_type_expr(self, expr: TypeExpr) -> Optional[TypeRef]:
        """Transform type expression."""
        if not expr:
            return None
        core_type = self.desugar_and_transform(expr)
        return TypeRef(type=core_type) if core_type else None
    
    def desugar_and_transform(self, expr: TypeExpr) -> Optional[CoreType]:
        """Desugar and transform type expression."""
        if isinstance(expr, TSPrimitive):
            return self.transform_primitive(expr)
        elif isinstance(expr, TSAny):
            return CTAny()
        elif isinstance(expr, TSUnknown):
            return CTUnknown()
        elif isinstance(expr, TSNever):
            return CTNever()
        elif isinstance(expr, TSArray):
            return self.transform_array(expr)
        elif isinstance(expr, TSMap):
            return self.transform_map(expr)
        elif isinstance(expr, TSTuple):
            return self.transform_tuple(expr)
        elif isinstance(expr, TSUnion):
            return self.transform_union(expr)
        elif isinstance(expr, TSObject):
            return self.transform_object(expr)
        elif isinstance(expr, TSLiteral):
            return self.transform_literal(expr)
        elif isinstance(expr, TSRef):
            return self.transform_ref(expr)
        elif isinstance(expr, TSGenericApp):
            return self.transform_generic_app(expr)
        elif isinstance(expr, TSNullable):
            return self.transform_nullable(expr)
        else:
            self.context.errors.append(f"Unknown type expression kind: {type(expr).__name__}")
            return None
    
    def transform_primitive(self, prim: TSPrimitive) -> CoreType:
        """Transform primitive type."""
        # Desugar list and dict
        if prim.name == 'list':
            return CTList(element=TypeRef(type=CTAny()))
        
        if prim.name == 'dict':
            return CTMap(
                key=TypeRef(type=CTPrimitive(name='string')),
                value=TypeRef(type=CTAny()),
                string_keyed_only=True
            )
        
        # Regular primitives
        if prim.name in ('int', 'float', 'string', 'bool'):
            return CTPrimitive(name=prim.name)
        
        return CTAny()
    
    def transform_array(self, arr: TSArray) -> CTList:
        """Transform array type."""
        element = self.transform_type_expr(arr.element)
        return CTList(element=element or TypeRef(type=CTAny()))
    
    def transform_map(self, map_type: TSMap) -> CTMap:
        """Transform map type."""
        key = self.transform_type_expr(map_type.key)
        value = self.transform_type_expr(map_type.value)
        
        # Check if key is string
        is_string_key = (key and key.type.kind == 'Primitive' and 
                        key.type.name == 'string')
        
        return CTMap(
            key=key or TypeRef(type=CTAny()),
            value=value or TypeRef(type=CTAny()),
            string_keyed_only=is_string_key
        )
    
    def transform_tuple(self, tuple_type: TSTuple) -> CTTuple:
        """Transform tuple type."""
        elements = [self.transform_type_expr(e) for e in tuple_type.elements]
        elements = [e for e in elements if e is not None]
        rest = self.transform_type_expr(tuple_type.rest) if tuple_type.rest else None
        
        return CTTuple(elements=elements, rest=rest)
    
    def transform_union(self, union: TSUnion) -> CoreType:
        """Transform union type."""
        variants = [self.transform_type_expr(v) for v in union.variants]
        variants = [v for v in variants if v is not None]
        
        # Check if all variants are string literals for enum detection
        all_string_literals = all(
            isinstance(v, TSLiteral) and isinstance(v.value, StringLit)
            for v in union.variants
        )
        
        if all_string_literals:
            string_variants = []
            for v in union.variants:
                if isinstance(v, TSLiteral) and isinstance(v.value, StringLit):
                    string_variants.append({'value': v.value.value})
            
            return CTEnumString(variants=string_variants)
        
        return CTUnion(variants=variants)
    
    def transform_object(self, obj: TSObject) -> CTStruct:
        """Transform object type."""
        fields = [self.transform_field(f) for f in obj.fields]
        
        return CTStruct(
            fields=fields,
            closed=obj.closed,
            additional_props_type=(
                self.transform_type_expr(obj.index_signature['value'])
                if obj.index_signature else None
            )
        )
    
    def transform_field(self, field: ObjectField) -> IRField:
        """Transform object field."""
        type_ref = self.transform_type_expr(field.type)
        
        return IRField(
            name=field.name,
            type=type_ref or TypeRef(type=CTAny()),
            optional=field.optional,
            readonly=field.readonly,
            default_value=field.default_value,
            doc=field.doc,
            attrs=field.attrs
        )
    
    def transform_literal(self, lit: TSLiteral) -> CoreType:
        """Transform literal type."""
        if isinstance(lit.value, StringLit):
            return CTEnumString(variants=[{'value': lit.value.value}])
        
        # Handle null literal
        if isinstance(lit.value, NullLit):
            return CTNullable(inner=TypeRef(type=CTNever()))
        
        # For other literals
        return CTAny()
    
    def transform_ref(self, ref: TSRef) -> CoreType:
        """Transform type reference."""
        # Check if it's a type parameter
        if ref.name in self.context.type_params:
            return CTRef(ref={'type_param': ref.name})
        
        # Check if it's a known type
        type_def = self.context.type_map.get(ref.name)
        if type_def:
            return CTRef(ref={'def_id': type_def.id})
        
        # Handle special built-in types
        if ref.name in ('Dict', 'Tuple'):
            # These should be handled via generic application
            return CTAny()
        
        self.context.errors.append(f"Unknown type reference: {ref.name}")
        return CTAny()
    
    def transform_generic_app(self, app: TSGenericApp) -> CoreType:
        """Transform generic type application."""
        callee_name = app.callee.name
        
        # Handle built-in generic types
        if callee_name == 'Dict':
            if len(app.args) != 2:
                self.context.errors.append(f"Dict requires exactly 2 type arguments")
                return CTAny()
            
            key = self.transform_type_expr(app.args[0])
            value = self.transform_type_expr(app.args[1])
            
            # Warn if key is not string
            if key and key.type.kind == 'Primitive' and key.type.name != 'string':
                self.context.errors.append(f"Warning: Dict key type should be string for v0.1")
            
            return CTMap(
                key=key or TypeRef(type=CTPrimitive(name='string')),
                value=value or TypeRef(type=CTAny()),
                string_keyed_only=True
            )
        
        if callee_name == 'Tuple':
            elements = [self.transform_type_expr(a) for a in app.args]
            elements = [e for e in elements if e is not None]
            return CTTuple(elements=elements)
        
        # Handle user-defined generic types
        type_def = self.context.type_map.get(callee_name)
        if type_def:
            type_args = [self.transform_type_expr(a) for a in app.args]
            type_args = [a for a in type_args if a is not None]
            return CTRef(ref={'def_id': type_def.id}, type_args=type_args)
        
        self.context.errors.append(f"Unknown generic type: {callee_name}")
        return CTAny()
    
    def transform_nullable(self, nullable: TSNullable) -> CTNullable:
        """Transform nullable type."""
        inner = self.transform_type_expr(nullable.inner)
        return CTNullable(inner=inner or TypeRef(type=CTAny()))
    
    def get_errors(self) -> List[str]:
        """Get transformation errors."""
        return self.context.errors