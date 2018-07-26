import logging
import random
from modules.GCSBase.grammar.grammar import Grammar
from modules.Stochastic.Stochastic import Stochastic
from modules.GCSBase.domain.symbol import Symbol
from modules.sGCS.domain.sRule import sRule
from modules.Loader.test_data import TestData
from typing import List


class sGCSGrammar(Grammar):

    def __init__(self, settings = None):
        self.__settings = settings
        super().__init__(settings)
        self.__logger = logging.getLogger("sgcs_grammar")
        self.__logger.info("SGCS Grammar Module inited.")
        self.__positives_sample_amount = 0
        self.__negative_sample_amount = 0
        self.__stochastic = Stochastic()
        if settings is not None:
            self.__new_ones_only = self.__settings.get_value("sgcs", "new_ones_only") == "True"
            self.__estimation_method = self.__settings.get_value("sgcs", "probability_estimation_method")
            self.__negative_sample_estimation = self.__settings.get_value("sgcs", "negative_sample_estimation") == "True"
            self.__estimation_type = self.__settings.get_value("sgcs", "estimation_type")

    @property
    def positives_sample_amount(self):
        return self.__positives_sample_amount

    @property
    def negative_sample_amount(self):
        return self.__negative_sample_amount

    @property
    def estimation_method(self):
        return self.__estimation_method

    @property
    def new_ones_only(self):
        return self.__new_ones_only

    @property
    def negative_sample_estimation(self):
        return self.__negative_sample_estimation

    @property
    def estimation_type(self):
        return self.__estimation_type

    @positives_sample_amount.setter
    def positives_sample_amount(self, x):
        self.__positives_sample_amount = x

    @negative_sample_amount.setter
    def negative_sample_amount(self, x):
        self.__negative_sample_amount = x

    @estimation_method.setter
    def estimation_method(self, x):
        self.__estimation_method = x

    @new_ones_only.setter
    def new_ones_only(self, x):
        self.__new_ones_only = x

    @negative_sample_estimation.setter
    def negative_sample_estimation(self, x):
        self.__negative_sample_estimation = x

    @estimation_type.setter
    def estimation_type(self, x):
        self.__estimation_type = x

    def adjust_parameters(self):
        self.__stochastic.estimate_prob(self)

    def normalize_grammar(self):
        # stochastic = Stochastic()
        self.__stochastic.normalize(self)

    def init_grammar(self, data: TestData):
        super().init_grammar(data)
        self.assign_probabilities_and_normalize_grammar()

    def assign_probabilities_and_normalize_grammar(self):
        for rule in self.get_rules():
            rule.probability = random.uniform(0, 1)
        self.__stochastic.normalize(self)

    @staticmethod
    def get_rule_rand_non_terminal_rule(left: Symbol, right1: Symbol, right2: Symbol):
        return sRule([left, right1, right2], random.uniform(0, 1))

    @staticmethod
    def get_rule_from_string(rule_string, symbols: List[Symbol]):
        return sRule(rule_string, symbols)






