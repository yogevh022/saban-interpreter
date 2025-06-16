from lexer.types import ASSIGNMENT_OPERATORS, ARITHMETIC_OPERATORS, END_LINE_TOKENS
from lexer.lexer import token_type_is_reserved
from parser.types import *


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
            identifier = self.identity() # identifier or function call (which results in Identifier)
            if token.type in UNARY_OPERATORS:
                self.eat(token.type)
                value = BinaryOperation(operator=token.type, left=identifier)
                return Assign(identifier=identifier, value=value, return_mode='before')
            return identifier
        elif token.type in UNARY_OPERATORS:
            self.eat(token.type)
            expr = self.expr()
            value = BinaryOperation(operator=token.type, left=expr)
            return Assign(identifier=expr, value=value, return_mode='after')
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
        while self.current_token.type in (TokenType.IDENTIFIER, TokenType.DOT, TokenType.LBRACKET, TokenType.LPAREN):
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
                dot = False
                self.eat(TokenType.LBRACKET)
                index = self.expr()
                self.eat(TokenType.RBRACKET)
                identifier.address.append(index)
            elif token.type == TokenType.LPAREN:
                dot = False
                self.eat(TokenType.LPAREN)
                args = self.args() if self.current_token.type != TokenType.RPAREN else []
                self.eat(TokenType.RPAREN)
                identifier = Identifier(address=[FunctionCall(identifier=identifier, args=args)])
        if dot:
            raise Exception("Unexpected dot at the end of identifier")
        identifier.validate_address() # raise exception if invalid indexing e.g. with float
        return identifier

    def args(self):
        args = [self.expr()]
        while self.current_token.type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            args.append(self.expr())
        return args

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

    def value_start_statement(self, expression):
        token = self.current_token
        if token.type in ARITHMETIC_OPERATORS:
            self.eat(token.type)
            return BinaryOperation(operator=token.type, left=expression, right=self.expr())
        raise Exception(f"Unexpected operator {token.type} for type {expression}")


    def statement(self):
        if token_type_is_reserved(self.current_token.type):
            return # TODO handle reserved keywords
        expression = self.expr()
        if isinstance(expression, (Primitive, BinaryOperation)):
            if self.current_token.type not in END_LINE_TOKENS:
                raise Exception(f"Expected end of line token, got {self.current_token.type}")
            return expression

        return expression

    def parse(self):
        ast = []
        while self.current_token.type != TokenType.EOF:
            if self.current_token.type in END_LINE_TOKENS:
                self.eat(self.current_token.type)
                continue
            ast.append(self.statement())
        return ast
