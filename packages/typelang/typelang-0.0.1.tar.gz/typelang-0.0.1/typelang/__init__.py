"""Typelang - A TypeScript-flavored schema definition language."""

from .compiler import Compiler, compile_file
from .parser import Parser
from .transformer import Transformer
from .codegen_typescript import TypeScriptGenerator
from .codegen_python_dataclass import PythonDataclassGenerator
from .codegen_python_pydantic import PythonPydanticGenerator
from .codegen_jsonschema import JSONSchemaGenerator

__version__ = "0.1.0"

__all__ = [
    "Compiler",
    "compile_file",
    "Parser",
    "Transformer",
    "TypeScriptGenerator",
    "PythonDataclassGenerator",
    "PythonPydanticGenerator",
    "JSONSchemaGenerator",
]
