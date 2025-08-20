"""CLI entry point for Typelang compiler."""

import argparse
import sys
import json
from .compiler import Compiler


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        prog='typelang',
        description='Typelang compiler - compile schema definitions to various target languages',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''Examples:
  typelang schema.tl -o types.ts
  typelang schema.tl -t py-pydantic -o models.py
  typelang schema.tl -t jsonschema
  typelang schema.tl -t ir -o schema.ir.json'''
    )
    
    parser.add_argument(
        'input',
        help='Input Typelang file (.tl or .md)'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output file path (optional, defaults to stdout)'
    )
    
    parser.add_argument(
        '-t', '--target',
        default='ts',
        help='Target format (default: ts). Available: ts, py-dataclass, py-pydantic, jsonschema, ir'
    )
    
    args = parser.parse_args()
    
    # Map target aliases
    target_map = {
        'ts': 'typescript',
        'typescript': 'typescript',
        'py-dataclass': 'python-dataclass',
        'python-dataclass': 'python-dataclass',
        'py-pydantic': 'python-pydantic',
        'python-pydantic': 'python-pydantic',
        'jsonschema': 'jsonschema',
        'json-schema': 'jsonschema',
        'ir': 'ir'
    }
    
    target = target_map.get(args.target, args.target)
    
    if target not in target_map.values():
        print(f"Error: Unknown target '{args.target}'")
        print("Available targets: ts, py-dataclass, py-pydantic, jsonschema, ir")
        sys.exit(1)
    
    # Read input file
    try:
        with open(args.input, 'r') as f:
            source = f.read()
    except Exception as e:
        print(f"Error reading {args.input}: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Extract code from markdown if needed
    if args.input.endswith('.md'):
        import re
        match = re.search(r'```(?:ts|typescript)?\n([\s\S]*?)```', source)
        if match:
            source = match.group(1)
    
    # Compile
    compiler = Compiler()
    
    if target == 'ir':
        # Generate IR directly
        from .parser import Parser
        from .transformer import Transformer
        
        try:
            parser = Parser(source)
            ast = parser.parse()
            transformer = Transformer()
            ir = transformer.transform(ast)
            
            # Convert IR to JSON-serializable format
            result = json.dumps(ir, default=lambda o: o.__dict__, indent=2)
        except Exception as e:
            print(f"Compilation error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        result = compiler.compile(source, target)
        
        if result is None:
            print("Compilation failed:", file=sys.stderr)
            for error in compiler.get_errors():
                print(f"  {error}", file=sys.stderr)
            sys.exit(1)
    
    # Output result
    if args.output:
        # Determine extension if not present
        import os
        if not os.path.splitext(args.output)[1]:
            ext_map = {
                'typescript': '.ts',
                'python-dataclass': '.py',
                'python-pydantic': '.py',
                'jsonschema': '.json',
                'ir': '.json'
            }
            args.output += ext_map.get(target, '')
        
        try:
            with open(args.output, 'w') as f:
                f.write(result)
            print(f"Successfully compiled to {args.output}", file=sys.stderr)
        except Exception as e:
            print(f"Error writing {args.output}: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Output to stdout
        print(result)


if __name__ == '__main__':
    main()