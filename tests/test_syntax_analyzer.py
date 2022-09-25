from unittest import TestCase
from transpiler.base import GrammarRule, Tag, NonTerm
from transpiler.syntax_analyzer import SyntaxAnalyzer


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
            (Tag.LAMBDA,),
        }),
        GrammarRule(NonTerm.EXPR, {
            (Tag.T_INTEGER, Tag.SEMICOLON),
        }),
    ]

    complex_rules = [
        # _Start⟶Descr begin Prog end dot
        # Descr⟶Vars
        # Descr⟶lambda
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

        GrammarRule(NonTerm._START, {
            (NonTerm.DESCR, Tag.BEGIN, NonTerm.PROG, Tag.END, Tag.DOT)
        }),
        GrammarRule(NonTerm.DESCR, {
            (NonTerm.VARS,),
            (Tag.LAMBDA,)
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
        })
    ]

    def test_first_set_simple_rules(self):
        sa = SyntaxAnalyzer(None, self.simple_rules)
        sa._build_first()

        self.assertDictEqual(sa._first, {
            NonTerm.PROG: {Tag.VAR},
            NonTerm.VARS: {Tag.LAMBDA},
            NonTerm.EXPR: {Tag.T_INTEGER},
        })

    def test_first_set_complex_rules(self):
        sa = SyntaxAnalyzer(None, self.complex_rules)
        sa._build_first()

        self.assertSetEqual(
            sa._first[NonTerm._START],
            {Tag.BEGIN, Tag.VAR},
        )
        self.assertSetEqual(
            sa._first[NonTerm.DESCR],
            {Tag.VAR, Tag.LAMBDA},
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
