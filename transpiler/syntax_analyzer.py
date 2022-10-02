from functools import lru_cache
import logging
from typing import Any, Generator, Iterable
from transpiler.base import (
    NormalizedGrammarRule,
    Symbol,
    Token,
    GrammarRule,
    NonTerminal,
    Terminal,
    Special,
    TranspilerError,
    normalize_rules,
)


logger = logging.getLogger(__name__)


class GrammarError(TranspilerError):
    pass


class SyntaxError(TranspilerError):
    pass


class SyntaxAnalyzer:
    def __init__(self, rules: list[GrammarRule] | tuple[GrammarRule]):
        self.rules = rules
        self._first: dict[NonTerminal, set[Terminal | Special]] = {}
        self._follow: dict[NonTerminal, set[Terminal | Special]] = {}
        self._predict_table: dict[NonTerminal, dict[Terminal, GrammarRule]] = {}
        self._build_first()
        self._build_follow()
        self._build_predict_table()

    def first(self, chain: Symbol | tuple) -> set[Terminal]:
        if isinstance(chain, Symbol):
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

    @lru_cache
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
        for rule in normalize_rules(self.rules):
            right_first = self.first(rule.right)
            for symbol in right_first:
                if isinstance(symbol, NonTerminal):
                    continue
                if isinstance(symbol, Terminal):
                    self._insert_into_predict_table(rule.left, symbol, rule)
                if Special.LAMBDA in right_first:
                    follow_left = self.follow(rule.left)
                    for fsymbol in follow_left:
                        if fsymbol is Special.LIMITER:
                            self._insert_into_predict_table(
                                rule.left,
                                fsymbol,
                                rule
                            )
                        if not isinstance(fsymbol, Terminal):
                            continue
                        self._insert_into_predict_table(
                            rule.left,
                            fsymbol,
                            rule
                        )

    def _insert_into_predict_table(self, key1, key2, rule):
        val1 = self._predict_table.get(key1, {})
        self._predict_table[key1] = val1
        val2 = self._predict_table[key1].get(key2)
        if val2 is not None and val2 != rule:
            raise GrammarError(
                f'Provided grammar is not LL(1) since [{key1}][{key2}] got '
                f'multiple rules: \n{self._predict_table[key1][key2]} '
                f'and {rule}'
            )
        else:
            self._predict_table[key1][key2] = rule

    def predict(self, key1, key2) -> NormalizedGrammarRule:
        val1 = self._predict_table.get(key1)
        if val1 is None:
            return None
        return self._predict_table[key1].get(key2)

    def parse(self, tokens: Generator[Token, Any, Any]):
        stack = [self.__get_start_symbol(), Special.LIMITER]
        token = tokens.__next__()
        head = self.__get_start_symbol()

        while head != Special.LIMITER:
            current_token = token
            if head == token.tag:
                stack.pop(0)
                logger.debug(f'parsed token {token}')
                token = tokens.__next__()
            elif isinstance(head, Terminal) or \
                (rule := self.predict(head, current_token.tag)) is None:
                raise SyntaxError(
                    f'{current_token} at line {current_token.line}'
                )
            else:
                logger.debug(f'using rule {rule}')
                stack.pop(0)
                for symbol in reversed(rule.right):
                    if symbol is Special.LAMBDA:
                        continue
                    stack.insert(0, symbol)
            head = stack[0]
