from textwrap import dedent

from .grammar import AbstractItem, Alternative, Grammar, Rule


class ParserGenerator:
    def _generate_alternative_(self, alt: Alternative, rule: Rule):
        var_names = []
        attributes = []
        for item in alt.items:
            assert isinstance(item, AbstractItem), "expected alternative item to be an AbstractItem"
            cond = item.generate_condition()
            var_name = f"v{len(var_names)}"
            var_names.append(var_name)
            attributes.append(item.attributes)
            print(f"            {var_name} = {cond}")
        print(f"            node = self._wrap_node(")
        print(f"                {rule.name!r},")
        print(f"                [{', '.join(var_names)}],")
        print(f"                {attributes!r}")
        print(f"            )")
        print(f"            return node")

    def _generate_alternative(self, alt: Alternative, rule: Rule):
        print(f"        cut = False")
        print(f"        try:")
        self._generate_alternative_(alt, rule)
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

    def generate_parser(self, grammar: Grammar, class_name: str = None):
        class_name = class_name or "Parser"
        print(dedent("""\
        from pegomancy.parse import \\
            CutError, \\
            ParseError, \\
            RawTextParser, \\
            parsing_rule, \\
            left_recursive_parsing_rule
        """))
        print("from pegomancy.grammar_items import ItemAttributes")
        for verbatim in grammar.prelude:
            print(verbatim)
        print("\n")
        print(f"class {class_name}(RawTextParser):")
        rules = grammar.rules
        for rule in rules:
            self._generate_rule(rule)
