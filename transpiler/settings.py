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


LEXER_REGEX_FLAGS = re.IGNORECASE


class Tag(Terminal):
    ID = 'id'
    NUMBER_INT = 'number_int'
    NUMBER_FLOAT = 'number_float'
    LBRACKET = 'lbracket'
    RBRACKET = 'rbracket'
    LBRACKET_SQUARE = 'lbracket_square'
    RBRACKET_SQUARE = 'rbracket_square'
    SEMICOLON = 'semicolon'
    COLON = 'colon'
    COMMA = 'comma'
    DOT = 'dot'
    QUOTE = "quote"
    TYPE_HINT = 'type_hint'
    COMPARE = 'compare'
    MATH_OPERATOR = 'math_operator'
    BOOLEAN_OPERATOR = 'boolean_operator'
    BOOLEAN_NOT = 'boolean_not'
    ASSIGN = 'assign'
    OP_ASSIGN = 'op_assign'
    RANGE = 'range'
    BOOLEAN_VALUE = 'boolean_value'

    VAR = 'var'
    IF = 'if'
    THEN = 'then'
    ELSE = 'else'
    CASE = 'case'
    OF = 'of'
    FOR = 'for'
    WHILE = 'while'
    REPEAT = 'repeat'
    UNTIL = 'until'
    DO = 'do'
    TO = 'to'
    DOWNTO = 'downto'
    BEGIN = 'begin'
    END = 'end'
    PROCEDURE = 'procedure'
    FUNCTION = 'function'


class NT(NonTerminal):
    VARS = 'VARS'
    DEFINE_VAR = 'DEFINE_VAR'
    DEFINE_VAR_WITHOUT_SEMICOLON = 'DEFINE_VAR_WITHOUT_SEMICOLON'
    DEFINE_VARS_RECURSIVE = 'DEFINE_VARS_RECURSIVE'
    DEFINE_VAR_ASSIGNMENT = 'DEFINE_VAR_ASSIGNMENT'
    OPTIONAL_DEFINE_VAR_ASSIGNMENT = 'OPTIONAL_DEFINE_VAR_ASSIGNMENT'
    DEFINE_INLINE_VAR = 'DEFINE_INLINE_VAR'
    ANY_ASSIGN = 'ANY_ASSIGN'
    OPERATOR = 'OPERATOR'

    ABSTRACT_EXPR = 'ABSTRACT_EXPR'

    STRING_EXPR = 'STRING_EXPR'
    STRING_PART = 'STRING_PART'

    ABSTRACT_EXPR_RIGHT = 'ABSTRACT_EXPR_RIGHT'
    ABSTRACT_EXPR_VALUE = 'ABSTRACT_EXPR_VALUE'
    ABSTRACT_EXPR_OP = 'ABSTRACT_EXPR_OP'
    ABSTRACT_EXPR_WITH_NOT = 'ABSTRACT_EXPR_WITH_NOT'

    NUMBER = 'NUMBER'
    BOOLEAN_OPTIONAL_NOT = 'BOOLEAN_OPTIONAL_NOT'
    OPTIONAL_CALL = 'OPTIONAL_CALL'
    COMPARABLE = 'COMPARABLE'

    PROG = 'PROG'
    BODY = 'BODY'
    COMPLEX_OP_BODY = 'COMPLEX_OP_BODY'

    IF_BLOCK = 'IF_BLOCK'
    OPTIONAL_ELSE_BLOCK = 'OPTIONAL_ELSE_BLOCK'
    ELSE_BLOCK_RIGHT = 'ELSE_BLOCK_RIGHT'
    ELIF_BLOCK = 'ELIF_BLOCK'
    ELSE_BLOCK = 'ELSE_BLOCK'
    IF_BLOCK_RIGHT = 'IF_BLOCK_RIGHT'

    FOR_LOOP_BLOCK = 'FOR_LOOP_BLOCK'
    FOR_LOOP_KEY = 'FOR_LOOP_KEY'

    REPEAT_LOOP_BLOCK = 'REPEAT_LOOP_BLOCK'
    WHILE_LOOP_BLOCK = 'WHILE_LOOP_BLOCK'

    ABSTRACT_STATEMENT = 'ABSTRACT_STATEMENT'
    ABSTRACT_STATEMENT_RIGHT = 'ABSTRACT_STATEMENT_RIGHT'

    CALL = 'CALL'
    CALL_ARGS = 'CALL_ARGS'
    CALL_ARGS_RIGHT = 'CALL_ARGS_RIGHT'

    MANIPULATE_VAR = 'MANIPULATE_VAR'


