from modules.Covering.NewCovering.new_covering import NewCovering
from settings.settings import Settings
from ...Crowding.crowding import Crowding
from ...GCSBase.domain.Rule import Rule, RuleOrigin
from ...GCSBase.domain.symbol import Symbol
from ...GCSBase.grammar.grammar import Grammar
from ...GCSBase.utils.random_utils import RandomUtils
from ...sGCS.domain.sRule import sRuleBuilder


class AggressiveNewCovering(NewCovering):

    def __init__(self, crowding: Crowding, settings: Settings):
        super().__init__(crowding, settings)

    def add_new_rule(self, grammar: Grammar, first_symbol: Symbol, second_symbol: Symbol = None) -> Rule:
        new_rule = self.produce_rule(grammar, first_symbol, second_symbol)
        self.crowding.add_rule(grammar, new_rule)
        self.iteration.add_covering_rule(new_rule)
        return new_rule

    def produce_rule(self, grammar: Grammar, first_right_symbol: Symbol, second_right_symbol: Symbol) -> Rule:
        left_symbol = self.get_left_symbol(grammar)
        probability = RandomUtils.get_random_probability()
        return sRuleBuilder() \
            .left_symbol(left_symbol) \
            .first_right_symbol(first_right_symbol) \
            .second_right_symbol(second_right_symbol) \
            .probability(probability) \
            .origin(RuleOrigin.COVERING) \
            .create()
