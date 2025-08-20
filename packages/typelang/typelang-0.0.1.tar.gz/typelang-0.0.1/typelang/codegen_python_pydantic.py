"""Python Pydantic code generator for Typelang."""

from typing import Dict, List, Optional, Set
from .ir_types import *


class PythonPydanticGenerator:
    """Generate Python Pydantic code from IR."""
    
    def __init__(self, program: IRProgram):
        """Initialize generator with IR program."""
        self.program = program
        self.indent = '    '
        self.current_indent = 0
        self.type_map: Dict[int, IRTypeDef] = {}
        self.imports: Set[str] = set()
        self.forward_refs: Set[str] = set()
        
        for type_def in program.types:
            self.type_map[type_def.id] = type_def
    
    def generate(self) -> str:
        """Generate Python Pydantic code."""
        lines = []
        
        # Collect imports
        self.collect_imports()
        
        # Generate imports
        import_lines = self.generate_imports()
        if import_lines:
            lines.append(import_lines)
            lines.append('')
        
        # Generate forward references
        forward_refs = self.generate_forward_refs()
        if forward_refs:
            lines.append(forward_refs)
            lines.append('')
        
        # Generate type definitions
        for type_def in self.program.types:
            generated = self.generate_type_def(type_def)
            if generated:
                lines.append(generated)
                lines.append('')
        
        return '\n'.join(lines).rstrip() + '\n'
    
    def collect_imports(self):
        """Collect necessary imports."""
        self.imports.add('from pydantic import BaseModel, Field')
        self.imports.add('from typing import Any, List, Dict, Union, Optional, Literal')
        
        # Check if we need forward refs
        for type_def in self.program.types:
            self.collect_type_imports(type_def.body)
    
    def collect_type_imports(self, type_: CoreType):
        """Collect imports for a specific type."""
        if isinstance(type_, CTList):
            pass  # List already imported
        elif isinstance(type_, CTMap):
            pass  # Dict already imported
        elif isinstance(type_, CTUnion):
            pass  # Union already imported
        elif isinstance(type_, CTStruct):
            for field in type_.fields:
                if field.type:
                    self.collect_type_imports(field.type.type)
        elif isinstance(type_, CTRef):
            if 'def_id' in type_.ref:
                type_def = self.type_map.get(type_.ref['def_id'])
                if type_def:
                    self.forward_refs.add(type_def.name)
    
    def generate_imports(self) -> str:
        """Generate import statements."""
        return '\n'.join(sorted(self.imports))
    
    def generate_forward_refs(self) -> str:
        """Generate forward reference declarations."""
        if not self.forward_refs:
            return ''
        
        lines = []
        for ref in sorted(self.forward_refs):
            lines.append(f"'{ref}' = '{ref}'")
        return '\n'.join(lines)
    
    def generate_type_def(self, def_: IRTypeDef) -> str:
        """Generate Python type definition."""
        lines = []
        
        # Add docstring if present
        if def_.doc and def_.doc.js_doc:
            lines.append(f'"""{def_.doc.js_doc}"""')
            lines.append('')
        
        # Generate type alias or Pydantic model
        if isinstance(def_.body, CTStruct):
            lines.append(self.generate_pydantic_model(def_))
        else:
            # Generate type alias
            type_params = self.generate_type_params(def_.type_params)
            body = self.generate_core_type(def_.body)
            
            if type_params:
                lines.append(f"# Generic type not fully supported in Python < 3.12")
                lines.append(f"{def_.name} = {body}")
            else:
                lines.append(f"{def_.name} = {body}")
        
        return '\n'.join(lines)
    
    def generate_pydantic_model(self, def_: IRTypeDef) -> str:
        """Generate a Pydantic model definition."""
        lines = []
        
        # Docstring
        if def_.doc and def_.doc.js_doc:
            lines.append(f'"""{def_.doc.js_doc}"""')
        
        # Class definition
        class_name = def_.name
        if def_.type_params:
            # Note: Full generic support requires Python 3.12+
            lines.append(f"class {class_name}(BaseModel):")
        else:
            lines.append(f"class {class_name}(BaseModel):")
        
        self.current_indent += 1
        
        # Generate fields
        struct = def_.body
        if struct.fields:
            for field in struct.fields:
                field_lines = self.generate_field(field)
                lines.extend(field_lines)
        else:
            lines.append(self.indent_str("pass"))
        
        # Add model config if needed
        if struct.closed:
            lines.append('')
            lines.append(self.indent_str("class Config:"))
            self.current_indent += 1
            lines.append(self.indent_str("extra = 'forbid'"))
            self.current_indent -= 1
        
        self.current_indent -= 1
        
        return '\n'.join(lines)
    
    def generate_field(self, field: IRField) -> List[str]:
        """Generate a Pydantic field."""
        lines = []
        
        # Add field docstring if present
        if field.doc and field.doc.js_doc:
            lines.append(self.indent_str(f'"""{field.doc.js_doc}"""'))
        
        # Generate field type
        field_type = self.generate_type_ref(field.type)
        
        # Handle optional fields
        if field.optional:
            field_type = f"Optional[{field_type}]"
        
        # Generate Field() with metadata
        field_kwargs = []
        
        if field.default_value is not None:
            # Handle default value
            if isinstance(field.default_value, StringLit):
                field_kwargs.append(f"default='{field.default_value.value}'")
            elif isinstance(field.default_value, NumberLit):
                field_kwargs.append(f"default={field.default_value.value}")
            elif isinstance(field.default_value, BoolLit):
                field_kwargs.append(f"default={field.default_value.value}")
            elif isinstance(field.default_value, NullLit):
                field_kwargs.append("default=None")
        elif field.optional:
            field_kwargs.append("default=None")
        
        if field.doc and field.doc.js_doc:
            field_kwargs.append(f"description='{field.doc.js_doc}'")
        
        # Generate field with Field()
        if field_kwargs:
            field_str = f"{field.name}: {field_type} = Field({', '.join(field_kwargs)})"
        else:
            field_str = f"{field.name}: {field_type}"
        
        lines.append(self.indent_str(field_str))
        
        return lines
    
    def generate_type_params(self, params: List[IRTypeParam]) -> str:
        """Generate type parameters."""
        if not params:
            return ""
        
        # Note: Full generic support requires Python 3.12+
        return ""
    
    def generate_type_ref(self, ref: TypeRef) -> str:
        """Generate type reference."""
        return self.generate_core_type(ref.type)
    
    def generate_core_type(self, type_: CoreType) -> str:
        """Generate core type."""
        if isinstance(type_, CTAny):
            return "Any"
        elif isinstance(type_, CTUnknown):
            return "Any"
        elif isinstance(type_, CTNever):
            return "Any"  # Python doesn't have Never
        elif isinstance(type_, CTPrimitive):
            return self.generate_primitive(type_)
        elif isinstance(type_, CTList):
            element = self.generate_type_ref(type_.element)
            return f"List[{element}]"
        elif isinstance(type_, CTMap):
            key = self.generate_type_ref(type_.key)
            value = self.generate_type_ref(type_.value)
            return f"Dict[{key}, {value}]"
        elif isinstance(type_, CTTuple):
            return self.generate_tuple(type_)
        elif isinstance(type_, CTUnion):
            return self.generate_union(type_)
        elif isinstance(type_, CTEnumString):
            return self.generate_enum_string(type_)
        elif isinstance(type_, CTStruct):
            # For inline structs, generate a dict type
            return "Dict[str, Any]"
        elif isinstance(type_, CTRef):
            return self.generate_ref(type_)
        elif isinstance(type_, CTNullable):
            inner = self.generate_type_ref(type_.inner)
            return f"Optional[{inner}]"
        else:
            return "Any"
    
    def generate_primitive(self, prim: CTPrimitive) -> str:
        """Generate primitive type."""
        if prim.name == 'int':
            return 'int'
        elif prim.name == 'float':
            return 'float'
        elif prim.name == 'string':
            return 'str'
        elif prim.name == 'bool':
            return 'bool'
        elif prim.name == 'bytes':
            return 'bytes'
        else:
            return 'Any'
    
    def generate_tuple(self, tuple_: CTTuple) -> str:
        """Generate tuple type."""
        if not tuple_.elements and not tuple_.rest:
            return "tuple"
        
        elements = [self.generate_type_ref(e) for e in tuple_.elements]
        
        if tuple_.rest:
            # Variable length tuple
            rest_type = self.generate_type_ref(tuple_.rest)
            return f"tuple[{', '.join(elements)}, *{rest_type}]" if elements else f"tuple[{rest_type}, ...]"
        
        return f"tuple[{', '.join(elements)}]"
    
    def generate_union(self, union: CTUnion) -> str:
        """Generate union type."""
        variants = [self.generate_type_ref(v) for v in union.variants]
        return f"Union[{', '.join(variants)}]"
    
    def generate_enum_string(self, enum: CTEnumString) -> str:
        """Generate string enum type."""
        variants = [f"Literal['{v['value']}']" for v in enum.variants]
        if len(variants) == 1:
            return variants[0]
        return f"Union[{', '.join(variants)}]"
    
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
                    # Note: Generic type application not fully supported
                    return f"'{name}'"
                
                return f"'{name}'"
        
        return 'Any'
    
    def indent_str(self, s: str) -> str:
        """Indent a string."""
        return self.indent * self.current_indent + s