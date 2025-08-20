"""Lexer for Typelang."""

import re
from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional, Any
import json

from .ast_types import Span


class TokenType(Enum):
    """Token types for Typelang."""
    # Literals
    IDENTIFIER = auto()
    STRING_LITERAL = auto()
    NUMBER_LITERAL = auto()
    
    # Keywords
    TYPE = auto()
    INT = auto()
    FLOAT = auto()
    STRING = auto()
    BOOL = auto()
    LIST = auto()
    DICT = auto()
    ANY = auto()
    UNKNOWN = auto()
    NEVER = auto()
    READONLY = auto()
    TRUE = auto()
    FALSE = auto()
    NULL = auto()
    
    # Symbols
    LEFT_BRACE = auto()
    RIGHT_BRACE = auto()
    LEFT_BRACKET = auto()
    RIGHT_BRACKET = auto()
    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()
    LESS_THAN = auto()
    GREATER_THAN = auto()
    EQUALS = auto()
    COLON = auto()
    SEMICOLON = auto()
    COMMA = auto()
    QUESTION = auto()
    PIPE = auto()
    AMPERSAND = auto()
    AT = auto()
    DOT = auto()
    
    # Comments
    COMMENT = auto()
    JSDOC = auto()
    
    # Special
    EOF = auto()
    NEWLINE = auto()


@dataclass
class Token:
    """Token with type, value, and location."""
    type: TokenType
    value: str
    span: Span


