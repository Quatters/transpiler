import re

from transpiler.base import Def, Rule


LEXER_REGEX_FLAGS = re.IGNORECASE

RULES = [
    # types
    Rule(Def.T_INTEGER, r'\binteger\b'),
    Rule(Def.T_REAL, r'\breal\b'),
    Rule(Def.T_BOOLEAN, r'\bboolean\b'),
    Rule(Def.T_CHAR, r'\bchar\b'),
    Rule(Def.T_STRING, r'\bstring\b'),
    Rule(Def.T_ARRAY, r'\barray\b'),

    # comparisons
    Rule(Def.EQ, r'='),
    Rule(Def.NE, r'\<\>'),
    Rule(Def.LE, r'\<='),
    Rule(Def.LT, r'\<'),
    Rule(Def.GE, r'\>='),
    Rule(Def.GT, r'\>'),

    # operators
    Rule(Def.PLUS, r'\+'),
    Rule(Def.MINUS, r'\-'),
    Rule(Def.MULTIPLY, '\*'),
    Rule(Def.DIVIDE, r'/'),
    Rule(Def.ASSIGN, r'\:='),
    Rule(Def.PLUS_ASSIGN, '\+='),
    Rule(Def.MINUS_ASSIGN, r'\-='),
    Rule(Def.MULTIPLY_ASSIGN, '\*='),
    Rule(Def.DIVIDE_ASSIGN, r'/='),
    Rule(Def.RANGE, r'\.\.'),

    # boolean
    Rule(Def.TRUE, r'\btrue\b'),
    Rule(Def.FALSE, r'\bfalse\b'),

    # other key words
    Rule(Def.VAR, r'\bvar\b'),
    Rule(Def.IF, r'\bif\b'),
    Rule(Def.THEN, r'\bthen\b'),
    Rule(Def.ELSE, r'\belse\b'),
    Rule(Def.CASE, r'\bcase\b'),
    Rule(Def.OF, r'\bof\b'),
    Rule(Def.FOR, r'\bfor\b'),
    Rule(Def.WHILE, r'\bwhile\b'),
    Rule(Def.UNTIL, r'\buntil\b'),
    Rule(Def.DO, r'\bdo\b'),
    Rule(Def.BEGIN, r'\bbegin\b'),
    Rule(Def.END, r'\bend\b'),
    Rule(Def.PROCEDURE, r'\bprocedure\b'),
    Rule(Def.FUNCTION, r'\bfunction\b'),

    # general
    Rule(Def.ID, r'\b[_a-zA-Z]\w*\b'),
    Rule(Def.NUMBER_FLOAT, r'\b[-+]?\d+\.\d+\b'),
    Rule(Def.NUMBER_INT, r'\b[-+]?[0-9]+\b'),
    Rule(Def.LBRACKET, r'\('),
    Rule(Def.RBRACKET, r'\)'),
    Rule(Def.LBRACKET_SQUARE, r'\['),
    Rule(Def.RBRACKET_SQUARE, r'\]'),
    Rule(Def.SEMICOLON, r';'),
    Rule(Def.COLON, r':'),
    Rule(Def.COMMA, r','),
    Rule(Def.DOT, r'\.'),
    Rule(Def.QUOTE, r"\'"),
    Rule(Def.DQUOTE, r'"'),
]
