import string
from textwrap import dedent
from typing import List, Optional

from .parse import RawTextParser
from .grammar \
    import AbstractItem, RegexItem, LiteralItem, RuleItem, ZeroOrMore, OneOrMore, Maybe, \
    Rule, Alternative, Grammar


class GrammarParser(RawTextParser):
    """
    Bootstrapping parser that parses grammars.
    """
    IDENTIFIER_CHARS = string.ascii_letters + "_"

    def __init__(self, data):
        super().__init__(data)
        self.synthesized_rules = []

    def _synthesize_rule(self, alts):
        rule = Rule(f"synthesized_rule_{len(self.synthesized_rules)}", alts)
        self.synthesized_rules.append(rule)
        return rule.name

    def eat_whitespace(self, at_least=0, whitespace=" \t"):
        return len(self.expect_regex(rf"[{whitespace}]*")) >= at_least

    def identifier(self) -> Optional[str]:
        return self.expect_regex(r"[a-zA-Z0-9_]+")

    def string(self) -> Optional[str]:
        pos = self.mark()
        opening_quote = self.expect_string('"') or self.expect_string("'")
        s = self.read_while(lambda c: c != opening_quote)
        if not self.eof() and self.expect_string(opening_quote):
            return s
        self.rewind(pos)
        return None

    def regex(self) -> Optional[str]:
        pos = self.mark()
        if self.expect_string("r") and (s := self.string()):
            return s
        self.rewind(pos)
        return None

    def atom(self) -> Optional[AbstractItem]:
        if r := self.regex():
            return RegexItem(r)
        if s := self.string():
            return LiteralItem(s)
        if identifier := self.identifier():
            return RuleItem(identifier)
        if self.expect_string("(") and \
                (alts := self.alternatives()) and \
                self.expect_string(")"):
            rule_name = self._synthesize_rule(alts)
            return RuleItem(rule_name)
        return None

    def peg_construct(self):
        pos = self.mark()
        if atom := self.atom():
            if self.expect_string("?"):
                return Maybe(atom)
            if self.expect_string("*"):
                return ZeroOrMore(atom)
            if self.expect_string("+"):
                return OneOrMore(atom)
            return atom
        self.rewind(pos)
        return None

    def unnamed_item(self):
        return self.peg_construct()

    def named_item(self):
        pos = self.mark()
        if (name := self.expect_regex(r"[a-zA-Z_][a-zA-Z0-9_]*")) and self.expect_string(":"):
            if item := self.unnamed_item():
                item.name = name
                return item
        self.rewind(pos)
        return None

    def item(self) -> Optional:
        pos = self.mark()
        if named_item := self.named_item():
            return named_item
        self.rewind(pos)
        if unnamed_item := self.unnamed_item():
            return unnamed_item
        self.rewind(pos)
        return None

    def verbatim_text(self) -> Optional[str]:
        return self.expect_enclosed(opening="{", closing="}")

    def alternative(self) -> Optional[Alternative]:
        items = []
        while item := self.item():
            items.append(item)
            self.eat_whitespace()
        if not items:
            return None
        self.eat_whitespace()
        return Alternative(items) if items else None

    def alternatives(self) -> Optional[List[Alternative]]:
        pos = self.mark()
        if alt := self.alternative():
            alts = [alt]
            altpos = self.mark()
            while (self.expect_string("\n") or True) and \
                    self.eat_whitespace() and self.expect_string("|") and self.eat_whitespace() and \
                    (alt := self.alternative()):
                alts.append(alt)
                altpos = self.mark()
            self.rewind(altpos)
            return alts
        self.rewind(pos)
        return None

    def rule(self) -> Optional[Rule]:
        pos = self.mark()
        if rule_name := self.identifier():
            if self.expect_string(":"):
                self.eat_whitespace()
                if (alts := self.alternatives()) and self.expect_string("\n"):
                    return Rule(rule_name, alts)
        self.rewind(pos)
        return None

    def rules(self) -> Optional[List[Rule]]:
        pos = self.mark()
        if rule := self.rule():
            rules = [rule]
            while rule := self.rule():
                rules.append(rule)
            if self.eof():
                return rules
        self.rewind(pos)
        return None

    def verbatim_block(self) -> Optional[str]:
        pos = self.mark()
        if (verbatim := self.verbatim_text()) and self.expect_string("\n"):
            return verbatim.strip(" ")
        self.rewind(pos)
        return None

    def directive(self):
        pos = self.mark()
        if self.expect_string("@verbatim"):
            if self.eat_whitespace(at_least=1) and (verbatim_block := self.verbatim_block()):
                return "@verbatim", dedent(verbatim_block)
        elif self.expect_string("@rule_handler"):
            if self.eat_whitespace(at_least=1) and \
                    (handler := self.expect_regex(r"[a-zA-Z_][a-zA-Z0-9_]*")) and \
                    self.eat_whitespace(at_least=1, whitespace="\n"):
                return "@rule_handler", handler
        self.rewind(pos)
        return None

    def prelude(self):
        directives = []
        while directive := self.directive():
            directives.append(directive)
        return directives

    def grammar(self) -> Optional[Grammar]:
        pos = self.mark()
        if (prelude := self.prelude()) is not None and (rules := self.rules()):
            verbatim_directives = [directive[1] for directive in prelude if directive[0] == "@verbatim"]
            rule_handlers = [directive[1] for directive in prelude if directive[0] == "@rule_handler"] + [None]
            return Grammar(verbatim_directives, rules + self.synthesized_rules, rule_handlers[0])
        self.rewind(pos)
        return None