LEXER_RULES = [
    LexerRule(Tag.TYPE_HINT, r'\binteger|real|boolean|char|string\b'),
    LexerRule(Tag.NUMBER_FLOAT, r'[\-\+]?\d+\.\d+'),
    LexerRule(Tag.NUMBER_INT, r'[\-\+]?\d+'),
    LexerRule(Tag.COMPARE, r'=|\<\>|\<=|\<|\>=|\>'),
    LexerRule(Tag.OP_ASSIGN, r'\+=|\-=|\*=|/='),
    LexerRule(Tag.MATH_OPERATOR, r'\+|\-|\*|/'),
    LexerRule(Tag.BOOLEAN_OPERATOR, r'\band|or|xor\b'),
    LexerRule(Tag.BOOLEAN_NOT, r'\bnot\b'),
    LexerRule(Tag.ASSIGN, r'\:='),
    LexerRule(Tag.RANGE, r'\.\.'),
    LexerRule(Tag.BOOLEAN_VALUE, r'\btrue|false\b'),

    LexerRule(Tag.VAR, r'\bvar\b'),
    LexerRule(Tag.IF, r'\bif\b'),
    LexerRule(Tag.THEN, r'\bthen\b'),
    LexerRule(Tag.ELSE, r'\belse\b'),
    LexerRule(Tag.CASE, r'\bcase\b'),
    LexerRule(Tag.OF, r'\bof\b'),
    LexerRule(Tag.FOR, r'\bfor\b'),
    LexerRule(Tag.WHILE, r'\bwhile\b'),
    LexerRule(Tag.REPEAT, r'\brepeat\b'),
    LexerRule(Tag.UNTIL, r'\buntil\b'),
    LexerRule(Tag.DO, r'\bdo\b'),
    LexerRule(Tag.TO, r'\bto\b'),
    LexerRule(Tag.DOWNTO, r'\bdownto\b'),
    LexerRule(Tag.BEGIN, r'\bbegin\b'),
    LexerRule(Tag.END, r'\bend\b'),
    LexerRule(Tag.PROCEDURE, r'\bprocedure\b'),
    LexerRule(Tag.FUNCTION, r'\bfunction\b'),

    LexerRule(Tag.ID, r'\b[_a-zA-Z]\w*\b'),
    LexerRule(Tag.LBRACKET, r'\('),
    LexerRule(Tag.RBRACKET, r'\)'),
    LexerRule(Tag.LBRACKET_SQUARE, r'\['),
    LexerRule(Tag.RBRACKET_SQUARE, r'\]'),
    LexerRule(Tag.SEMICOLON, r';'),
    LexerRule(Tag.COLON, r':'),
    LexerRule(Tag.COMMA, r','),
    LexerRule(Tag.DOT, r'\.'),
    LexerRule(Tag.QUOTE, r"\'"),
]

