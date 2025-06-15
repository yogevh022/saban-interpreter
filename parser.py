from typing import List, Optional, Union, Any

from pydantic import BaseModel, field_validator

from lexer import TokenType


class Primitive(BaseModel):
    value: Any

class Number(Primitive):
    value: int | float

    def __repr__(self):
        return f"Number({self.value})"

class String(Primitive):
    value: str

    def __repr__(self):
        return f"String({self.value})"

class Identifier(BaseModel):
    address: List[Union[Primitive, 'Identifier', 'FunctionCall']] = []

    @property
    def dereferenced(self) -> Number | String:
        return String(value=f'*{self.__repr__()}')

    def validate_address(self):
        if any(not isinstance(a, (Primitive, Identifier, FunctionCall)) for a in self.address):
            raise ValueError("All elements in address must be str or int")

    def __repr__(self):
        return f"Identifier({'.'.join(str(a) for a in self.address)})"

class FunctionCall(BaseModel):
    identifier: Identifier # identifier of the function
    args: List[Union[Primitive, Identifier, 'FunctionCall']] = []


def binary_op(op: str, left, right):
    if op == '+':
        return Number(value=left.value + right.value)
    elif op == '-':
        return Number(value=left.value - right.value)
    elif op == '*':
        return Number(value=left.value * right.value)
    elif op == '/':
        return Number(value=left.value / right.value)
    else:
        raise ValueError(f"Unsupported binary operator: {op}")


class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            raise Exception(f"Parsing error: Expected {token_type}, got {self.current_token.type}")

    def factor(self):
        token = self.current_token
        if token.type == TokenType.NUMBER:
            self.eat(TokenType.NUMBER)
            return Number(value=token.value)
        elif token.type == TokenType.STRING:
            self.eat(TokenType.STRING)
            return String(value=token.value)
        elif token.type == TokenType.IDENTIFIER:
            return self.identity()
        elif token.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            expr = self.expr()
            self.eat(TokenType.RPAREN)
            return expr
        else:
            raise Exception(f"Unexpected token: {token}")

    def identity(self):
        identifier = Identifier()
        dot = True
        while self.current_token.type in (TokenType.IDENTIFIER, TokenType.DOT, TokenType.LBRACKET):
            token = self.current_token
            if token.type == TokenType.IDENTIFIER:
                if not dot:
                    raise Exception(f"Unexpected identifier: {token.value}")
                self.eat(TokenType.IDENTIFIER)
                identifier.address.append(String(value=token.value))
                dot = False
            elif token.type == TokenType.DOT:
                if dot:
                    raise Exception("Unexpected double dot")
                self.eat(TokenType.DOT)
                dot = True
            elif token.type == TokenType.LBRACKET:
                self.eat(TokenType.LBRACKET)
                index = self.expr()
                self.eat(TokenType.RBRACKET)
                identifier.address.append(index)
        if dot:
            raise Exception("Unexpected dot at the end of identifier")
        identifier.validate_address() # raise exception if invalid indexing e.g. with float
        return identifier

    def term(self):
        node = self.factor()
        while self.current_token.type in (TokenType.MULTIPLY, TokenType.DIVIDE):
            token = self.current_token
            if token.type == TokenType.MULTIPLY:
                self.eat(TokenType.MULTIPLY)
            elif token.type == TokenType.DIVIDE:
                self.eat(TokenType.DIVIDE)
            node = binary_op(token.value, node, self.factor())
        return node

    def expr(self):
        node = self.term()
        while self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            token = self.current_token
            if token.type == TokenType.PLUS:
                self.eat(TokenType.PLUS)
            elif token.type == TokenType.MINUS:
                self.eat(TokenType.MINUS)
            node = binary_op(token.value, node, self.term())
        return node


    def parse(self):
        z = self.expr()
        print(z)

if __name__ == '__main__':
    from lexer import Lexer, TokenType

    input_code = """object.prop['0'][0]"""
    lx = Lexer(input_code)
    parser = Parser(lx)
    parser.parse()
