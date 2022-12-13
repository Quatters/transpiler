from transpiler.lexer import Lexer
from transpiler.syntax_analyzer import SyntaxAnalyzer
from transpiler.semantic_analyzer import SemanticAnalyzer
from transpiler.settings import LEXER_RULES, GRAMMAR_RULES, Tag


def transpile(code: str):
    lexer = Lexer(Tag, LEXER_RULES)
    lexer.buffer = code

    syntax_analyzer = SyntaxAnalyzer(GRAMMAR_RULES)
    tree = syntax_analyzer.parse(lexer.tokens)
    semantic_analyzer = SemanticAnalyzer(tree, code)

    return semantic_analyzer.parse()
