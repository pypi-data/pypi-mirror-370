"""Parser for Typelang."""

import json
from typing import List, Optional, Any
from .lexer import Lexer, TokenType, Token
from .ast_types import *


class Parser:
    """Parser for Typelang source code."""
    
    def __init__(self, input_text: str):
        """Initialize parser with input text."""
        lexer = Lexer(input_text)
        self.tokens = lexer.lex()
        self.current = 0
        self.current_jsdoc = None
        self.current_attrs = []
    
    def peek(self) -> Token:
        """Peek at current token."""
        if self.current < len(self.tokens):
            return self.tokens[self.current]
        return self.tokens[-1]  # Return EOF token
    
    def peek_type(self) -> TokenType:
        """Peek at current token type."""
        return self.peek().type
    
    def advance(self) -> Token:
        """Advance to next token and return current."""
        token = self.peek()
        if self.current < len(self.tokens) - 1:
            self.current += 1
        return token
    
    def consume(self, expected_type: TokenType, message: str = None) -> Token:
        """Consume a token of expected type."""
        token = self.peek()
        if token.type != expected_type:
            msg = message or f"Expected {expected_type} but got {token.type} at line {token.span.line}"
            raise SyntaxError(msg)
        return self.advance()
    
    def skip_newlines(self):
        """Skip newline tokens."""
        while self.peek_type() == TokenType.NEWLINE:
            self.advance()
    
    def collect_comments_and_attrs(self):
        """Collect JSDoc comments and attributes."""
        self.current_jsdoc = None
        self.current_attrs = []
        
        while True:
            self.skip_newlines()
            
            if self.peek_type() == TokenType.JSDOC:
                self.current_jsdoc = self.advance().value
            elif self.peek_type() == TokenType.COMMENT:
                self.advance()  # Skip regular comments
            elif self.peek_type() == TokenType.AT:
                attr_token = self.advance()
                attr = json.loads(attr_token.value)
                self.current_attrs.append(Attr(key=attr['key'], value=attr.get('value')))
            else:
                break
    
    def parse_identifier(self) -> Identifier:
        """Parse an identifier."""
        token = self.consume(TokenType.IDENTIFIER)
        return Identifier(name=token.value, span=token.span)
    
    def parse_primitive_type(self) -> Optional[TypeExpr]:
        """Parse a primitive type."""
        token = self.peek()
        
        primitive_map = {
            TokenType.INT: 'int',
            TokenType.FLOAT: 'float',
            TokenType.STRING: 'string',
            TokenType.BOOL: 'bool',
            TokenType.LIST: 'list',
            TokenType.DICT: 'dict',
        }
        
        if token.type in primitive_map:
            self.advance()
            return TSPrimitive(name=primitive_map[token.type], span=token.span)
        
        if token.type == TokenType.ANY:
            self.advance()
            return TSAny(span=token.span)
        
        if token.type == TokenType.UNKNOWN:
            self.advance()
            return TSUnknown(span=token.span)
        
        if token.type == TokenType.NEVER:
            self.advance()
            return TSNever(span=token.span)
        
        return None
    
    def parse_string_literal(self) -> TSLiteral:
        """Parse a string literal."""
        token = self.consume(TokenType.STRING_LITERAL)
        return TSLiteral(
            value=StringLit(value=token.value),
            span=token.span
        )
    
    def parse_object_field(self) -> ObjectField:
        """Parse an object field."""
        # Collect field-level comments and attrs
        field_jsdoc = self.current_jsdoc
        field_attrs = list(self.current_attrs)
        self.current_jsdoc = None
        self.current_attrs = []
        
        readonly = False
        if self.peek_type() == TokenType.READONLY:
            self.advance()
            readonly = True
        
        name_token = self.consume(TokenType.IDENTIFIER)
        
        optional = False
        if self.peek_type() == TokenType.QUESTION:
            self.advance()
            optional = True
        
        self.consume(TokenType.COLON)
        type_expr = self.parse_type_expr()
        
        return ObjectField(
            name=name_token.value,
            type=type_expr,
            optional=optional,
            readonly=readonly,
            span=name_token.span,
            doc=Doc(js_doc=field_jsdoc) if field_jsdoc else None,
            attrs=field_attrs if field_attrs else None
        )
    
    def parse_object_type(self) -> TSObject:
        """Parse an object type."""
        start_token = self.consume(TokenType.LEFT_BRACE)
        self.skip_newlines()
        
        fields = []
        
        while self.peek_type() not in (TokenType.RIGHT_BRACE, TokenType.EOF):
            # Collect comments/attrs for this field
            self.collect_comments_and_attrs()
            
            # Check again after collecting comments
            if self.peek_type() in (TokenType.RIGHT_BRACE, TokenType.EOF):
                break
            
            # Skip regular comments
            if self.peek_type() == TokenType.COMMENT:
                self.advance()
                self.skip_newlines()
                continue
            
            fields.append(self.parse_object_field())
            
            self.skip_newlines()
            
            if self.peek_type() in (TokenType.COMMA, TokenType.SEMICOLON):
                self.advance()
                self.skip_newlines()
            elif self.peek_type() == TokenType.NEWLINE:
                self.skip_newlines()
        
        end_token = self.consume(TokenType.RIGHT_BRACE)
        
        return TSObject(
            fields=fields,
            closed=True,
            span=Span(
                start=start_token.span.start,
                end=end_token.span.end,
                line=start_token.span.line,
                col=start_token.span.col
            )
        )
    
    def parse_type_args(self) -> List[TypeExpr]:
        """Parse type arguments."""
        args = []
        
        self.consume(TokenType.LESS_THAN)
        self.skip_newlines()
        
        if self.peek_type() != TokenType.GREATER_THAN:
            args.append(self.parse_type_expr())
            
            while self.peek_type() == TokenType.COMMA:
                self.advance()
                self.skip_newlines()
                args.append(self.parse_type_expr())
        
        self.consume(TokenType.GREATER_THAN)
        
        return args
    
    def parse_primary_type(self) -> TypeExpr:
        """Parse a primary type expression."""
        # Check for primitives first
        primitive = self.parse_primitive_type()
        if primitive:
            return primitive
        
        # String literals
        if self.peek_type() == TokenType.STRING_LITERAL:
            return self.parse_string_literal()
        
        # Null literal
        if self.peek_type() == TokenType.NULL:
            token = self.advance()
            return TSLiteral(value=NullLit(), span=token.span)
        
        # Object types
        if self.peek_type() == TokenType.LEFT_BRACE:
            return self.parse_object_type()
        
        # Type references and generic applications
        if self.peek_type() == TokenType.IDENTIFIER:
            name_token = self.advance()
            ref = TSRef(name=name_token.value, span=name_token.span)
            
            # Check for generic type application
            if self.peek_type() == TokenType.LESS_THAN:
                args = self.parse_type_args()
                return TSGenericApp(callee=ref, args=args, span=ref.span)
            
            return ref
        
        # Parenthesized types
        if self.peek_type() == TokenType.LEFT_PAREN:
            self.advance()
            type_expr = self.parse_type_expr()
            self.consume(TokenType.RIGHT_PAREN)
            return type_expr
        
        raise SyntaxError(f"Unexpected token {self.peek().type} at line {self.peek().span.line}")
    
    def parse_postfix_type(self) -> TypeExpr:
        """Parse a postfix type (with array suffix)."""
        type_expr = self.parse_primary_type()
        
        # Handle array types
        while self.peek_type() == TokenType.LEFT_BRACKET:
            self.advance()
            self.consume(TokenType.RIGHT_BRACKET)
            type_expr = TSArray(element=type_expr, span=type_expr.span)
        
        return type_expr
    
    def parse_type_expr(self) -> TypeExpr:
        """Parse a type expression (including unions)."""
        types = [self.parse_postfix_type()]
        
        # Handle union types
        while self.peek_type() == TokenType.PIPE:
            self.advance()
            self.skip_newlines()
            types.append(self.parse_postfix_type())
        
        if len(types) == 1:
            return types[0]
        
        return TSUnion(variants=types, span=types[0].span)
    
    def parse_type_param(self) -> TypeParam:
        """Parse a type parameter."""
        name = self.parse_identifier()
        
        constraint = None
        default_type = None
        
        # Parse default type with =
        if self.peek_type() == TokenType.EQUALS:
            self.advance()
            default_type = self.parse_type_expr()
        
        return TypeParam(
            name=name,
            constraint=constraint,
            default_type=default_type,
            span=name.span
        )
    
    def parse_type_params(self) -> Optional[List[TypeParam]]:
        """Parse type parameters."""
        if self.peek_type() != TokenType.LESS_THAN:
            return None
        
        params = []
        
        self.advance()  # consume <
        self.skip_newlines()
        
        if self.peek_type() != TokenType.GREATER_THAN:
            params.append(self.parse_type_param())
            
            while self.peek_type() == TokenType.COMMA:
                self.advance()
                self.skip_newlines()
                params.append(self.parse_type_param())
        
        self.consume(TokenType.GREATER_THAN)
        
        return params
    
    def parse_type_decl(self) -> TypeDecl:
        """Parse a type declaration."""
        # Store the comments/attrs that were collected before this decl
        decl_jsdoc = self.current_jsdoc
        decl_attrs = list(self.current_attrs)
        self.current_jsdoc = None
        self.current_attrs = []
        
        type_token = self.consume(TokenType.TYPE)
        self.skip_newlines()
        
        name = self.parse_identifier()
        type_params = self.parse_type_params()
        
        self.skip_newlines()
        self.consume(TokenType.EQUALS)
        self.skip_newlines()
        
        type_expr = self.parse_type_expr()
        
        return TypeDecl(
            name=name,
            type_params=type_params,
            type=type_expr,
            alias_kind='alias',
            span=Span(
                start=type_token.span.start,
                end=type_expr.span.end if type_expr.span else type_token.span.end,
                line=type_token.span.line,
                col=type_token.span.col
            ),
            doc=Doc(js_doc=decl_jsdoc) if decl_jsdoc else None,
            attrs=decl_attrs if decl_attrs else None
        )
    
    def parse(self) -> Module:
        """Parse the input and return AST module."""
        body = []
        
        while self.peek_type() != TokenType.EOF:
            self.skip_newlines()
            
            if self.peek_type() == TokenType.EOF:
                break
            
            # Collect any leading comments/attrs
            self.collect_comments_and_attrs()
            
            # Check if we have a type declaration
            if self.peek_type() == TokenType.TYPE:
                body.append(self.parse_type_decl())
            elif self.peek_type() != TokenType.EOF:
                # Skip any remaining standalone comments
                if self.peek_type() in (TokenType.COMMENT, TokenType.JSDOC):
                    self.advance()
                elif self.peek_type() != TokenType.EOF:
                    raise SyntaxError(f"Unexpected token {self.peek().type} at line {self.peek().span.line}")
            
            self.skip_newlines()
        
        return Module(body=body)