from enum import Enum
from typing import Any
from pydantic import BaseModel


class TokenType(str, Enum):
    # types
    IDENTIFIER = "IDENTIFIER"
    NUMBER = 'NUMBER'
    STRING = 'STRING'
    BOOL = 'BOOL'

    # comparison operators
    EQUALS = 'EQUALS'

    # punctuation
    COLON = 'COLON'
    SEMICOLON = 'SEMICOLON'
    COMMA = 'COMMA'
    DOT = 'DOT'

    # special
    BLANK = 'BLANK'
    EOF = 'EOF'

    # brackets and parentheses
    LPAREN = 'LPAREN'
    RPAREN = 'RPAREN'
    LBRACKET = 'LBRACKET'
    RBRACKET = 'RBRACKET'
    LCURLY = 'LCURLY'
    RCURLY = 'RCURLY'

    # arithmetic operators
    PLUS = 'PLUS'
    MINUS = 'MINUS'
    MULTIPLY = 'MULTIPLY'
    DIVIDE = 'DIVIDE'
    MODULUS = 'MODULUS'
    EXPONENT = 'EXPONENT'

    # unary operators
    INCREMENT = 'INCREMENT'
    DECREMENT = 'DECREMENT'

    # assignment operators
    ASSIGN = 'ASSIGN'
    ADDITION_ASSIGN = 'ADDITION_ASSIGN'
    SUBTRACTION_ASSIGN = 'SUBTRACTION_ASSIGN'
    MULTIPLICATION_ASSIGN = 'MULTIPLICATION_ASSIGN'
    DIVISION_ASSIGN = 'DIVISION_ASSIGN'
    MODULUS_ASSIGN = 'MODULUS_ASSIGN'
    EXPONENT_ASSIGN = 'EXPONENT_ASSIGN'

    # reserved keywords
    IF = 'IF'
    ELSE = 'ELSE'
    WHILE = 'WHILE'
    FN = 'FN'
    RETURN = 'RETURN'
    BREAK = 'BREAK'
    CONTINUE = 'CONTINUE'


UNARY_OPERATORS = {
    TokenType.INCREMENT,
    TokenType.DECREMENT
}

END_LINE_TOKENS = {
    TokenType.SEMICOLON,
    TokenType.EOF
}

ASSIGNMENT_OPERATORS = {
    TokenType.ASSIGN,
    TokenType.ADDITION_ASSIGN,
    TokenType.SUBTRACTION_ASSIGN,
    TokenType.MULTIPLICATION_ASSIGN,
    TokenType.DIVISION_ASSIGN,
    TokenType.MODULUS_ASSIGN,
    TokenType.EXPONENT_ASSIGN
}

AUGMENTED_ASSIGNMENT_TO_ARITHMETIC = {
    TokenType.ADDITION_ASSIGN: TokenType.PLUS,
    TokenType.SUBTRACTION_ASSIGN: TokenType.MINUS,
    TokenType.MULTIPLICATION_ASSIGN: TokenType.MULTIPLY,
    TokenType.DIVISION_ASSIGN: TokenType.DIVIDE,
    TokenType.MODULUS_ASSIGN: TokenType.MODULUS,
    TokenType.EXPONENT_ASSIGN: TokenType.EXPONENT
}

RESERVED_KEYWORDS = {
    'if': TokenType.IF,
    'else': TokenType.ELSE,
    'while': TokenType.WHILE,
    'fn': TokenType.FN,
    'return': TokenType.RETURN,
    'break': TokenType.BREAK,
    'continue': TokenType.CONTINUE
}

BOOLEAN_OPERATORS = {
    'true': TokenType.BOOL,
    'false': TokenType.BOOL
}

ARITHMETIC_TYPE_TO_CHAR = {
    TokenType.PLUS: '+',
    TokenType.MINUS: '-',
    TokenType.MULTIPLY: '*',
    TokenType.DIVIDE: '/',
    TokenType.MODULUS: '%',
    TokenType.EXPONENT: '**'
}

SINGLE_CHAR_TOKENS = {
    '(': TokenType.LPAREN,
    ')': TokenType.RPAREN,
    '[': TokenType.LBRACKET,
    ']': TokenType.RBRACKET,
    '{': TokenType.LCURLY,
    '}': TokenType.RCURLY,
    ':': TokenType.COLON,
    ';': TokenType.SEMICOLON,
    ',': TokenType.COMMA,
    '.': TokenType.DOT,
}


class Token(BaseModel):
    type: TokenType = TokenType.BLANK
    value: Any = None

    def __repr__(self):
        return f"Token({self.type.value}: {self.value})"
