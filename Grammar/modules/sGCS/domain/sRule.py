from typing import List

from modules.GCSBase.domain.Rule import Rule, RuleOrigin
from modules.GCSBase.domain.symbol import Symbol


class sRule(Rule):

    def __init__(self, symbols: List[Symbol] = None, prob=0):
        super().__init__(symbols)
        self.probability = prob
        self.sum_inside_outside_usage_probability = 0.0
        self.count = 0.0
        self.positive_count = 0.0
        self.positive_sum_inside_outside_usages = 0.0
        self.negative_count = 0.0
        self.negative_sum_inside_outside_usages = 0.0
        self.is_new = False

    @classmethod
    def from_symbols(cls, probability: float, left_symbol: Symbol, first_right_symbol: Symbol,
                     second_right_symbol: Symbol = None, origin: RuleOrigin = RuleOrigin.UNKNOWN):
        rule = cls()
        rule.left, rule.right1, rule.right2 = left_symbol, first_right_symbol, second_right_symbol
        rule.probability = probability
        rule.origin = origin
        return rule

    def add_inside_outside_probability_for_counting(self, value):
        pass

    def add_inside_outside_probability_for_counting(self, value: float, is_sentence_positive: bool):
        if is_sentence_positive:
            self.positive_sum_inside_outside_usages += value
        else:
            self.negative_sum_inside_outside_usages += value

    def calculate_counts(self, result: float):
        if result != 0.0:
            self.count += (self.probability / result) * self.sum_inside_outside_usage_probability
            self.positive_count += (self.probability / result) * self.positive_sum_inside_outside_usages
            self.negative_count += (self.probability / result) * self.negative_sum_inside_outside_usages

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return "({} -> {}{} P={}, F={}, Origin={}, count={}, neg_count = {}, pos_count = {}, fertility = {})".\
            format(self.left, (self.right1 or ""), (self.right2 or ""),
                   round(self.probability, 2), round(self.fitness, 2),
                   self.origin, round(self.count, 2), int(self.negative_count),
                   int(self.positive_count), self.fertility)

class sRuleBuilder():
    def __init__(self):
        self.__left_symbol = None
        self.__first_right_symbol = None
        self.__second_right_symbol = None
        self.__probability = None
        self.__origin = RuleOrigin.UNKNOWN

    def left_symbol(self, value: Symbol):
        self.__left_symbol = value
        return self

    def first_right_symbol(self, value: Symbol):
        self.__first_right_symbol = value
        return self

    def second_right_symbol(self, value: Symbol):
        self.__second_right_symbol = value
        return self

    def probability(self, value: float):
        self.__probability = value
        return self

    def origin(self, origin: RuleOrigin):
        self.__origin = origin
        return self

    def create(self) -> Rule:
        return sRule.from_symbols(self.__probability, self.__left_symbol, self.__first_right_symbol,
                                  self.__second_right_symbol, self.__origin)
