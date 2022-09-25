from pathlib import Path
from pprint import pprint
from transpiler.lexer import Lexer
from transpiler.syntax_analyzer import SyntaxAnalyzer
from transpiler.settings import LEXER_RULES, GRAMMAR_RULES


ROOT = Path(__file__).parent.parent.absolute()

code = (ROOT / 'examples/valid.pas').read_text()

lexer = Lexer(code, LEXER_RULES)

print('Tokens parsed by lexer:')
for token in lexer.tokens:
    print(token)

syntax_analyzer = SyntaxAnalyzer(lexer.tokens, GRAMMAR_RULES)

syntax_analyzer._build_first()

print('First set:')
pprint(syntax_analyzer._first)