GRAMMAR_RULES = [
    GrammarRule(Special.START, {
        (NT.DEFINE_VARS_RECURSIVE, NT.PROG),
    }),

    # vars
    GrammarRule(NT.DEFINE_VARS_RECURSIVE, {
        (NT.DEFINE_VAR, NT.DEFINE_VARS_RECURSIVE),
        (Special.LAMBDA,),
    }),
    GrammarRule(NT.DEFINE_VAR, {
        (
            Tag.VAR,
            Tag.ID,
            Tag.COLON,
            Tag.TYPE_HINT,
            NT.OPTIONAL_DEFINE_VAR_ASSIGNMENT,
            Tag.SEMICOLON,
        ),
    }),
    GrammarRule(NT.DEFINE_VAR_WITHOUT_SEMICOLON, {
        (
            Tag.VAR,
            Tag.ID,
            Tag.COLON,
            Tag.TYPE_HINT,
            NT.OPTIONAL_DEFINE_VAR_ASSIGNMENT,
        ),
    }),
    GrammarRule(NT.OPTIONAL_DEFINE_VAR_ASSIGNMENT, {
        (Tag.ASSIGN, NT.ABSTRACT_EXPR),
        (Special.LAMBDA,)
    }),
    GrammarRule(NT.DEFINE_VAR_ASSIGNMENT, {
        (Tag.ASSIGN, NT.ABSTRACT_EXPR),
    }),
    GrammarRule(NT.DEFINE_INLINE_VAR, {
        (
            Tag.VAR,
            Tag.ID,
            Tag.COLON,
            Tag.TYPE_HINT,
            NT.DEFINE_VAR_ASSIGNMENT,
        ),
    }),

    # strings
    GrammarRule(NT.STRING_EXPR, {
        (Tag.QUOTE, NT.STRING_PART, Tag.QUOTE),
    }),
    GrammarRule(NT.STRING_PART,
        {(Special.LAMBDA,)} |
        # string may contain any tag except '
        {(tag, NT.STRING_PART) for tag in Tag if tag is not Tag.QUOTE}
    ),

    # boolean and math expressions
    GrammarRule(NT.ABSTRACT_EXPR, {
        (NT.ABSTRACT_EXPR_VALUE, NT.ABSTRACT_EXPR_RIGHT),
    }),
    GrammarRule(NT.ABSTRACT_EXPR_RIGHT, {
        (
            NT.ABSTRACT_EXPR_OP,
            NT.ABSTRACT_EXPR_VALUE,
            NT.ABSTRACT_EXPR_RIGHT,
        ),
        (Special.LAMBDA,)
    }),
    GrammarRule(NT.ABSTRACT_EXPR_VALUE, {
        (NT.NUMBER,),
        (Tag.ID, NT.OPTIONAL_CALL),
        (Tag.BOOLEAN_VALUE,),
        (NT.BOOLEAN_OPTIONAL_NOT, NT.ABSTRACT_EXPR_WITH_NOT),
        (NT.STRING_EXPR,),
    }),
    GrammarRule(NT.ABSTRACT_EXPR_OP, {
        (Tag.MATH_OPERATOR,),
        (Tag.BOOLEAN_OPERATOR,),
        (Tag.COMPARE,),
    }),
    GrammarRule(NT.NUMBER, {
        (Tag.NUMBER_INT,),
        (Tag.NUMBER_FLOAT,),
    }),
    GrammarRule(NT.ABSTRACT_EXPR_WITH_NOT, {
        (Tag.LBRACKET, NT.ABSTRACT_EXPR, Tag.RBRACKET),
    }),
    GrammarRule(NT.BOOLEAN_OPTIONAL_NOT, {
        (Tag.BOOLEAN_NOT,),
        (Special.LAMBDA,),
    }),
    GrammarRule(NT.OPTIONAL_CALL, {
        (NT.CALL,),
        (Special.LAMBDA,)
    }),
    GrammarRule(NT.COMPARABLE, {
        (Tag.ID,),
        (Tag.BOOLEAN_VALUE,),
        (NT.NUMBER,),
        (NT.STRING_EXPR,)
    }),

    # prog
    GrammarRule(NT.PROG, {
        (Tag.BEGIN, NT.BODY, Tag.END, Tag.DOT)
    }),
    GrammarRule(NT.COMPLEX_OP_BODY, {
        (Tag.BEGIN, NT.BODY, Tag.END),
        (NT.ABSTRACT_STATEMENT,),
        (NT.DEFINE_VAR_WITHOUT_SEMICOLON,),
    }),
    GrammarRule(NT.BODY, {
        (NT.DEFINE_VAR, NT.BODY),
        (NT.ABSTRACT_STATEMENT, Tag.SEMICOLON, NT.BODY),
        (NT.IF_BLOCK, NT.BODY),
        (NT.FOR_LOOP_BLOCK, NT.BODY),
        (NT.WHILE_LOOP_BLOCK, NT.BODY),
        (NT.REPEAT_LOOP_BLOCK, NT.BODY),
        (Special.LAMBDA,),
    }),

    # any statement except variable defining
    GrammarRule(NT.ABSTRACT_STATEMENT, {
        (Tag.ID, NT.ABSTRACT_STATEMENT_RIGHT),
    }),
    GrammarRule(NT.ABSTRACT_STATEMENT_RIGHT, {
        (NT.CALL,),
        (NT.MANIPULATE_VAR,),
    }),

    # do something with existing variable
    GrammarRule(NT.MANIPULATE_VAR, {
        (NT.ANY_ASSIGN, NT.ABSTRACT_EXPR),
    }),
    GrammarRule(NT.ANY_ASSIGN, {
        (Tag.ASSIGN,),
        (Tag.OP_ASSIGN,),
    }),

    # call function with or without arguments
    GrammarRule(NT.CALL, {
        (Tag.LBRACKET, NT.CALL_ARGS, Tag.RBRACKET),
    }),
    GrammarRule(NT.CALL_ARGS, {
        (NT.ABSTRACT_EXPR, NT.CALL_ARGS_RIGHT),
        (Special.LAMBDA,)
    }),
    GrammarRule(NT.CALL_ARGS_RIGHT, {
        (Tag.COMMA, NT.ABSTRACT_EXPR),
        (Special.LAMBDA,)
    }),

    # if blocks, with optional else if and else
    GrammarRule(NT.IF_BLOCK, {
        (
            Tag.IF,
            NT.IF_BLOCK_RIGHT,
            NT.ELSE_BLOCK,
            Tag.SEMICOLON
        ),
    }),
    GrammarRule(NT.IF_BLOCK_RIGHT, {
        (NT.ABSTRACT_EXPR, Tag.THEN, NT.COMPLEX_OP_BODY)
    }),
    GrammarRule(NT.ELSE_BLOCK, {
        (Tag.ELSE, NT.ELSE_BLOCK_RIGHT, NT.ELSE_BLOCK),
        (Special.LAMBDA,),
    }),
    GrammarRule(NT.ELSE_BLOCK_RIGHT, {
        (NT.COMPLEX_OP_BODY,),
        (Tag.IF, NT.IF_BLOCK_RIGHT),
    }),

    # for loops with to or downto word
    GrammarRule(NT.FOR_LOOP_BLOCK, {
        (
            Tag.FOR,
            NT.DEFINE_INLINE_VAR,
            NT.FOR_LOOP_KEY,
            NT.ABSTRACT_EXPR,
            Tag.DO,
            NT.COMPLEX_OP_BODY,
            Tag.SEMICOLON,
        ),
    }),
    GrammarRule(NT.FOR_LOOP_KEY, {
        (Tag.TO,),
        (Tag.DOWNTO,)
    }),

    # while loops
    GrammarRule(NT.WHILE_LOOP_BLOCK, {
        (
            Tag.WHILE,
            NT.ABSTRACT_EXPR,
            Tag.DO,
            NT.COMPLEX_OP_BODY,
            Tag.SEMICOLON
        )
    }),

    # repeat loops
    GrammarRule(NT.REPEAT_LOOP_BLOCK, {
        (Tag.REPEAT, NT.BODY, Tag.UNTIL, NT.ABSTRACT_EXPR, Tag.SEMICOLON),
    })
]


SHARP_FUNCTIONS = {
    "print": "Console.WriteLine",
    "sqrt": "Sqrt",
    "exp": "Exp",
    "sqr": "Sqr"
}
