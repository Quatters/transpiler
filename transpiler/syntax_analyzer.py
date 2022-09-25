from collections import OrderedDict
from typing import Iterable
from transpiler.base import Tag, NonTerm, Token, GrammarRule


LIMITER = '__LIMITER__'


class SyntaxAnalyzer:
    def __init__(
        self,
        tokens: Iterable[Token],
        rules: list[GrammarRule],
    ):
        self.tokens = tokens
        self.rules = rules
        self._first: OrderedDict[NonTerm, set[Tag]] = OrderedDict()
        self._follow: OrderedDict[NonTerm, set[Tag]] = OrderedDict()
        self._build_first()
        self._build_follow()

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

    def _build_follow(self):
        start_symbol = self.rules[0].left
        if not start_symbol is NonTerm._START and \
            [rule.left for rule in self.rules if rule.left is NonTerm._START]:
                start_symbol = NonTerm._START
        self._follow[start_symbol] = {LIMITER}

        changed = True
        while changed:
            changed = False
            for rule in self.rules:
                for chain in rule.right:
                    for idx, symbol in enumerate(chain):
                        if not isinstance(symbol, NonTerm):
                            continue
                        after_chain = chain[idx + 1:]
                        after_chain_first = set()
                        if after_chain:
                            after_chain_first = self.first(after_chain)
                        lambda_in_after_chain = Tag.LAMBDA in after_chain
                        result = self._follow.get(symbol, set()) \
                            | after_chain_first
                        if lambda_in_after_chain:
                            result |= self._follow[rule.left]
                        if result != self._follow.get(symbol, set()):
                            self._follow[symbol] = result
                            changed = True
