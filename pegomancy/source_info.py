from typing import NamedTuple
from itertools import islice
from bisect import bisect_right


class SourceLocation(NamedTuple):
    """
    Class representing a location inside the source text
    """
    offset: int
    line: int
    column: int

    def __repr__(self):
        return f"SourceLocation(offset={self.offset}, line={self.line}, column={self.column})"

    def __str__(self):
        return f"{self.line}:{self.column}"


class SourceRange(NamedTuple):
    """
    Class representing a range of text inside the source text
    """
    start: SourceLocation
    end: SourceLocation

    def __repr__(self):
        return f"SourceRange(start={self.start!r}, end={self.end!r})"


class _LineCache:
    """
    Class maintaining a cache of the locations for each line inside the source text
    """

    def __init__(self, text: str, *, build_lazily=True):
        self.text = text
        self.line_offsets = []
        self.line_ranges = []
        self.fully_built = False
        if build_lazily is False:
            self._build_cache(up_to=len(self.text))

    def _build_cache(self, up_to: int):
        if self.fully_built is True:
            return
        if not self.line_ranges:
            start = SourceLocation(0, line=1, column=1)
        else:
            prev_end = self.line_ranges[-1].end
            start = SourceLocation(prev_end.offset + 1, line=prev_end.line + 1, column=1)
        for i, c in islice(enumerate(self.text), start.offset, up_to):
            if c == "\n":
                end = SourceLocation(i, line=start.line, column=i - start.offset)
                self.line_offsets.append(start.offset)
                self.line_ranges.append(SourceRange(start, end))
                start = SourceLocation(end.offset + 1, line=end.line + 1, column=1)
        if up_to >= len(self.text):
            end = SourceLocation(up_to, line=start.line, column=up_to - start.offset)
            self.line_offsets.append(start.offset)
            self.line_ranges.append(SourceRange(start, end))
            self.fully_built = True

    def line_range_from_offset(self, offset: int) -> SourceRange:
        up_to = offset + 1
        while up_to < len(self.text) and self.text[up_to] != "\n":
            up_to += 1
        self._build_cache(up_to=up_to + 1)
        index = bisect_right(self.line_offsets, offset)
        if index > 0:
            index -= 1
        return self.line_ranges[index]


class SourceIndex:
    """
    Class indexing the source text to allow retrieving extended location information
    """

    def __init__(self, text: str, *, build_lazily=True):
        self.text = text
        self.line_cache = _LineCache(text, build_lazily=build_lazily)

    def line_range_from_offset(self, offset: int) -> SourceRange:
        """
        Retrieve the range associated with the line containing the given offset

        :param offset:              the offset
        :return:                    a SourceRange representing the line
        """
        return self.line_cache.line_range_from_offset(offset)

    def line_from_offset(self, offset: int) -> int:
        """
        Retrieve the number of the line containing the given offset

        :param offset:              the offset
        :return:                    the line number
        """
        return self.line_range_from_offset(offset).start.line

    def column_from_position(self, offset: int) -> int:
        """
        Retrieve the number of the column containing the given offset

        :param offset:              the position
        :return:                    the column number
        """
        current_offset = offset
        while current_offset > 0 and (current_offset >= len(self.text) or self.text[current_offset] != "\n"):
            current_offset -= 1
        return offset - current_offset

    def text_in_range(self, source_range: SourceRange) -> str:
        """
        Retrieve the text delimited by a given SourceRange

        :param source_range:        the range to use to select text
        :return:                    the text
        """
        return self.text[source_range.start.offset:source_range.end.offset]

    def location_from_offset(self, offset: int) -> SourceLocation:
        """
        Retrieve the extended location information for a given offset

        :param offset:              the offset
        :return:                    the extended location information
        """
        line = self.line_from_offset(offset)
        column = self.column_from_position(offset)
        return SourceLocation(offset, line=line, column=column)

    def range_from_offset_range(self, start_offset: int, end_offset: int) -> SourceRange:
        """
        Retrieve the extended range information from a range of offsets

        :param start_offset:        the offset delimiting the start of the range
        :param end_offset:          the offset delimiting the end of the range
        :return:                    the extended range information
        """
        return SourceRange(self.location_from_offset(start_offset), self.location_from_offset(end_offset))
