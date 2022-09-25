from copy import deepcopy
from typing import Iterable
from transpiler.base import Tag, NonTerm, Token, GrammarRule


LIMITER = 'LIMITER'


class SyntaxAnalyzer:
    _first = None
    _follow = None

    def __init__(
        self,
        tokens: Iterable[Token],
        rules: list[GrammarRule],
    ):
        self.tokens = tokens
        self.rules = rules

    def _collect_set(
        self,
        initial_set: set,
        symbols: Iterable,
        additional_set: set
    ):
        result = deepcopy(initial_set)

        for idx, symbol in enumerate(symbols):
            if isinstance(symbol, NonTerm):
                result |= {
                    s for s in self._first.get(symbol, set())
                    if s != Tag.LAMBDA
                }
                if Tag.LAMBDA in self._first.get(symbol, set()):
                    if idx + 1 < len(symbols) and \
                        symbols[idx + 1] != Tag.LAMBDA:
                        continue
                    result |= additional_set
                else:
                    break
            else:
                result |= {symbol}
                break

        return result

    def _build_first(self):
        self._first = {rule.left: set() for rule in self.rules}

        changed = True
        while changed:
            changed = False
            for rule in self.rules:
                s = self._first.get(rule.left, set())
                for production in rule.right:
                    s |= self._collect_set(s, production, {Tag.LAMBDA})

                if (len(self._first.get(rule.left, set())) or -1) != len(s):
                    self._first[rule.left] = deepcopy(s)
                    changed = True

