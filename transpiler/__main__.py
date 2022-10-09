import sys
from pathlib import Path
from transpiler.lexer import Lexer
from transpiler.syntax_analyzer import SyntaxAnalyzer
from transpiler.settings import Tag, LEXER_RULES, GRAMMAR_RULES


filepath = sys.argv[1]
code = Path(filepath).read_text()

lexer = Lexer(Tag, LEXER_RULES, filepath)
lexer.buffer = code

syntax_analyzer = SyntaxAnalyzer(GRAMMAR_RULES, filepath)
syntax_analyzer.parse(lexer.tokens)
