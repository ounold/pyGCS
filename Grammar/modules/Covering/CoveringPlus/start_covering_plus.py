from modules.GCSBase.domain.Rule import RuleOrigin
from ..Covering import Covering
from ...GCSBase.domain import Rule
from ...GCSBase.domain.symbol import Symbol
from ...GCSBase.grammar.grammar import Grammar
from ...GCSBase.utils.random_utils import RandomUtils
from ...sGCS.domain.sRule import sRuleBuilder


class StartCoveringPlus(Covering):

    def __init__(self):
        super().__init__()

    def add_new_rule(self, grammar: Grammar, first_symbol: Symbol, second_symbol: Symbol = None) -> Rule:
        new_rule = self.produce_rule(grammar, first_symbol)
        grammar.add_rule(new_rule)
        self.iteration.add_covering_rule(new_rule)
        self.log_rule(new_rule)
        return new_rule

    def produce_rule(self, grammar: Grammar, symbol: Symbol) -> Rule:
        probability = RandomUtils.get_random_probability()
        left_symbol = grammar.get_start_symbol()
        return sRuleBuilder() \
            .left_symbol(left_symbol) \
            .first_right_symbol(symbol) \
            .probability(probability) \
            .origin(RuleOrigin.COVERING) \
            .create()
