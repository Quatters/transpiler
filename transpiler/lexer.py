import logging
import re
from transpiler.base import (
    WHITESPACE,
    TranspilerError,
    Token,
    Special,
    Terminal
)
from transpiler.settings import LEXER_REGEX_FLAGS


logger = logging.getLogger(__name__)


class LexerError(TranspilerError):
    pass


class UnexpectedTokenError(LexerError):
    pass


class Lexer:
    """
    Token parser from code sequence.
    """

    def __init__(self, terminal_cls: type[Terminal], rules: list):
        self.terminal_cls = terminal_cls
        parts = [f'(?P<{rule.tag.value}>{rule.regex})' for rule in rules]
        self.regex = re.compile('|'.join(parts), flags=LEXER_REGEX_FLAGS)
        self.pos: int = 0
        self.line: int = 1
        self.line_pos: int = 1

        self.buffer: str | None = None
        self.buffer_length: int = -1

    @property
    def tokens(self):
        assert self.buffer is not None, 'nothing to tokenize'
        self.buffer_length = len(self.buffer)

        while (token := self._parse_token()):
            yield token
        yield Token(Special.LIMITER, Special.LIMITER.value, -1, -1)

        self.buffer = None
        self.buffer_length = -1

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
            token = Token(
                self.terminal_cls(group),
                cursor.group(group),
                self.pos + 1,
                self._get_line()
            )
            logger.debug(f'parsed token {token}')
            self.pos = cursor.end()
            return token

        raise UnexpectedTokenError(
            f'{self.buffer[self.pos]} at line {self._get_line()}'
        )

    def _get_line(self):
        return self.buffer.count('\n', 0, self.pos) + 1

    def _get_error_area(self):
        area = self.buffer[self.pos - 15:self.pos + 15].rstrip('\n ')
        pointer = ' ' * 19 + '^'
        while area.startswith(' '):
            area = area[1:]
            pointer = pointer[1:]
        return f'\n\n... {area} ...' + '\n' + pointer
