from modules.GCSBase.domain.Rule import RuleOrigin
from ..Covering import Covering
from ...Crowding.crowding import Crowding
from ...GCSBase.domain import Rule
from ...GCSBase.domain.symbol import Symbol
from ...GCSBase.grammar.grammar import Grammar
from ...GCSBase.utils.random_utils import RandomUtils
from ...sGCS.domain.sRule import sRuleBuilder


class AggressiveCoveringPlus(Covering):

    def __init__(self, crowding: Crowding):
        super().__init__(crowding)

    def add_new_rule(self, grammar: Grammar, first_symbol: Symbol, second_symbol: Symbol = None) -> Rule:
        new_rule = self.produce_rule(grammar, first_symbol, second_symbol)
        was_added = self.crowding.add_rule(grammar, new_rule)
        self.iteration.add_covering_rule(new_rule)
        self.log_rule(new_rule, was_added)
        return new_rule

    def produce_rule(self, grammar: Grammar, first_symbol: Symbol, second_symbol: Symbol) -> Rule:
        random_left_symbol = RandomUtils.get_random_nonterminal_symbol_from(grammar)
        probability = RandomUtils.get_random_probability()
        return sRuleBuilder() \
            .left_symbol(random_left_symbol) \
            .first_right_symbol(first_symbol) \
            .second_right_symbol(second_symbol) \
            .probability(probability) \
            .origin(RuleOrigin.COVERING) \
            .create()
