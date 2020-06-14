from pegomancy.parse import CutError, ParseError, RawTextParser, parsing_rule, left_recursive_parsing_rule


class GrammarParser(RawTextParser):
    def _wrap_node(self, rule_name, values):
        if isinstance(values, list) and len(values) == 1:
            values = values[0]
        if self.rule_handler is not None and hasattr(self.rule_handler, rule_name):
            values = getattr(self.rule_handler, rule_name)(values)
        return values

    def _repeat(self, minimum, f, *args):
        pos = self.mark()
        matches = []
        while True:
            last = self.mark()
            try:
                matches.append(f(*args))
            except ParseError:
                self.rewind(last)
                break
        if len(matches) >= minimum:
            return matches
        self.rewind(pos)
        raise self.make_error(message=f"expected at least {minimum} repetitions of a {f.__name__}", pos=self.mark())

    def _lookahead(self, f, *args):
        pos = self.mark()
        result = f(*args)
        self.rewind(pos)
        return result

    def _not_lookahead(self, f, *args):
        try:
            self._lookahead(f, *args)
            raise self.make_error(message=f"unexpected {f.__name__}", pos=self.mark())
        except ParseError:
            pass

    def _maybe(self, f, *args):
        pos = self.mark()
        try:
            return f(*args)
        except ParseError:
            self.rewind(pos)
            return None

    @parsing_rule
    def synthesized_rule_0(self):
        pos = self.mark()
        cut = False
        try:
            name = self.expect_regex(r'[a-zA-Z_][a-zA-Z0-9_]*')
            self.expect_string(':')
            node = self._wrap_node('synthesized_rule_0', {'name': name})
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
            v0 = self._maybe(lambda *args: self.expect_regex(r'[ \n\t]+'))
            node = self._wrap_node('__', [v0])
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
            self.expect_string('@verbatim')
            self.expect_string('%{')
            block = self.expect_regex(r'^(.*?)(?=%})')
            self.expect_string('%}')
            self._repeat(1, lambda *args: self.expect_string('\n'))
            node = self._wrap_node('verbatim_block', {'block': block})
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
            self.expect_string('@set')
            self.expect_regex(r'[ \t]+')
            setting = self.expect_regex(r'[a-zA-Z_][a-zA-Z0-9_]*')
            self._repeat(1, lambda *args: self.expect_string('\n'))
            node = self._wrap_node('setting', {'setting': setting})
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
            node = self._wrap_node('rule_name', [v0])
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
            node = self._wrap_node('literal', [v0, v1, v2])
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
            node = self._wrap_node('literal', [v0, v1, v2])
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
            node = self._wrap_node('regex', [v0, v1])
            return node
        except ParseError as e:
            self.rewind(pos)
            if cut is True:
                raise CutError(e.message, e.location)

        raise self.make_error(message=f"expected a regex", pos=self.mark())

    @parsing_rule
    def cut(self):
        pos = self.mark()
        cut = False
        try:
            v0 = self.expect_string('~')
            node = self._wrap_node('cut', [v0])
            return node
        except ParseError as e:
            self.rewind(pos)
            if cut is True:
                raise CutError(e.message, e.location)

        raise self.make_error(message=f"expected a cut", pos=self.mark())

    @parsing_rule
    def atom(self):
        pos = self.mark()
        cut = False
        try:
            v0 = self.regex()
            node = self._wrap_node('atom', [v0])
            return node
        except ParseError as e:
            self.rewind(pos)
            if cut is True:
                raise CutError(e.message, e.location)

        cut = False
        try:
            v0 = self.literal()
            node = self._wrap_node('atom', [v0])
            return node
        except ParseError as e:
            self.rewind(pos)
            if cut is True:
                raise CutError(e.message, e.location)

        cut = False
        try:
            rule_name = self.rule_name()
            node = self._wrap_node('atom', {'rule_name': rule_name})
            return node
        except ParseError as e:
            self.rewind(pos)
            if cut is True:
                raise CutError(e.message, e.location)

        cut = False
        try:
            self.expect_string('(')
            parenthesized_alts = self.alternatives()
            self.expect_string(')')
            node = self._wrap_node('atom', {'parenthesized_alts': parenthesized_alts})
            return node
        except ParseError as e:
            self.rewind(pos)
            if cut is True:
                raise CutError(e.message, e.location)

        cut = False
        try:
            v0 = self.cut()
            node = self._wrap_node('atom', [v0])
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
            atom = self.atom()
            self.expect_string('?')
            node = self._wrap_node('maybe', {'atom': atom})
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
            atom = self.atom()
            self.expect_string('+')
            node = self._wrap_node('one_or_more', {'atom': atom})
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
            atom = self.atom()
            self.expect_string('*')
            node = self._wrap_node('zero_or_more', {'atom': atom})
            return node
        except ParseError as e:
            self.rewind(pos)
            if cut is True:
                raise CutError(e.message, e.location)

        raise self.make_error(message=f"expected a zero_or_more", pos=self.mark())

    @parsing_rule
    def lookahead(self):
        pos = self.mark()
        cut = False
        try:
            self.expect_string('&')
            item = self.item()
            node = self._wrap_node('lookahead', {'item': item})
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
            self.expect_string('!')
            item = self.item()
            node = self._wrap_node('negative_lookahead', {'item': item})
            return node
        except ParseError as e:
            self.rewind(pos)
            if cut is True:
                raise CutError(e.message, e.location)

        raise self.make_error(message=f"expected a negative_lookahead", pos=self.mark())

    @parsing_rule
    def item(self):
        pos = self.mark()
        cut = False
        try:
            v0 = self.maybe()
            node = self._wrap_node('item', [v0])
            return node
        except ParseError as e:
            self.rewind(pos)
            if cut is True:
                raise CutError(e.message, e.location)

        cut = False
        try:
            v0 = self.one_or_more()
            node = self._wrap_node('item', [v0])
            return node
        except ParseError as e:
            self.rewind(pos)
            if cut is True:
                raise CutError(e.message, e.location)

        cut = False
        try:
            v0 = self.zero_or_more()
            node = self._wrap_node('item', [v0])
            return node
        except ParseError as e:
            self.rewind(pos)
            if cut is True:
                raise CutError(e.message, e.location)

        cut = False
        try:
            v0 = self.lookahead()
            node = self._wrap_node('item', [v0])
            return node
        except ParseError as e:
            self.rewind(pos)
            if cut is True:
                raise CutError(e.message, e.location)

        cut = False
        try:
            v0 = self.negative_lookahead()
            node = self._wrap_node('item', [v0])
            return node
        except ParseError as e:
            self.rewind(pos)
            if cut is True:
                raise CutError(e.message, e.location)

        cut = False
        try:
            v0 = self.atom()
            node = self._wrap_node('item', [v0])
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
            name = self._maybe(lambda *args: self.synthesized_rule_0())
            item = self.item()
            node = self._wrap_node('named_item', {'name': name, 'item': item})
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
            v0 = self._repeat(1, lambda *args: self.named_item())
            node = self._wrap_node('alternative', [v0])
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
            alts = self.alternatives()
            self.__()
            self.expect_string('|')
            alt = self.alternative()
            node = self._wrap_node('alternatives', {'alts': alts, 'alt': alt})
            return node
        except ParseError as e:
            self.rewind(pos)
            if cut is True:
                raise CutError(e.message, e.location)

        cut = False
        try:
            alt = self.alternative()
            node = self._wrap_node('alternatives', {'alt': alt})
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
            name = self.rule_name()
            self.expect_string(':')
            alts = self.alternatives()
            self._repeat(1, lambda *args: self.expect_string('\n'))
            node = self._wrap_node('rule', {'name': name, 'alts': alts})
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
            verbatim = self._repeat(0, lambda *args: self.verbatim_block())
            settings = self._repeat(0, lambda *args: self.setting())
            rules = self._repeat(1, lambda *args: self.rule())
            node = self._wrap_node('grammar', {'verbatim': verbatim, 'settings': settings, 'rules': rules})
            return node
        except ParseError as e:
            self.rewind(pos)
            if cut is True:
                raise CutError(e.message, e.location)

        raise self.make_error(message=f"expected a grammar", pos=self.mark())
