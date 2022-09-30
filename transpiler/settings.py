import os
import re
import logging

from transpiler.base import (
    Terminal,
    NonTerminal,
    LexerRule,
    GrammarRule,
    Special,
)

logging.basicConfig(
    format='%(levelname)s:[%(module)s:%(lineno)d]: %(message)s',
    level=os.getenv('LOG_LEVEL', logging.WARNING),
)


class Tag(Terminal):
    """
    Possible token names enumeration.
    """

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


class NonTerm(NonTerminal):
    DESCR = 'DESCR'
    PROG = 'PROG'
    VARS = 'VARS'
    EXPR = 'EXPR'
    TYPE = 'TYPE'
    CALL = 'CALL'
    ARGS = 'ARGS'


LEXER_REGEX_FLAGS = re.IGNORECASE

LEXER_RULES = [
    # types
    LexerRule(Tag.T_INTEGER, r'\binteger\b'),
    LexerRule(Tag.T_REAL, r'\breal\b'),
    LexerRule(Tag.T_BOOLEAN, r'\bboolean\b'),
    LexerRule(Tag.T_CHAR, r'\bchar\b'),
    LexerRule(Tag.T_STRING, r'\bstring\b'),
    LexerRule(Tag.T_ARRAY, r'\barray\b'),

    # comparisons
    LexerRule(Tag.EQ, r'='),
    LexerRule(Tag.NE, r'\<\>'),
    LexerRule(Tag.LE, r'\<='),
    LexerRule(Tag.LT, r'\<'),
    LexerRule(Tag.GE, r'\>='),
    LexerRule(Tag.GT, r'\>'),

    # operators
    LexerRule(Tag.PLUS, r'\+'),
    LexerRule(Tag.MINUS, r'\-'),
    LexerRule(Tag.MULTIPLY, '\*'),
    LexerRule(Tag.DIVIDE, r'/'),
    LexerRule(Tag.ASSIGN, r'\:='),
    LexerRule(Tag.PLUS_ASSIGN, '\+='),
    LexerRule(Tag.MINUS_ASSIGN, r'\-='),
    LexerRule(Tag.MULTIPLY_ASSIGN, '\*='),
    LexerRule(Tag.DIVIDE_ASSIGN, r'/='),
    LexerRule(Tag.RANGE, r'\.\.'),

    # boolean
    LexerRule(Tag.TRUE, r'\btrue\b'),
    LexerRule(Tag.FALSE, r'\bfalse\b'),

    # other key words
    LexerRule(Tag.VAR, r'\bvar\b'),
    LexerRule(Tag.IF, r'\bif\b'),
    LexerRule(Tag.THEN, r'\bthen\b'),
    LexerRule(Tag.ELSE, r'\belse\b'),
    LexerRule(Tag.CASE, r'\bcase\b'),
    LexerRule(Tag.OF, r'\bof\b'),
    LexerRule(Tag.FOR, r'\bfor\b'),
    LexerRule(Tag.WHILE, r'\bwhile\b'),
    LexerRule(Tag.UNTIL, r'\buntil\b'),
    LexerRule(Tag.DO, r'\bdo\b'),
    LexerRule(Tag.TO, r'\bto\b'),
    LexerRule(Tag.BEGIN, r'\bbegin\b'),
    LexerRule(Tag.END, r'\bend\b'),
    LexerRule(Tag.PROCEDURE, r'\bprocedure\b'),
    LexerRule(Tag.FUNCTION, r'\bfunction\b'),

    # general
    LexerRule(Tag.ID, r'\b[_a-zA-Z]\w*\b'),
    LexerRule(Tag.NUMBER_FLOAT, r'\b[-+]?\d+\.\d+\b'),
    LexerRule(Tag.NUMBER_INT, r'\b[-+]?[0-9]+\b'),
    LexerRule(Tag.LBRACKET, r'\('),
    LexerRule(Tag.RBRACKET, r'\)'),
    LexerRule(Tag.LBRACKET_SQUARE, r'\['),
    LexerRule(Tag.RBRACKET_SQUARE, r'\]'),
    LexerRule(Tag.SEMICOLON, r';'),
    LexerRule(Tag.COLON, r':'),
    LexerRule(Tag.COMMA, r','),
    LexerRule(Tag.DOT, r'\.'),
    LexerRule(Tag.QUOTE, r"\'"),
    LexerRule(Tag.DQUOTE, r'"'),
]

GRAMMAR_RULES = [
    GrammarRule(Special.START, {
        (NonTerm.DESCR, Tag.BEGIN, NonTerm.PROG, Tag.END, Tag.DOT)
    }),
    GrammarRule(NonTerm.DESCR, {
        (NonTerm.VARS,),
        (Special.LAMBDA,)
    }),
    GrammarRule(NonTerm.VARS, {
        (Tag.VAR, Tag.ID, Tag.ASSIGN, NonTerm.EXPR, Tag.SEMICOLON),
        (Tag.VAR, Tag.ID, Tag.COLON, NonTerm.TYPE, Tag.ASSIGN, NonTerm.EXPR,
         Tag.SEMICOLON),
    }),
    GrammarRule(NonTerm.PROG, {
        (NonTerm.VARS, NonTerm.PROG),
        (NonTerm.CALL, NonTerm.PROG),
    }),
    GrammarRule(NonTerm.EXPR, {
        (Tag.QUOTE, Tag.ID, Tag.QUOTE),
        (Tag.DQUOTE, Tag.ID, Tag.DQUOTE),
        (Tag.NUMBER_INT,),
        (Tag.NUMBER_FLOAT,),
    }),
    GrammarRule(NonTerm.CALL, {
        (Tag.ID, Tag.LBRACKET, NonTerm.ARGS, Tag.RBRACKET, Tag.SEMICOLON),
    })
]
