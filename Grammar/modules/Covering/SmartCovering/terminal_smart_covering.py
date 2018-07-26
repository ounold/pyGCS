from ..Covering import Covering
from ...Crowding.crowding import Crowding
from ...GCSBase.domain.Rule import Rule, RuleOrigin
from ...GCSBase.domain.symbol import Symbol
from ...GCSBase.grammar.grammar import Grammar
from ...GCSBase.utils.random_utils import RandomUtils
from ...sGCS.domain.sRule import sRuleBuilder


class TerminalSmartCovering(Covering):

    def __init__(self, crowding: Crowding):
        super().__init__(crowding)
        self.crowding = crowding

    def add_new_rule(self, grammar: Grammar, first_symbol: Symbol, second_symbol: Symbol = None) -> Rule:
        new_rule = self.produce_rule(grammar, first_symbol)
        self.crowding.add_rule(grammar, new_rule)
        self.iteration.add_covering_rule(new_rule)
        return new_rule

    def produce_rule(self, grammar: Grammar, right_symbol: Symbol) -> Rule:
        random_left_symbol = RandomUtils.get_random_nonterminal_symbol_from(grammar)
        probability = RandomUtils.get_random_probability()
        return sRuleBuilder() \
            .left_symbol(random_left_symbol) \
            .first_right_symbol(right_symbol) \
            .probability(probability) \
            .origin(RuleOrigin.COVERING) \
            .create()
