from typing import List

from modules.Crowding.crowding import Crowding
from modules.GCSBase.domain.Rule import Rule
from modules.GCSBase.grammar.grammar import Grammar


class DummyCrowding(Crowding):

    def __init__(self, settings=None):
        super().__init__(settings)

    def add_rule(self, grammar: Grammar, rule: Rule) -> bool:
        grammar.add_rule(rule)
        return True

    def add_rules(self, grammar: Grammar, new_rules: List[Rule]) -> None:
        for rule in new_rules:
            grammar.add_rule(rule)


