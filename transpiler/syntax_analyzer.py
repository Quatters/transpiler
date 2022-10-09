from sty import fg
from functools import lru_cache
import logging
from typing import Any, Generator
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
from transpiler.tree import ParseTree, Node


logger = logging.getLogger(__name__)


class GrammarError(TranspilerError):
    pass


class SyntaxError(TranspilerError):
    pass


class SyntaxAnalyzer:
    def __init__(
        self,
        rules: list[GrammarRule] | tuple[GrammarRule],
        filepath: str | None = None
    ):
        self.rules = rules
        self._first: dict[NonTerminal, set[Terminal | Special]] = {}
        self._follow: dict[NonTerminal, set[Terminal | Special]] = {}
        self._predict_table: dict[NonTerminal, dict[Terminal, GrammarRule]] = {}

        self.filepath = filepath

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

    def parse(self, tokens: Generator[Token, Any, Any]) -> ParseTree:
        tree = ParseTree(root=self.__get_start_symbol())
        head: Node = tree.root
        stack: list[Node] = [head, ParseTree.get_node(Special.LIMITER)]
        token = tokens.__next__()

        while head.tag != Special.LIMITER:
            current_token = token
            if head.tag == token.tag:
                head.token = token
                prev_token = stack.pop(0).token
                logger.debug(
                    f'parsed token {fg.li_yellow}{token}{fg.rs} at line '
                    f'{token.line} ({token.tag}), '
                    f'waiting {stack[0]}'
                )
                token = tokens.__next__()
            elif isinstance(head.tag, Terminal) or \
                    (rule := self.predict(head.tag, current_token.tag)) is None:
                logger.debug(f'head: {head}, stack: {stack}')
                expected_token = head.tag.value.replace('_', ' ')
                line = current_token.line
                msg = (
                    f"'{current_token}' at line {line}. "
                    f"Expected '{expected_token}'"
                )
                if current_token.tag is Special.LIMITER:
                    line = prev_token.line
                    msg = f'unexpected end of string at line {line}'
                if self.filepath is not None:
                    msg += f' ({self.filepath}:{line})'
                raise SyntaxError(msg)
            else:
                logger.debug(f'using rule {rule}')
                stack.pop(0)
                for symbol in reversed(rule.right):
                    if symbol is Special.LAMBDA:
                        continue
                    node = tree.add(symbol, to=head)
                    stack.insert(0, node)
            head = stack[0]

        return tree
