from pathlib import Path
from pprint import pprint
from transpiler.lexer import Lexer
from transpiler.syntax_analyzer import SyntaxAnalyzer
from transpiler.base import GrammarRule, LexerRule, Terminal, NonTerminal, Special


ROOT = Path(__file__).parent.parent.absolute()


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
    BEGIN = 'begin'
    END = 'end'
    PROCEDURE = 'procedure'
    FUNCTION = 'function'


class NT(NonTerminal):
    VARS = 'VARS'
    DEFINE_VARS = 'DEFINE_VARS'
    DEFINE_VAR_ASSIGNMENT = 'DEFINE_VAR_ASSIGNMENT'
    ANY_ASSIGN = 'ANY_ASSIGN'
    OPERATOR = 'OPERATOR'

    ABSTRACT_EXPR = 'ABSTRACT_EXPR'
    ABSTRACT_COMPLEX_EXPR = 'ABSTRACT_COMPLEX_EXPR'

    STRING_EXPR = 'STRING_EXPR'
    STRING_PART = 'STRING_PART'

    MATH_EXPR = 'MATH_EXPR'
    MATH_EXPR_RIGHT = 'MATH_EXPR_RIGHT'
    MATH_EXPR_VALUE = 'MATH_EXPR_VALUE'
    NUMBER = 'NUMBER'

    BOOLEAN_EXPR = 'BOOLEAN_EXPR'
    BOOLEAN_EXPR_RIGHT = 'BOOLEAN_EXPR_RIGHT'
    BOOLEAN_EXPR_VALUE = 'BOOLEAN_EXPR_VALUE'
    BOOLEAN_OPTIONAL_NOT = 'BOOLEAN_OPTIONAL_NOT'

    PROG = 'PROG'
    BODY = 'BODY'
    COMPLEX_OP_BODY = 'COMPLEX_OP_BODY'

    IF_BLOCK = 'IF_BLOCK'
    ELIF_BLOCK = 'ELIF_BLOCK'
    ELSE_BLOCK = 'ELSE_BLOCK'
    IF_BLOCK_HELPER = 'IF_BLOCK_HELPER'

    FOR_LOOP_BLOCK = 'FOR_LOOP_BLOCK'
    REPEAT_LOOP_BLOCK = 'REPEAT_LOOP_BLOCK'
    WHILE_LOOP_BLOCK = 'WHILE_LOOP_BLOCK'

    ABSTRACT_STATEMENT = 'ABSTRACT_STATEMENT'
    ABSTRACT_STATEMENT_HELPER = 'ABSTRACT_STATEMENT_HELPER'
    CALL = 'CALL'
    MANIPULATE_VAR = 'MANIPULATE_VAR'


