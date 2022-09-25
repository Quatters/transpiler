import re
from enum import Enum


WHITESPACE = re.compile('\S')


class TranspilerError(Exception):
    pass


class Entity(Enum):
    def __repr__(self) -> str:
        return self.value


class Special(Entity):
    LAMBDA = '__LAMBDA__'
    START = '__START__'
    LIMITER = '__LIMITER__'


class Terminal(Entity):
    pass


class NonTerminal(Entity):
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

    def __init__(self, tag: Terminal, value: str, pos: int):
        self.tag = tag
        self.value = value
        self.pos = pos

    def __str__(self):
        return f'{self.value} {self.tag.value}'

class GrammarRule:
    def __init__(
        self,
        left: NonTerminal,
        right: set[tuple()]
    ):
        self.left = left
        self.right = right

    def __repr__(self) -> str:
        return f'{self.left} -> {self.right}'
