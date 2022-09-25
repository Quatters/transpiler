import re
from transpiler.base import WHITESPACE, TranspilerError, Token
from transpiler.settings import LEXER_REGEX_FLAGS, Tag


class LexerError(TranspilerError):
    pass


class UnexpectedTokenError(LexerError):
    def __init__(self, ref):
        return super().__init__(ref)


class Lexer:
    """
    Token parser from code sequence.
    """

    def __init__(self, code: str, rules: list[tuple[Tag, str]]) -> None:
        parts = [f'(?P<{rule.tag.value}>{rule.regex})' for rule in rules]
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
            token = Token(Tag(group), cursor.group(group), self.pos + 1)
            self.pos = cursor.end()
            return token

        raise UnexpectedTokenError(self._get_error_area())

    def _get_error_area(self):
        area = self.buffer[self.pos - 15:self.pos + 15].rstrip('\n ')
        pointer = ' ' * 19 + '^'
        while area.startswith(' '):
            area = area[1:]
            pointer = pointer[1:]
        return f'\n\n... {area} ...' + '\n' + pointer
