from abc import abstractmethod, ABCMeta
from textwrap import dedent
from typing import List

from .grammar_parser import GrammarParser


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

    def setting(self, node):
        return node["setting"]

    def grammar(self, node):
        verbatim = node["verbatim"]
        settings = {setting: True for setting in node["settings"]}
        rules = self.synthesized_rules + node["rules"]
        return Grammar(verbatim, rules, **settings)


class AbstractItem(metaclass=ABCMeta):
    def __init__(self, target, name=None):
        self.target = target
        self.name = name

    @abstractmethod
    def generate_condition(self) -> str:
        pass

    @staticmethod
    def is_nested() -> bool:
        return False

    def is_named(self) -> bool:
        return self.name is not None

    def __repr__(self):
        return f"{type(self).__name__}(target={self.target!r}, name={self.name!r})"


class RegexItem(AbstractItem):
    def generate_condition(self) -> str:
        v = self.target.replace("'", "\\'")
        return f"self.expect_regex(r'{v}')"


class LiteralItem(AbstractItem):
    def generate_condition(self) -> str:
        v = self.target.replace("'", "\\'")
        return f"self.expect_string('{v}')"


class RuleItem(AbstractItem):
    def generate_condition(self) -> str:
        return f"self.{self.target}()"


class Maybe(AbstractItem):
    def generate_condition(self) -> str:
        return f"self._maybe(lambda *args: {self.target.generate_condition()})"

    @staticmethod
    def is_nested() -> bool:
        return True


class ZeroOrMore(AbstractItem):
    def generate_condition(self) -> str:
        return f"self._repeat(0, lambda *args: {self.target.generate_condition()})"

    @staticmethod
    def is_nested() -> bool:
        return True


class OneOrMore(AbstractItem):
    def generate_condition(self) -> str:
        return f"self._repeat(1, lambda *args: {self.target.generate_condition()})"

    @staticmethod
    def is_nested() -> bool:
        return True


class Lookahead(AbstractItem):
    def generate_condition(self) -> str:
        return f"self._lookahead(lambda *args: {self.target.generate_condition()})"

    @staticmethod
    def is_nested() -> bool:
        return True


class NegativeLookahead(AbstractItem):
    def generate_condition(self) -> str:
        return f"self._not_lookahead(lambda *args: {self.target.generate_condition()})"

    @staticmethod
    def is_nested() -> bool:
        return True


class CutItem(AbstractItem):
    def __init__(self):
        super().__init__(None)

    def generate_condition(self) -> str:
        return f"cut = True"

    def is_named(self) -> bool:
        return False


class EOFItem(AbstractItem):
    def __init__(self):
        super().__init__(None)

    def generate_condition(self) -> str:
        return f"self.expect_eof()"

    def is_named(self) -> bool:
        return False


class Alternative:
    def __init__(self, items: List):
        self.items = items

    def __repr__(self):
        return f"Alternative(items={self.items!r})"


class Rule:
    def __init__(self, name: str, alternatives: List[Alternative]):
        self.name = name
        self.alternatives = alternatives

    def is_left_recursive(self) -> bool:
        for alt in self.alternatives:
            item = alt.items[0]
            while item.is_nested():
                item = item.target
            if isinstance(item, RuleItem) and item.target == self.name:
                return True
        return False

    def __repr__(self):
        return f"Rule(name={self.name!r}, alternatives={self.alternatives!r})"


class Grammar:
    def __init__(
            self,
            verbatim_prelude: List,
            rules: List[Rule],
    ):
        self.prelude = verbatim_prelude
        self.rules = rules

    def __repr__(self):
        return f"Grammar(prelude={self.prelude!r}, rules={self.rules!r})"

    @staticmethod
    def from_specification(text: str) -> 'Grammar':
        grammar_parser = GrammarParser(
            text,
            comments_regex=r"#[^\n]*",
            rule_handler=GrammarParserRuleHandler(),
        )
        return grammar_parser.grammar()
