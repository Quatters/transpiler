from typing import Iterable
from transpiler.base import (
    Entity,
    Token,
    GrammarRule,
    NonTerminal,
    Terminal,
    Special,
)


class SyntaxAnalyzer:
    def __init__(self, tokens: Iterable[Token], rules: Iterable[GrammarRule]):
        self.tokens = tokens
        self.rules = rules
        self._first: dict[NonTerminal, set[Terminal | Special]] = {}
        self._follow: dict[NonTerminal, set[Terminal | Special]] = {}
        self._predict_table = {}
        self._build_first()
        self._build_follow()

    def first(self, chain: Entity | Iterable[Entity]) -> set[Terminal]:
        if isinstance(chain, Entity):
            chain = (chain,)
        if len(chain) == 0:
            return {Special.LAMBDA}
        symbol = chain[0]

        if isinstance(symbol, Terminal) or symbol is Special.LAMBDA:
            return {symbol}

        nonterm_first = self._first.get(symbol, set())
        lambda_in_nonterm_first = Special.LAMBDA in nonterm_first
        result = nonterm_first - {Special.LAMBDA}
        if lambda_in_nonterm_first:
            result |= self.first(chain[1:])

        return result

    def follow(self, nonterm: NonTerminal) -> set[Terminal]:
        return self._follow.get(nonterm, set())

    def _build_first(self):
        changed = True
        while changed:
            changed = False
            for rule in self.rules:
                for chain in rule.right:
                    result = self._first.get(rule.left, set()) \
                        | self.first(chain)
                    if result and result != self._first.get(rule.left, set()):
                        self._first[rule.left] = result
                        changed = True

    def __get_start_symbol(self):
        start_symbol = self.rules[0].left
        if start_symbol is not Special.START and \
            [rule.left for rule in self.rules
             if rule.left is Special.START]:
                start_symbol = Special.START
        return start_symbol


    def _build_follow(self):
        start_symbol = self.__get_start_symbol()
        self._follow[start_symbol] = {Special.LIMITER}

        changed = True
        while changed:
            changed = False
            for rule in self.rules:
                for chain in rule.right:
                    for idx, symbol in enumerate(chain):
                        if not isinstance(symbol, NonTerminal):
                            continue
                        after_chain = chain[idx + 1:]
                        after_chain_first = self.first(after_chain)
                        lambda_in_after_chain = \
                            Special.LAMBDA in after_chain_first
                        result = self._follow.get(symbol, set()) \
                            | after_chain_first - {Special.LAMBDA}
                        if lambda_in_after_chain:
                            result |= self._follow.get(rule.left, set())
                        if result and result != self._follow.get(symbol, set()):
                            self._follow[symbol] = result
                            changed = True

    def _build_predict_table(self):
        for rule in self.rules:
            for chain in rule.right:
                for symbol in self.first(chain):
                    if not isinstance(symbol, Terminal):
                        continue
                    self._insert_into_predict_table(rule.left, symbol, rule)
                    if symbol is Special.LAMBDA:
                        for fsymbol in self.follow(rule.left):
                            if not isinstance(symbol, Terminal):
                                continue
                            self._insert_into_predict_table(
                                rule.left,
                                fsymbol,
                                rule
                            )
                            if fsymbol is Special.LIMITER:
                                self._insert_into_predict_table(
                                    rule.left,
                                    Special.LIMITER,
                                    rule
                                )

    def _insert_into_predict_table(self, key1, key2, rule):
        val1 = self._predict_table.get(key1, {})
        self._predict_table[key1] = val1
        val2 = self._predict_table[key1].get(key2, set())
        val2.add(rule)
        self._predict_table[key1][key2] = val2
