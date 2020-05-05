from abc import abstractmethod, ABCMeta
from typing import List, Optional


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
        return f"({self.target.generate_condition()} or True)"

    @staticmethod
    def is_nested() -> bool:
        return True


class ZeroOrMore(AbstractItem):
    def generate_condition(self) -> str:
        return f"self.repeat(0, lambda *args: {self.target.generate_condition()})"

    @staticmethod
    def is_nested() -> bool:
        return True


class OneOrMore(AbstractItem):
    def generate_condition(self) -> str:
        return f"self.repeat(1, lambda *args: {self.target.generate_condition()})"

    @staticmethod
    def is_nested() -> bool:
        return True


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
            rule_handler: Optional[str],
    ):
        self.prelude = verbatim_prelude
        self.rules = rules
        self.rule_handler = rule_handler

    def __repr__(self):
        return f"Grammar(verbatim_imports={self.prelude!r}, rules={self.rules!r}, rule_handler={self.rule_handler!r})"
