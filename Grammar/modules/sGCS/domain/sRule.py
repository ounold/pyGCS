from typing import List
import math
from modules.GCSBase.domain.Rule import Rule, RuleOrigin
from modules.GCSBase.domain.symbol import Symbol


class sRule(Rule):

    def __init__(self, symbols: List[Symbol] = None, prob=0, *args):
        super().__init__(symbols)
        self.probability = prob
        self.sum_inside_outside_usage_probability = 0.0
        self.count = 0.0
        self.positive_count = 0.0
        self.positive_sum_inside_outside_usages = 0.0
        self.negative_count = 0.0
        self.negative_sum_inside_outside_usages = 0.0
        self.is_new = False
        self.usages_in_invalid_parsing_parsed = 0
        self.usages_in_proper_parsing_parsed = 0
        self.usage_in_distinct_proper_parsed = 0
        self.usage_in_distinct_invalid_parsed = 0
        self.count_in_sentence = list()
        self.apriori = 0
        self.positive_parsed_probs = list()
        self.negative_parsed_probs = list()
        self.count_inside_outside_usage_probability = 0


    @staticmethod
    def from_dict(rule_dict):
        left = Symbol.from_dict(rule_dict['left'])
        right1 = Symbol.from_dict(rule_dict['right1'])
        right2 = None
        if rule_dict['right2'] is not None:
            right2 = Symbol.from_dict(rule_dict['right2'])
        return sRule([left, right1, right2])


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

    def reset_usages_and_points(self):
        super().reset_usages_and_points()
        self.sum_inside_outside_usage_probability = 0.0
        self.count = 0.0
        self.positive_count = 0.0
        self.positive_sum_inside_outside_usages = 0.0
        self.negative_count = 0.0
        self.negative_sum_inside_outside_usages = 0.0
        self.usages_in_invalid_parsing_parsed = 0
        self.usages_in_proper_parsing_parsed = 0
        self.usage_in_distinct_proper_parsed = 0
        self.usage_in_distinct_invalid_parsed = 0
        self.apriori = 0
        self.positive_parsed_probs = list()
        self.negative_parsed_probs = list()
        self.count_in_sentence = list()

    def calculate_counts(self, result: float):
        if result > 1*10**(-10):
            new_count = 0 if self.sum_inside_outside_usage_probability == 0.0 else \
                (self.probability / result) * self.sum_inside_outside_usage_probability#/self.count_inside_outside_usage_probability
            self.count += new_count
            self.positive_count += (self.probability / result) * self.positive_sum_inside_outside_usages
            self.negative_count += (self.probability / result) * self.negative_sum_inside_outside_usages
            self.count_in_sentence.append(new_count)
        else:
            self.count_in_sentence.append(0.0)

    def json_str(self):
        json_values = dict()
        json_values["left"] = self.left.json_str()
        json_values["right1"] = self.right1.json_str()
        if self.right2 is not None:
            json_values["right2"] = self.right2.json_str()
        json_values["probability"] = self.probability
        return json_values

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return "({} -> {}{} P={}, F={}, Origin={}, count={}, neg_count = {}, pos_count = {}, " \
               "proper_usage = {}, proper_usage_parsed = {}, distinct_proper = {}, distinct_proper_parsed = {}, " \
               "invalid_usage = {}, invalid_usage_parsed = {}, distinct_invalid = {}, distinct_invalid_parsed= {}, " \
               "fertility = {})".\
            format(self.left, (self.right1 or ""), (self.right2 or ""),
                   round(self.probability, 2), round(self.fitness, 2),
                   self.origin, round(self.count, 2), int(self.negative_count),
                   int(self.positive_count),
                   self.usages_in_proper_parsing, self.usages_in_proper_parsing_parsed, self.usage_in_distinct_proper,
                   self.usage_in_distinct_proper_parsed,
                   self.usages_in_invalid_parsing, self.usages_in_invalid_parsing_parsed, self.usage_in_distinct_invalid,
                   self.usage_in_distinct_invalid_parsed, self.fertility)

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


