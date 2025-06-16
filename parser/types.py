from pydantic import BaseModel, model_validator
from typing import List, Any, Literal, Optional

from lexer.types import TokenType, UNARY_OPERATORS


class Type(BaseModel):
    def __repr__(self):
        return self.__str__()


class Primitive(Type):
    value: Any


class Number(Primitive):
    value: int | float

    def __str__(self):
        return f"Number({self.value})"


class String(Primitive):
    value: str

    def __str__(self):
        return f"String({self.value})"


class Identifier(Type):
    address: List[Type] = list()

    @property
    def dereferenced(self) -> Number | String:
        return String(value=f'*{self.__str__()}')

    def __str__(self):
        return f"Identifier({'.'.join(str(a) for a in self.address)})"


class Array(Type):
    elements: List[Type] = list()

    def __str__(self):
        return f"Array({', '.join(str(e) for e in self.elements)})"


class ObjectProperty(Type):
    key: Primitive
    value: Type

    def __str__(self):
        return f"ObjectProperty({self.key}: {self.value})"

    @model_validator(mode='before')
    @classmethod
    def validate_object_property(cls, values):
        if not isinstance(values['key'], Primitive):
            raise ValueError(f'Object key must be a primitive type, got {type(values['key']).__name__}')
        return values


class Object(Type):
    properties: List[ObjectProperty] = []

    def __str__(self):
        return f"Object({self.properties})"


class BinaryOperation(Type):
    operator: Literal[TokenType.PLUS, TokenType.MINUS, TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.EXPONENT, TokenType.INCREMENT, TokenType.DECREMENT]
    left: Type
    right: Optional[Type]

    def __str__(self):
        return f"BinaryOperation({self.left} {self.operator.value} {self.right})"

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
    args: List[Type] = list()

    def __str__(self):
        return f'{self.identifier.__str__()}({self.args})'


class Assign(Type):
    identifier: Identifier
    value: Type
    return_mode: Literal['before', 'after'] = 'after'

    def __str__(self):
        return f"Assign({self.identifier} = {self.value})"

    @model_validator(mode='before')
    @classmethod
    def validate_assign(cls, values):
        if not isinstance(values['identifier'], Identifier):
            raise ValueError(f"Assign identifier must be an Identifier, got {type(values['identifier']).__name__}")
        if not isinstance(values['value'], Type):
            raise ValueError(f"Assign value must be a Type, got {type(values['value']).__name__}")
        return values
