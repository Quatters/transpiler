import logging
from unittest import TestCase
from transpiler.base import (
    Token,
    GrammarRule,
    LexerRule,
    NormalizedGrammarRule,
    Special,
    Terminal,
    NonTerminal,
)
from transpiler.lexer import Lexer, UnexpectedTokenError
from transpiler.syntax_analyzer import GrammarError, SyntaxAnalyzer
from transpiler.semantic_analyzer import SemanticAnalyzer, SemanticError, TranspilerError
from transpiler import settings


logger = logging.getLogger(__name__)

class NonTerm(NonTerminal):
    DESCR = 'DESCR'
    PROG = 'PROG'
    VARS = 'VARS'
    EXPR = 'EXPR'
    TYPE = 'TYPE'
    CALL = 'CALL'
    ARGS = 'ARGS'


class Tag(Terminal):
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


class MathTerminal(Terminal):
    NUM = 'NUM',
    PLUS = '+'
    MULTIPLY = '*'
    LBRACKET = '('
    RBRACKET = ')'


class MathNonTerminal(NonTerminal):
    E = 'E'
    T = 'T'
    _E = '_E'
    _T = '_T'
    F = 'F'


class LexerTestCase(TestCase):
    def test_invalid_token(self):
        code = """
            begi%n
            end.
        """
        lexer = Lexer(Tag, LEXER_RULES)
        lexer.buffer = code
        with self.assertRaises(UnexpectedTokenError) as error:
            list(lexer.tokens)
        self.assertEqual(str(error.exception), r"'%' at line 2")

    def test_types(self):
        code = """
            var
                var1 := 'var1';
                var2: integer := 2;
                var3: BooLeAn := tRUe;
                var4: real := 146.00;
                var5: array [1..3] of string;

            begin
                writeln(var1);
            end.
        """

        lexer = Lexer(Tag, LEXER_RULES)
        lexer.buffer = code
        tokens = list(lexer.tokens)

        self.assertEqual(tokens[0].tag, Tag.VAR)
        self.assertEqual(tokens[1].tag, Tag.ID)
        self.assertEqual(tokens[2].tag, Tag.ASSIGN)
        self.assertEqual(tokens[3].tag, Tag.QUOTE)
        self.assertEqual(tokens[4].tag, Tag.ID)
        self.assertEqual(tokens[5].tag, Tag.QUOTE)
        self.assertEqual(tokens[6].tag, Tag.SEMICOLON)
        self.assertEqual(tokens[7].tag, Tag.ID)
        self.assertEqual(tokens[8].tag, Tag.COLON)
        self.assertEqual(tokens[9].tag, Tag.T_INTEGER)
        self.assertEqual(tokens[10].tag, Tag.ASSIGN)
        self.assertEqual(tokens[11].tag, Tag.NUMBER_INT)
        self.assertEqual(tokens[12].tag, Tag.SEMICOLON)
        self.assertEqual(tokens[13].tag, Tag.ID)
        self.assertEqual(tokens[14].tag, Tag.COLON)
        self.assertEqual(tokens[15].tag, Tag.T_BOOLEAN)
        self.assertEqual(tokens[16].tag, Tag.ASSIGN)
        self.assertEqual(tokens[17].tag, Tag.TRUE)
        self.assertEqual(tokens[18].tag, Tag.SEMICOLON)
        self.assertEqual(tokens[19].tag, Tag.ID)
        self.assertEqual(tokens[20].tag, Tag.COLON)
        self.assertEqual(tokens[21].tag, Tag.T_REAL)
        self.assertEqual(tokens[22].tag, Tag.ASSIGN)
        self.assertEqual(tokens[23].tag, Tag.NUMBER_FLOAT)
        self.assertEqual(tokens[24].tag, Tag.SEMICOLON)
        self.assertEqual(tokens[25].tag, Tag.ID)
        self.assertEqual(tokens[26].tag, Tag.COLON)
        self.assertEqual(tokens[27].tag, Tag.T_ARRAY)
        self.assertEqual(tokens[28].tag, Tag.LBRACKET_SQUARE)
        self.assertEqual(tokens[29].tag, Tag.NUMBER_INT)
        self.assertEqual(tokens[30].tag, Tag.RANGE)
        self.assertEqual(tokens[31].tag, Tag.NUMBER_INT)
        self.assertEqual(tokens[32].tag, Tag.RBRACKET_SQUARE)
        self.assertEqual(tokens[33].tag, Tag.OF)
        self.assertEqual(tokens[34].tag, Tag.T_STRING)
        self.assertEqual(tokens[35].tag, Tag.SEMICOLON)
        self.assertEqual(tokens[36].tag, Tag.BEGIN)
        self.assertEqual(tokens[37].tag, Tag.ID)
        self.assertEqual(tokens[38].tag, Tag.LBRACKET)
        self.assertEqual(tokens[39].tag, Tag.ID)
        self.assertEqual(tokens[40].tag, Tag.RBRACKET)
        self.assertEqual(tokens[41].tag, Tag.SEMICOLON)
        self.assertEqual(tokens[42].tag, Tag.END)
        self.assertEqual(tokens[43].tag, Tag.DOT)


