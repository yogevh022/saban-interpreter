from enum import Enum
from typing import Any
from pydantic import BaseModel


class TokenType(str, Enum):
    IDENTIFIER = "IDENTIFIER"
    NUMBER = 'NUMBER'
    STRING = 'STRING'
    PLUS = 'PLUS'
    MINUS = 'MINUS'
    MULTIPLY = 'MULTIPLY'
    DIVIDE = 'DIVIDE'
    MODULUS = 'MODULUS'
    EXPONENT = 'EXPONENT'
    EQUALS = 'EQUALS'
    CHECK_EQUALS = 'CHECK_EQUALS'
    DOT = 'DOT'
    LBRACKET = 'LBRACKET'
    RBRACKET = 'RBRACKET'
    LPAREN = 'LPAREN'
    RPAREN = 'RPAREN'
    LCURLY = 'LCURLY'
    RCURLY = 'RCURLY'
    NEWLINE = 'NEWLINE'
    COLON = 'COLON'
    SEMICOLON = 'SEMICOLON'
    COMMA = 'COMMA'
    BLANK = 'BLANK'
    EOF = 'EOF'


class Token(BaseModel):
    type: TokenType = TokenType.BLANK
    value: Any

    def __repr__(self):
        return f"Token({self.type.value}: {self.value})"


class Lexer:
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos] if self.text else None

    def peek(self):
        if self.pos + 1 < len(self.text):
            return self.text[self.pos + 1]
        return None

    def advance(self):
        self.pos += 1
        self.current_char = self.text[self.pos] if len(self.text) > self.pos else None

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def number(self):
        result = ''
        dot = False
        while self.current_char is not None and (self.current_char.isdigit() or (self.current_char == '.' and not dot)):
            if self.current_char == '.':
                dot = True
            result += self.current_char
            self.advance()
        return Token(type=TokenType.NUMBER, value=float(result) if dot else int(result))

    def string(self, start_char: str):
        result = ''
        self.advance()
        while self.current_char is not None and self.current_char != start_char:
            if self.current_char == '\\':
                result += self.current_char
                self.advance()
            result += self.current_char
            self.advance()
        self.advance()
        return Token(type=TokenType.STRING, value=result)

    def identifier(self):
        result = ''
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()
        return Token(type=TokenType.IDENTIFIER, value=result)

    def get_next_token(self) -> Token:
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            if self.current_char.isdigit():
                return self.number()
            if self.current_char.isalpha() or self.current_char == '_':
                return self.identifier()
            if self.current_char in ('"', "'"):
                return self.string(self.current_char)
            if self.current_char == '.':
                self.advance()
                return Token(type=TokenType.DOT, value='.')
            if self.current_char == ',':
                self.advance()
                return Token(type=TokenType.COMMA, value=',')
            if self.current_char == '[':
                self.advance()
                return Token(type=TokenType.LBRACKET, value='[')
            if self.current_char == ']':
                self.advance()
                return Token(type=TokenType.RBRACKET, value=']')
            if self.current_char == '(':
                self.advance()
                return Token(type=TokenType.LPAREN, value='(')
            if self.current_char == ')':
                self.advance()
                return Token(type=TokenType.RPAREN, value=')')
            if self.current_char == '{':
                self.advance()
                return Token(type=TokenType.LCURLY, value='{')
            if self.current_char == '}':
                self.advance()
                return Token(type=TokenType.RCURLY, value='}')
            if self.current_char == '+':
                self.advance()
                return Token(type=TokenType.PLUS, value='+')
            if self.current_char == '-':
                self.advance()
                return Token(type=TokenType.MINUS, value='-')
            if self.current_char == '*':
                self.advance()
                if self.current_char == '*':
                    self.advance()
                    return Token(type=TokenType.EXPONENT, value='**')
                return Token(type=TokenType.MULTIPLY, value='*')
            if self.current_char == '/':
                self.advance()
                return Token(type=TokenType.DIVIDE, value='/')
            if self.current_char == '%':
                self.advance()
                return Token(type=TokenType.MODULUS, value='%')
            if self.current_char == '=':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(type=TokenType.CHECK_EQUALS, value='==')
                return Token(type=TokenType.EQUALS, value='=')
            if self.current_char == ';':
                self.advance()
                return Token(type=TokenType.SEMICOLON, value=';')
            if self.current_char == ':':
                self.advance()
                return Token(type=TokenType.COLON, value=':')
            if self.current_char == '\\':
                self.advance()
                if self.current_char == 'n':
                    self.advance()
                    return Token(type=TokenType.NEWLINE, value='\n')
                raise Exception(f"Invalid escape sequence: \\{self.current_char}")
            raise Exception(f"Invalid character: {self.current_char}")
        return Token(type=TokenType.EOF, value=None)
