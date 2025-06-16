from pydantic import BaseModel, model_validator
from typing import List, Any, Literal, Optional

from lexer.types import TokenType, UNARY_OPERATORS


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
    operator: Literal[TokenType.PLUS, TokenType.MINUS, TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.EXPONENT, TokenType.INCREMENT, TokenType.DECREMENT]
    left: Type
    right: Optional[Type]

    def __str__(self):
        return f"BinaryOperation({self.left} {self.operator.value} {self.right})"

    def __repr__(self):
        return self.__str__()

    @model_validator(mode='before')
    @classmethod
    def validate_binary_operation(cls, values):
        if values['operator'] in UNARY_OPERATORS:
            values['right'] = Number(value=1)
            if values['operator'] == TokenType.INCREMENT:
                values['operator'] = TokenType.PLUS
            elif values['operator'] == TokenType.DECREMENT:
                values['operator'] = TokenType.MINUS
        elif values['right'] is None:
            raise ValueError("BinaryOperation requires a right operand for non-unary operators")
        return values

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
    return_mode: Literal['before', 'after'] = 'after'

    def __str__(self):
        return f"Assign({self.identifier} = {self.value})"

    def __repr__(self):
        return self.__str__()
