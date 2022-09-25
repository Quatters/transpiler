from collections import OrderedDict
from typing import Iterable
from transpiler.base import Tag, NonTerm, Token, GrammarRule


LIMITER = 'LIMITER'


class SyntaxAnalyzer:
    _first: OrderedDict[NonTerm, set[Tag]] = OrderedDict()
    _follow = None

    def __init__(
        self,
        tokens: Iterable[Token],
        rules: list[GrammarRule],
    ):
        self.tokens = tokens
        self.rules = rules

    def first(self, chain: tuple[Tag, NonTerm]) -> set[Tag]:
        symbol = chain[0]
        if isinstance(symbol, Tag):
            return {symbol}

        nonterm_first = self._first.get(symbol, set())
        lambda_in_nonterm_first = Tag.LAMBDA in nonterm_first
        result = {s for s in nonterm_first if not s is Tag.LAMBDA}
        if lambda_in_nonterm_first:
            result |= self.first(chain[1:])

        return result


    def _build_first(self):
        changed = True
        while changed:
            changed = False
            for rule in self.rules:
                for chain in rule.right:
                    result = self._first.get(rule.left, set()) \
                        | self.first(chain)
                    if result != self._first.get(rule.left, set()):
                        changed = True
                        self._first[rule.left] = result