class Lexer:
    """Lexer for Typelang source code."""
    
    KEYWORDS = {
        'type': TokenType.TYPE,
        'int': TokenType.INT,
        'float': TokenType.FLOAT,
        'string': TokenType.STRING,
        'bool': TokenType.BOOL,
        'list': TokenType.LIST,
        'dict': TokenType.DICT,
        'any': TokenType.ANY,
        'unknown': TokenType.UNKNOWN,
        'never': TokenType.NEVER,
        'readonly': TokenType.READONLY,
        'true': TokenType.TRUE,
        'false': TokenType.FALSE,
        'null': TokenType.NULL,
    }
    
    SINGLE_CHAR_TOKENS = {
        '{': TokenType.LEFT_BRACE,
        '}': TokenType.RIGHT_BRACE,
        '[': TokenType.LEFT_BRACKET,
        ']': TokenType.RIGHT_BRACKET,
        '(': TokenType.LEFT_PAREN,
        ')': TokenType.RIGHT_PAREN,
        '<': TokenType.LESS_THAN,
        '>': TokenType.GREATER_THAN,
        '=': TokenType.EQUALS,
        ':': TokenType.COLON,
        ';': TokenType.SEMICOLON,
        ',': TokenType.COMMA,
        '?': TokenType.QUESTION,
        '|': TokenType.PIPE,
        '&': TokenType.AMPERSAND,
        '.': TokenType.DOT,
    }
    
    def __init__(self, input_text: str):
        """Initialize lexer with input text."""
        self.input = input_text
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
    
    def peek(self, offset: int = 0) -> str:
        """Peek at character at current position + offset."""
        pos = self.position + offset
        return self.input[pos] if pos < len(self.input) else ''
    
    def advance(self) -> str:
        """Advance position and return current character."""
        if self.position < len(self.input):
            char = self.input[self.position]
            self.position += 1
            if char == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            return char
        return ''
    
    def skip_whitespace(self):
        """Skip whitespace characters."""
        while self.position < len(self.input):
            char = self.peek()
            if char in ' \t\r':
                self.advance()
            elif char == '\n':
                start = self.position
                self.advance()
                self.add_token(TokenType.NEWLINE, '\n', start)
            else:
                break
    
    def read_identifier(self) -> str:
        """Read an identifier."""
        result = []
        while self.position < len(self.input):
            char = self.peek()
            if char.isalnum() or char in '_$':
                result.append(self.advance())
            else:
                break
        return ''.join(result)
    
    def read_number(self) -> str:
        """Read a number literal."""
        result = []
        while self.position < len(self.input):
            char = self.peek()
            if char.isdigit() or char == '.':
                result.append(self.advance())
            else:
                break
        return ''.join(result)
    
    def read_string(self, quote: str) -> str:
        """Read a string literal."""
        result = []
        self.advance()  # Skip opening quote
        
        while self.position < len(self.input):
            char = self.peek()
            if char == quote:
                self.advance()  # Skip closing quote
                break
            elif char == '\\':
                self.advance()
                if self.position < len(self.input):
                    result.append(self.advance())
            else:
                result.append(self.advance())
        
        return ''.join(result)
    
    def read_line_comment(self) -> str:
        """Read a line comment."""
        result = []
        self.advance()  # Skip first /
        self.advance()  # Skip second /
        
        while self.position < len(self.input) and self.peek() != '\n':
            result.append(self.advance())
        
        return ''.join(result).strip()
    
    def read_block_comment(self) -> str:
        """Read a block comment."""
        result = []
        self.advance()  # Skip /
        self.advance()  # Skip *
        
        is_jsdoc = self.peek() == '*' and self.peek(1) != '/'
        if is_jsdoc:
            self.advance()  # Skip extra *
        
        while self.position < len(self.input):
            if self.peek() == '*' and self.peek(1) == '/':
                self.advance()  # Skip *
                self.advance()  # Skip /
                break
            result.append(self.advance())
        
        return ''.join(result).strip()
    
    def read_attribute(self) -> dict:
        """Read an attribute."""
        self.advance()  # Skip @
        key_parts = [self.read_identifier()]
        
        # Handle nested attribute keys like @db.table
        while self.peek() == '.':
            self.advance()
            key_parts.append(self.read_identifier())
        
        full_key = '.'.join(key_parts)
        
        # Check for attribute value
        self.skip_whitespace()
        value = None
        
        if self.peek() == '(':
            self.advance()  # Skip (
            self.skip_whitespace()
            
            if self.peek() in '"\'':
                quote = self.peek()
                value = self.read_string(quote)
            elif self.peek().isdigit():
                value = float(self.read_number())
            elif self.input[self.position:self.position+4] == 'true':
                self.position += 4
                value = True
            elif self.input[self.position:self.position+5] == 'false':
                self.position += 5
                value = False
            
            self.skip_whitespace()
            if self.peek() == ')':
                self.advance()
        
        return {'key': full_key, 'value': value}
    
    def add_token(self, token_type: TokenType, value: str, start: int):
        """Add a token to the token list."""
        span = Span(
            start=start,
            end=self.position,
            line=self.line,
            col=self.column - len(value)
        )
        self.tokens.append(Token(token_type, value, span))
    
    def lex(self) -> List[Token]:
        """Tokenize the input and return list of tokens."""
        self.tokens = []
        
        while self.position < len(self.input):
            self.skip_whitespace()
            
            if self.position >= len(self.input):
                break
            
            start = self.position
            char = self.peek()
            
            # Comments
            if char == '/' and self.peek(1) == '/':
                comment = self.read_line_comment()
                self.add_token(TokenType.COMMENT, comment, start)
                continue
            
            if char == '/' and self.peek(1) == '*':
                comment = self.read_block_comment()
                is_jsdoc = self.input[start + 2] == '*'
                self.add_token(TokenType.JSDOC if is_jsdoc else TokenType.COMMENT, comment, start)
                continue
            
            # Attributes
            if char == '@':
                attr = self.read_attribute()
                self.add_token(TokenType.AT, json.dumps(attr), start)
                continue
            
            # String literals
            if char in '"\'':
                string_val = self.read_string(char)
                self.add_token(TokenType.STRING_LITERAL, string_val, start)
                continue
            
            # Number literals
            if char.isdigit():
                num_val = self.read_number()
                self.add_token(TokenType.NUMBER_LITERAL, num_val, start)
                continue
            
            # Identifiers and keywords
            if char.isalpha() or char in '_$':
                id_val = self.read_identifier()
                token_type = self.KEYWORDS.get(id_val, TokenType.IDENTIFIER)
                self.add_token(token_type, id_val, start)
                continue
            
            # Single character tokens
            if char in self.SINGLE_CHAR_TOKENS:
                self.advance()
                self.add_token(self.SINGLE_CHAR_TOKENS[char], char, start)
                continue
            
            # Unknown character
            raise SyntaxError(f"Unexpected character '{char}' at line {self.line}, column {self.column}")
        
        # Add EOF token
        self.add_token(TokenType.EOF, '', self.position)
        
        return self.tokens