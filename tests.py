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
from transpiler.semantic_analyzer import SemanticAnalyzer, SemanticError
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
        self.assertEqual(str(error.exception), r"% at line 2")

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

    def check_not_fails(self, code):
        lexer = self.get_lexer(code)
        sa = self.get_syntax_analyzer()
        tree = sa.parse(lexer.tokens)
        sem_an = self.get_semantic_analyzer(tree)
        code = sem_an.parse()
        self.assertTrue(sem_an.tree.is_semantically_correct)

    def check_fails(self, code, err=SemanticError):
        lexer = self.get_lexer(code)
        sa = self.get_syntax_analyzer()
        tree = sa.parse(lexer.tokens)

        sem_an = self.get_semantic_analyzer(tree)
        with self.assertRaises(err) as error:
            sem_an.parse()

        logger.info(f"Raised {error.exception}")

    def test_expressions_syntax(self):
        code = """
            var a: integer := (1 * 2 - 4) * 5 / 7 - 8;
            begin
                var b: boolean := not (1 > 2) and false;
            end.
        """
        lexer = self.get_lexer(code)
        sa = self.get_syntax_analyzer()
        sa.parse(lexer.tokens)

    def test_for_loop_syntax(self):
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

    def test_while_loop_syntax(self):
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

    def test_repeat_loop_syntax(self):
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

    def test_if_syntax(self):
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

    def test_types_semantic(self):
        self.check_not_fails("""
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
                var s1: string := s;

                var ch: char := 'a';
                var ch2: char := ch;

                ch := 'b';
                ch2 := ch;

                s := '- / + * false true';
                s1 := s;

                var k: boolean := 1 + 2 = 3;
                var lol: boolean := ((1 + 2) * 3 > 4) and not (k or FALSE);

                var new_var : integer := 10;
                new_var := new_var * 5;
            end.
        """)

    def test_reassignment_semantic(self):
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

    def test_convert_vars_semantic(self):
        self.check_fails("""
            begin
                var c: real := 10.0;
                var b: integer := c;
            end.
        """)

        self.check_fails("""
            begin
                var a: integer := 15;
                var b: boolean := a;
            end.
        """)

        self.check_fails("""
            begin
                var a: integer := true;
            end.
        """)

        self.check_fails("""
            begin
                var b: string := 10;
            end.
        """)

        self.check_fails("""
            begin
                var t: integer := 10 and 8 or 16;
            end.
        """)

    def test_boolean_type(self):
        self.check_fails("""
            begin
                var a: boolean := 10 + (1 = 1);
            end.
        """)

        self.check_fails("""
            begin
                var a: boolean := 1 + 10;
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
                var a: boolean := 10 and 1 or 16;
            end.
        """)

        self.check_fails("""
            begin
                var a: boolean := true + false;
            end.
        """)

    def test_string(self):
        self.check_fails("""
            begin
                var c: char := 'c' + 'asd';
            end.
        """)

        self.check_not_fails("""
            begin
                var a: char := 'c';
                var b: char := a;
            end.
        """)

        self.check_not_fails("""
            begin
                var s: string := 'asd' + 'dsa';
            end.
        """)

        self.check_fails("""
            begin
                var s: string := 'asd' - 'dsa';
            end.
        """)

        self.check_fails("""
            begin
                var s: string := 'asd' / 'dsa';
            end.
        """)

        self.check_fails("""
            begin
                var s: string := 'asd' * 'dsa';
            end.
        """)

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

        self.check_fails("""
            begin
                var s: char := '';
            end.
        """)

        self.check_fails("""
            begin
                var s: string := 'asd' and 'fgh' or 'asdsdf';
            end.
        """)

        self.check_fails("""
            begin
                var s: string := false;
            end.
        """)

    def test_compare(self):
        self.check_not_fails("""
            begin
                var k: boolean := 1 + 2 = 3;
            end.
        """)

    def test_scopes(self):
        self.check_fails("""
             begin
                 a := 10;
             end.
         """)

        self.check_fails("""
            begin
                var t3: boolean := true and false or t1 + true;
            end.
        """)

        self.check_not_fails("""
            var global1: integer := 1;
            var global2: real := 2.0;

            begin
                global1 := 2;
                global2 := global1;
            end.
        """)

        self.check_fails("""
            begin
                if (10 > 15) then
                begin
                    var i: integer := 10;
                end
                else if (100 > 90) then
                begin
                    print(i);
                end;
            end.
        """)

        self.check_fails("""
            begin
                if (10 > 15) then
                    var i: integer := 10
                else if (10 > 15) then
                    print(i);
            end.
        """)

        self.check_fails("""
            begin
                if (10 > 15) then
                    var i: integer := 10
                else
                    print(i);
            end.
        """)

        self.check_fails("""
            begin
                for var a: integer := 1 to 10 do
                    var b: boolean := true;

                b := false;
            end.
        """)

        self.check_fails("""
            begin
                for var b: integer := 1 to 10 do
                begin
                    var a: boolean := true;
                    if a > 1 then
                    begin
                        a := not (a);
                    end;
                end;

                a := false;
            end.
        """)

        self.check_fails("""
            begin
                while true do
                begin
                    var b: integer := 10;
                    while true do
                    begin
                        b := 15;
                        var n: integer := 5;
                    end;
                    n := 10;
                end;
            end.
        """)

        self.check_fails("""
            var a: integer := 10;
            begin
                var a: integer := 20;
            end.
        """)

        self.check_fails("""
            var a: integer := 10;
            begin
                for var a: integer := 1 to 10 do
                    print(a);
            end.
        """)

        self.check_fails("""
            var a: integer := 10;
            begin
                if true then
                begin
                    for var a: integer := 1 to 10 do
                        print();
                end;
            end.
        """)

    def test_call_functions(self):
        self.check_not_fails("""
            begin
                print('some text');

                var a: real := 1 + sqrt(5);

                var b: integer := func1(func2(1), 1);
                var c: integer := func1(func2(func3(func4())));
                var d: integer := func1(func2(func3(c, b))) + func1();
                var e: integer :=
                    func1(func2(func3(func4(5, sqrt(8))), sqrt(2)))
                    + func1(func2(func3(c, b))) + func1();

                var lol: boolean := 1.2 > sqrt(2);
                var lol2: boolean := sqrt(1) > sqrt(2);
                var lol3: boolean := '__lol__' < 'kek';
                var lol4: boolean := '' <> '' or '' >= '' or
                    '' <= '' or '' > '' or '' = '';
            end.
        """)

    def test_for_loop_semantic(self):
        self.check_not_fails("""
            begin
                var a: integer := 10;
                for var i: integer := 3 downto 1 do
                    a := 1;
            end.
        """)

        self.check_fails("""
            begin
                var a: integer := 10;
                for var i: integer := 'str' downto 1 do
                    a := 1;
            end.
        """)

        self.check_fails("""
            begin
                for var a: boolean := 1 to 10 do
                    var b: boolean := true;
            end.
        """)

        self.check_fails("""
             begin
                 for var a: boolean := true to 10 do
                     var b: boolean := true;
             end.
         """)

        self.check_fails("""
            begin
                for var i: integer := 1 to 10 do
                    i := i + 1;
                i := 12;
            end.
        """)

        self.check_fails("""
            begin
                for var i: integer := 1 to 10 do
                begin
                    print(i);
                    i := i + 1;
                end;
                i := 12;
            end.
        """)

        self.check_not_fails("""
            begin
                for var i: integer := 1 to 10 do
                begin
                    print(i);
                    i := i + 1;
                end;
            end.
        """)

        self.check_not_fails("""
            begin
                for var i: integer := 1 to 10 do
                    print(i);
            end.
        """)

        self.check_not_fails("""
            begin
                for var i: integer := 1 + 1 to 10 do
                    print(i);
            end.
        """)

        self.check_not_fails("""
            begin
                var a: integer := 1;
                for var i: integer := a + 1 to 10 do
                    print(i);
            end.
        """)

        self.check_fails("""
            begin
                for var i: real := 1 to 10 do
                    print(i);
            end.
        """)

        self.check_fails("""
            begin
                for var i: integer := 1.0 to 10 do
                    print(i);
            end.
        """)

        self.check_fails("""
            begin
                for var i: integer := true to 10 do
                    print(i);
            end.
        """)

        self.check_fails("""
            begin
                for var i: integer := 'a' to 10 do
                    print(i);
            end.
        """)

        self.check_fails("""
            begin
                for var i: integer := 'asd' to 10 do
                    print(i);
            end.
        """)

        self.check_fails("""
            begin
                for var i: integer := 1 to 10.0 do
                    print(i);
            end.
        """)

        self.check_fails("""
            begin
                for var i: integer := 1 to true do
                    print(i);
            end.
        """)

        self.check_fails("""
            begin
                for var i: integer := 1 to 'a' do
                    print(i);
            end.
        """)

        self.check_fails("""
            begin
                for var i: integer := 1 to 'ads' do
                    print(i);
            end.
        """)

        self.check_not_fails("""
            begin
                for var i: integer := 1 to 10 do
                begin
                    for var j: integer := 1 to 10 do
                        print(i);
                end;
            end.
        """)

        self.check_fails("""
            begin
                for var i: integer := 1 to 10 do
                begin
                    for var j: integer := 1 to 10 do
                        print(i);
                    j := 10;
                    i := 10;
                end;
            end.
        """)

        self.check_fails("""
            begin
                for var i: integer := 1 to 10 do
                begin
                    for var i: integer := 1 to 10 do
                        print(i);
                end;
            end.
        """)

    def test_if_semantic(self):
        self.check_not_fails("""
            begin
                if true then
                begin
                end
                else if 1 > 1 then
                    print(1)
                else
                    print(2);
            end.
        """)

        self.check_not_fails("""
            begin
                if (5 > 4) then
                begin
                    print('lol');
                end;
            end.
        """)

        self.check_not_fails("""
            begin
                if (5.0 > 4.0) then
                begin
                    print('lol');
                end;
            end.
        """)

        self.check_not_fails("""
            begin
                if (true > false) then
                begin
                    print('lol');
                end;
            end.
        """)

        self.check_not_fails("""
            begin
                var a: integer := 10;
                var b: integer := 15;
                if (a > b) then
                begin
                    print('lol');
                end;
            end.
        """)

        self.check_not_fails("""
            begin
                var a: real := 1.0;
                var b: integer := 15;
                if (a > b) then
                begin
                    print('lol');
                end;
            end.
        """)

        self.check_not_fails("""
            begin
                if (10 > 15) then
                begin
                    print('lol');
                end
                else if (100 < 90) then
                begin
                    print('lol');
                end;
            end.
        """)

        self.check_not_fails("""
            begin
                if (true) then
                begin
                    print('lol');
                end;
            end.
        """)

        self.check_not_fails("""
            begin
                if (true and false) then
                begin
                    print('lol');
                end;
            end.
        """)

        self.check_not_fails("""
            begin
                var b: boolean := sqrt(1) > sqrt(3);
                if (sqrt(1) > sqrt(3)) then
                begin
                    print('lol');
                end;
            end.
        """)

        self.check_not_fails("""
            begin
                if ('asd' > 'dsa') then
                begin
                    print('lol');
                end;
            end.
        """)

        self.check_fails("""
            begin
                if (true > 15) then
                begin
                    print('lol');
                end;
            end.
        """)

        self.check_not_fails("""
            begin
                if (true) then
                begin
                    print('lol');
                end
                else
                begin
                    print('lol');
                end;
            end.
        """)

        self.check_fails("""
            begin
                if (true) then
                begin
                    print('lol');
                end
                else
                begin
                    print('lol');
                end
                else
                begin
                    print('lol');
                end;
            end.
        """)

        self.check_not_fails("""
            begin
                if true then
                begin
                    if true then
                        print()
                    else
                        print();
                end
                else
                    print(1);
            end.
        """)


    def test_until_loop_semantic(self):
        self.check_not_fails("""
            begin
                var b: boolean := 1 > 3;
                repeat
                    print();
                    var a: real := somefunc() - sqrt(2.4);
                until not (true) or b;
            end.
        """)

        self.check_not_fails("""
            begin
                repeat
                    print();
                    var a: real := somefunc() - sqrt(2.4);
                until 'c' > 'a';
            end.
        """)

        self.check_not_fails("""
                    begin
                        repeat
                            print();
                        until true;
                    end.
                """)

        self.check_not_fails("""
                    begin
                        var a: boolean := false;
                        repeat
                            print();
                        until a;
                    end.
                """)

        self.check_not_fails("""
                    begin
                        var a: boolean := false;
                        repeat
                            repeat
                                print();
                            until true;
                            print();
                        until a;
                    end.
                """)

        self.check_not_fails("""
                    begin
                        repeat
                            print();
                        until 10 > 18;
                    end.
                """)

        self.check_not_fails("""
                    begin
                        repeat
                            print();
                        until 10.06 > 18.5;
                    end.
                """)

        self.check_not_fails("""
                    begin
                        repeat
                            print();
                        until sqrt(1) > sqrt(5);
                    end.
                """)

        self.check_not_fails("""
            begin
                var a: boolean := false;
                repeat
                    if a then
                        print();
                until a;
            end.
        """)

        self.check_not_fails("""
            begin
                repeat
                    for var i: integer := 1 to 10 do
                    begin
                        i := 15;
                        print(i);
                    end;
                until true and (10 > 19);
            end.
        """)

        self.check_fails("""
            begin
                repeat
                    print();
                    var a: real := somefunc() - sqrt(2.4);
                until 'c';
            end.
        """)

        self.check_fails("""
                    begin
                        repeat
                            print();
                        until 'asd';
                    end.
                """)

        self.check_fails("""
            var a: integer;
            var b: real;
            begin
                repeat
                    print();
                    var a: real := somefunc() - sqrt(2.4);
                until a - b;
            end.
        """)

        self.check_fails("""
            begin
                repeat
                    print();
                until a > 10;
            end.
        """)

        self.check_fails("""
            begin
                repeat
                    print();
                until 'asd' + 'sdf';
            end.
        """)

    def test_while_loop_semantic(self):
        self.check_not_fails("""
            var b: boolean := false;

            begin
                var a: boolean := false;
                while a or true and 1 > 2 and 3 = 4 or not (7 - 8 <> -1) do
                    print();

                while a or true and 1 > 2 and 3 = 4 or not (7 - 8 <> -1) do
                begin
                    print();
                    var c: real := somefunc() - sqrt(2.4);
                    b := not(b);
                end;
            end.
        """)

        self.check_not_fails("""
            begin
                var a: boolean := false;
                var b: boolean := false;

                var c: integer := 10;
                var d: integer := 15;

                while a do
                    print();

                while a and b do
                    print();

                while true do
                    print();

                while true and b do
                    print();

                while c = d do
                    print();

                while c = d and a do
                    print();

            end.
        """)

        self.check_not_fails("""
            begin
                var a: boolean := false;
                var b: boolean := false;

                var c: integer := 10;
                var d: integer := 15;

                while a do
                begin
                    print();
                    print();
                end;

                while a and b do
                begin
                    print();
                    print();
                end;

                while true do
                begin
                    print();
                    print();
                end;

                while true and b do
                begin
                    print();
                    print();
                end;

                while c = d do
                begin
                    print();
                    print();
                end;

                while c = d and a do
                begin
                    print();
                    print();
                end;
            end.
        """)

        self.check_not_fails("""
            begin
                var a: integer := 2;
                var b: integer := 1;

                while sqrt(a) = sqrt(b) do
                    print();
            end.
        """)

        self.check_not_fails("""
            begin
                while true do
                begin
                    while false do
                        print();
                    print();
                    print();
                end;
            end.
        """)

        self.check_not_fails("""
            begin
                while true do
                begin
                    print();
                    while true or false do
                    begin
                        print();
                    end;

                    var a: integer := 10;
                end;
            end.
        """)

        self.check_fails("""
            begin
                var a: integer := 1;

                while a do
                    print();
            end.
        """)

        self.check_fails("""
            begin
                var a: integer := 1;

                while a + 2 do
                    print();
            end.
        """)

        self.check_fails("""
            begin
                while 'str' do
                    print();
            end.
        """)

        self.check_fails("""
            begin
                while 2.5 do
                    print();
            end.
        """)

        self.check_fails("""
            begin
                while 'c' do
                    print();
            end.
        """)

        self.check_fails("""
            begin
                while true do
                begin
                    while 'asd' do
                        print();
                end;
            end.
        """)

        self.check_fails("""
            begin
                while 3 and true do
                    print();
            end.
        """)

        self.check_fails("""
            begin
                var a: integer := 1;

                while a = (2 and true) do
                    print();
            end.
        """)

    def test_key_words_in_string_semantic(self):
        self.check_not_fails("""
            begin
                if true then
                    print()
                else
                    print('else');
            end.
        """)

        self.check_not_fails("""
            begin
                if true then
                    print()
                else
                    var str: string := 'else';
            end.
        """)

        self.check_not_fails("""
            begin
                var s: string := 'else';
            end.
        """)

        self.check_not_fails("""
            begin
                print('str');
            end.
        """)

        self.check_not_fails("""
            begin
                print('for');
            end.
        """)

        self.check_not_fails("""
            begin
                print('var');
            end.
        """)

        self.check_not_fails("""
            begin
                for var i: integer := 1 to 10 do
                begin
                    print('for');
                    if true then
                        var a: string := 'if'
                    else
                        print('else');
                end;
            end.
        """)

    def test_division(self):
        self.check_fails("""
            begin
                var a: integer := 10 / 5;
            end.
        """)

        self.check_fails("""
            begin
                var s: string := 'asd' / 'sgd';
            end.
        """)

    def test_operational_assignments(self):

        self.check_fails("""
            begin
                var a: integer := 1;
                a += 1;
            end.
        """, NotImplementedError)

        self.check_fails("""
            begin
                var a: integer := 1;
                a -= 1;
            end.
        """, NotImplementedError)

        self.check_fails("""
            begin
                var a: integer := 1;
                a *= 1;
            end.
        """, NotImplementedError)

        self.check_fails("""
            begin
                var a: integer := 1;
                a /= 1;
            end.
        """, NotImplementedError)

        self.check_fails("""
            begin
                var a: integer := 1;
                a += true;
            end.
        """, NotImplementedError)

        self.check_not_fails("""
            begin
                var a: string := '+=';
            end.
        """)

        self.check_fails("""
            begin
                var a: integer := 1;
                if (true) then
                    a *= 2;
            end.
        """, NotImplementedError)

    def test_generator(self):
        template = """
        {0}

        namespace Transpiler
        {{
            internal class Program
            {{
                {1}
                public static void Main(string[] args)
                {2}
            }}
        }}
        """
        # можно сравнивать только параметры

        # code = """
        #     begin
        #         var a: integer := 10;
        #         a := 15 + 20 + 30;
        #     end.
        # """


        # code = """
        #     begin
        #         var a: integer := ((10 + 1) * 3) - 100;
        #         var b: boolean := not (true);
        #     end.
        # """

        # self.check_not_fails("""
        #     begin
        #       for var i: integer := 0 to 3 do
        #       begin
        #         var g: boolean := true;
        #       end;
        #       var g: boolean := true;
        #     end.
        # """)

        # self.check_not_fails("""
        #     begin
        #         var a: integer := 10;
        #         for var i: integer := 1 + a to a do
        #             print(i);
        #     end.
        # """)

        code = """
            begin
                var asd: integer;
                if true then
                    var a: integer := 10
                else if false then
                    var b: integer := 15
                else
                    var c: integer := 20;
            end.
        """

        # code = """
        #     begin
        #         repeat
        #             var a: integer := 1;
        #         until true;
        #     end.
        # """

        # code = """
        #     begin
        #         while true do
        #             var a: integer := 10;
        #     end.
        # """

        # code = """
        #     begin
        #         var c: integer := 15;
        #         for var i: integer := 1 to c do
        #             var a: integer;
        #
        #         for var i: integer := 10 downto 1 do
        #             var g: string := 'asdgf' + 'fsdf';
        #     end.
        # """

        # code = """
        #     begin
        #         var b: boolean := 15 > 10;
        #         b := false;
        #         if true and b then
        #         begin
        #             var a: integer:= 10;
        #         end;
        #     end.
        # """

        # code = """
        #     var g1: boolean := true;
        #     var g2: real := 15.5;
        #     begin
        #         var a: integer := 10 + 12;
        #         var b: integer := 5 * 9;
        #         var c: boolean := a = b;
        #         a := 15 + 30;
        #         c := g1 and true;
        #     end.
        # """

        # code = """
        #     begin
        #         var b: boolean := true and false or false = true <> false;
        #     end.
        # """


        # code = """
        #     begin
        #         var b: boolean := 'asd' = ('asd' = 'asd') and true;
        #     end.
        # """

        # code = """
        #     begin
        #         var c: string := 'asdads' + 'asd ads' + 'asdf' + 'dfg';
        #     end.
        # """

        # code = """
        #     begin
        #         var a: integer := 10 + 19;
        #     end.
        # """

        # code = """
        #     begin
        #         var b: boolean := 'asd' = ('sgsd' + ('asd' + 'sdf'));
        #     end.
        # """

        # code = """
        #     begin
        #         var b: boolean := 'ad' = ('ads' + 'ad');
        #     end.
        # """

        # self.check_not_fails("""
        #     begin
        #         var c: string := '\n';
        #     end.
        # """)

        # self.check_not_fails("""
        #     var a: integer := 10;
        #     a := 15;
        #     begin
        #         var c: char := 'c' + 'asd';
        #     end.
        # """)

        # code = """
        #     begin
        #         var a: integer := 10 + (5 * 4);
        #         var b: real := 10.0;
        #         var c: char := 'a';
        #         var d: string := 'str';
        #         var e: boolean := true;
        #     end.
        # """

        # code = """
        #     begin
        #         var b: boolean := 'a' <> 'c';
        #     end.
        # """

        #
        # code = """
        #     begin
        #         for var i: integer := 1 to 3 do
        #             print(i);
        #     end.
        # """
        #
        # code = """
        #     begin
        #         var i: integer;
        #         i := 10;
        #     end.
        # """

        lexer = self.get_lexer(code)
        sa = self.get_syntax_analyzer()
        tree = sa.parse(lexer.tokens)
        sem_an = self.get_semantic_analyzer(tree)
        code_result = sem_an.parse()
        print(code_result)
        self.assertTrue(sem_an.tree.is_semantically_correct)


