import sys
from textwrap import dedent
from typing import TextIO

from .grammar import AbstractItem, Alternative, Grammar, Rule


class ParserGenerator:
    def _generate_alternative_(self, alt: Alternative, rule: Rule, fprint):
        var_names = []
        attributes = []
        for item in alt.items:
            assert isinstance(item, AbstractItem), "expected alternative item to be an AbstractItem"
            cond = item.generate_condition()
            var_name = f"v{len(var_names)}"
            var_names.append(var_name)
            attributes.append(item.attributes)
            fprint(f"            {var_name} = {cond}")
        fprint(f"            node = self._wrap_node(")
        fprint(f"                {rule.name!r},")
        fprint(f"                [{', '.join(var_names)}],")
        fprint(f"                {attributes!r}")
        fprint(f"            )")
        fprint(f"            return node")

    def _generate_alternative(self, alt: Alternative, rule: Rule, fprint):
        fprint(f"        cut = False")
        fprint(f"        try:")
        self._generate_alternative_(alt, rule, fprint)
        fprint(f"        except ParseError as e:")
        fprint(f"            self.rewind(pos)")
        fprint(f"            if cut is True:")
        fprint(f"                raise CutError(e.message, e.location)")
        fprint()

    def _generate_rule(self, rule: Rule, fprint):
        if rule.is_left_recursive():
            fprint(f"    @left_recursive_parsing_rule")
        else:
            fprint(f"    @parsing_rule")
        fprint(f"    def {rule.name}(self):")
        fprint(f"        pos = self.mark()")
        for alt in rule.alternatives:
            self._generate_alternative(alt, rule, fprint)
        fprint(f"        raise self.make_error(message=f\"expected a {rule.name}\", pos=self.mark())")
        fprint()

    def generate_parser(self, grammar: Grammar, class_name: str = None, file: TextIO = None):
        class_name = class_name or "Parser"
        file = file or sys.stdout

        def fprint(*args, **kwargs):
            print(*args, **kwargs, file=file)

        fprint(dedent("""\
        from pegomancy.parse import \\
            CutError, \\
            ParseError, \\
            RawTextParser, \\
            parsing_rule, \\
            left_recursive_parsing_rule
        """))
        fprint("from pegomancy.grammar_items import ItemAttributes")
        for verbatim in grammar.prelude:
            fprint(verbatim)
        fprint("\n")
        fprint(f"class {class_name}(RawTextParser):")
        rules = grammar.rules
        for rule in rules:
            self._generate_rule(rule, fprint)
