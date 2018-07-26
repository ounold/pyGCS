import logging
import math
from typing import List

from modules.GCSBase.domain.types.AaaRulesHandlingType import AaaRulesHandlingType
from modules.sGCS.domain.sRule import sRule
from modules.GCSBase.domain.symbol import Symbol
from modules.sGCS.domain.sCellRule import sCellRule


class Stochastic:
    def __init__(self, settings=None):

        self.__logger = logging.getLogger("stochastic")
        self.__logger.info("Stochastic module inited.")
        self.settings = settings

    def normalize(self, grammar):
        for symbol in grammar.nonTerminalSymbols:
            self.normalize_rule(grammar, symbol)

    @staticmethod
    def normalize_rule(grammar, left):
        prob_sum = 0
        count_rules = 0
        for rule in grammar.get_rules():
            if rule.left == left:
                prob_sum += rule.probability
                count_rules += 1
        if prob_sum == 0:
            for rule in grammar.get_rules():
                if rule.left == left:
                    rule.probability = 1 / count_rules
        else:
            for rule in grammar.get_rules():
                if rule.left == left:
                    rule.probability = rule.probability / prob_sum

    def estimate_prob(self, grammar, method="IO"):
        if method == "IO":
            self.__logger.info("Calling Inside-Outside")
            self.inside_outside(grammar, grammar.estimation_type)
        elif method == "CE":
            self.__logger.info("Calling Contrastive Estimation")

    @staticmethod
    def init_rules_inside_outside_probabilities(cyk):
        for rule in cyk.grammar.get_rules():
            rule: sRule = rule
            rule.sum_inside_outside_usage_probability = 0.0
            rule.positive_sum_inside_outside_usages = 0.0
            rule.negative_sum_inside_outside_usages = 0.0

    def update_rules_count_after_sentence_parsing(self, cyk, learning_on: bool, cyk_start_cell_rules,
                                                  cyk_start_cell_rules_probability, positive: bool):
        if learning_on and cyk.settings.get_value('covering', 'is_terminal_covering_allowed') == "True":
            sentence_probability = self.calculate_sentence_probability(cyk, cyk_start_cell_rules,
                                                                       cyk_start_cell_rules_probability, positive)
            for rule in cyk.grammar.get_rules():
                rule: sRule = rule
                rule.calculate_counts(sentence_probability)

    def calculate_sentence_probability(self, cyk, cyk_start_cell_rules, cyk_start_cell_rules_probabilities, positive):
        self.calculate_inside_probabilities(cyk)
        start_cell_rules = []
        for i in range(len(cyk_start_cell_rules)):
            if cyk_start_cell_rules[i].rule.is_start():
                start_cell_rules.append(cyk_start_cell_rules[i])
        self.calculate_outside_probabilities(cyk, start_cell_rules)

        start_cell_rules = []
        for i in range(len(cyk.rules_table[len(cyk.sequence) - 1][0])):
            if cyk_start_cell_rules[i].rule.is_start():
                start_cell_rules.append(cyk_start_cell_rules[i])
        self.count(cyk, start_cell_rules, positive)

        sentence_probability: float = 0.0
        for i in range(len(cyk.grammar.nonTerminalSymbols)):
            if cyk.grammar.nonTerminalSymbols[i].is_start():
                if cyk_start_cell_rules_probabilities[i] is not cyk.default_value:
                    sentence_probability += cyk_start_cell_rules_probabilities[i].item_2
        return sentence_probability

    @staticmethod
    def calculate_inside_probabilities(cyk):
        for i in range(len(cyk.sequence)):
            for j in range(len(cyk.sequence)):
                for cell_rule in cyk.rules_table[i][j]:
                    cell_rule.inside = cyk.probability_array[i][j][cell_rule.rule.left.index].item_2

    @staticmethod
    def calculate_outside_probabilities(cyk, cell_rules_to_analyse):
        for rule in cell_rules_to_analyse:
            rule.outside = 1.0
        for i in reversed(range(len(cyk.sequence))):
            for j in reversed(range(len(cyk.sequence))):
                rules_processed = []
                for rule_parent in cyk.rules_table[i][j]:
                    if rules_processed.__contains__(rule_parent.rule):
                        continue
                    rules_processed.append(rule_parent.rule)
                    for k in reversed(range(i - 1)):
                        children_1 = [child for child in cyk.rules_table[k][j]
                                      if child.rule.left == rule_parent.rule.right1]
                        children_2 = [child for child in cyk.rules_table[i - k - 1][j + k + 1]
                                      if child.rule.left == rule_parent.rule.right2]
                        if len(children_1) > 0 and len(children_2) > 0:
                            for child_rule in children_1:
                                if child_rule.rule.left == rule_parent.rule.right1:
                                    child_rule.outside += rule_parent.outside * \
                                                          rule_parent.rule.probability * \
                                                          children_2[0].inside
                            for child_rule in children_2:
                                if child_rule.rule.left == rule_parent.rule.right2:
                                    child_rule.outside += rule_parent.outside * \
                                                          rule_parent.rule.probability * \
                                                          children_1[0].inside

    def count(self, cyk, cell_rules_to_analyse, is_sentence_positive: bool):
        """
        For each given rule check if it was already calculated and if not calculates inside outside probabilities
        for it. Then checks all rules which start with this rule either first right or second right symbol.
        :param cell_rules_to_analyse:
        :param is_sentence_positive:
        :param cyk
        :return:
        """
        while len(cell_rules_to_analyse) > 0:
            new_cell_rules = []
            for cell_rule in cell_rules_to_analyse:
                if cell_rule.calculated:
                    continue
                cell_rule.calculated = True
                right_one_rules = []
                right_two_rules = []
                if cell_rule.cell_1_coordinates is not None:
                    cell_one_x = cell_rule.cell_1_coordinates.x
                    cell_one_y = cell_rule.cell_1_coordinates.y
                    right_1: Symbol = cell_rule.rule.right1
                    rules = cyk.find_matching_rules_in_rules_container(cell_one_x, cell_one_y, right_1)
                    new_cell_rules.extend(rules)
                    right_one_rules.extend(rules)
                if cell_rule.cell_2_coordinates is not None:
                    cell_two_x = cell_rule.cell_2_coordinates.x
                    cell_two_y = cell_rule.cell_2_coordinates.y
                    right_2: Symbol = cell_rule.rule.right2
                    rules = cyk.find_matching_rules_in_rules_container(cell_two_x, cell_two_y, right_2)
                    new_cell_rules.extend(rules)
                    right_two_rules.extend(rules)
                self.calculate_inside_outside_for_cell_rule(cell_rule, right_one_rules,
                                                            right_two_rules, is_sentence_positive)
            cell_rules_to_analyse = new_cell_rules

    @staticmethod
    def calculate_inside_outside_for_cell_rule(cell_rule: sCellRule, right_one_rules,
                                               right_two_rules, is_sentence_positive: bool):
        if len(right_one_rules) is not 0 and len(right_two_rules) is not 0:
            rule: sRule = cell_rule.rule
            value = cell_rule.outside * right_one_rules[0].inside * right_two_rules[0].inside
            rule.add_inside_outside_probability_for_counting(value, is_sentence_positive)
            rule.sum_inside_outside_usage_probability += value
        elif len(right_one_rules) is 0 and len(right_two_rules) is 0:
            rule: sRule = cell_rule.rule
            rule.add_inside_outside_probability_for_counting(cell_rule.outside, is_sentence_positive)
            rule.sum_inside_outside_usage_probability += cell_rule.outside

    def inside_outside(self, grammar, estimation_type):
        new_ones_only = grammar.new_ones_only
        positive_examples_amount = grammar.positives_sample_amount
        negative_examples_amount = grammar.negative_sample_amount
        self.__logger.info("Inside - Outside estimation")
        to_be_removed: List[sRule] = []
        for r in grammar.get_rules():
            self.__logger.info(r)
            if r.usages_in_invalid_parsing == 0 and r.usages_in_proper_parsing == 0:
                continue
            else:
                left = r.left
                sum_all_counts_with_left_symbol = 0
                sum_all_positives_counts = 0
                sum_all_negatives_counts = 0
                for rule in grammar.get_rules():
                    if rule.left == left:
                        sum_all_counts_with_left_symbol += rule.count
                        sum_all_negatives_counts += rule.negative_count
                        sum_all_positives_counts += rule.positive_count
                if new_ones_only & r.is_new or not new_ones_only:
                    if r.is_new:
                        r.is_New = False
                    if estimation_type == "DifferentialEstimation":
                        estimated_probability_p = 0 if sum_all_positives_counts == 0 \
                            else r.positive_count / sum_all_positives_counts
                        estimated_probability_n = 0 if sum_all_negatives_counts == 0 \
                            else r.negative_count / sum_all_negatives_counts
                        estimated_probability_p_scaled = 0 if positive_examples_amount == 0 \
                            else estimated_probability_p / positive_examples_amount
                        estimated_probability_n_scaled = 0 if negative_examples_amount == 0 \
                            else estimated_probability_n / negative_examples_amount
                        new_probability = estimated_probability_p_scaled - estimated_probability_n_scaled
                    elif estimation_type == "OnlyPositivesEstimation":
                        new_probability = 0 if sum_all_positives_counts == 0 \
                            else r.positive_count / sum_all_positives_counts
                    else:
                        new_probability = 0 if sum_all_counts_with_left_symbol == 0 \
                            else r.count / sum_all_counts_with_left_symbol

                    self.__logger.info("[Inside-Outside] Probability for {} is {}".format(r, str(new_probability)))

                    if math.isnan(new_probability) or new_probability <= 0:
                        if not r.is_terminal(AaaRulesHandlingType.TERMINALS) and not r.is_start():
                            to_be_removed.append(r)
                    else:

                        r.probability = new_probability

        for r in to_be_removed:
            grammar.remove_rule(r)

        grammar.normalize_grammar()

    def contrastive_estimation(self, grammar):
        raise NotImplementedError

