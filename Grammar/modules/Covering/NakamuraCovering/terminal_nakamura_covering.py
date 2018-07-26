from .nakamura_covering import NakamuraCovering
from ...Crowding.crowding import Crowding
from ...GCSBase.domain.Rule import Rule
from ...GCSBase.domain.symbol import Symbol
from ...GCSBase.grammar.grammar import Grammar


class TerminalNakamuraCovering(NakamuraCovering):

    def __init__(self, crowding: Crowding):
        super().__init__(crowding)

    def add_new_rule(self, grammar: Grammar, first_symbol: Symbol, second_symbol: Symbol = None) -> Rule:
        new_rule = self.produce_rule(grammar, first_symbol)
        if not self.rule_is_effective(grammar, new_rule.left):
            self.make_rule_effective(grammar, new_rule)
        else:
            self.crowding.add_rule(grammar, new_rule)
            self.iteration.add_covering_rule(new_rule)
        return new_rule
