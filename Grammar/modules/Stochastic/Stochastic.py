import logging
import math
import random
import _pickle as pickle
import operator
from typing import List

from modules.GCSBase.domain.types.AaaRulesHandlingType import AaaRulesHandlingType
from modules.sGCS.domain.sRule import sRule
from modules.GCSBase.domain.symbol import Symbol
from modules.sGCS.domain.sCellRule import sCellRule
from modules.Parsers.CYK.sGCS.ProbabilityArrayCell import ProbabilityArrayCell
from modules.GCSBase.domain import Rule
from modules.GCSBase.domain.Coordinates import Coordinates

from copy import deepcopy


class Stochastic:
    def __init__(self, settings=None, cyk=None):

        self.__logger = logging.getLogger("stochastic")
        self.__logger.info("Stochastic module inited.")
        self.settings = settings
        self.cyk = cyk
        self.__train_data = None
        self.neighborhoods = dict()

    @property
    def train_data(self):
        return self.__train_data

    @train_data.setter
    def train_data(self, x):
        self.__train_data = x
        self.get_neighborhoods()

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

    def estimate_prob(self, grammar, method="Standard"):
        if grammar.estimation_method == "IO":
            self.__logger.info("Calling Inside-Outside")
            self.inside_outside(grammar, grammar.estimation_type)

    @staticmethod
    def init_rules_inside_outside_probabilities(cyk):
        for rule in cyk.grammar.get_rules():
            rule: sRule = rule
            rule.sum_inside_outside_usage_probability = 0.0
            rule.count_inside_outside_usage_probability = 0.0
            rule.positive_sum_inside_outside_usages = 0.0
            rule.negative_sum_inside_outside_usages = 0.0

            # TODO: remove completly

    def calculate_cell(self, mode, default_value, probability_array, parent_cell_1: Coordinates,
                       parent_cell_2: Coordinates,
                       cell_coordinates: Coordinates,
                       rule: Rule):

        rule_left_index = rule.left.index
        rule_right_1_index = rule.right1.index
        rule_right_2_index = rule.right2.index
        cell_probability = probability_array[cell_coordinates.x][cell_coordinates.y][rule_left_index]
        parent_cell_1_probability = probability_array[parent_cell_1.x][parent_cell_1.y][rule_right_1_index]
        parent_cell_2_probability = probability_array[parent_cell_2.x][parent_cell_2.y][rule_right_2_index]

        if mode == "BaumWelch":
            cell_probability = self.__calculate_baum_welch_rule_cell_probability(default_value, cell_probability,
                                                                                 parent_cell_1_probability,
                                                                                 parent_cell_2_probability, rule)
        elif mode == "Viterbi":
            cell_probability = self.__calculate_viterbi_rule_cell_probability(default_value, cell_probability,
                                                                              parent_cell_1_probability,
                                                                              parent_cell_2_probability, rule)
        elif mode == "MinProb":
            cell_probability = self.__calculate_min_prob_rule_cell_probability(default_value, cell_probability,
                                                                               parent_cell_1_probability,
                                                                               parent_cell_2_probability, rule)
        probability_array[cell_coordinates.x][cell_coordinates.y][rule_left_index] = cell_probability

    def new_calculate_cell(self, mode, default_value, parent_cell_prob: ProbabilityArrayCell,
                           parent_cell_2_prob: ProbabilityArrayCell, cell_prob: ProbabilityArrayCell,
                           rule: Rule) -> ProbabilityArrayCell:
        if mode == "BaumWelch":
            cell_probability = self.__calculate_baum_welch_rule_cell_probability(default_value, cell_prob,
                                                                                 parent_cell_prob,
                                                                                 parent_cell_2_prob, rule)
        elif mode == "Viterbi":
            cell_probability = self.__calculate_viterbi_rule_cell_probability(default_value, cell_prob,
                                                                              parent_cell_prob,
                                                                              parent_cell_2_prob, rule)
        elif mode == "MinProb":
            cell_probability = self.__calculate_min_prob_rule_cell_probability(default_value, cell_prob,
                                                                               parent_cell_prob,
                                                                               parent_cell_2_prob, rule)
        return cell_probability

    @staticmethod
    def __calculate_baum_welch_rule_cell_probability(default_value, cell_probability: ProbabilityArrayCell,
                                                     parent_cell_1_probability: ProbabilityArrayCell,
                                                     parent_cell_2_probability: ProbabilityArrayCell,
                                                     rule: sRule) -> ProbabilityArrayCell:

        if cell_probability == default_value:
            cell_probability = ProbabilityArrayCell()
            cell_probability.item_1 = rule.probability * \
                                      parent_cell_1_probability.item_1 * \
                                      parent_cell_2_probability.item_1
            cell_probability.item_2 = rule.probability * \
                                      parent_cell_1_probability.item_2 * \
                                      parent_cell_2_probability.item_2
        else:
            cell_probability.item_1 = cell_probability.item_1 + \
                                      (rule.probability *
                                       parent_cell_1_probability.item_1 *
                                       parent_cell_2_probability.item_1)
            cell_probability.item_2 = cell_probability.item_2 + \
                                      (rule.probability *
                                       parent_cell_1_probability.item_2 *
                                       parent_cell_2_probability.item_2)
        return cell_probability

    @staticmethod
    def __calculate_viterbi_rule_cell_probability(default_value, cell_probability: ProbabilityArrayCell,
                                                  parent_cell_1_probability: ProbabilityArrayCell,
                                                  parent_cell_2_probability: ProbabilityArrayCell,
                                                  rule: sRule):
        if cell_probability == default_value:
            cell_probability = ProbabilityArrayCell()
            cell_probability.item_1 = math.log10(rule.probability) + \
                                      parent_cell_1_probability.item_1 + parent_cell_2_probability.item_1

            cell_probability.item_2 = (rule.probability *
                                       parent_cell_1_probability.item_2 *
                                       parent_cell_2_probability.item_2)

        else:
            cell_probability.item_1 = max(cell_probability.item_1,
                                          math.log10(rule.probability) + parent_cell_1_probability.item_1 +
                                          parent_cell_2_probability.item_1)

            cell_probability.item_2 = cell_probability.item_2 + (rule.probability *
                                                                 parent_cell_1_probability.item_2 *
                                                                 parent_cell_2_probability.item_2)
        return cell_probability

    @staticmethod
    def __calculate_min_prob_rule_cell_probability(default_value, cell_probability: ProbabilityArrayCell,
                                                   parent_cell_1_probability: ProbabilityArrayCell,
                                                   parent_cell_2_probability: ProbabilityArrayCell,
                                                   rule: sRule):
        if cell_probability == default_value:
            cell_probability = ProbabilityArrayCell()
            cell_probability.item_1 = min(min(rule.probability * parent_cell_1_probability.item_1),
                                          parent_cell_2_probability.item_1)

            cell_probability.item_2 = rule.probability * \
                                      parent_cell_1_probability.item_2 * \
                                      parent_cell_2_probability.item_2
        else:
            cell_probability.item_1 = max(cell_probability.item_1,
                                          min(min(rule.probability), parent_cell_1_probability.item_1,
                                              parent_cell_2_probability.item_1))
            cell_probability.item_2 = cell_probability.item_2 + rule.probability * \
                                                                parent_cell_1_probability.item_2 * \
                                                                parent_cell_2_probability.item_2
        return cell_probability

    def update_rules_count_after_sentence_parsing(self, cyk, learning_on: bool, cyk_start_cell_rules,
                                                  cyk_start_cell_rules_probability, positive: bool):
        rules_table = cyk.rules_table
        probability_array = cyk.probability_array
        find_matching_rules_in_rules_container = cyk.find_matching_rules_in_rules_container
        if True:  # learning_on and cyk.settings.get_value('covering', 'is_terminal_covering_allowed') == "True":
            sentence_probability = self.calculate_sentence_probability(cyk.sequence, cyk.rules_table,
                                                                       cyk.probability_array, cyk.grammar,
                                                                       cyk.default_value,
                                                                       cyk.find_matching_rules_in_rules_container,
                                                                       cyk_start_cell_rules,
                                                                       cyk_start_cell_rules_probability, positive)
            for rule in cyk.grammar.get_rules():
                rule: sRule = rule
                rule.calculate_counts(sentence_probability)
            return sentence_probability
        return 0

    def calculate_sentence_probability(self, sequence, rules_table, probability_array, grammar, default_value,
                                       find_matching_rules_in_rules_container,
                                       cyk_start_cell_rules, cyk_start_cell_rules_probabilities, positive):
        self.calculate_inside_probabilities(sequence, rules_table, probability_array)

        if grammar.estimation_method == "IO":
            start_cell_rules = []
            for i in range(len(cyk_start_cell_rules)):
                if cyk_start_cell_rules[i].rule.is_start():
                    start_cell_rules.append(cyk_start_cell_rules[i])
            self.calculate_outside_probabilities(sequence, rules_table, start_cell_rules)

            start_cell_rules = []
            for i in range(len(rules_table[len(sequence) - 1][0])):
                if cyk_start_cell_rules[i].rule.is_start():
                    start_cell_rules.append(cyk_start_cell_rules[i])
            self.count(rules_table, find_matching_rules_in_rules_container, start_cell_rules, positive)

        sentence_probability: float = 0.0
        for i in range(len(grammar.nonTerminalSymbols)):
            if grammar.nonTerminalSymbols[i].is_start():
                if cyk_start_cell_rules_probabilities[i] is not default_value:
                    sentence_probability += cyk_start_cell_rules_probabilities[i].item_2
        return sentence_probability

    @staticmethod
    def calculate_inside_probabilities(sequence, rules_table, probability_array):
        for i in range(len(sequence)):
            for j in range(len(sequence) - i):
                for cell_rule in rules_table[i][j]:
                    cell_rule.inside = probability_array[i][j][cell_rule.rule.left.index].item_2

    @staticmethod
    def calculate_outside_probabilities(sequence, rules_table, cell_rules_to_analyse):
        for rule in cell_rules_to_analyse:
            rule.outside = 1.0
        for i in reversed(range(len(sequence))):
            for j in reversed(range(len(sequence) - i)):
                for rule_parent in rules_table[i][j]:
                    if rule_parent.proceeded:
                        continue
                    rule_parent.proceeded = True
                    for k in reversed(range(i)):
                        children_1 = [child for child in rules_table[k][j]
                                      if child.rule.left.index == rule_parent.rule.right1.index]
                        children_2 = [child for child in rules_table[i - k - 1][j + k + 1]
                                      if child.rule.left.index == rule_parent.rule.right2.index]
                        if len(children_1) > 0 and len(children_2) > 0:
                            for child_rule in children_1:
                                if child_rule.rule.left.index == rule_parent.rule.right1.index:
                                    child_rule.outside += rule_parent.outside * \
                                                          rule_parent.rule.probability * \
                                                          children_2[0].inside
                            for child_rule in children_2:
                                if child_rule.rule.left.index == rule_parent.rule.right2.index:
                                    child_rule.outside += rule_parent.outside * \
                                                          rule_parent.rule.probability * \
                                                          children_1[0].inside

    def count(self, rules_table, find_matching_rules_in_rules_container, cell_rules_to_analyse,
              is_sentence_positive: bool):
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
                    rules = find_matching_rules_in_rules_container(rules_table, cell_one_x, cell_one_y, right_1)
                    new_cell_rules.extend(rules)
                    right_one_rules.extend(rules)
                if cell_rule.cell_2_coordinates is not None:
                    cell_two_x = cell_rule.cell_2_coordinates.x
                    cell_two_y = cell_rule.cell_2_coordinates.y
                    right_2: Symbol = cell_rule.rule.right2
                    rules = find_matching_rules_in_rules_container(rules_table, cell_two_x, cell_two_y, right_2)
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
            rule.count_inside_outside_usage_probability += 1
        elif len(right_one_rules) is 0 and len(right_two_rules) is 0:
            rule: sRule = cell_rule.rule
            rule.add_inside_outside_probability_for_counting(cell_rule.outside, is_sentence_positive)
            rule.sum_inside_outside_usage_probability += cell_rule.outside
            rule.count_inside_outside_usage_probability += 1

    def inside_outside(self, grammar, estimation_type):
        new_ones_only = grammar.new_ones_only
        positive_examples_amount = grammar.positives_sample_amount
        negative_examples_amount = grammar.negative_sample_amount
        self.__logger.info("Inside - Outside estimation")
        to_be_removed: List[sRule] = []
        for r in grammar.get_rules():
            self.__logger.info(r)
            if r.positive_count == 0 and r.negative_count == 0:
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
                    if estimation_type == "CE":
                        neigh_count = 0
                        count = 0
                        for i in range(len(self.train_data)):
                            if not self.train_data[i].positive:
                                pass
                            else:
                                neigh_count += sum(operator.itemgetter(*self.neighborhoods[i])(r.count_in_sentence)) if \
                                    len(self.neighborhoods[i]) > 1 else r.count_in_sentence[self.neighborhoods[i][0]]
                                count += r.count_in_sentence[i]
                        ce_count = 0 if count == 0 else count / (count + neigh_count)

                        new_probability2 = 0 if (r.positive_count + positive_examples_amount * r.negative_count) == 0 \
                            else r.positive_count / (r.positive_count + positive_examples_amount * r.negative_count)
                        #print("np = {}, np2 = {}".format(ce_count, new_probability2))

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
                    elif estimation_type == "Standard" or estimation_type == "CE":
                        if estimation_type == "CE":
                            new_probability = 0 if sum_all_counts_with_left_symbol == 0 \
                                else r.count / sum_all_counts_with_left_symbol * ce_count
                            # print(
                            #     "{}->{}{}, count = {}, p_count = {}, n_count = {}, ce_count = {}, io = {}, old_prob = {}, new_prob = {}".
                            #     format(r.left, r.right1, r.right2 if r.right2 is not None else "",
                            #            round(r.count, 2), round(r.positive_count, 2), round(r.negative_count, 2),
                            #            round(ce_count, 2),
                            #            round(0 if sum_all_counts_with_left_symbol == 0 \
                            #                      else r.count / sum_all_counts_with_left_symbol, 2),
                            #            round(r.probability, 2), round(new_probability, 2)))
                        else:
                            new_probability = 0 if sum_all_counts_with_left_symbol == 0 \
                                else r.count / sum_all_counts_with_left_symbol
                            # print(
                            #     "{}->{}{}, count = {}, p_count = {}, n_count = {}, io = {}, old_prob = {}, new_prob = {}".
                            #     format(r.left, r.right1, r.right2 if r.right2 is not None else "",
                            #            round(r.count, 2), round(r.positive_count, 2), round(r.negative_count, 2),
                            #            round(0 if sum_all_counts_with_left_symbol == 0 \
                            #                      else r.count / sum_all_counts_with_left_symbol, 2),
                            #            round(r.probability, 2), round(new_probability, 2)))


                    else:
                        raise Exception("Choose estimation type")
                    if (math.isnan(new_probability) or new_probability <= 0) and \
                            not r.is_terminal(AaaRulesHandlingType.TERMINALS) and not r.is_start():
                            to_be_removed.append(r)
                    else:
                        if new_probability != 0:
                            diff = new_probability - r.probability
                            r.probability += diff/4
                        else:
                            r.probability = 0

                    self.__logger.info("[Inside-Outside] Probability for {} is {}".format(r, str(new_probability)))

        for r in to_be_removed:
            grammar.remove_rule(r)

        #grammar.normalize_grammar()

    def get_neighborhoods(self):
        type = self.settings.get_value("sgcs", "neighborhood_type")
        size = int(self.settings.get_value("sgcs", "max_neighborhood_size"))
        for i in range(len(self.train_data)):
            if self.train_data[i].positive:
                neigh = [i]
                if type == "AllNegatives":
                    for j in range(len(self.train_data)):
                        if not self.train_data[j].positive:
                            neigh.append(j)
                if type == "SameLength":
                    for j in range(len(self.train_data)):
                        if not self.train_data[j].positive and \
                                abs(len(self.train_data[j].sequence) - len(self.train_data[i].sequence)) <= 1:
                            neigh.append(j)
                if len(neigh) > size:
                    neigh = [neigh[i] for i in sorted(random.sample(range(len(neigh)), size))]
                self.neighborhoods[i] = neigh


