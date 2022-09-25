from unittest import TestCase
from transpiler.lexer import Lexer, UnexpectedTokenError
from transpiler.settings import LEXER_RULES, Tag


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
