import re

PAT_IS_NUMBER = r'^\d+\.?\d+$'
PAT_IS_VALID_VARIABLE = r'^[a-zA-Z_][a-zA-Z0-9_]*$'
PAT_IS_STRING = r'^".*"$'

def is_number(value: str) -> bool:
    return bool(re.match(PAT_IS_NUMBER, value))

def is_valid_variable(value: str) -> bool:
    return bool(re.match(PAT_IS_VALID_VARIABLE, value))

def is_string(value: str) -> bool:
    return bool(re.match(PAT_IS_STRING, value))