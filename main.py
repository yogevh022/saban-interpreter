from parser.parser import Parser
from lexer.lexer import Lexer
from interpreter.interpreter import Interpreter

if __name__ == '__main__':

    i1 = """object.prop['0'][0]"""
    i2 = """object('prop', prop(), 1)"""
    i3 = """object = 3"""
    i4 = """object()() = 4"""
    i5 = """2 = 2"""
    i6 = """
        a = 4; b = a+7;c=b;
    """
    i7 = """a= {1: 2, 'b': {1: 22}};"""
    i8 = """a = [1, 2, 3]; a;a[0] = 4; a;"""
    i9 = """a = 2; ++a; a;"""
    lx = Lexer(i9)
    parser = Parser(lx)
    ast = parser.parse()
    interpreter = Interpreter(ast)
    for st in ast:
        print(st)
    interpreter.interpret()
