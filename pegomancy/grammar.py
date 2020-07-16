from dataclasses import dataclass, field
from textwrap import dedent
from typing import List

from .grammar_parser import GrammarParser
from .grammar_items import ItemAttributes, AbstractItem


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

    def cut(self, _):
        return CutItem()

    def eof_(self, _):
        return EOFItem()

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
        if name is not None:
            item.attributes.name = name["name"]
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

    def setting(self, node):
        return node["setting"]

    def grammar(self, node):
        verbatim = node["verbatim"]
        settings = {setting: True for setting in node["settings"]}
        rules = self.synthesized_rules + node["rules"]
        return Grammar(verbatim, rules, **settings)


@dataclass
class RegexItem(AbstractItem):
    target: str
    attributes: ItemAttributes = field(default_factory=ItemAttributes)

    def generate_condition(self) -> str:
        v = self.target.replace("'", "\\'")
        return f"self.expect_regex(r'{v}')"


@dataclass
class LiteralItem(AbstractItem):
    target: str
    attributes: ItemAttributes = field(default_factory=ItemAttributes)

    def generate_condition(self) -> str:
        v = self.target.replace("'", "\\'")
        return f"self.expect_string('{v}')"


@dataclass
class RuleItem(AbstractItem):
    rule_name: str
    attributes: ItemAttributes = field(default_factory=ItemAttributes)

    def generate_condition(self) -> str:
        return f"self.{self.rule_name}()"


@dataclass
class Maybe(AbstractItem):
    inner_item: AbstractItem
    attributes: ItemAttributes = field(default_factory=ItemAttributes)

    def generate_condition(self) -> str:
        return f"self._maybe(lambda *args: {self.inner_item.generate_condition()})"

    @staticmethod
    def is_nested() -> bool:
        return True


@dataclass
class ZeroOrMore(AbstractItem):
    inner_item: AbstractItem
    attributes: ItemAttributes = field(default_factory=ItemAttributes)

    def generate_condition(self) -> str:
        return f"self._repeat(0, lambda *args: {self.inner_item.generate_condition()})"

    @staticmethod
    def is_nested() -> bool:
        return True


@dataclass
class OneOrMore(AbstractItem):
    inner_item: AbstractItem
    attributes: ItemAttributes = field(default_factory=ItemAttributes)

    def generate_condition(self) -> str:
        return f"self._repeat(1, lambda *args: {self.inner_item.generate_condition()})"

    @staticmethod
    def is_nested() -> bool:
        return True


@dataclass
class Lookahead(AbstractItem):
    inner_item: AbstractItem
    attributes: ItemAttributes = field(default_factory=ItemAttributes)

    def generate_condition(self) -> str:
        return f"self._lookahead(lambda *args: {self.inner_item.generate_condition()})"

    @staticmethod
    def is_nested() -> bool:
        return True


@dataclass
class NegativeLookahead(AbstractItem):
    inner_item: AbstractItem
    attributes: ItemAttributes = field(default_factory=ItemAttributes)

    def generate_condition(self) -> str:
        return f"self._not_lookahead(lambda *args: {self.inner_item.generate_condition()})"

    @staticmethod
    def is_nested() -> bool:
        return True


@dataclass
class CutItem(AbstractItem):
    attributes: ItemAttributes = field(default_factory=lambda: ItemAttributes(ignore=True))

    def generate_condition(self) -> str:
        return f"cut = True"


@dataclass
class EOFItem(AbstractItem):
    attributes: ItemAttributes = field(default_factory=lambda: ItemAttributes(ignore=True))

    def generate_condition(self) -> str:
        return f"self.expect_eof()"


@dataclass
class Alternative:
    items: List


@dataclass
class Rule:
    name: str
    alternatives: List[Alternative]

    def is_left_recursive(self) -> bool:
        for alt in self.alternatives:
            item = alt.items[0]
            while item.is_nested():
                item = item.inner_item
            if isinstance(item, RuleItem) and item.rule_name == self.name:
                return True
        return False


@dataclass
class Grammar:
    prelude: List
    rules: List[Rule]

    @staticmethod
    def from_specification(text: str) -> 'Grammar':
        grammar_parser = GrammarParser(
            text,
            comments_regex=r"#[^\n]*",
            rule_handler=GrammarParserRuleHandler(),
        )
        return grammar_parser.grammar()
