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
    OPERATOR = 'operator'
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
    DEFINE_VARS_HELPER = 'DEFINE_VARS_HELPER'
    MANIPULATE_VAR = 'MANIPULATE_VAR'
    MANIPULATE_VAR_HELPER = 'MANIPULATE_VAR_HELPER'
    ANY_ASSIGN = 'ANY_ASSIGN'
    ID_OR_EXPRESSION = 'ID_OR_EXPRESSION'

    ABSTRACT_EXPRESSION = 'ABSTRACT_EXPRESSION'

    STRING_EXPRESSION = 'STRING_EXPRESSION'
    STRING_PART = 'STRING_PART'

    NUMBER_EXPRESSION = 'NUMBER_EXPRESSION'
    NUMBER = 'NUMBER'
    _NUMBER_EXPRESSION = '_NUMBER_EXPRESSION'
    NUMBER_EXPRESSION_HELPER = 'NUMBER_EXPRESSION_HELPER'

    PROG = 'PROG'
    PROG_BODY = 'PROG_BODY'
    IF_CONDITION = 'IF_CONDITION'
    CONDITION = 'CONDITION'
    COMPLEX_OP_BODY = 'COMPLEX_OP_BODY'
    SINGLE_OPERATION = 'SINGLE_OPERATION'


LEXER_RULES = [
    LexerRule(Tag.TYPE_HINT, r'\binteger|real|boolean|char|string\b'),
    LexerRule(Tag.COMPARE, r'=|\<\>|\<=|\<|\>=|\>'),
    LexerRule(Tag.OP_ASSIGN, r'\+=|\-=|\*=|/='),
    LexerRule(Tag.OPERATOR, r'\+|\-|\*|/'),
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
            NT.DEFINE_VARS_HELPER,
        ),
    }),
    GrammarRule(NT.DEFINE_VARS_HELPER, {
        (NT.DEFINE_VARS,),
        (Special.LAMBDA,)
    }),
    GrammarRule(NT.DEFINE_VAR_ASSIGNMENT, {
        (Tag.ASSIGN, NT.ABSTRACT_EXPRESSION),
        (Special.LAMBDA,)
    }),
    GrammarRule(NT.ABSTRACT_EXPRESSION, {
        (Tag.BOOLEAN_VALUE,),
        (NT.STRING_EXPRESSION,),
        (NT.NUMBER_EXPRESSION,),
    }),
    GrammarRule(NT.STRING_EXPRESSION, {
        (Tag.QUOTE, NT.STRING_PART, Tag.QUOTE),
    }),
    GrammarRule(NT.STRING_PART, {
        (Tag.ID, NT.STRING_PART),
        (Special.LAMBDA,),
    }),
    GrammarRule(NT.NUMBER_EXPRESSION, {
        (NT.NUMBER_EXPRESSION_HELPER, NT._NUMBER_EXPRESSION),
    }),
    GrammarRule(NT._NUMBER_EXPRESSION, {
        (Tag.OPERATOR, NT.NUMBER_EXPRESSION_HELPER, NT._NUMBER_EXPRESSION),
        (Special.LAMBDA,),
    }),
    GrammarRule(NT.NUMBER_EXPRESSION_HELPER, {
        (Tag.LBRACKET, NT.NUMBER_EXPRESSION, Tag.RBRACKET),
        (NT.NUMBER,),
    }),
    GrammarRule(NT.NUMBER, {
        (Tag.NUMBER_INT,),
        (Tag.NUMBER_FLOAT,),
    }),
    GrammarRule(NT.MANIPULATE_VAR, {
        (
            Tag.ID,
            NT.ANY_ASSIGN,
            NT.ID_OR_EXPRESSION,
            Tag.SEMICOLON,
            NT.MANIPULATE_VAR,
        ),
        (Special.LAMBDA,)
    }),
    GrammarRule(NT.ANY_ASSIGN, {
        (Tag.ASSIGN,),
        (Tag.OP_ASSIGN,),
    }),
    GrammarRule(NT.ID_OR_EXPRESSION, {
        (Tag.ID,),
        (NT.ABSTRACT_EXPRESSION,),
    }),

    # prog
    GrammarRule(NT.PROG, {
        (Tag.BEGIN, NT.PROG_BODY, Tag.END, Tag.DOT)
    }),
    GrammarRule(NT.PROG_BODY, {
        (NT.MANIPULATE_VAR,)
    }),
    GrammarRule(NT.IF_CONDITION, {
        (Tag.IF, NT.CONDITION, Tag.THEN, NT.COMPLEX_OP_BODY)
    }),
    GrammarRule(NT.COMPLEX_OP_BODY, {
        (Tag.BEGIN, NT.PROG_BODY, Tag.END, Tag.SEMICOLON),
        (NT.SINGLE_OPERATION,)
    })
]

code = (ROOT / 'examples/supported_syntax.pas').read_text()

lexer = Lexer(Tag, LEXER_RULES)
lexer.buffer = code

syntax_analyzer = SyntaxAnalyzer(GRAMMAR_RULES)
syntax_analyzer.parse(lexer.tokens)