class SyntaxAnalyzerTestCase(TestCase):
    """
    Reference: https://mikedevice.github.io/first-follow/
    """

    simple_rules = [
        # Prog⟶var Vars begin Expr end
        # Vars⟶
        # Expr⟶t_integer semicolon

        GrammarRule(NonTerm.PROG, {
            (Tag.VAR, NonTerm.VARS, Tag.BEGIN, NonTerm.EXPR, Tag.END),
        }),
        GrammarRule(NonTerm.VARS, {
            (Special.LAMBDA,),
        }),
        GrammarRule(NonTerm.EXPR, {
            (Tag.T_INTEGER, Tag.SEMICOLON),
        }),
    ]

    complex_rules = [
        # _Start⟶Descr begin Prog end dot
        # Descr⟶Vars
        # Descr⟶
        # Vars⟶var id assign Expr semicolon
        # Vars⟶var id colon Type assign Expr semicolon
        # Prog⟶Vars Prog
        # Prog⟶Call Prog
        # Expr⟶quote id quote
        # Expr⟶dquoute id dquote
        # Expr⟶number_int
        # Expr⟶number_float
        # Call⟶id lbracket Args rbracket semicolon
        # Type⟶t_integer
        # Type⟶t_real
        # Type⟶t_boolean
        # Type⟶t_string
        # Type⟶t_char
        # Type⟶t_array
        # Args⟶id

        GrammarRule(Special.START, {
            (NonTerm.DESCR, Tag.BEGIN, NonTerm.PROG, Tag.END, Tag.DOT)
        }),
        GrammarRule(NonTerm.DESCR, {
            (NonTerm.VARS,),
            (Special.LAMBDA,)
        }),
        GrammarRule(NonTerm.VARS, {
            (Tag.VAR, Tag.ID, Tag.ASSIGN, NonTerm.EXPR, Tag.SEMICOLON),
            (Tag.VAR, Tag.ID, Tag.COLON, NonTerm.TYPE, Tag.ASSIGN,
             NonTerm.EXPR, Tag.SEMICOLON),
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
            (Tag.ID, Tag.LBRACKET, NonTerm.ARGS, Tag.RBRACKET,
             Tag.SEMICOLON),
        }),
        GrammarRule(NonTerm.TYPE, {
            (Tag.T_INTEGER,),
            (Tag.T_REAL,),
            (Tag.T_BOOLEAN,),
            (Tag.T_STRING,),
            (Tag.T_CHAR,),
            (Tag.T_ARRAY,),
        }),
        GrammarRule(NonTerm.ARGS, {
            (Tag.ID,),
        }),
    ]

    math_expression_rules = [
        GrammarRule(MathNonTerminal.E, {
            (MathNonTerminal.T, MathNonTerminal._E)
        }),
        GrammarRule(MathNonTerminal._E, {
            (MathTerminal.PLUS, MathNonTerminal.T, MathNonTerminal._E),
            (Special.LAMBDA,)
        }),
        GrammarRule(MathNonTerminal.T, {
            (MathNonTerminal.F, MathNonTerminal._T),
        }),
        GrammarRule(MathNonTerminal._T, {
            (MathTerminal.MULTIPLY, MathNonTerminal.F, MathNonTerminal._T),
            (Special.LAMBDA,)
        }),
        GrammarRule(MathNonTerminal.F, {
            (MathTerminal.LBRACKET, MathNonTerminal.E, MathTerminal.RBRACKET),
            (MathTerminal.NUM,)
        })
    ]

    normalized_math_expression_rules = [
        NormalizedGrammarRule(
            MathNonTerminal.E,
            (MathNonTerminal.T, MathNonTerminal._E)
        ),
        NormalizedGrammarRule(
            MathNonTerminal._E,
            (MathTerminal.PLUS, MathNonTerminal.T, MathNonTerminal._E)
        ),
        NormalizedGrammarRule(
            MathNonTerminal._E,
            (Special.LAMBDA,)
        ),
        NormalizedGrammarRule(
            MathNonTerminal.T,
            (MathNonTerminal.F, MathNonTerminal._T)
        ),
        NormalizedGrammarRule(
            MathNonTerminal._T,
            (MathTerminal.MULTIPLY, MathNonTerminal.F, MathNonTerminal._T)
        ),
        NormalizedGrammarRule(
            MathNonTerminal._T,
            (Special.LAMBDA,)
        ),
        NormalizedGrammarRule(
            MathNonTerminal.F,
            (MathTerminal.NUM,)
        ),
        NormalizedGrammarRule(
            MathNonTerminal.F,
            (MathTerminal.LBRACKET, MathNonTerminal.E, MathTerminal.RBRACKET)
        ),
    ]

    def test_math_expression_rules(self):
        sa = SyntaxAnalyzer(self.math_expression_rules)

        # check FIRST
        self.assertSetEqual(
            sa.first(MathNonTerminal.E),
            {MathTerminal.NUM, MathTerminal.LBRACKET}
        )
        self.assertSetEqual(
            sa.first(MathNonTerminal._E),
            {Special.LAMBDA, MathTerminal.PLUS}
        )
        self.assertSetEqual(
            sa.first(MathNonTerminal.T),
            {MathTerminal.NUM, MathTerminal.LBRACKET}
        )
        self.assertSetEqual(
            sa.first(MathNonTerminal._T),
            {Special.LAMBDA, MathTerminal.MULTIPLY}
        )
        self.assertSetEqual(
            sa.first(MathNonTerminal.F),
            {MathTerminal.NUM, MathTerminal.LBRACKET}
        )

        # check FOLLOW
        self.assertSetEqual(
            sa.follow(MathNonTerminal.E),
            {Special.LIMITER, MathTerminal.RBRACKET}
        )
        self.assertSetEqual(
            sa.follow(MathNonTerminal._E),
            {Special.LIMITER, MathTerminal.RBRACKET}
        )
        self.assertSetEqual(
            sa.follow(MathNonTerminal.T),
            {Special.LIMITER, MathTerminal.RBRACKET, MathTerminal.PLUS}
        )
        self.assertSetEqual(
            sa.follow(MathNonTerminal._T),
            {Special.LIMITER, MathTerminal.RBRACKET, MathTerminal.PLUS}
        )
        self.assertSetEqual(
            sa.follow(MathNonTerminal.F),
            {Special.LIMITER, MathTerminal.RBRACKET, MathTerminal.PLUS,
             MathTerminal.MULTIPLY}
        )

        # check predict table
        self.assertEqual(
            sa._predict_table[MathNonTerminal.E][MathTerminal.NUM],
            self.normalized_math_expression_rules[0],
        )
        self.assertEqual(
            sa._predict_table[MathNonTerminal.E][MathTerminal.LBRACKET],
            self.normalized_math_expression_rules[0],
        )

        self.assertEqual(
            sa._predict_table[MathNonTerminal._E][MathTerminal.PLUS],
            self.normalized_math_expression_rules[1],
        )
        self.assertEqual(
            sa._predict_table[MathNonTerminal._E][MathTerminal.RBRACKET],
            self.normalized_math_expression_rules[2],
        )
        self.assertEqual(
            sa._predict_table[MathNonTerminal._E][Special.LIMITER],
            self.normalized_math_expression_rules[2],
        )

        self.assertEqual(
            sa._predict_table[MathNonTerminal.T][MathTerminal.NUM],
            self.normalized_math_expression_rules[3],
        )
        self.assertEqual(
            sa._predict_table[MathNonTerminal.T][MathTerminal.LBRACKET],
            self.normalized_math_expression_rules[3],
        )

        self.assertEqual(
            sa._predict_table[MathNonTerminal._T][MathTerminal.PLUS],
            self.normalized_math_expression_rules[5],
        )
        self.assertEqual(
            sa._predict_table[MathNonTerminal._T][MathTerminal.MULTIPLY],
            self.normalized_math_expression_rules[4],
        )
        self.assertEqual(
            sa._predict_table[MathNonTerminal._T][MathTerminal.RBRACKET],
            self.normalized_math_expression_rules[5],
        )
        self.assertEqual(
            sa._predict_table[MathNonTerminal._T][Special.LIMITER],
            self.normalized_math_expression_rules[5],
        )

        self.assertEqual(
            sa._predict_table[MathNonTerminal.F][MathTerminal.NUM],
            self.normalized_math_expression_rules[6],
        )
        self.assertEqual(
            sa._predict_table[MathNonTerminal.F][MathTerminal.LBRACKET],
            self.normalized_math_expression_rules[7],
        )

        # check parsing
        def tokens():
            yield Token(MathTerminal.NUM, '1', 0, 1)
            yield Token(MathTerminal.PLUS, '+', 0, 1)
            yield Token(MathTerminal.NUM, '2', 0, 1)
            yield Token(MathTerminal.MULTIPLY, '*', 0, 1)
            yield Token(MathTerminal.NUM, '3', 0, 1)
            yield Token(Special.LIMITER, Special.LIMITER.value)

        sa.parse(tokens())

    def test_first_set_simple_rules(self):
        sa = SyntaxAnalyzer(self.simple_rules)

        self.assertDictEqual(sa._first, {
            NonTerm.PROG: {Tag.VAR},
            NonTerm.VARS: {Special.LAMBDA},
            NonTerm.EXPR: {Tag.T_INTEGER},
        })

    def test_first_set_complex_rules(self):
        with self.assertRaises(GrammarError):
            sa = SyntaxAnalyzer(self.complex_rules)

            self.assertSetEqual(
                sa._first[Special.START],
                {Tag.BEGIN, Tag.VAR},
            )
            self.assertSetEqual(
                sa._first[NonTerm.DESCR],
                {Tag.VAR, Special.LAMBDA},
                NonTerm.DESCR
            )
            self.assertSetEqual(
                sa._first[NonTerm.VARS],
                {Tag.VAR},
                NonTerm.VARS
            )
            self.assertSetEqual(
                sa._first[NonTerm.PROG],
                {Tag.VAR, Tag.ID},
                NonTerm.PROG
            )
            self.assertSetEqual(
                sa._first[NonTerm.EXPR],
                {Tag.QUOTE, Tag.DQUOTE, Tag.NUMBER_INT, Tag.NUMBER_FLOAT},
                NonTerm.EXPR
            )
            self.assertSetEqual(
                sa._first[NonTerm.CALL],
                {Tag.ID},
                NonTerm.CALL
            )
            self.assertSetEqual(
                sa._first[NonTerm.TYPE],
                {Tag.T_INTEGER, Tag.T_REAL, Tag.T_BOOLEAN, Tag.T_CHAR,
                 Tag.T_STRING, Tag.T_ARRAY}
            )
            self.assertSetEqual(
                sa._first[NonTerm.ARGS],
                {Tag.ID},
            )

    def test_follow_set_simple_rules(self):
        sa = SyntaxAnalyzer(self.simple_rules)

        self.assertDictEqual(sa._follow, {
            NonTerm.PROG: {Special.LIMITER},
            NonTerm.VARS: {Tag.BEGIN},
            NonTerm.EXPR: {Tag.END},
        })

    def test_follow_set_complex_rules(self):
        with self.assertRaises(GrammarError):
            sa = SyntaxAnalyzer(self.complex_rules)

            self.assertSetEqual(
                sa._follow[Special.START],
                {Special.LIMITER},
            )
            self.assertSetEqual(
                sa._follow[NonTerm.DESCR],
                {Tag.BEGIN},
            )
            self.assertSetEqual(
                sa._follow[NonTerm.VARS],
                {Tag.BEGIN, Tag.VAR, Tag.ID},
            )
            self.assertSetEqual(
                sa._follow[NonTerm.PROG],
                {Tag.END},
            )
            self.assertSetEqual(
                sa._follow[NonTerm.EXPR],
                {Tag.SEMICOLON},
            )
            self.assertSetEqual(
                sa._follow[NonTerm.CALL],
                {Tag.VAR, Tag.ID},
            )
            self.assertSetEqual(
                sa._follow[NonTerm.TYPE],
                {Tag.ASSIGN},
            )
            self.assertSetEqual(
                sa._follow[NonTerm.ARGS],
                {Tag.RBRACKET},
            )


