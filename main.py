from lexer import Lexer, TokenType


if __name__ == '__main__':
    input_code = """
    object.prop[0][0]
    """
    input_code2 = """object.prop[0][0]"""
    lx = Lexer(input_code2)
    while True:
        token = lx.get_next_token()
        if token.type == TokenType.EOF:
            break
        print(token)