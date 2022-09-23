from pathlib import Path
from transpiler.lexer import Lexer
from transpiler.settings import RULES


ROOT = Path(__file__).parent.parent.absolute()

code = (ROOT / 'examples/valid.pas').read_text()

lexer = Lexer(code, RULES)

for token in lexer.tokens:
    print(token)
