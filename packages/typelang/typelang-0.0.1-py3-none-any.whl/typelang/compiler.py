"""Main compiler interface for Typelang."""

from typing import Optional, List
from .parser import Parser
from .transformer import Transformer
from .codegen_typescript import TypeScriptGenerator
from .codegen_python_dataclass import PythonDataclassGenerator
from .codegen_python_pydantic import PythonPydanticGenerator
from .codegen_jsonschema import JSONSchemaGenerator


class Compiler:
    """Main compiler for Typelang."""
    
    def __init__(self):
        """Initialize compiler."""
        self.errors: List[str] = []
    
    def compile(self, source: str, target: str = "typescript") -> Optional[str]:
        """Compile Typelang source to target language.
        
        Args:
            source: Typelang source code
            target: Target language (typescript, python-dataclass, python-pydantic, jsonschema)
        
        Returns:
            Generated code or None if errors occurred
        """
        try:
            # Parse source to AST
            parser = Parser(source)
            ast = parser.parse()
            
            # Transform AST to IR
            transformer = Transformer()
            ir = transformer.transform(ast)
            
            # Check for transformation errors
            transform_errors = transformer.get_errors()
            if transform_errors:
                self.errors.extend(transform_errors)
                # Continue anyway - errors are recoverable
            
            # Generate target code
            if target == "typescript":
                generator = TypeScriptGenerator(ir)
                return generator.generate()
            elif target == "python-dataclass":
                generator = PythonDataclassGenerator(ir)
                return generator.generate()
            elif target == "python-pydantic":
                generator = PythonPydanticGenerator(ir)
                return generator.generate()
            elif target == "jsonschema":
                generator = JSONSchemaGenerator(ir)
                return generator.generate()
            else:
                self.errors.append(f"Unknown target: {target}")
                return None
        
        except SyntaxError as e:
            self.errors.append(f"Syntax error: {e}")
            return None
        except Exception as e:
            self.errors.append(f"Compilation error: {e}")
            return None
    
    def get_errors(self) -> List[str]:
        """Get compilation errors."""
        return self.errors


def compile_file(input_path: str, output_path: Optional[str] = None, target: str = "typescript") -> bool:
    """Compile a Typelang file.
    
    Args:
        input_path: Path to input file
        output_path: Path to output file (optional, will derive from input if not provided)
        target: Target language
    
    Returns:
        True if successful, False otherwise
    """
    # Read input file
    try:
        with open(input_path, 'r') as f:
            source = f.read()
    except Exception as e:
        print(f"Error reading {input_path}: {e}")
        return False
    
    # Compile
    compiler = Compiler()
    result = compiler.compile(source, target)
    
    if result is None:
        print("Compilation failed:")
        for error in compiler.get_errors():
            print(f"  {error}")
        return False
    
    # Determine output path if not provided
    if output_path is None:
        import os
        base = os.path.splitext(input_path)[0]
        
        if target == "typescript":
            output_path = base + ".ts"
        elif target == "python-dataclass":
            output_path = base + "_dataclass.py"
        elif target == "python-pydantic":
            output_path = base + "_pydantic.py"
        elif target == "jsonschema":
            output_path = base + ".schema.json"
        else:
            output_path = base + ".out"
    
    # Write output file
    try:
        with open(output_path, 'w') as f:
            f.write(result)
        print(f"Successfully compiled to {output_path}")
        return True
    except Exception as e:
        print(f"Error writing {output_path}: {e}")
        return False