from pegomancy.parse import RawTextParser, parsing_rule, left_recursive_parsing_rule

from pegomancy.grammar import \
    Grammar, Rule, Alternative, RuleItem, RegexItem, LiteralItem, Maybe, \
    OneOrMore, ZeroOrMore, Lookahead, NegativeLookahead
from textwrap import dedent


class GrammarParserRuleHandler:
    def __init__(self):
        self.synthesized_rules = []

    def _synthesize_rule(self, alts):
        rule = Rule(f"synthesized_rule_{len(self.synthesized_rules)}", alts)
        self.synthesized_rules.append(rule)
        return rule.name

    def rule_name(self, node):
        return node

    def literal(self, node):
        return LiteralItem(node[1])

    def regex(self, node):
        return RegexItem(node[1].target)

    def lookahead(self, node):
        return Lookahead(node["item"])

    def negative_lookahead(self, node):
        return NegativeLookahead(node["item"])

    def atom(self, node):
        if isinstance(node, dict):
            if "parenthesized_alts" in node:
                node["rule_name"] = self._synthesize_rule(node["parenthesized_alts"])
            return RuleItem(node["rule_name"])
        return node

    def maybe(self, node):
        return Maybe(node["atom"])

    def one_or_more(self, node):
        return OneOrMore(node["atom"])

    def zero_or_more(self, node):
        return ZeroOrMore(node["atom"])

    def named_item(self, node):
        item = node["item"]
        name = node.get("name")
        if name is not True:
            item.name = name["name"]
        return item

    def alternative(self, node):
        return Alternative(node)

    def alternatives(self, node):
        alts = node.get("alts") or []
        return alts + [node.get("alt")]

    def rule(self, node):
        alts = node["alts"]
        return Rule(node["name"], alts)

    def verbatim_block(self, node):
        return dedent(node["block"])

    def rule_handler(self, node):
        return node["handler"]

    def setting(self, node):
        return node["setting"]

    def grammar(self, node):
        verbatim = node["verbatim"]
        rule_handler = node["handler"] if node["handler"] is not True else None
        settings = {setting: True for setting in node["settings"]}
        rules = self.synthesized_rules + node["rules"]
        return Grammar(verbatim, rules, rule_handler, **settings)