LEXER_RULES = [
    LexerRule(Tag.TYPE_HINT, r'\binteger|real|boolean|char|string\b'),
    LexerRule(Tag.NUMBER_FLOAT, r'\b[-+]?\d+\.\d+\b'),
    LexerRule(Tag.NUMBER_INT, r'\b[-+]?[0-9]+\b'),
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
    LexerRule(Tag.UNTIL, r'\buntil\b'),
    LexerRule(Tag.DO, r'\bdo\b'),
    LexerRule(Tag.TO, r'\bto\b'),
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
        (NT.VARS, NT.PROG),
    }),

    # vars
    GrammarRule(NT.VARS, {
        (Tag.VAR, NT.DEFINE_VARS, NT.VARS),
        (Special.LAMBDA,)
    }),
    GrammarRule(NT.DEFINE_VARS, {
        (
            Tag.ID,
            Tag.COLON,
            Tag.TYPE_HINT,
            NT.DEFINE_VAR_ASSIGNMENT,
            Tag.SEMICOLON,
            NT.DEFINE_VARS
        ),
        (Special.LAMBDA,)
    }),
    GrammarRule(NT.DEFINE_VAR_ASSIGNMENT, {
        (Tag.ASSIGN, NT.ABSTRACT_EXPR),
        (Special.LAMBDA,)
    }),

    GrammarRule(NT.ABSTRACT_EXPR, {
        (NT.MATH_EXPR,),
        # (NT.BOOLEAN_EXPR,),
        (NT.STRING_EXPR,),
    }),

    GrammarRule(NT.STRING_EXPR, {
        (Tag.QUOTE, NT.STRING_PART, Tag.QUOTE),
    }),
    GrammarRule(NT.STRING_PART,
        {(Special.LAMBDA,)} |
        # string may contain any tag except '
        {(tag, NT.STRING_PART) for tag in Tag if tag is not Tag.QUOTE}
    ),

    GrammarRule(NT.MATH_EXPR, {
        (NT.MATH_EXPR_VALUE, NT.MATH_EXPR_RIGHT),
    }),
    GrammarRule(NT.MATH_EXPR_RIGHT, {
        (Tag.MATH_OPERATOR, NT.MATH_EXPR_VALUE, NT.MATH_EXPR_RIGHT),
        (Special.LAMBDA,),
    }),
    GrammarRule(NT.MATH_EXPR_VALUE, {
        (Tag.ID,),
        (NT.NUMBER,),
        (Tag.LBRACKET, NT.MATH_EXPR, Tag.RBRACKET),
    }),
    GrammarRule(NT.NUMBER, {
        (Tag.NUMBER_INT,),
        (Tag.NUMBER_FLOAT,),
    }),

    # GrammarRule(NT.BOOLEAN_EXPR, {
    #     (
    #         # NT.BOOLEAN_OPTIONAL_NOT,
    #         Tag.LBRACKET,
    #         # NT.BOOLEAN_OPTIONAL_NOT,
    #         NT.BOOLEAN_EXPR_VALUE,
    #         Tag.RBRACKET,
    #         NT.BOOLEAN_EXPR_RIGHT,
    #     )
    # }),
    # GrammarRule(NT.BOOLEAN_EXPR_RIGHT, {
    #     (Tag.BOOLEAN_OPERATOR, NT.BOOLEAN_EXPR),
    #     (Special.LAMBDA,),
    # }),
    # GrammarRule(NT.BOOLEAN_EXPR_VALUE, {
    #     (Tag.ID,),
    #     (Tag.BOOLEAN_VALUE,),
    #     (NT.MATH_EXPR, Tag.COMPARE, NT.MATH_EXPR),
    # }),
    # GrammarRule(NT.BOOLEAN_OPTIONAL_NOT, {
    #     (Tag.BOOLEAN_NOT,),
    #     (Special.LAMBDA,),
    # }),

    # prog
    GrammarRule(NT.PROG, {
        (Tag.BEGIN, NT.BODY, Tag.END, Tag.DOT)
    }),
    GrammarRule(NT.COMPLEX_OP_BODY, {
        (Tag.BEGIN, NT.BODY, Tag.END),
        (NT.ABSTRACT_STATEMENT,)
    }),
    GrammarRule(NT.BODY, {
        (NT.ABSTRACT_STATEMENT, NT.BODY),
        (Special.LAMBDA,),
    }),

    GrammarRule(NT.ABSTRACT_STATEMENT, {
        (Tag.ID, NT.ABSTRACT_STATEMENT_HELPER, Tag.SEMICOLON),
    }),
    GrammarRule(NT.ABSTRACT_STATEMENT_HELPER, {
        (NT.CALL,),
        (NT.MANIPULATE_VAR,),
    }),

    GrammarRule(NT.MANIPULATE_VAR, {
        (NT.ANY_ASSIGN, NT.ABSTRACT_EXPR),
    }),
    GrammarRule(NT.ANY_ASSIGN, {
        (Tag.ASSIGN,),
        (Tag.OP_ASSIGN,),
    }),

    GrammarRule(NT.IF_BLOCK, {
        (
            Tag.IF,
            NT.IF_BLOCK_HELPER,
            NT.ELIF_BLOCK,
            NT.ELSE_BLOCK,
            Tag.SEMICOLON
        ),
    }),
    GrammarRule(NT.IF_BLOCK_HELPER, {
        (NT.BOOLEAN_EXPR, Tag.THEN, NT.COMPLEX_OP_BODY)
    }),
    GrammarRule(NT.ELIF_BLOCK, {
        (Tag.ELSE, Tag.IF, NT.IF_BLOCK_HELPER),
    }),
    GrammarRule(NT.ELSE_BLOCK, {
        (Tag.ELSE, NT.COMPLEX_OP_BODY,),
        (Special.LAMBDA,)
    })
]

code = (ROOT / 'examples/supported_syntax.pas').read_text()

lexer = Lexer(Tag, LEXER_RULES)
lexer.buffer = code

syntax_analyzer = SyntaxAnalyzer(GRAMMAR_RULES)
syntax_analyzer.parse(lexer.tokens)
