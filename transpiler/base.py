import re
from enum import Enum


WHITESPACE = re.compile('\S')


class TranspilerError(Exception):
    pass


class Symbol(Enum):
    def __repr__(self) -> str:
        return str(self.value)

    def __str__(self) -> str:
        return str(self.value)

    def __eq__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)


class Special(Symbol):
    LAMBDA = '__LAMBDA__'
    START = '__START__'
    LIMITER = '__LIMITER__'


class Terminal(Symbol):
    pass


class NonTerminal(Symbol):
    pass


class LexerRule:
    """
    Token definition and regular expression mapping. Used by lexer.
    """

    def __init__(self, tag: Terminal, regex: str) -> None:
        self.tag = tag
        self.regex = regex


class Token:
    """
    Minimal sensible unit of code sequence.
    """

    def __init__(self, tag: Terminal, value: str, pos: int, line: int):
        self.tag = tag
        self.value = value
        self.pos = pos
        self.line = line

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self.value)

class GrammarRule:
    def __init__(self, left: NonTerminal, right: set[tuple]):
        self.left = left
        self.right = right

    def __repr__(self) -> str:
        return f'{repr(self.left)} -> {self.right}'


class NormalizedGrammarRule:
    def __init__(self, left: NonTerminal, right: tuple):
        self.left = left
        self.right = right

    def __repr__(self) -> str:
        return f'{repr(self.left)} -> {self.right}'

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self.left == other.left and self.right == other.right

    def __hash__(self) -> int:
        return hash((self.left, self.right))


def normalize_rules(rule_list: list[GrammarRule]) \
    -> list[NormalizedGrammarRule]:
    normalized_rules = []
    for rule in rule_list:
        for chain in rule.right:
            normalized_rules.append(
                NormalizedGrammarRule(rule.left, chain)
            )
    return normalized_rules