class GrammarParser(RawTextParser):
    def __init__(self, data):
        super().__init__(data)
        self._rule_handler = GrammarParserRuleHandler()

    def _wrap_node(self, rule_name, values):
        if isinstance(values, list) and len(values) == 1:
            values = values[0]
        if self._rule_handler is not None and hasattr(self._rule_handler, rule_name):
            values = getattr(self._rule_handler, rule_name)(values)
        return values

    def _repeat(self, minimum, f, *args):
        pos = self.mark()
        matches = []
        while (match := f(*args)) is not None:
            matches.append(match)
        if len(matches) >= minimum:
            return matches
        self.rewind(pos)
        return None

    def _lookahead(self, f, *args):
        pos = self.mark()
        result = f(*args)
        self.rewind(pos)
        return result

    @parsing_rule
    def synthesized_rule_0(self):
        pos = self.mark()
        if (True
                and (name := self.expect_regex(r'[a-zA-Z_][a-zA-Z0-9_]*')) is not None
                and self.expect_string(':') is not None
        ):
            return self._wrap_node('synthesized_rule_0', {'name': name})
        self.rewind(pos)
        return None

    @parsing_rule
    def _(self):
        pos = self.mark()
        if (True
                and (v0 := (self.expect_regex(r'[ \t]+') or True)) is not None
        ):
            return self._wrap_node('_', [v0])
        self.rewind(pos)
        return None

    @parsing_rule
    def __(self):
        pos = self.mark()
        if (True
                and (v0 := (self.expect_regex(r'[ \n\t]+') or True)) is not None
        ):
            return self._wrap_node('__', [v0])
        self.rewind(pos)
        return None

    @parsing_rule
    def verbatim_block(self):
        pos = self.mark()
        if (True
                and self.expect_string('@verbatim') is not None
                and self._() is not None
                and self.expect_string('%{') is not None
                and (block := self.expect_regex(r'^(.*?)(?=%})')) is not None
                and self.expect_string('%}') is not None
                and self.expect_string('\n') is not None
        ):
            return self._wrap_node('verbatim_block', {'block': block})
        self.rewind(pos)
        return None

    @parsing_rule
    def rule_handler(self):
        pos = self.mark()
        if (True
                and self.expect_string('@rule_handler') is not None
                and self.expect_regex(r'[ \t]+') is not None
                and (handler := self.expect_regex(r'[a-zA-Z_][a-zA-Z0-9_]*')) is not None
                and self.expect_string('\n') is not None
        ):
            return self._wrap_node('rule_handler', {'handler': handler})
        self.rewind(pos)
        return None

    @parsing_rule
    def setting(self):
        pos = self.mark()
        if (True
                and self.expect_string('@set') is not None
                and self.expect_regex(r'[ \t]+') is not None
                and (setting := self.expect_regex(r'[a-zA-Z_][a-zA-Z0-9_]*')) is not None
                and self.expect_string('\n') is not None
        ):
            return self._wrap_node('setting', {'setting': setting})
        self.rewind(pos)
        return None

    @parsing_rule
    def rule_name(self):
        pos = self.mark()
        if (True
                and (v0 := self.expect_regex(r'[a-zA-Z_][a-zA-Z0-9_]*')) is not None
        ):
            return self._wrap_node('rule_name', [v0])
        self.rewind(pos)
        return None

    @parsing_rule
    def literal(self):
        pos = self.mark()
        if (True
                and (v0 := self.expect_string('"')) is not None
                and (v1 := self.expect_regex(r'[^"]*')) is not None
                and (v2 := self.expect_string('"')) is not None
        ):
            return self._wrap_node('literal', [v0, v1, v2])
        self.rewind(pos)
        if (True
                and (v0 := self.expect_string('\'')) is not None
                and (v1 := self.expect_regex(r'[^\']*')) is not None
                and (v2 := self.expect_string('\'')) is not None
        ):
            return self._wrap_node('literal', [v0, v1, v2])
        self.rewind(pos)
        return None

    @parsing_rule
    def regex(self):
        pos = self.mark()
        if (True
                and (v0 := self.expect_string('r')) is not None
                and (v1 := self.literal()) is not None
        ):
            return self._wrap_node('regex', [v0, v1])
        self.rewind(pos)
        return None

    @parsing_rule
    def atom(self):
        pos = self.mark()
        if (True
                and (v0 := self.regex()) is not None
        ):
            return self._wrap_node('atom', [v0])
        self.rewind(pos)
        if (True
                and (v0 := self.literal()) is not None
        ):
            return self._wrap_node('atom', [v0])
        self.rewind(pos)
        if (True
                and (rule_name := self.rule_name()) is not None
        ):
            return self._wrap_node('atom', {'rule_name': rule_name})
        self.rewind(pos)
        if (True
                and self.expect_string('(') is not None
                and self._() is not None
                and (parenthesized_alts := self.alternatives()) is not None
                and self._() is not None
                and self.expect_string(')') is not None
        ):
            return self._wrap_node('atom', {'parenthesized_alts': parenthesized_alts})
        self.rewind(pos)
        return None

    @parsing_rule
    def maybe(self):
        pos = self.mark()
        if (True
                and (atom := self.atom()) is not None
                and self.expect_string('?') is not None
        ):
            return self._wrap_node('maybe', {'atom': atom})
        self.rewind(pos)
        return None

    @parsing_rule
    def one_or_more(self):
        pos = self.mark()
        if (True
                and (atom := self.atom()) is not None
                and self.expect_string('+') is not None
        ):
            return self._wrap_node('one_or_more', {'atom': atom})
        self.rewind(pos)
        return None

    @parsing_rule
    def zero_or_more(self):
        pos = self.mark()
        if (True
                and (atom := self.atom()) is not None
                and self.expect_string('*') is not None
        ):
            return self._wrap_node('zero_or_more', {'atom': atom})
        self.rewind(pos)
        return None

    @parsing_rule
    def lookahead(self):
        pos = self.mark()
        if (True
                and self.expect_string('&') is not None
                and (item := self.item()) is not None
        ):
            return self._wrap_node('lookahead', {'item': item})
        self.rewind(pos)
        return None

    @parsing_rule
    def negative_lookahead(self):
        pos = self.mark()
        if (True
                and self.expect_string('!') is not None
                and (item := self.item()) is not None
        ):
            return self._wrap_node('negative_lookahead', {'item': item})
        self.rewind(pos)
        return None

    @parsing_rule
    def item(self):
        pos = self.mark()
        if (True
                and (v0 := self.maybe()) is not None
        ):
            return self._wrap_node('item', [v0])
        self.rewind(pos)
        if (True
                and (v0 := self.one_or_more()) is not None
        ):
            return self._wrap_node('item', [v0])
        self.rewind(pos)
        if (True
                and (v0 := self.zero_or_more()) is not None
        ):
            return self._wrap_node('item', [v0])
        self.rewind(pos)
        if (True
                and (v0 := self.lookahead()) is not None
        ):
            return self._wrap_node('item', [v0])
        self.rewind(pos)
        if (True
                and (v0 := self.negative_lookahead()) is not None
        ):
            return self._wrap_node('item', [v0])
        self.rewind(pos)
        if (True
                and (v0 := self.atom()) is not None
        ):
            return self._wrap_node('item', [v0])
        self.rewind(pos)
        return None

    @parsing_rule
    def named_item(self):
        pos = self.mark()
        if (True
                and (name := (self.synthesized_rule_0() or True)) is not None
                and (item := self.item()) is not None
        ):
            return self._wrap_node('named_item', {'name': name, 'item': item})
        self.rewind(pos)
        return None

    @parsing_rule
    def itemsp(self):
        pos = self.mark()
        if (True
                and (v0 := self.named_item()) is not None
                and self._() is not None
        ):
            return self._wrap_node('itemsp', [v0])
        self.rewind(pos)
        return None

    @parsing_rule
    def alternative(self):
        pos = self.mark()
        if (True
                and self._() is not None
                and (v0 := self._repeat(1, lambda *args: self.itemsp())) is not None
        ):
            return self._wrap_node('alternative', [v0])
        self.rewind(pos)
        return None

    @left_recursive_parsing_rule
    def alternatives(self):
        pos = self.mark()
        if (True
                and (alts := self.alternatives()) is not None
                and self.__() is not None
                and self.expect_string('|') is not None
                and self._() is not None
                and (alt := self.alternative()) is not None
        ):
            return self._wrap_node('alternatives', {'alts': alts, 'alt': alt})
        self.rewind(pos)
        if (True
                and self._() is not None
                and (alt := self.alternative()) is not None
        ):
            return self._wrap_node('alternatives', {'alt': alt})
        self.rewind(pos)
        return None

    @parsing_rule
    def rule(self):
        pos = self.mark()
        if (True
                and (name := self.rule_name()) is not None
                and self.expect_string(':') is not None
                and self._() is not None
                and (alts := self.alternatives()) is not None
                and self.expect_string('\n') is not None
        ):
            return self._wrap_node('rule', {'name': name, 'alts': alts})
        self.rewind(pos)
        return None

    @parsing_rule
    def grammar(self):
        pos = self.mark()
        if (True
                and (verbatim := self._repeat(0, lambda *args: self.verbatim_block())) is not None
                and (handler := (self.rule_handler() or True)) is not None
                and (settings := self._repeat(0, lambda *args: self.setting())) is not None
                and (rules := self._repeat(1, lambda *args: self.rule())) is not None
        ):
            return self._wrap_node(
                'grammar',
                {'verbatim': verbatim, 'handler': handler, 'settings': settings, 'rules': rules}
            )
        self.rewind(pos)
        return None
