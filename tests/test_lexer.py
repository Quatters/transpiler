from unittest import TestCase
from transpiler.base import Tag
from transpiler.lexer import Lexer, UnexpectedTokenError
from transpiler.settings import LEXER_RULES


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

        self.assertEqual(tokens[0].def_, Tag.VAR)
        self.assertEqual(tokens[1].def_, Tag.ID)
        self.assertEqual(tokens[2].def_, Tag.ASSIGN)
        self.assertEqual(tokens[3].def_, Tag.QUOTE)
        self.assertEqual(tokens[4].def_, Tag.ID)
        self.assertEqual(tokens[5].def_, Tag.QUOTE)
        self.assertEqual(tokens[6].def_, Tag.SEMICOLON)
        self.assertEqual(tokens[7].def_, Tag.ID)
        self.assertEqual(tokens[8].def_, Tag.COLON)
        self.assertEqual(tokens[9].def_, Tag.T_INTEGER)
        self.assertEqual(tokens[10].def_, Tag.ASSIGN)
        self.assertEqual(tokens[11].def_, Tag.NUMBER_INT)
        self.assertEqual(tokens[12].def_, Tag.SEMICOLON)
        self.assertEqual(tokens[13].def_, Tag.ID)
        self.assertEqual(tokens[14].def_, Tag.COLON)
        self.assertEqual(tokens[15].def_, Tag.T_BOOLEAN)
        self.assertEqual(tokens[16].def_, Tag.ASSIGN)
        self.assertEqual(tokens[17].def_, Tag.TRUE)
        self.assertEqual(tokens[18].def_, Tag.SEMICOLON)
        self.assertEqual(tokens[19].def_, Tag.ID)
        self.assertEqual(tokens[20].def_, Tag.COLON)
        self.assertEqual(tokens[21].def_, Tag.T_REAL)
        self.assertEqual(tokens[22].def_, Tag.ASSIGN)
        self.assertEqual(tokens[23].def_, Tag.NUMBER_FLOAT)
        self.assertEqual(tokens[24].def_, Tag.SEMICOLON)
        self.assertEqual(tokens[25].def_, Tag.ID)
        self.assertEqual(tokens[26].def_, Tag.COLON)
        self.assertEqual(tokens[27].def_, Tag.T_ARRAY)
        self.assertEqual(tokens[28].def_, Tag.LBRACKET_SQUARE)
        self.assertEqual(tokens[29].def_, Tag.NUMBER_INT)
        self.assertEqual(tokens[30].def_, Tag.RANGE)
        self.assertEqual(tokens[31].def_, Tag.NUMBER_INT)
        self.assertEqual(tokens[32].def_, Tag.RBRACKET_SQUARE)
        self.assertEqual(tokens[33].def_, Tag.OF)
        self.assertEqual(tokens[34].def_, Tag.T_STRING)
        self.assertEqual(tokens[35].def_, Tag.SEMICOLON)
        self.assertEqual(tokens[36].def_, Tag.BEGIN)
        self.assertEqual(tokens[37].def_, Tag.ID)
        self.assertEqual(tokens[38].def_, Tag.LBRACKET)
        self.assertEqual(tokens[39].def_, Tag.ID)
        self.assertEqual(tokens[40].def_, Tag.RBRACKET)
        self.assertEqual(tokens[41].def_, Tag.SEMICOLON)
        self.assertEqual(tokens[42].def_, Tag.END)
        self.assertEqual(tokens[43].def_, Tag.DOT)
