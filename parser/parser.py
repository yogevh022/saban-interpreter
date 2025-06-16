from typing import Callable

from lexer.types import ASSIGNMENT_OPERATORS, END_LINE_TOKENS, Token, RESERVED_KEYWORDS
from parser.types import *


class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token: Token = self.lexer.get_next_token()
        self.type_handlers = {
            TokenType.NUMBER: self.number,
            TokenType.STRING: self.string,
            TokenType.IDENTIFIER: self.identifier,
            TokenType.LPAREN: self.paren_expr,
            TokenType.LCURLY: self.object,
            TokenType.LBRACKET: self.array,
            **{t: self.unary for t in UNARY_OPERATORS}
        }
        self.identity_handlers = {
            TokenType.IDENTIFIER: self.handle_identity_identifier,
            TokenType.DOT: self.handle_identity_dot,
            TokenType.LBRACKET: self.handle_identity_lbracket,
            TokenType.LPAREN: self.handle_identity_lparen,
        }

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            raise Exception(f"Parsing error: Expected {token_type}, got {self.current_token.type}")

    def number(self, token: Token):
        self.eat(TokenType.NUMBER)
        return Number(value=token.value)

    def string(self, token: Token):
        self.eat(TokenType.STRING)
        return String(value=token.value)

    def identifier(self, token: Token):
        identifier = self.get_identity()  # identifier or function call (which results in Identifier)
        token = self.current_token
        if token.type in UNARY_OPERATORS:
            self.eat(token.type)
            value = BinaryOperation(operator=token.type, left=identifier)
            return Assign(identifier=identifier, value=value, return_mode='before')
        return identifier

    def unary(self, token: Token):
        self.eat(token.type)
        expr = self.expr() # if this is not an Identifier, it will raise an exception
        value = BinaryOperation(operator=token.type, left=expr)
        return Assign(identifier=expr, value=value, return_mode='after')

    def paren_expr(self, token: Token):
        self.eat(TokenType.LPAREN)
        expr = self.expr()
        self.eat(TokenType.RPAREN)
        return expr

    def object(self, token: Token):
        obj = Object()
        self.eat(TokenType.LCURLY)
        while self.current_token.type != TokenType.RCURLY:
            key = self.expr()
            self.eat(TokenType.COLON)
            obj.properties.append(ObjectProperty(key=key, value=self.expr()))
            if self.current_token.type == TokenType.COMMA:
                self.eat(TokenType.COMMA)
        self.eat(TokenType.RCURLY)
        return obj

    def array(self, token: Token):
        arr = Array()
        self.eat(TokenType.LBRACKET)
        while self.current_token.type != TokenType.RBRACKET:
            arr.elements.append(self.expr())
            if self.current_token.type == TokenType.COMMA:
                self.eat(TokenType.COMMA)
        self.eat(TokenType.RBRACKET)
        return arr

    def args(self):
        args = []
        self.eat(TokenType.LPAREN)
        while self.current_token.type != TokenType.RPAREN:
            args.append(self.expr())
            if self.current_token.type == TokenType.COMMA:
                self.eat(TokenType.COMMA)
        self.eat(TokenType.RPAREN)
        return args

    def factor(self):
        token: Token = self.current_token
        handler: Callable[[Token], Type] = self.type_handlers.get(token.type)
        if handler:
            return handler(token)
        raise Exception(f"Unexpected token: {token}")

    def handle_identity_identifier(self, identity: Identifier, token: Token, access_dot: bool):
        if not access_dot:
            raise Exception(f"Unexpected identifier: {token.value}")
        self.eat(TokenType.IDENTIFIER)
        identity.address.append(String(value=token.value))

    def handle_identity_dot(self, identity: Identifier, token: Token, access_dot: bool):
        if access_dot:
            raise Exception("Unexpected double dot")
        self.eat(TokenType.DOT)

    def handle_identity_lbracket(self, identity: Identifier, token: Token, access_dot: bool):
        self.eat(TokenType.LBRACKET)
        index = self.expr()
        self.eat(TokenType.RBRACKET)
        identity.address.append(index)

    def handle_identity_lparen(self, identity: Identifier, token: Token, access_dot: bool):
        return Identifier(address=[FunctionCall(identifier=identity, args=self.args())])

    def get_identity(self):
        identity = Identifier()
        access_dot: bool = True
        while self.current_token.type in self.identity_handlers:
            token = self.current_token
            handler: Callable[[Identifier, Token, bool], Identifier | None] = self.identity_handlers[token.type]
            identity_override = handler(identity, token, access_dot)
            identity = identity_override if identity_override else identity
            access_dot = True if token.type == TokenType.DOT else False
        if access_dot:
            raise Exception("Unexpected dot at the end of identifier")
        return identity

    def exponent(self):
        node = self.factor()
        while self.current_token.type == TokenType.EXPONENT:
            token = self.current_token
            self.eat(TokenType.EXPONENT)
            node = BinaryOperation(operator=token.type, left=node, right=self.factor())
        return node

    def term(self):
        node = self.exponent()
        while self.current_token.type in (TokenType.MULTIPLY, TokenType.DIVIDE):
            token = self.current_token
            if token.type == TokenType.MULTIPLY:
                self.eat(TokenType.MULTIPLY)
            elif token.type == TokenType.DIVIDE:
                self.eat(TokenType.DIVIDE)
            node = BinaryOperation(operator=token.type, left=node, right=self.exponent())
        return node

    def expr(self):
        node = self.term()
        while self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            token = self.current_token
            if token.type == TokenType.PLUS:
                self.eat(TokenType.PLUS)
            elif token.type == TokenType.MINUS:
                self.eat(TokenType.MINUS)
            node = BinaryOperation(operator=token.type, left=node, right=self.term())
        else:
            if self.current_token.type in ASSIGNMENT_OPERATORS:
                token = self.current_token
                self.eat(token.type)
                value = self.expr()
                value = value if token.type == TokenType.ASSIGN else (
                BinaryOperation(operator=token.type, left=node, right=value))
                if not isinstance(node, Identifier):
                    raise Exception(f"Cannot assign value to non-identifier: {node}")
                return Assign(identifier=node, value=value)
        return node

    def statement(self):
        if self.current_token.type in RESERVED_KEYWORDS.values():
            return # TODO handle reserved keywords
        return self.expr()

    def parse(self):
        ast = []
        while self.current_token.type != TokenType.EOF:
            if self.current_token.type in END_LINE_TOKENS:
                self.eat(self.current_token.type)
                continue
            ast.append(self.statement())
        return ast
