import re
from typing import Optional

from .source_info import SourceIndex


class Reader:
    """
    Class managing basic operations on the source text
    """

    def __init__(
            self,
            text: str,
            *,
            whitespace_regex: Optional[str] = r"[ \t]+",
            comments_regex: Optional[str] = None,
    ):
        """
        :param text:                the text to process
        :param whitespace_regex:    the regex pattern to use to match whitespace, or None for no whitespace support
        :param comments_regex:      the regex pattern to use to match comments, or None for no comments support
        """
        self.whitespace_regex = whitespace_regex
        self.comments_regex = comments_regex
        self.text = text
        self.cursor = 0
        self.source_index = SourceIndex(self.text, build_lazily=True)

    def debug(self, lookahead: int = 10):
        """
        Debug the current state of the reader

        :param lookahead:           the number of characters to consider when printing
        """
        print(f"DEBUG: cursor: {self.cursor}, text: {self.text[self.cursor:self.cursor + lookahead]!r}")

    def eof(self) -> bool:
        """
        Check whether the reader has reached the end of the source text

        :return:                    True if the reader has reached the end of the source text, False otherwise
        """
        return self.cursor == len(self.text)

    def peek(self):
        """
        Retrieve the current character without consuming it

        :return:                    the retrieved character
        """
        return self.text[self.cursor]

    def get(self):
        """
        Retrieve the current character and consume it

        :return:                    the retrieved character
        """
        c = self.peek()
        self.advance(1)
        return c

    def expect_regex(self, regex):
        """
        Match text with a regex pattern and consume it

        :param regex:               the pattern to match with
        :return:                    the consumed text
        """
        result = re.match(regex, self.text[self.cursor:], flags=re.DOTALL | re.MULTILINE)
        if result is None:
            return None
        self.advance(result.end(0))
        return result.group(0)

    def expect_string(self, literal: str, match_full_token: bool = True):
        """
        Match text with a literal string and consume it

        :param literal:             the literal to match with
        :param match_full_token:    whether or not the match must consume a full token
        :return:                    the consumed text
        """
        pos = self.mark()
        if self.text[self.cursor:].startswith(literal):
            self.advance(len(literal))
            if not match_full_token or self.eof():
                return literal
            p = self.peek()
            if not (p.isalnum() and all(map(str.isalnum, literal))):
                return literal
        self.rewind(pos)
        return None

    def consume_whitespace(self):
        """
        Consume whitespace as matched using the whitespace_regex pattern

        :return:                    the consumed text, or None if no match was found
        """
        if self.whitespace_regex is not None:
            return self.expect_regex(self.whitespace_regex)
        return None

    def consume_comment(self):
        """
        Consume a comment as matched using the comment_regex pattern

        :return:                    the consumed text, or None if no match was found
        """
        if self.comments_regex is not None:
            return self.expect_regex(self.comments_regex)
        return None

    def consume_non_significant(self):
        """
        Consume non-significant text, that is comments and whitespace
        """
        while True:
            pos = self.mark()
            self.consume_comment()
            self.consume_whitespace()
            if pos == self.mark():
                break

    def advance(self, offset: int):
        """
        Move the cursor forward

        :param offset:              the offset to add to the current cursor position
        """
        self.rewind(self.cursor + offset)

    def mark(self) -> int:
        """
        Get the current position of the cursor

        :return:                    the current position of the cursor
        """
        return self.cursor

    def rewind(self, position: int):
        """
        Rewind the cursor to an existing position

        :param position:            the position at which to rewind
        """
        self.cursor = position
