from typing import Iterable
from transpiler.base import Tag, Token


class SyntaxAnalyzer:
    def __init__(self, tokens: Iterable[Token]):
        self.tokens = tokens
