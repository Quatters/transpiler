from transpiler.lexer import Lexer
from transpiler.syntax_analyzer import SyntaxAnalyzer
from transpiler.semantic_analyzer import SemanticAnalyzer
from transpiler.settings import Tag, LEXER_RULES, GRAMMAR_RULES


def transpile(code: str) -> str:
    lexer = Lexer(Tag, LEXER_RULES)
    lexer.buffer = code

    syntax_analyzer = SyntaxAnalyzer(GRAMMAR_RULES)
    tree = syntax_analyzer.parse(lexer.tokens)

    semantic_analyzer = SemanticAnalyzer(tree, code)
    return semantic_analyzer.parse()
