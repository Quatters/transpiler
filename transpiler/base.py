import re
from enum import Enum


WHITESPACE = re.compile('\S')


class TranspilerError(Exception):
    pass


class Tag(Enum):
    """
    Possible token names enumeration.
    """

    def __repr__(self) -> str:
        return self.value

    # general
    ID = 'ID'
    NUMBER_INT = 'NUMBER_INT'
    NUMBER_FLOAT = 'NUMBER_FLOAT'
    LBRACKET = 'LBRACKET'
    RBRACKET = 'RBRACKET'
    LBRACKET_SQUARE = 'LBRACKET_SQUARE'
    RBRACKET_SQUARE = 'RBRACKET_SQUARE'
    SEMICOLON = 'SEMICOLON'
    COLON = 'COLON'
    COMMA = 'COMMA'
    DOT = 'DOT'
    QUOTE = 'QUOTE'
    DQUOTE = 'DQOUTE'

    # types
    T_INTEGER = 'T_INTEGER'
    T_REAL = 'T_REAL'
    T_BOOLEAN = 'T_BOOLEAN'
    T_CHAR = 'T_CHAR'
    T_STRING = 'T_STRING'
    T_ARRAY = 'T_ARRAY'

    # comparisons
    EQ = 'EQ'
    NE = 'NE'
    LE = 'LE'
    LT = 'LT'
    GE = 'GE'
    GT = 'GT'

    # operators
    PLUS = 'PLUS'
    MINUS = 'MINUS'
    MULTIPLY = 'MULTIPLY'
    DIVIDE = 'DIVIDE'
    ASSIGN = 'ASSIGN'
    PLUS_ASSIGN = 'PLUS_ASSIGN'
    MINUS_ASSIGN = 'MINUS_ASSIGN'
    MULTIPLY_ASSIGN = 'MULTIPLY_ASSIGN'
    DIVIDE_ASSIGN = 'DIVIDE_ASSIGN'
    RANGE = 'RANGE'

    # boolean
    TRUE = 'TRUE'
    FALSE = 'FALSE'

    # other key words
    VAR = 'VAR'
    IF = 'IF'
    THEN = 'THEN'
    ELSE = 'ELSE'
    CASE = 'CASE'
    OF = 'OF'
    FOR = 'FOR'
    WHILE = 'WHILE'
    REPEAT = 'REPEAT'
    UNTIL = 'UNTIL'
    DO = 'DO'
    TO = 'TO'
    BEGIN = 'BEGIN'
    END = 'END'
    PROCEDURE = 'PROCEDURE'
    FUNCTION = 'FUNCTION'


class LexerRule:
    """
    Token definition and regular expression mapping. Used by lexer.
    """

    def __init__(self, tag: Tag, regex: str) -> None:
        self.tag = tag
        self.regex = regex


class Token:
    """
    Minimal sensible unit of code sequence.
    """

    def __init__(self, tag: Tag, value: str, pos: int):
        self.tag = tag
        self.value = value
        self.pos = pos

    def __str__(self):
        return f'{self.value} {self.tag.value}'
