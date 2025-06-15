from parser.parser import Parser
from lexer import Lexer


if __name__ == '__main__':
    from lexer import Lexer, TokenType, token_type_is_reserved

    i1 = """object.prop['0'][0]"""
    i2 = """object('prop', prop(), 1)"""
    i3 = """object = 3"""
    i4 = """object()() = 4"""
    lx = Lexer(i4)
    parser = Parser(lx)
    parser.parse()
