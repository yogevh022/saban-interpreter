from lexer.types import *


class Lexer:
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos] if self.text else None
        self.special_tokenizers = {
            '*': self.tokenize_asterisk,
            '/': self.tokenize_forward_slash,
            '%': self.tokenize_percent,
            '=': self.tokenize_equals,
            '-': self.tokenize_minus,
            '+': self.tokenize_plus,
        }

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
        floating_point = False
        while self.current_char is not None and (self.current_char.isdigit() or (self.current_char == '.' and not floating_point)):
            if self.current_char == '.':
                floating_point = True
            result += self.current_char
            self.advance()
        return Token(type=TokenType.NUMBER, value=float(result) if floating_point else int(result))

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

    def keyword(self):
        result = ''
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()
        if result in RESERVED_KEYWORDS:
            return Token(type=RESERVED_KEYWORDS[result], value=result)
        if result in BOOLEAN_OPERATORS:
            return Token(type=TokenType.BOOL, value=True if result == 'true' else False)
        return Token(type=TokenType.IDENTIFIER, value=result)

    def tokenize_asterisk(self):
        self.advance()
        if self.current_char == '*':
            self.advance()
            if self.current_char == '=':
                self.advance()
                return Token(type=TokenType.EXPONENT_ASSIGN, value='**=')
            return Token(type=TokenType.EXPONENT, value='**')
        if self.current_char == '=':
            self.advance()
            return Token(type=TokenType.MULTIPLICATION_ASSIGN, value='*=')
        return Token(type=TokenType.MULTIPLY, value='*')

    def tokenize_forward_slash(self):
        self.advance()
        if self.current_char == '=':
            self.advance()
            return Token(type=TokenType.DIVISION_ASSIGN, value='/=')
        return Token(type=TokenType.DIVIDE, value='/')

    def tokenize_percent(self):
        self.advance()
        if self.current_char == '=':
            self.advance()
            return Token(type=TokenType.MODULUS_ASSIGN, value='%=')
        return Token(type=TokenType.MODULUS, value='%')

    def tokenize_equals(self):
        self.advance()
        if self.current_char == '=':
            self.advance()
            return Token(type=TokenType.EQUALS, value='==')
        return Token(type=TokenType.ASSIGN, value='=')

    def tokenize_minus(self):
        self.advance()
        if self.current_char == '-':
            self.advance()
            return Token(type=TokenType.DECREMENT, value='--')
        if self.current_char == '=':
            self.advance()
            return Token(type=TokenType.SUBTRACTION_ASSIGN, value='-=')
        return Token(type=TokenType.MINUS, value='-')

    def tokenize_plus(self):
        self.advance()
        if self.current_char == '+':
            self.advance()
            return Token(type=TokenType.INCREMENT, value='++')
        if self.current_char == '=':
            self.advance()
            return Token(type=TokenType.ADDITION_ASSIGN, value='+=')
        return Token(type=TokenType.PLUS, value='+')

    def get_next_token(self) -> Token:
        while self.current_char is not None:
            char = self.current_char
            if char.isspace():
                self.skip_whitespace()
                continue
            if char.isdigit():
                return self.number()
            if char.isalpha() or char == '_':
                return self.keyword() # identifiers and keywords
            if char in ('"', "'"):
                return self.string(char)
            if char in SINGLE_CHAR_TOKENS:
                self.advance()
                return Token(type=SINGLE_CHAR_TOKENS[char], value=char)
            if char in self.special_tokenizers:
                return self.special_tokenizers[char]()
            raise Exception(f"Invalid character: {char}")
        return Token(type=TokenType.EOF, value=None)
