from typing import Any

from lexer.types import ARITHMETIC_TYPE_TO_CHAR
from parser.types import Identifier, BinaryOperation, Primitive, Assign, Object, Array


def validate_indexable(value: dict | list, index: Any):
    if isinstance(value, dict):
        if index not in value:
            raise KeyError(f"Identifier '{index}' not found in memory")
    elif isinstance(value, list):
        if not isinstance(index, int):
            raise TypeError(f"List index must be an integer, got {type(index).__name__}")


def safe_get(value: dict | list, index: Any, default=None):
    if isinstance(value, dict):
        return value.get(index, default)
    return value[index] if 0 <= index < len(value) else default


class Interpreter:
    def __init__(self, ast):
        self.ast = ast
        self.memory = {}

    def identity_value(self, identifier: Identifier):
        current_value = self.memory
        for part in identifier.address:
            prim_part = self.interpret_type(part)
            validate_indexable(current_value, prim_part) # raises KeyError or TypeError if invalid indexing
            current_value = current_value[prim_part]
        return current_value

    def interpret_type(self, node):
        if isinstance(node, Identifier):
            return self.identity_value(node)
        elif isinstance(node, BinaryOperation):
            return self.execute_binary_operation(node)
        elif isinstance(node, Assign):
            return self.execute_assign(node)
        elif isinstance(node, Primitive):
            return node.value
        elif isinstance(node, Object):
            return {prop.key.value: self.interpret_type(prop.value) for prop in node.properties}
        elif isinstance(node, Array):
            return [self.interpret_type(i) for i in node.elements]
        else:
            raise TypeError(f"Unsupported type for interpretation: {type(node).__name__}")

    def execute_assign(self, assign: Assign):
        literal_value = self.interpret_type(assign.value)
        memory_cursor: list | dict = self.memory
        address_to_modify = self.interpret_type(assign.identifier.address[-1])
        for part in assign.identifier.address[:-1]:
            prim_part = self.interpret_type(part)
            validate_indexable(memory_cursor, prim_part)
            memory_cursor = memory_cursor[prim_part]
        old_value = safe_get(memory_cursor, address_to_modify)
        memory_cursor[address_to_modify] = literal_value
        return literal_value if assign.return_mode == 'after' else old_value

    def execute_binary_operation(self, operation: BinaryOperation):
        left = self.interpret_type(operation.left)
        right = self.interpret_type(operation.right)
        left = f'\'{left}\'' if isinstance(left, str) else left
        right = f'\'{right}\'' if isinstance(right, str) else right
        return eval(f'{left} {ARITHMETIC_TYPE_TO_CHAR[operation.operator.value]} {right}')

    def interpret(self):
        for statement in self.ast:
            print(self.interpret_type(statement))
        print(self.memory)
