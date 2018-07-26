from modules.Covering.Covering import Covering
from modules.Crowding.crowding import Crowding
from modules.GCSBase.domain.Rule import Rule, RuleOrigin
from modules.GCSBase.domain.symbol import Symbol
from modules.GCSBase.grammar.grammar import Grammar
from ...GCSBase.utils.random_utils import RandomUtils


class AggressiveStandardCovering(Covering):

    def __init__(self, crowding: Crowding):
        super().__init__(crowding)

    def add_new_rule(self, grammar: Grammar, first_symbol: Symbol, second_symbol: Symbol = None) -> Rule:
        new_rule = Rule([RandomUtils.get_random_nonterminal_symbol_from(grammar), first_symbol, second_symbol])
        new_rule.origin = RuleOrigin.COVERING
        self.crowding.add_rule(grammar, new_rule)
        self.iteration.add_covering_rule(new_rule)
        return new_rule
