from pydantic import BaseModel
from typing import List, Union, Any, Literal

from lexer import TokenType


class Type(BaseModel):
    pass


class Primitive(Type):
    value: Any


class Number(Primitive):
    value: int | float

    def __str__(self):
        return f"Number({self.value})"

    def __repr__(self):
        return self.__str__()


class String(Primitive):
    value: str

    def __str__(self):
        return f"String({self.value})"

    def __repr__(self):
        return self.__str__()


class Identifier(Type):
    address: List[Type] = []

    @property
    def dereferenced(self) -> Number | String:
        return String(value=f'*{self.__str__()}')

    def validate_address(self):
        if any(not isinstance(a, (Primitive, Identifier, FunctionCall)) for a in self.address):
            raise ValueError("All elements in address must be str or int")

    def __str__(self):
        return f"Identifier({'.'.join(str(a) for a in self.address)})"

    def __repr__(self):
        return self.__str__()


class BinaryOperation(Type):
    operator: Literal[TokenType.PLUS, TokenType.MINUS, TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.EXPONENT]
    left: Type
    right: Type

    def __str__(self):
        return f"BinaryOperation({self.left} {self.operator.value} {self.right})"

    def __repr__(self):
        return self.__str__()


class FunctionCall(Type):
    identifier: Identifier # identifier of the function
    args: List[Type] = []

    def __str__(self):
        return f'{self.identifier.__str__()}({self.args})'

    def __repr__(self):
        return self.__str__()


class Assign(Type):
    identifier: Identifier
    value: Type

    def __str__(self):
        return f"Assign({self.identifier} = {self.value})"

    def __repr__(self):
        return self.__str__()
