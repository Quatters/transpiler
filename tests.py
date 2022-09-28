from pprint import pprint
from unittest import TestCase
from transpiler.base import GrammarRule, Special, Terminal, NonTerminal
from transpiler.settings import LEXER_RULES, Tag, NonTerm
from transpiler.lexer import Lexer, UnexpectedTokenError
from transpiler.syntax_analyzer import SyntaxAnalyzer


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
        lexer = Lexer(code, LEXER_RULES)
        with self.assertRaises(UnexpectedTokenError) as error:
            list(lexer.tokens)
        self.assertEqual(str(error.exception), '\n\n... begi%n ...\n        ^')

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

        lexer = Lexer(code, LEXER_RULES)
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

    def test_math_expression_rules(self):
        sa = SyntaxAnalyzer(None, self.math_expression_rules)

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
        sa._build_predict_table()
        pprint(sa._predict_table)

    def test_first_set_simple_rules(self):
        sa = SyntaxAnalyzer(None, self.simple_rules)

        self.assertDictEqual(sa._first, {
            NonTerm.PROG: {Tag.VAR},
            NonTerm.VARS: {Special.LAMBDA},
            NonTerm.EXPR: {Tag.T_INTEGER},
        })

    def test_first_set_complex_rules(self):
        sa = SyntaxAnalyzer(None, self.complex_rules)

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
        sa = SyntaxAnalyzer(None, self.simple_rules)

        self.assertDictEqual(sa._follow, {
            NonTerm.PROG: {Special.LIMITER},
            NonTerm.VARS: {Tag.BEGIN},
            NonTerm.EXPR: {Tag.END},
        })

    def test_follow_set_complex_rules(self):
        sa = SyntaxAnalyzer(None, self.complex_rules)

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

    def test_predict_table_simple_rules(self):
        sa = SyntaxAnalyzer(None, self.simple_rules)
        sa._build_predict_table()

        # print('\n')
        # pprint(sa._predict_table)

    def test_predict_table_complex_rules(self):
        sa = SyntaxAnalyzer(None, self.complex_rules)
        sa._build_predict_table()

        # print('\n')
        # pprint(sa._predict_table)
