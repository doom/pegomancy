import re
import string
from typing import Optional


class Reader:
    """
    Class managing basic operations on the source text
    """

    def __init__(
            self,
            text: str,
            *,
            whitespace_regex: Optional[str] = None,
            comments_regex: Optional[str] = None,
    ):
        self.whitespace_regex = whitespace_regex
        self.comments_regex = comments_regex
        self.text = text
        self.cursor = 0

    def debug(self, lookahead: int = 10):
        print(f"DEBUG: cursor: {self.cursor}, text: {self.text[self.cursor:self.cursor + lookahead]!r}")

    def eof(self) -> bool:
        return self.cursor == len(self.text)

    def peek(self):
        return self.text[self.cursor]

    def get(self):
        c = self.peek()
        self.advance(1)
        return c

    def expect_regex(self, regex):
        """
        Match text with a regex pattern and consume it

        :param regex:       the pattern to match with
        :return:            the consumed text
        """
        result = re.match(regex, self.text[self.cursor:], flags=re.DOTALL | re.MULTILINE)
        if result is None:
            return None
        self.advance(result.end(0))
        return result.group(0)

    def expect_string(self, literal: str, allow_partial: bool = False):
        pos = self.mark()
        if self.text[self.cursor:].startswith(literal):
            self.advance(len(literal))
            if allow_partial or self.eof():
                return literal
            p = self.peek()
            if p is None or not (p.isalnum() and all(map(str.isalnum, literal))):
                return literal
        self.rewind(pos)
        return None

    def advance(self, offset: int):
        return self.rewind(self.cursor + offset)

    def mark(self):
        return self.cursor

    def rewind(self, cursor):
        self.cursor = cursor
