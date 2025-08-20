"""JSON Schema code generator for Typelang."""

import json
from typing import Dict, List, Optional, Any
from .ir_types import *


class JSONSchemaGenerator:
    """Generate JSON Schema from IR."""
    
    def __init__(self, program: IRProgram):
        """Initialize generator with IR program."""
        self.program = program
        self.type_map: Dict[int, IRTypeDef] = {}
        self.definitions: Dict[str, Any] = {}
        
        for type_def in program.types:
            self.type_map[type_def.id] = type_def
    
    def generate(self) -> str:
        """Generate JSON Schema."""
        # Generate definitions for all types
        for type_def in self.program.types:
            schema = self.generate_type_def(type_def)
            if schema:
                self.definitions[type_def.name] = schema
        
        # Create root schema
        root_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "definitions": self.definitions
        }
        
        # If there's a single type, make it the root
        if len(self.program.types) == 1:
            type_def = self.program.types[0]
            root_schema.update(self.definitions[type_def.name])
            del root_schema["definitions"]
        
        return json.dumps(root_schema, indent=2)
    
    def generate_type_def(self, def_: IRTypeDef) -> Dict[str, Any]:
        """Generate JSON Schema for a type definition."""
        schema = self.generate_core_type(def_.body)
        
        # Add title
        schema["title"] = def_.name
        
        # Add description if present
        if def_.doc and def_.doc.js_doc:
            schema["description"] = def_.doc.js_doc
        
        return schema
    
    def generate_core_type(self, type_: CoreType) -> Dict[str, Any]:
        """Generate JSON Schema for a core type."""
        if isinstance(type_, CTAny):
            return {}
        elif isinstance(type_, CTUnknown):
            return {}
        elif isinstance(type_, CTNever):
            return {"not": {}}
        elif isinstance(type_, CTPrimitive):
            return self.generate_primitive(type_)
        elif isinstance(type_, CTList):
            return self.generate_list(type_)
        elif isinstance(type_, CTMap):
            return self.generate_map(type_)
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
            return self.generate_nullable(type_)
        else:
            return {}
    
    def generate_primitive(self, prim: CTPrimitive) -> Dict[str, Any]:
        """Generate JSON Schema for a primitive type."""
        if prim.name == 'int':
            return {"type": "integer"}
        elif prim.name == 'float':
            return {"type": "number"}
        elif prim.name == 'string':
            return {"type": "string"}
        elif prim.name == 'bool':
            return {"type": "boolean"}
        elif prim.name == 'bytes':
            return {"type": "string", "contentEncoding": "base64"}
        else:
            return {}
    
    def generate_list(self, list_type: CTList) -> Dict[str, Any]:
        """Generate JSON Schema for a list type."""
        items = self.generate_type_ref(list_type.element)
        return {
            "type": "array",
            "items": items
        }
    
    def generate_map(self, map_type: CTMap) -> Dict[str, Any]:
        """Generate JSON Schema for a map type."""
        if map_type.string_keyed_only:
            # Object with string keys
            value_schema = self.generate_type_ref(map_type.value)
            return {
                "type": "object",
                "additionalProperties": value_schema
            }
        else:
            # Generic map - represent as array of key-value pairs
            key_schema = self.generate_type_ref(map_type.key)
            value_schema = self.generate_type_ref(map_type.value)
            return {
                "type": "array",
                "items": {
                    "type": "array",
                    "items": [key_schema, value_schema],
                    "minItems": 2,
                    "maxItems": 2
                }
            }
    
    def generate_tuple(self, tuple_type: CTTuple) -> Dict[str, Any]:
        """Generate JSON Schema for a tuple type."""
        items = [self.generate_type_ref(e) for e in tuple_type.elements]
        
        schema = {
            "type": "array",
            "items": items,
            "minItems": len(items),
            "maxItems": len(items)
        }
        
        if tuple_type.rest:
            # Variable length tuple
            rest_schema = self.generate_type_ref(tuple_type.rest)
            schema["items"] = items if items else rest_schema
            if items:
                schema["additionalItems"] = rest_schema
            del schema["maxItems"]
        
        return schema
    
    def generate_union(self, union: CTUnion) -> Dict[str, Any]:
        """Generate JSON Schema for a union type."""
        variants = [self.generate_type_ref(v) for v in union.variants]
        
        # Check if null is in the union
        has_null = any(
            isinstance(v.type, CTNullable) and isinstance(v.type.inner.type, CTNever)
            for v in union.variants
        )
        
        if has_null:
            # Remove null variant and add to type array
            non_null_variants = [
                self.generate_type_ref(v) for v in union.variants
                if not (isinstance(v.type, CTNullable) and isinstance(v.type.inner.type, CTNever))
            ]
            
            if len(non_null_variants) == 1:
                schema = non_null_variants[0]
                if "type" in schema:
                    if isinstance(schema["type"], list):
                        schema["type"].append("null")
                    else:
                        schema["type"] = [schema["type"], "null"]
                else:
                    return {"anyOf": non_null_variants + [{"type": "null"}]}
            else:
                return {"anyOf": non_null_variants + [{"type": "null"}]}
        
        if len(variants) == 1:
            return variants[0]
        
        return {"anyOf": variants}
    
    def generate_enum_string(self, enum: CTEnumString) -> Dict[str, Any]:
        """Generate JSON Schema for a string enum."""
        values = [v['value'] for v in enum.variants]
        
        if len(values) == 1:
            return {"type": "string", "const": values[0]}
        
        return {
            "type": "string",
            "enum": values
        }
    
    def generate_struct(self, struct: CTStruct) -> Dict[str, Any]:
        """Generate JSON Schema for a struct."""
        properties = {}
        required = []
        
        for field in struct.fields:
            field_schema = self.generate_type_ref(field.type)
            
            # Add field description
            if field.doc and field.doc.js_doc:
                field_schema["description"] = field.doc.js_doc
            
            properties[field.name] = field_schema
            
            if not field.optional:
                required.append(field.name)
        
        schema = {
            "type": "object",
            "properties": properties
        }
        
        if required:
            schema["required"] = required
        
        if struct.closed:
            schema["additionalProperties"] = False
        elif struct.additional_props_type:
            schema["additionalProperties"] = self.generate_type_ref(struct.additional_props_type)
        
        return schema
    
    def generate_ref(self, ref: CTRef) -> Dict[str, Any]:
        """Generate JSON Schema for a type reference."""
        if 'type_param' in ref.ref:
            # Type parameters not supported in JSON Schema
            return {}
        
        if 'def_id' in ref.ref:
            type_def = self.type_map.get(ref.ref['def_id'])
            if type_def:
                # Return a reference to the definition
                return {"$ref": f"#/definitions/{type_def.name}"}
        
        return {}
    
    def generate_nullable(self, nullable: CTNullable) -> Dict[str, Any]:
        """Generate JSON Schema for a nullable type."""
        # Special case: nullable of never is just null
        if isinstance(nullable.inner.type, CTNever):
            return {"type": "null"}
        
        inner_schema = self.generate_type_ref(nullable.inner)
        
        # Add null to the type
        if "type" in inner_schema:
            if isinstance(inner_schema["type"], list):
                inner_schema["type"].append("null")
            else:
                inner_schema["type"] = [inner_schema["type"], "null"]
        else:
            return {"anyOf": [inner_schema, {"type": "null"}]}
        
        return inner_schema
    
    def generate_type_ref(self, ref: TypeRef) -> Dict[str, Any]:
        """Generate JSON Schema for a type reference."""
        return self.generate_core_type(ref.type)