from .grammar import AbstractItem, Alternative, Grammar, Rule, RuleItem, CutItem, EOFItem


class ParserGenerator:
    def _generate_wrap_node(self):
        print("    def _wrap_node(self, rule_name, values):")
        print("        if isinstance(values, list) and len(values) == 1:")
        print("            values = values[0]")
        print("        if self.rule_handler is not None and hasattr(self.rule_handler, rule_name):")
        print("            values = getattr(self.rule_handler, rule_name)(values)")
        print("        return values")

    def _generate_named_alternative(self, alt: Alternative, rule: Rule):
        items = []
        for item in alt.items:
            assert isinstance(item, AbstractItem)
            cond = item.generate_condition()
            if not item.is_named() or isinstance(item, (CutItem, EOFItem)):
                print(f"            {cond}")
            else:
                items.append(item.name)
                print(f"            {item.name} = {cond}")
        kwargs_items = [f"'{name}': {name}" for name in items]
        print(f"            node = self._wrap_node({rule.name!r}, {{{', '.join(kwargs_items)}}})")
        print(f"            return node")

    def _generate_unnamed_alternative(self, alt: Alternative, rule: Rule):
        items = []
        for item in alt.items:
            assert isinstance(item, AbstractItem)
            cond = item.generate_condition()
            if isinstance(item, (CutItem, EOFItem)) or (isinstance(item, RuleItem) and item.target.startswith("_")):
                print(f"            {cond}")
            else:
                var_name = f"v{len(items)}"
                items.append(var_name)
                print(f"            {var_name} = {cond}")
        print(f"            node = self._wrap_node({rule.name!r}, [{', '.join(items)}])")
        print(f"            return node")

    def _generate_alternative(self, alt: Alternative, rule: Rule):
        print(f"        cut = False")
        print(f"        try:")
        any_named = any(map(lambda i: i.is_named(), alt.items))
        if any_named:
            self._generate_named_alternative(alt, rule)
        else:
            self._generate_unnamed_alternative(alt, rule)
        print(f"        except ParseError as e:")
        print(f"            self.rewind(pos)")
        print(f"            if cut is True:")
        print(f"                raise CutError(e.message, e.location)")
        print()

    def _generate_rule(self, rule: Rule):
        if rule.is_left_recursive():
            print(f"    @left_recursive_parsing_rule")
        else:
            print(f"    @parsing_rule")
        print(f"    def {rule.name}(self):")
        print(f"        pos = self.mark()")
        for alt in rule.alternatives:
            self._generate_alternative(alt, rule)
        print(f"        raise self.make_error(message=f\"expected a {rule.name}\", pos=self.mark())")
        print()

    def _generate_repeat_method(self):
        print("    def _repeat(self, minimum, f, *args):")
        print("        pos = self.mark()")
        print("        matches = []")
        print("        while True:")
        print("            last = self.mark()")
        print("            try:")
        print("                matches.append(f(*args))")
        print("            except ParseError:")
        print("                self.rewind(last)")
        print("                break")
        print("        if len(matches) >= minimum:")
        print("            return matches")
        print("        self.rewind(pos)")
        print("        raise self.make_error(message=f\"expected at least {minimum} repetitions of a {f.__name__}\", pos=self.mark())")
        print()

    def _generate_lookahead_method(self):
        print("    def _lookahead(self, f, *args):")
        print("        pos = self.mark()")
        print("        result = f(*args)")
        print("        self.rewind(pos)")
        print("        return result")
        print()
        print("    def _not_lookahead(self, f, *args):")
        print("        try:")
        print("            self._lookahead(f, *args)")
        print("            raise self.make_error(message=f\"unexpected {f.__name__}\", pos=self.mark())")
        print("        except ParseError:")
        print("            pass")
        print()

    def _generate_maybe_method(self):
        print("    def _maybe(self, f, *args):")
        print("        pos = self.mark()")
        print("        try:")
        print("            return f(*args)")
        print("        except ParseError:")
        print("            self.rewind(pos)")
        print("            return None")
        print()

    def generate_parser(self, grammar: Grammar, class_name: str = None):
        class_name = class_name or "Parser"
        print(f"from pegomancy.parse import CutError, ParseError, RawTextParser, parsing_rule, left_recursive_parsing_rule")
        for verbatim in grammar.prelude:
            print(verbatim)
        print("\n")
        print(f"class {class_name}(RawTextParser):")
        self._generate_wrap_node()
        self._generate_repeat_method()
        self._generate_lookahead_method()
        self._generate_maybe_method()
        rules = grammar.rules
        for rule in rules:
            self._generate_rule(rule)
