"""TypeScript code generator for Typelang."""

import json
from typing import Dict, List, Optional
from .ir_types import *


class TypeScriptGenerator:
    """Generate TypeScript code from IR."""
    
    def __init__(self, program: IRProgram):
        """Initialize generator with IR program."""
        self.program = program
        self.indent = '  '
        self.current_indent = 0
        self.type_map: Dict[int, IRTypeDef] = {}
        
        for type_def in program.types:
            self.type_map[type_def.id] = type_def
    
    def generate(self) -> str:
        """Generate TypeScript code."""
        lines = []
        
        for type_def in self.program.types:
            generated = self.generate_type_def(type_def)
            if generated:
                lines.append(generated)
        
        return '\n\n'.join(lines)
    
    def generate_type_def(self, def_: IRTypeDef) -> str:
        """Generate TypeScript type definition."""
        lines = []
        
        # Add JSDoc if present
        if def_.doc and def_.doc.js_doc:
            lines.append(f"/** {def_.doc.js_doc} */")
        
        # Add attributes as comments
        if def_.attrs:
            for attr in def_.attrs:
                value = f"({json.dumps(attr.value)})" if attr.value is not None else ""
                lines.append(f"// @{attr.key}{value}")
        
        # Generate type declaration
        type_params = self.generate_type_params(def_.type_params)
        body = self.generate_core_type(def_.body)
        
        keyword = "type" if def_.kind == "newtype" else "export type"
        lines.append(f"{keyword} {def_.name}{type_params} = {body}")
        
        return '\n'.join(lines)
    
    def generate_type_params(self, params: List[IRTypeParam]) -> str:
        """Generate type parameters."""
        if not params:
            return ""
        
        param_strs = []
        for p in params:
            s = p.name
            if p.constraint:
                s += f" extends {self.generate_type_ref(p.constraint)}"
            if p.default_type:
                s += f" = {self.generate_type_ref(p.default_type)}"
            param_strs.append(s)
        
        return f"<{', '.join(param_strs)}>"
    
    def generate_type_ref(self, ref: TypeRef) -> str:
        """Generate type reference."""
        return self.generate_core_type(ref.type)
    
    def generate_core_type(self, type_: CoreType) -> str:
        """Generate core type."""
        if isinstance(type_, CTAny):
            return "any"
        elif isinstance(type_, CTUnknown):
            return "unknown"
        elif isinstance(type_, CTNever):
            return "never"
        elif isinstance(type_, CTPrimitive):
            return self.generate_primitive(type_)
        elif isinstance(type_, CTList):
            return f"{self.generate_type_ref(type_.element)}[]"
        elif isinstance(type_, CTMap):
            if type_.string_keyed_only:
                return f"Record<string, {self.generate_type_ref(type_.value)}>"
            # For non-string keys, use Map
            return f"Map<{self.generate_type_ref(type_.key)}, {self.generate_type_ref(type_.value)}>"
        elif isinstance(type_, CTTuple):
            return self.generate_tuple(type_)
        elif isinstance(type_, CTUnion):
            return self.generate_union(type_)
        elif isinstance(type_, CTEnumString):
            return self.generate_enum_string(type_)
        elif isinstance(type_, CTStruct):
            return self.generate_struct(type_)
        elif isinstance(type_, CTRef):
            return self.generate_ref(type_)
        elif isinstance(type_, CTNullable):
            # Special case: nullable of never is just null
            if type_.inner.type.kind == "Never":
                return "null"
            return f"{self.generate_type_ref(type_.inner)} | null"
        else:
            return "unknown"
    
    def generate_primitive(self, prim: CTPrimitive) -> str:
        """Generate primitive type."""
        if prim.name in ('int', 'float'):
            return 'number'
        elif prim.name == 'string':
            return 'string'
        elif prim.name == 'bool':
            return 'boolean'
        elif prim.name == 'bytes':
            return 'Uint8Array'
        else:
            return 'unknown'
    
    def generate_tuple(self, tuple_: CTTuple) -> str:
        """Generate tuple type."""
        elements = [self.generate_type_ref(e) for e in tuple_.elements]
        
        if tuple_.rest:
            elements.append(f"...{self.generate_type_ref(tuple_.rest)}[]")
        
        return f"[{', '.join(elements)}]"
    
    def generate_union(self, union: CTUnion) -> str:
        """Generate union type."""
        variants = [self.generate_type_ref(v) for v in union.variants]
        return ' | '.join(variants)
    
    def generate_enum_string(self, enum: CTEnumString) -> str:
        """Generate string enum type."""
        variants = [f"'{v['value']}'" for v in enum.variants]
        return ' | '.join(variants)
    
    def generate_struct(self, struct: CTStruct) -> str:
        """Generate struct type."""
        lines = ['{']
        self.current_indent += 1
        
        for field in struct.fields:
            field_lines = []
            
            # Add field JSDoc
            if field.doc and field.doc.js_doc:
                field_lines.append(self.indent_str(f"/** {field.doc.js_doc} */"))
            
            # Add field attributes as comments
            if field.attrs:
                for attr in field.attrs:
                    value = f"({json.dumps(attr.value)})" if attr.value is not None else ""
                    field_lines.append(self.indent_str(f"// @{attr.key}{value}"))
            
            # Generate field
            readonly = "readonly " if field.readonly else ""
            optional = "?" if field.optional else ""
            field_type = self.generate_type_ref(field.type)
            field_lines.append(self.indent_str(f"{readonly}{field.name}{optional}: {field_type}"))
            
            lines.extend(field_lines)
        
        # Handle additional properties
        if not struct.closed and struct.additional_props_type:
            lines.append(self.indent_str(f"[key: string]: {self.generate_type_ref(struct.additional_props_type)}"))
        
        self.current_indent -= 1
        lines.append('}')
        
        return '\n'.join(lines)
    
    def generate_ref(self, ref: CTRef) -> str:
        """Generate type reference."""
        if 'type_param' in ref.ref:
            return ref.ref['type_param']
        
        if 'def_id' in ref.ref:
            type_def = self.type_map.get(ref.ref['def_id'])
            if type_def:
                name = type_def.name
                
                # Add type arguments if present
                if ref.type_args:
                    args = [self.generate_type_ref(a) for a in ref.type_args]
                    name += f"<{', '.join(args)}>"
                
                return name
        
        return 'unknown'
    
    def indent_str(self, s: str) -> str:
        """Indent a string."""
        return self.indent * self.current_indent + s