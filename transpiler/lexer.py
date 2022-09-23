import re
from enum import Enum

from transpiler.base import WHITESPACE, Def, TranspilerError
from transpiler.settings import LEXER_REGEX_FLAGS


class Token:
    """
    Minimal sensible unit of code sequence.
    """

    def __init__(self, def_: Def, value: str, pos: int):
        self.def_ = def_
        self.value = value
        self.pos = pos

    def __str__(self):
        return self.value


class LexerError(TranspilerError):
    pass


class UnexpectedTokenError(LexerError):
    def __init__(self, ref):
        return super().__init__(f'near {ref}')


class Lexer:
    """
    Token parser from code sequence.
    """

    def __init__(self, code: str, rules: list[tuple[Def, str]]) -> None:
        parts = [f'(?P<{rule.def_.value}>{rule.regex})' for rule in rules]
        self.regex = re.compile('|'.join(parts), flags=LEXER_REGEX_FLAGS)
        self.pos: int = 0
        self.line: int = 1
        self.line_pos: int = 1
        self.buffer: str = code
        self.buffer_length = len(self.buffer)

    @property
    def tokens(self):
        while (token := self._parse_token()):
            yield token

    def _parse_token(self) -> Token | None:
        if self.pos > self.buffer_length:
            return None

        cursor = WHITESPACE.search(self.buffer, self.pos)
        if cursor is None:
            return None

        self.pos = cursor.start()
        cursor = self.regex.match(self.buffer, self.pos)
        if cursor:
            group = cursor.lastgroup
            token = Token(Def(group), cursor.group(group), self.pos + 1)
            self.pos = cursor.end()
            return token

        msg = self.buffer[self.pos - 15:self.pos + 15].strip()
        raise UnexpectedTokenError(msg)
