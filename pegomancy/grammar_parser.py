from pegomancy.parse import \
    CutError, \
    ParseError, \
    RawTextParser, \
    parsing_rule, \
    left_recursive_parsing_rule

from pegomancy.grammar_items import ItemAttributes


class GrammarParser(RawTextParser):
    @parsing_rule
    def synthesized_rule_0(self):
        pos = self.mark()
        cut = False
        try:
            v0 = self.expect_regex(r'[a-zA-Z_][a-zA-Z0-9_]*')
            v1 = self.expect_string(':')
            node = self._wrap_node(
                'synthesized_rule_0',
                [v0, v1],
                [ItemAttributes(name='name', ignore=False), ItemAttributes(name=None, ignore=False)]
            )
            return node
        except ParseError as e:
            self.rewind(pos)
            if cut is True:
                raise CutError(e.message, e.location)

        raise self.make_error(message=f"expected a synthesized_rule_0", pos=self.mark())

    @parsing_rule
    def __(self):
        pos = self.mark()
        cut = False
        try:
            v0 = self._maybe(lambda: self.expect_regex(r'[ \n\t]+'))
            node = self._wrap_node(
                '__',
                [v0],
                [ItemAttributes(name=None, ignore=False)]
            )
            return node
        except ParseError as e:
            self.rewind(pos)
            if cut is True:
                raise CutError(e.message, e.location)

        raise self.make_error(message=f"expected a __", pos=self.mark())

    @parsing_rule
    def verbatim_block(self):
        pos = self.mark()
        cut = False
        try:
            v0 = self.expect_string('@verbatim')
            v1 = cut = True
            v2 = self.expect_string('%{')
            v3 = self.expect_regex(r'^(.*?)(?=%})')
            v4 = self.expect_string('%}')
            v5 = self._repeat(1, lambda: self.expect_string('\n'))
            node = self._wrap_node(
                'verbatim_block',
                [v0, v1, v2, v3, v4, v5],
                [ItemAttributes(name=None, ignore=False), ItemAttributes(name=None, ignore=True),
                 ItemAttributes(name=None, ignore=False), ItemAttributes(name='block', ignore=False),
                 ItemAttributes(name=None, ignore=False), ItemAttributes(name=None, ignore=False)]
            )
            return node
        except ParseError as e:
            self.rewind(pos)
            if cut is True:
                raise CutError(e.message, e.location)

        raise self.make_error(message=f"expected a verbatim_block", pos=self.mark())

    @parsing_rule
    def setting(self):
        pos = self.mark()
        cut = False
        try:
            v0 = self.expect_string('@set')
            v1 = cut = True
            v2 = self.expect_regex(r'[ \t]+')
            v3 = self.expect_regex(r'[a-zA-Z_][a-zA-Z0-9_]*')
            v4 = self._repeat(1, lambda: self.expect_string('\n'))
            node = self._wrap_node(
                'setting',
                [v0, v1, v2, v3, v4],
                [ItemAttributes(name=None, ignore=False), ItemAttributes(name=None, ignore=True),
                 ItemAttributes(name=None, ignore=False), ItemAttributes(name='setting', ignore=False),
                 ItemAttributes(name=None, ignore=False)]
            )
            return node
        except ParseError as e:
            self.rewind(pos)
            if cut is True:
                raise CutError(e.message, e.location)

        raise self.make_error(message=f"expected a setting", pos=self.mark())

    @parsing_rule
    def rule_name(self):
        pos = self.mark()
        cut = False
        try:
            v0 = self.expect_regex(r'[a-zA-Z_][a-zA-Z0-9_]*')
            node = self._wrap_node(
                'rule_name',
                [v0],
                [ItemAttributes(name=None, ignore=False)]
            )
            return node
        except ParseError as e:
            self.rewind(pos)
            if cut is True:
                raise CutError(e.message, e.location)

        raise self.make_error(message=f"expected a rule_name", pos=self.mark())

    @parsing_rule
    def literal(self):
        pos = self.mark()
        cut = False
        try:
            v0 = self.expect_string('"')
            v1 = self.expect_regex(r'[^"]*')
            v2 = self.expect_string('"')
            node = self._wrap_node(
                'literal',
                [v0, v1, v2],
                [ItemAttributes(name=None, ignore=False), ItemAttributes(name=None, ignore=False),
                 ItemAttributes(name=None, ignore=False)]
            )
            return node
        except ParseError as e:
            self.rewind(pos)
            if cut is True:
                raise CutError(e.message, e.location)

        cut = False
        try:
            v0 = self.expect_string('\'')
            v1 = self.expect_regex(r'[^\']*')
            v2 = self.expect_string('\'')
            node = self._wrap_node(
                'literal',
                [v0, v1, v2],
                [ItemAttributes(name=None, ignore=False), ItemAttributes(name=None, ignore=False),
                 ItemAttributes(name=None, ignore=False)]
            )
            return node
        except ParseError as e:
            self.rewind(pos)
            if cut is True:
                raise CutError(e.message, e.location)

        raise self.make_error(message=f"expected a literal", pos=self.mark())

    @parsing_rule
    def regex(self):
        pos = self.mark()
        cut = False
        try:
            v0 = self.expect_string('r')
            v1 = self.literal()
            node = self._wrap_node(
                'regex',
                [v0, v1],
                [ItemAttributes(name=None, ignore=False), ItemAttributes(name=None, ignore=False)]
            )
            return node
        except ParseError as e:
            self.rewind(pos)
            if cut is True:
                raise CutError(e.message, e.location)

        raise self.make_error(message=f"expected a regex", pos=self.mark())

    @parsing_rule
    def atom(self):
        pos = self.mark()
        cut = False
        try:
            v0 = self.regex()
            node = self._wrap_node(
                'atom',
                [v0],
                [ItemAttributes(name=None, ignore=False)]
            )
            return node
        except ParseError as e:
            self.rewind(pos)
            if cut is True:
                raise CutError(e.message, e.location)

        cut = False
        try:
            v0 = self.literal()
            node = self._wrap_node(
                'atom',
                [v0],
                [ItemAttributes(name=None, ignore=False)]
            )
            return node
        except ParseError as e:
            self.rewind(pos)
            if cut is True:
                raise CutError(e.message, e.location)

        cut = False
        try:
            v0 = self.rule_name()
            node = self._wrap_node(
                'atom',
                [v0],
                [ItemAttributes(name='rule_name', ignore=False)]
            )
            return node
        except ParseError as e:
            self.rewind(pos)
            if cut is True:
                raise CutError(e.message, e.location)

        cut = False
        try:
            v0 = self.expect_string('(')
            v1 = cut = True
            v2 = self.alternatives()
            v3 = self.expect_string(')')
            node = self._wrap_node(
                'atom',
                [v0, v1, v2, v3],
                [ItemAttributes(name=None, ignore=False), ItemAttributes(name=None, ignore=True),
                 ItemAttributes(name='parenthesized_alts', ignore=False), ItemAttributes(name=None, ignore=False)]
            )
            return node
        except ParseError as e:
            self.rewind(pos)
            if cut is True:
                raise CutError(e.message, e.location)

        raise self.make_error(message=f"expected a atom", pos=self.mark())

    @parsing_rule
    def maybe(self):
        pos = self.mark()
        cut = False
        try:
            v0 = self.atom()
            v1 = self.expect_string('?')
            node = self._wrap_node(
                'maybe',
                [v0, v1],
                [ItemAttributes(name='atom', ignore=False), ItemAttributes(name=None, ignore=False)]
            )
            return node
        except ParseError as e:
            self.rewind(pos)
            if cut is True:
                raise CutError(e.message, e.location)

        raise self.make_error(message=f"expected a maybe", pos=self.mark())

    @parsing_rule
    def one_or_more(self):
        pos = self.mark()
        cut = False
        try:
            v0 = self.atom()
            v1 = self.expect_string('+')
            node = self._wrap_node(
                'one_or_more',
                [v0, v1],
                [ItemAttributes(name='atom', ignore=False), ItemAttributes(name=None, ignore=False)]
            )
            return node
        except ParseError as e:
            self.rewind(pos)
            if cut is True:
                raise CutError(e.message, e.location)

        raise self.make_error(message=f"expected a one_or_more", pos=self.mark())

    @parsing_rule
    def zero_or_more(self):
        pos = self.mark()
        cut = False
        try:
            v0 = self.atom()
            v1 = self.expect_string('*')
            node = self._wrap_node(
                'zero_or_more',
                [v0, v1],
                [ItemAttributes(name='atom', ignore=False), ItemAttributes(name=None, ignore=False)]
            )
            return node
        except ParseError as e:
            self.rewind(pos)
            if cut is True:
                raise CutError(e.message, e.location)

        raise self.make_error(message=f"expected a zero_or_more", pos=self.mark())

    @parsing_rule
    def maybe_sep_by(self):
        pos = self.mark()
        cut = False
        try:
            v0 = self.expect_string('{')
            v1 = self.item()
            v2 = self.atom()
            v3 = self.expect_string('...')
            v4 = self.expect_string('}')
            v5 = self.expect_string('*')
            node = self._wrap_node(
                'maybe_sep_by',
                [v0, v1, v2, v3, v4, v5],
                [ItemAttributes(name=None, ignore=False), ItemAttributes(name='element', ignore=False),
                 ItemAttributes(name='separator', ignore=False), ItemAttributes(name=None, ignore=False),
                 ItemAttributes(name=None, ignore=False), ItemAttributes(name=None, ignore=False)]
            )
            return node
        except ParseError as e:
            self.rewind(pos)
            if cut is True:
                raise CutError(e.message, e.location)

        raise self.make_error(message=f"expected a maybe_sep_by", pos=self.mark())

    @parsing_rule
    def sep_by(self):
        pos = self.mark()
        cut = False
        try:
            v0 = self.expect_string('{')
            v1 = self.item()
            v2 = self.atom()
            v3 = self.expect_string('...')
            v4 = self.expect_string('}')
            v5 = self.expect_string('+')
            node = self._wrap_node(
                'sep_by',
                [v0, v1, v2, v3, v4, v5],
                [ItemAttributes(name=None, ignore=False), ItemAttributes(name='element', ignore=False),
                 ItemAttributes(name='separator', ignore=False), ItemAttributes(name=None, ignore=False),
                 ItemAttributes(name=None, ignore=False), ItemAttributes(name=None, ignore=False)]
            )
            return node
        except ParseError as e:
            self.rewind(pos)
            if cut is True:
                raise CutError(e.message, e.location)

        raise self.make_error(message=f"expected a sep_by", pos=self.mark())

    @parsing_rule
    def lookahead(self):
        pos = self.mark()
        cut = False
        try:
            v0 = self.expect_string('&')
            v1 = cut = True
            v2 = self.item()
            node = self._wrap_node(
                'lookahead',
                [v0, v1, v2],
                [ItemAttributes(name=None, ignore=False), ItemAttributes(name=None, ignore=True),
                 ItemAttributes(name='item', ignore=False)]
            )
            return node
        except ParseError as e:
            self.rewind(pos)
            if cut is True:
                raise CutError(e.message, e.location)

        raise self.make_error(message=f"expected a lookahead", pos=self.mark())

    @parsing_rule
    def negative_lookahead(self):
        pos = self.mark()
        cut = False
        try:
            v0 = self.expect_string('!')
            v1 = cut = True
            v2 = self.item()
            node = self._wrap_node(
                'negative_lookahead',
                [v0, v1, v2],
                [ItemAttributes(name=None, ignore=False), ItemAttributes(name=None, ignore=True),
                 ItemAttributes(name='item', ignore=False)]
            )
            return node
        except ParseError as e:
            self.rewind(pos)
            if cut is True:
                raise CutError(e.message, e.location)

        raise self.make_error(message=f"expected a negative_lookahead", pos=self.mark())

    @parsing_rule
    def cut(self):
        pos = self.mark()
        cut = False
        try:
            v0 = self.expect_string('~')
            node = self._wrap_node(
                'cut',
                [v0],
                [ItemAttributes(name=None, ignore=False)]
            )
            return node
        except ParseError as e:
            self.rewind(pos)
            if cut is True:
                raise CutError(e.message, e.location)

        raise self.make_error(message=f"expected a cut", pos=self.mark())

    @parsing_rule
    def eof_(self):
        pos = self.mark()
        cut = False
        try:
            v0 = self.expect_string('EOF')
            node = self._wrap_node(
                'eof_',
                [v0],
                [ItemAttributes(name=None, ignore=False)]
            )
            return node
        except ParseError as e:
            self.rewind(pos)
            if cut is True:
                raise CutError(e.message, e.location)

        raise self.make_error(message=f"expected a eof_", pos=self.mark())

    @parsing_rule
    def item(self):
        pos = self.mark()
        cut = False
        try:
            v0 = self.cut()
            node = self._wrap_node(
                'item',
                [v0],
                [ItemAttributes(name=None, ignore=False)]
            )
            return node
        except ParseError as e:
            self.rewind(pos)
            if cut is True:
                raise CutError(e.message, e.location)

        cut = False
        try:
            v0 = self.eof_()
            node = self._wrap_node(
                'item',
                [v0],
                [ItemAttributes(name=None, ignore=False)]
            )
            return node
        except ParseError as e:
            self.rewind(pos)
            if cut is True:
                raise CutError(e.message, e.location)

        cut = False
        try:
            v0 = self.sep_by()
            node = self._wrap_node(
                'item',
                [v0],
                [ItemAttributes(name=None, ignore=False)]
            )
            return node
        except ParseError as e:
            self.rewind(pos)
            if cut is True:
                raise CutError(e.message, e.location)

        cut = False
        try:
            v0 = self.maybe_sep_by()
            node = self._wrap_node(
                'item',
                [v0],
                [ItemAttributes(name=None, ignore=False)]
            )
            return node
        except ParseError as e:
            self.rewind(pos)
            if cut is True:
                raise CutError(e.message, e.location)

        cut = False
        try:
            v0 = self.maybe()
            node = self._wrap_node(
                'item',
                [v0],
                [ItemAttributes(name=None, ignore=False)]
            )
            return node
        except ParseError as e:
            self.rewind(pos)
            if cut is True:
                raise CutError(e.message, e.location)

        cut = False
        try:
            v0 = self.one_or_more()
            node = self._wrap_node(
                'item',
                [v0],
                [ItemAttributes(name=None, ignore=False)]
            )
            return node
        except ParseError as e:
            self.rewind(pos)
            if cut is True:
                raise CutError(e.message, e.location)

        cut = False
        try:
            v0 = self.zero_or_more()
            node = self._wrap_node(
                'item',
                [v0],
                [ItemAttributes(name=None, ignore=False)]
            )
            return node
        except ParseError as e:
            self.rewind(pos)
            if cut is True:
                raise CutError(e.message, e.location)

        cut = False
        try:
            v0 = self.lookahead()
            node = self._wrap_node(
                'item',
                [v0],
                [ItemAttributes(name=None, ignore=False)]
            )
            return node
        except ParseError as e:
            self.rewind(pos)
            if cut is True:
                raise CutError(e.message, e.location)

        cut = False
        try:
            v0 = self.negative_lookahead()
            node = self._wrap_node(
                'item',
                [v0],
                [ItemAttributes(name=None, ignore=False)]
            )
            return node
        except ParseError as e:
            self.rewind(pos)
            if cut is True:
                raise CutError(e.message, e.location)

        cut = False
        try:
            v0 = self.atom()
            node = self._wrap_node(
                'item',
                [v0],
                [ItemAttributes(name=None, ignore=False)]
            )
            return node
        except ParseError as e:
            self.rewind(pos)
            if cut is True:
                raise CutError(e.message, e.location)

        raise self.make_error(message=f"expected a item", pos=self.mark())

    @parsing_rule
    def named_item(self):
        pos = self.mark()
        cut = False
        try:
            v0 = self._maybe(lambda: self.synthesized_rule_0())
            v1 = self.item()
            node = self._wrap_node(
                'named_item',
                [v0, v1],
                [ItemAttributes(name='name', ignore=False), ItemAttributes(name='item', ignore=False)]
            )
            return node
        except ParseError as e:
            self.rewind(pos)
            if cut is True:
                raise CutError(e.message, e.location)

        raise self.make_error(message=f"expected a named_item", pos=self.mark())

    @parsing_rule
    def alternative(self):
        pos = self.mark()
        cut = False
        try:
            v0 = self._repeat(1, lambda: self.named_item())
            node = self._wrap_node(
                'alternative',
                [v0],
                [ItemAttributes(name=None, ignore=False)]
            )
            return node
        except ParseError as e:
            self.rewind(pos)
            if cut is True:
                raise CutError(e.message, e.location)

        raise self.make_error(message=f"expected a alternative", pos=self.mark())

    @left_recursive_parsing_rule
    def alternatives(self):
        pos = self.mark()
        cut = False
        try:
            v0 = self.alternatives()
            v1 = self.__()
            v2 = self.expect_string('|')
            v3 = cut = True
            v4 = self.alternative()
            node = self._wrap_node(
                'alternatives',
                [v0, v1, v2, v3, v4],
                [ItemAttributes(name='alts', ignore=False), ItemAttributes(name=None, ignore=False),
                 ItemAttributes(name=None, ignore=False), ItemAttributes(name=None, ignore=True),
                 ItemAttributes(name='alt', ignore=False)]
            )
            return node
        except ParseError as e:
            self.rewind(pos)
            if cut is True:
                raise CutError(e.message, e.location)

        cut = False
        try:
            v0 = self.alternative()
            node = self._wrap_node(
                'alternatives',
                [v0],
                [ItemAttributes(name='alt', ignore=False)]
            )
            return node
        except ParseError as e:
            self.rewind(pos)
            if cut is True:
                raise CutError(e.message, e.location)

        raise self.make_error(message=f"expected a alternatives", pos=self.mark())

    @parsing_rule
    def rule(self):
        pos = self.mark()
        cut = False
        try:
            v0 = self.rule_name()
            v1 = self.expect_string(':')
            v2 = cut = True
            v3 = self.alternatives()
            v4 = self._repeat(1, lambda: self.expect_string('\n'))
            node = self._wrap_node(
                'rule',
                [v0, v1, v2, v3, v4],
                [ItemAttributes(name='name', ignore=False), ItemAttributes(name=None, ignore=False),
                 ItemAttributes(name=None, ignore=True), ItemAttributes(name='alts', ignore=False),
                 ItemAttributes(name=None, ignore=False)]
            )
            return node
        except ParseError as e:
            self.rewind(pos)
            if cut is True:
                raise CutError(e.message, e.location)

        raise self.make_error(message=f"expected a rule", pos=self.mark())

    @parsing_rule
    def grammar(self):
        pos = self.mark()
        cut = False
        try:
            v0 = self._repeat(0, lambda: self.verbatim_block())
            v1 = self._repeat(0, lambda: self.setting())
            v2 = self._repeat(1, lambda: self.rule())
            v3 = cut = True
            v4 = self.expect_eof()
            node = self._wrap_node(
                'grammar',
                [v0, v1, v2, v3, v4],
                [ItemAttributes(name='verbatim', ignore=False), ItemAttributes(name='settings', ignore=False),
                 ItemAttributes(name='rules', ignore=False), ItemAttributes(name=None, ignore=True),
                 ItemAttributes(name=None, ignore=True)]
            )
            return node
        except ParseError as e:
            self.rewind(pos)
            if cut is True:
                raise CutError(e.message, e.location)

        raise self.make_error(message=f"expected a grammar", pos=self.mark())
