from typing import Callable, Dict, List, Optional

from .reader import Reader


class BaseParser:
    """
    Base class for all parsers
    """

    DEFAULT_WHITESPACE_REGEX = r"[ \t]+"

    def __init__(
            self,
            text: str,
            rule_handler=None,
            *,
            whitespace_regex: Optional[str] = DEFAULT_WHITESPACE_REGEX,
            comments_regex: Optional[str] = None,
    ):
        self.cache = {}
        self.reader = Reader(text, whitespace_regex=whitespace_regex, comments_regex=comments_regex)
        self.rule_handler = rule_handler

    def mark(self) -> int:
        """
        Get the current position of the cursor

        :return:            the current position of the cursor
        """
        return self.reader.mark()

    def rewind(self, pos: int):
        """
        Rewind the cursor to an existing position

        :param pos:         the position at which to rewind
        """
        self.reader.rewind(pos)

    def eof(self) -> bool:
        return self.reader.eof()

    def peek(self):
        return self.reader.peek()

    def get(self):
        return self.reader.get()


class RawTextParser(BaseParser):
    def read_while(self, predicate: Callable[[str], bool]) -> str:
        """
        Read data character by character while a predicate validates it

        :param predicate:           the predicate validating data
        :return:                    the data read
        """
        result = ""
        while not self.eof() and predicate(self.peek()):
            result += self.get()
        return result

    def expect_string(self, expected: str) -> Optional[str]:
        """
        Expect an exact string

        :param expected:            the expected string
        :return:                    the matched string if any, otherwise None
        """
        self.reader.consume_non_significant()
        return self.reader.expect_string(expected)

    def expect_enclosed(self, opening: str, closing: str) -> Optional[str]:
        """
        Expect a string enclosed between two delimiters

        :param opening:             the string to use as opening delimiter
        :param closing:             the string to use as closing delimiter
        :return:                    the matched string if any (without the delimiters), otherwise None
        """
        pos = self.mark()
        if self.expect_string(opening) is not None:
            s = self.read_while(lambda c: c != closing)
            if self.expect_string(closing) is not None:
                return s
        self.rewind(pos)
        return None

    def expect_quoted(self, quote: str = '"') -> Optional[str]:
        """
        Expect a quoted string

        :param quote:               the string to use as quote, default is '"'
        :return:                    the matched string if any (without the quotes), otherwise None
        """
        return self.expect_enclosed(opening=quote, closing=quote)

    def expect_regex(self, regex: str) -> Optional[str]:
        """
        Expect a string matching a regular expression

        :param regex:               the regular expression to match
        :return:                    the matched string if any, otherwise None
        """
        return self.reader.expect_regex(regex)


def parsing_rule(f):
    """
    Wrap a parsing function to memoize its calls

    :param f:                   the function to wrap
    :return:                    the wrapped function
    """

    def wrapped_func(self: BaseParser, *args):
        self.reader.consume_non_significant()
        pos = self.mark()
        position_cache = self.cache.get(pos)
        if position_cache is None:
            position_cache = self.cache[pos] = {}
        invocation_key = (f, args)
        if invocation_key in position_cache:
            result, end_position = position_cache[invocation_key]
            self.rewind(end_position)
        else:
            result = f(self, *args)
            end_position = self.mark()
            position_cache[invocation_key] = result, end_position
        return result

    return wrapped_func


def left_recursive_parsing_rule(f):
    """
    Wrap a left-recursive parsing function to memoize its calls

    :param f:                   the function to wrap
    :return:                    the wrapped function
    """

    def wrapped_func(self: BaseParser, *args):
        """
        The approach used here allows writing left-recursive rules, which otherwise would recurse indefinitely.
        Note that it does not support indirect left recursion.

        The idea is to first "seed" the cache with a failing result in order to "force" the recursion to stop.
        Then, we call the (undecorated) rule again, which will obtain the failing result from the cache and thus try
        the next alternative, caching that result. We keep on calling the (undecorated) rule ("growing the seed")
        until it stops growing (it either fails or does not parse more data than the previous call).

        The approach is described by:
        - "Packrat Parsers Can Support Left Recursion" (http://www.vpri.org/pdf/tr2007002_packrat.pdf)
        - "Left-recursive PEG Grammars" (https://link.medium.com/njpbvhxsE5)
        """
        self.reader.consume_non_significant()
        pos = self.mark()
        position_cache = self.cache.get(pos)
        if position_cache is None:
            position_cache = self.cache[pos] = {}
        invocation_key = (f, args)
        if invocation_key in position_cache:
            result, end_position = position_cache[invocation_key]
            self.rewind(end_position)
        else:
            position_cache[invocation_key] = None, pos
            last_result, last_pos = None, pos
            while True:
                self.rewind(pos)
                result = f(self, *args)
                end_position = self.mark()
                if end_position <= last_pos:
                    break
                position_cache[invocation_key] = result, end_position
                last_result, last_pos = result, end_position
            result = last_result
            self.rewind(last_pos)
        return result

    return wrapped_func
