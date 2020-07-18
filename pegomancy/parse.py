from typing import Callable, Dict, List, Optional

from .reader import Reader
from .source_info import SourceLocation


class ParseError(Exception):
    def __init__(self, message: str, location: SourceLocation):
        self.message = message
        self.location = location

    def __repr__(self):
        return f"ParseError(message={self.message!r}, location={self.location!r})"

    def __str__(self):
        return f"parse error: {self.message} (at {self.location})"


class CutError(Exception):
    def __init__(self, message: str, location: SourceLocation):
        self.message = message
        self.location = location

    def __repr__(self):
        return f"CutError(message={self.message!r}, location={self.location!r})"

    def __str__(self):
        return f"parse error: {self.message} (at {self.location})"


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

    def make_error(self, *, message: str, pos: int):
        return ParseError(message=message, location=self.reader.source_index.location_from_offset(pos))

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


def _handle_result(result):
    success, value = result
    if success:
        return value
    else:
        raise value


def _call_rule(f, self, *args):
    try:
        result = f(self, *args)
        return True, result
    except ParseError as e:
        return False, e


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
            result = _call_rule(f, self, *args)
            end_position = self.mark()
            position_cache[invocation_key] = result, end_position
        return _handle_result(result)

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
            failing_seed = self.make_error(message=f"expected a {f.__name__}", pos=pos)
            position_cache[invocation_key] = last_result, last_pos = (False, failing_seed), pos
            while True:
                self.rewind(pos)
                result = _call_rule(f, self, *args)
                end_position = self.mark()
                if end_position <= last_pos:
                    break
                position_cache[invocation_key] = result, end_position
                last_result, last_pos = result, end_position
            result = last_result
            self.rewind(last_pos)
        return _handle_result(result)

    return wrapped_func


class RawTextParser(BaseParser):
    def _wrap_node(self, rule_name, values, attributes):
        named = {}
        values, attributes = [list(t) for t in zip(*filter(lambda va: not va[1].ignore, zip(values, attributes)))]
        for value, attr in zip(values, attributes):
            if attr.name is not None:
                assert attr.name not in named, "two items cannot share the same name in the same alternative"
                named[attr.name] = value
        if named:
            values = named
        elif len(values) == 1:
            values = values[0]
        if self.rule_handler is not None and hasattr(self.rule_handler, rule_name):
            values = getattr(self.rule_handler, rule_name)(values)
        return values

    def _lookahead(self, f):
        """
        Apply a rule without consuming any input, succeeding if the rule succeeds

        :param f:                   the rule
        """
        pos = self.mark()
        result = f()
        self.rewind(pos)
        return result

    def _not_lookahead(self, f):
        """
        Apply a rule without consuming any input, succeeding if the rule fails

        :param f:                   the rule
        """
        try:
            self._lookahead(f)
        except ParseError:
            pass
        else:
            raise self.make_error(message=f"unexpected {f.__name__}", pos=self.mark())

    def _maybe(self, f):
        """
        Apply a parsing rule, succeeding even if the rule fails

        :param f:                   the rule
        """
        pos = self.mark()
        try:
            return f()
        except ParseError:
            self.rewind(pos)
            return None

    def _repeat(self, minimum, f):
        """
        Repeat a rule multiple times

        :param minimum:             the minimum number of times the rule must succeed
        :param f:                   the rule
        """
        pos = self.mark()
        matches = []
        while True:
            last = self.mark()
            try:
                matches.append(f())
            except ParseError:
                self.rewind(last)
                break
        if len(matches) >= minimum:
            return matches
        self.rewind(pos)
        raise self.make_error(
            message=f"expected at least {minimum} repetitions of a {f.__name__}",
            pos=self.mark()
        )

    def _sep_by(self, f, sep):
        pos = self.mark()
        try:
            matches = [f()]
            last = self.mark()
            while True:
                try:
                    matches.append(sep())
                except ParseError:
                    self.rewind(last)
                    break
                matches.append(f())
                last = self.mark()
            return matches
        except ParseError:
            self.rewind(pos)
            raise

    def _maybe_sep_by(self, f, sep):
        try:
            return self._sep_by(f, sep)
        except ParseError:
            return []

    @parsing_rule
    def expect_string(self, expected: str) -> str:
        """
        Expect an exact string

        :param expected:            the expected string
        :return:                    the matched string if any, otherwise None
        """
        s = self.reader.expect_string(expected)
        if s is None:
            raise self.make_error(message=f"expected '{expected}'", pos=self.mark())
        return s

    @parsing_rule
    def expect_regex(self, regex: str) -> str:
        """
        Expect a string matching a regular expression

        :param regex:               the regular expression to match
        :return:                    the matched string if any, otherwise None
        """
        s = self.reader.expect_regex(regex)
        if s is None:
            raise self.make_error(message=f"expected text matching the '{regex}' pattern", pos=self.mark())
        return s

    @parsing_rule
    def expect_eof(self):
        """
        Expect the cursor to have reached the end of the source text
        """
        if not self.eof():
            raise self.make_error(message=f"expected end of input", pos=self.mark())
