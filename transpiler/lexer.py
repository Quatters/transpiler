import logging
import re
from sty import fg
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

    def __init__(
        self,
        terminal_cls: type[Terminal],
        rules: list,
        filepath: str | None = None,
    ):
        self.terminal_cls = terminal_cls
        parts = [f'(?P<{rule.tag.value}>{rule.regex})' for rule in rules]
        self.regex = re.compile('|'.join(parts), flags=LEXER_REGEX_FLAGS)
        self.pos: int = 0
        self.line: int = 1
        self.line_pos: int = 1

        self.buffer: str | None = None
        self.buffer_length: int = -1

        self.filepath = filepath

    @property
    def tokens(self):
        assert self.buffer is not None, 'nothing to tokenize'
        self.buffer_length = len(self.buffer)

        while (token := self._parse_token()):
            if '__' not in token.tag.value:
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
            logger.debug(
                f'parsed token {fg.li_green}{token}{fg.rs} at line '
                f'{token.line} ({group})'
            )
            self.pos = cursor.end()
            return token

        line = self._get_line()
        msg = f"{self.buffer[self.pos]} at line {line}"
        if self.filepath is not None:
            msg += f" ({self.filepath}:{line})"
        raise UnexpectedTokenError(msg)

    def _get_line(self):
        return self.buffer.count('\n', 0, self.pos) + 1
