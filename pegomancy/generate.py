from .grammar import AbstractItem, Alternative, Grammar, Rule, RuleItem


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
            if not item.is_named():
                print(f"                and {cond} is not None")
            else:
                items.append(item.name)
                print(f"                and ({item.name} := {cond}) is not None")
        print(f"        ):")
        kwargs_items = [f"'{name}': {name}" for name in items]
        print(f"            return self._wrap_node({rule.name!r}, {{{', '.join(kwargs_items)}}})")

    def _generate_unnamed_alternative(self, alt: Alternative, rule: Rule):
        items = []
        for item in alt.items:
            assert isinstance(item, AbstractItem)
            cond = item.generate_condition()
            if isinstance(item, RuleItem) and item.target.startswith("_"):
                print(f"                and {cond} is not None")
            else:
                var_name = f"v{len(items)}"
                items.append(var_name)
                print(f"                and ({var_name} := {cond}) is not None")
        print(f"        ):")
        print(f"            return self._wrap_node({rule.name!r}, [{', '.join(items)}])")

    def _generate_alternative(self, alt: Alternative, rule: Rule):
        print(f"        if (True")
        any_named = any(map(lambda i: i.is_named(), alt.items))
        if any_named:
            self._generate_named_alternative(alt, rule)
        else:
            self._generate_unnamed_alternative(alt, rule)
        print(f"        self.rewind(pos)")

    def _generate_rule(self, rule: Rule):
        if rule.is_left_recursive():
            print(f"    @left_recursive_parsing_rule")
        else:
            print(f"    @parsing_rule")
        print(f"    def {rule.name}(self):")
        print(f"        pos = self.mark()")
        for alt in rule.alternatives:
            self._generate_alternative(alt, rule)

        print(f"        return None")
        print()

    def _generate_repeat_method(self):
        print("    def _repeat(self, minimum, f, *args):")
        print("        pos = self.mark()")
        print("        matches = []")
        print("        while (match := f(*args)) is not None:")
        print("            matches.append(match)")
        print("        if len(matches) >= minimum:")
        print("            return matches")
        print("        self.rewind(pos)")
        print("        return None")
        print()

    def _generate_lookahead_method(self):
        print("    def _lookahead(self, f, *args):")
        print("        pos = self.mark()")
        print("        result = f(*args)")
        print("        self.rewind(pos)")
        print("        return result")
        print()

    def generate_parser(self, grammar: Grammar, class_name: str = None):
        class_name = class_name or "Parser"
        print(f"from pegomancy.parse import RawTextParser, parsing_rule, left_recursive_parsing_rule")
        for verbatim in grammar.prelude:
            print(verbatim)
        print("\n")
        print(f"class {class_name}(RawTextParser):")
        self._generate_wrap_node()
        self._generate_repeat_method()
        self._generate_lookahead_method()
        rules = grammar.rules
        for rule in rules:
            self._generate_rule(rule)