class WorkingGrammarTestCase(TestCase):
    # For now there are not any asserts since testing parse tree is
    # extremely routine task. Nevertheless, if something would break the lexer
    # or syntax analyzer these tests will fail with their own exceptions.

    def get_lexer(self, code):
        lexer = Lexer(settings.Tag, settings.LEXER_RULES, 'dummy.pas')
        lexer.buffer = code
        return lexer

    def get_syntax_analyzer(self):
        sa = SyntaxAnalyzer(settings.GRAMMAR_RULES, 'dummy.pas')
        return sa

    def get_semantic_analyzer(self, tree):
        return SemanticAnalyzer(tree, "dummy.pas")

    def get_code_generator(self):
        raise NotImplementedError

    def test_expressions(self):
        code = """
            var a: integer := (1 * 2 - 4) * 5 / 7 - 8;
            begin
                var b: boolean := not (1 > 2) and false;
            end.
        """
        lexer = self.get_lexer(code)
        sa = self.get_syntax_analyzer()
        sa.parse(lexer.tokens)

    def test_for_loop(self):
        code = """
            begin
                for var i: integer := 1 to 3 do
                    print(i);

                for var i: integer := 1 to 3 do
                begin
                    print(i);
                end;

                for var i: integer := 3 downto 1 do
                    print(i);

                for var i: integer := 3 downto 1 do
                begin
                    print(i);
                    println(i);
                    somefunc(i);
                end;
            end.
        """
        lexer = self.get_lexer(code)
        sa = self.get_syntax_analyzer()
        sa.parse(lexer.tokens)

    def test_while_loop(self):
        code = """
            begin
                while 1 <= 2 do
                    print('hello world');

                while (1 < 2) or (1 = 2) do
                begin
                    print('hello world');
                end;
            end.
        """
        lexer = self.get_lexer(code)
        sa = self.get_syntax_analyzer()
        sa.parse(lexer.tokens)

    def test_repeat_loop(self):
        code = """
            begin
                var a: integer := 1;
                repeat
                    somefunc();
                    a += 1;
                until a < 3;
            end.
        """
        lexer = self.get_lexer(code)
        sa = self.get_syntax_analyzer()
        sa.parse(lexer.tokens)

    def test_if(self):
        code = """
            begin
                var a: integer := 1;

                if a = 1 then a := 1;
                if (a = 1) and (a = 2) then a := 2;

                if a = 1 then
                begin
                    a := 1;
                end;
                if (a = 1) and (a = 2) then
                begin
                    a := 2;
                end;

                if a = 1 then a := 1
                else a := 1;

                if (a = 1) or (a = 10) then a := 1
                else if (a - 1 = 0) then a := 1;

                if (a = 1) or (a = 10) then a := 1
                else if (a - 1 = 0) then a := 1
                else a := 1;

                if (a = 1) or (a = 10) then a := 1
                else if (a - 1 = 0) then a := 1
                else if (a - 1 = 0) then a := 1
                else if (a - 1 = 0) then a := 1
                else a := 1;
            end.
        """
        lexer = self.get_lexer(code)
        sa = self.get_syntax_analyzer()
        sa.parse(lexer.tokens)

    def test_types(self):
        code = """
            begin
                var a: integer := 10;
                var b: integer := a;
                var c: integer := a + 10;
                
                var r: real := 10.10;
                var r1: real := r;
                var r2: real := r + 10.20;
                
                r1 := 10;
                r := a;
                
                var expr: integer := a + 100 * ((8 - 200) + (2 * 3)) - b;
                var expr2: real := a + 100 * ((8 - r) + (2 * 3)) - b;
                
                var t: boolean := true;
                var f: boolean := false;
                t := f;
                t := not (true and f or false);
                
                var s: string := 's t r real + false' + 'adsf'; 
                
                var ch: char := 'a';              
            end.
        """


        lexer = self.get_lexer(code)
        sa = self.get_syntax_analyzer()
        tree = sa.parse(lexer.tokens)

        sem_an = self.get_semantic_analyzer(tree)
        sem_an.parse(tree.root)

    def test_int_convert_to_real(self):

        self.check_fails("""
            begin
                var c: real := 10.0;
                var a: real := 10;
                var b: integer := c;
            end.
        """)

        self.check_fails("""
            begin
                a := 10;
            end.
        """)

        self.check_fails("""
            begin
                var a: integer := 10;
                var a: integer := 15;           
            end.
        """)

        self.check_fails("""
            begin
                var a: integer;
                var a: integer := 15;           
            end.
        """)

        self.check_fails("""
            begin
                var a: integer := 15;
                var a: integer;           
            end.
        """)

        self.check_fails("""
            begin
                var a: boolean := 10;
            end.
        """)

        self.check_fails("""
            begin
                var a: boolean := true;
                a := 10;
            end.
        """)

        self.check_fails("""
            begin
                var a: boolean := 10 and 1;
            end.
        """)

        self.check_fails("""
            begin
                var a: integer := true;
            end.
        """)

        self.check_fails("""
            begin
                var b: boolean := false;
                var a: boolean := b and 10;
            end.
        """)

        self.check_fails("""
            begin
                var b: string := 10;
            end.
        """)

        self.check_fails("""
            begin
                var a: boolean := true + false;
            end.
        """)

        self.check_fails("""
            begin
                var t3: boolean := true and false or t1 + true;                  
            end.
        """)


        self.check_fails("""
            begin
                var t: integer := 10 and 8 or 16;                  
            end.
        """)

    def check_fails(self, code):
        lexer = self.get_lexer(code)
        sa = self.get_syntax_analyzer()
        tree = sa.parse(lexer.tokens)

        sem_an = self.get_semantic_analyzer(tree)
        with self.assertRaises(SemanticError) as error:
            sem_an.parse(tree.root)

        logger.info(sem_an.vars_dict)
        logger.info(f"Raised {error.exception}")
        # self.assertEqual(str(error.exception), r"'%' at line 2")

    def test_string(self):
        self.check_fails("""
            begin
                var b: string := 10;
            end.
        """)

        self.check_fails("""
            begin
                var s: string := 'asd' + 10;
            end.
        """)

        self.check_fails("""
            begin
                var s: char := 'asd';
            end.
        """)


