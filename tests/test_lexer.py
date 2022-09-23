from unittest import TestCase
from transpiler.base import Def
from transpiler.lexer import Lexer, UnexpectedTokenError
from transpiler.settings import RULES


class LexerTestCase(TestCase):
    def test_invalid_token(self):
        code = """
            begi%n
            end.
        """
        lexer = Lexer(code, RULES)
        with self.assertRaises(UnexpectedTokenError):
            list(lexer.tokens)

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

        lexer = Lexer(code, RULES)
        tokens = list(lexer.tokens)

        self.assertEqual(tokens[0].def_, Def.VAR)
        self.assertEqual(tokens[1].def_, Def.ID)
        self.assertEqual(tokens[2].def_, Def.ASSIGN)
        self.assertEqual(tokens[3].def_, Def.QUOTE)
        self.assertEqual(tokens[4].def_, Def.ID)
        self.assertEqual(tokens[5].def_, Def.QUOTE)
        self.assertEqual(tokens[6].def_, Def.SEMICOLON)
        self.assertEqual(tokens[7].def_, Def.ID)
        self.assertEqual(tokens[8].def_, Def.COLON)
        self.assertEqual(tokens[9].def_, Def.T_INTEGER)
        self.assertEqual(tokens[10].def_, Def.ASSIGN)
        self.assertEqual(tokens[11].def_, Def.NUMBER_INT)
        self.assertEqual(tokens[12].def_, Def.SEMICOLON)
        self.assertEqual(tokens[13].def_, Def.ID)
        self.assertEqual(tokens[14].def_, Def.COLON)
        self.assertEqual(tokens[15].def_, Def.T_BOOLEAN)
        self.assertEqual(tokens[16].def_, Def.ASSIGN)
        self.assertEqual(tokens[17].def_, Def.TRUE)
        self.assertEqual(tokens[18].def_, Def.SEMICOLON)
        self.assertEqual(tokens[19].def_, Def.ID)
        self.assertEqual(tokens[20].def_, Def.COLON)
        self.assertEqual(tokens[21].def_, Def.T_REAL)
        self.assertEqual(tokens[22].def_, Def.ASSIGN)
        self.assertEqual(tokens[23].def_, Def.NUMBER_FLOAT)
        self.assertEqual(tokens[24].def_, Def.SEMICOLON)
        self.assertEqual(tokens[25].def_, Def.ID)
        self.assertEqual(tokens[26].def_, Def.COLON)
        self.assertEqual(tokens[27].def_, Def.T_ARRAY)
        self.assertEqual(tokens[28].def_, Def.LBRACKET_SQUARE)
        self.assertEqual(tokens[29].def_, Def.NUMBER_INT)
        self.assertEqual(tokens[30].def_, Def.RANGE)
        self.assertEqual(tokens[31].def_, Def.NUMBER_INT)
        self.assertEqual(tokens[32].def_, Def.RBRACKET_SQUARE)
        self.assertEqual(tokens[33].def_, Def.OF)
        self.assertEqual(tokens[34].def_, Def.T_STRING)
        self.assertEqual(tokens[35].def_, Def.SEMICOLON)
        self.assertEqual(tokens[36].def_, Def.BEGIN)
        self.assertEqual(tokens[37].def_, Def.ID)
        self.assertEqual(tokens[38].def_, Def.LBRACKET)
        self.assertEqual(tokens[39].def_, Def.ID)
        self.assertEqual(tokens[40].def_, Def.RBRACKET)
        self.assertEqual(tokens[41].def_, Def.SEMICOLON)
        self.assertEqual(tokens[42].def_, Def.END)
        self.assertEqual(tokens[43].def_, Def.DOT)
