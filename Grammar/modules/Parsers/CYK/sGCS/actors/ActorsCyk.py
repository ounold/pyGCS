import _pickle as pickle
import logging
import math
from collections import deque
from random import randint

import pykka

from modules.Covering.Covering import Covering
from modules.GCSBase.SingleExampleEvaluation import SingleExampleEvaluation
from modules.GCSBase.domain import Rule
from modules.GCSBase.domain.Coordinates import Coordinates
from modules.GCSBase.utils.random_utils import RandomUtils
from modules.Parsers.CYK.Base import CYKBase
from modules.Parsers.CYK.sGCS.ProbabilityArrayCell import ProbabilityArrayCell
from modules.Parsers.CYK.sGCS.actors.JobsStateStorage import JobsStateStorage
from modules.Parsers.CYK.sGCS.actors.RulesAndProbabilityStorageActor import RulesAndProbabilityStorage
from modules.Parsers.CYK.sGCS.actors.RulesStorageActor import RulesStorageActor
from modules.Parsers.CYK.sGCS.actors.StorageActor import StorageActor
from modules.Parsers.CYK.sGCS.actors.TaskExecutorActor import TaskExecutorActor
from modules.Stochastic.Stochastic import Stochastic
from modules.sGCS.domain.sCellRule import sCellRule
from modules.sGCS.domain.sRule import sRule
from modules.sGCS.sGCS_grammar import sGCSGrammar


class ActorsSGCSCyk(CYKBase.CYKBase):
    def __init__(self, grammar: sGCSGrammar = None, default_value=None, settings=None,
                 start_covering: Covering = None, final_covering: Covering = None,
                 aggressive_covering: Covering = None, terminal_covering: Covering = None):

        super().__init__(grammar, default_value, settings,
                         aggressive_covering=aggressive_covering,
                         terminal_covering=terminal_covering,
                         final_covering=final_covering,
                         start_covering=start_covering)
        self.learning_on = True
        self.__logger = logging.getLogger("sgcs")
        self.__logger.info("sSGCS CYK Module inited.")
        self.__settings = settings
        self.__generated_rules_count = 0
        self.__Stochastic = Stochastic()

        if settings is not None:
            self.parsing_threshold = float(self.__settings.get_value('sgcs', 'parsing_threshold'))
            self.mode = self.__settings.get_value('general', 's_mode')

    @property
    def settings(self):
        return self.__settings

    def cyk_result(self, sentence: str, grammar: sGCSGrammar, positive: bool,
                   learning_on: bool) -> SingleExampleEvaluation:
        self.grammar = grammar
        self.learning_on = learning_on
        self.__generated_rules_count = 0

        self.__Stochastic.init_rules_inside_outside_probabilities(self)
        self.parse_sentence(sentence, positive)
        # result = self.get_result()
        # is_result_parsed = self.is_parsed(result)
        # self.__logger.info('Sentence {0} parsed by cyk as positive: {1}.'.format(sentence, is_result_parsed))
        #
        # full_rules_table = pickle.loads(pickle.dumps(self.rules_table, -1))
        #
        # cyk_start_cell_rules = self.rules_table[len(self.sequence) - 1][0]
        # cyk_start_cell_rules_probability = self.probability_array[len(self.sequence) - 1][0]
        #
        # self.__fill_usages_for_start_cell_rules(cyk_start_cell_rules, positive)
        # self._remove_unused_cell_rules(len(sentence))
        # self._fill_debts_profits(sentence, positive)
        # self.__Stochastic.update_rules_count_after_sentence_parsing(self, learning_on, cyk_start_cell_rules,
        #                                                             cyk_start_cell_rules_probability, positive)
        # self.__update_grammars_positives_and_negatives(is_result_parsed, positive)
        #
        # for rule in self.grammar.get_rules():
        #     rule.tmp_used = False
        #
        # return self.__create_evaluation(sentence, result, full_rules_table)

    def __create_evaluation(self, sentence, result: float, rules_table_copy) -> SingleExampleEvaluation:
        return SingleExampleEvaluation(result, self.is_parsed(result), self.rules_table, rules_table_copy, sentence)

    def get_result(self) -> float:
        if self.mode == 'Viterbi':
            result = -math.inf
        else:
            result = 0.0
        for i in range(len(self.grammar.nonTerminalSymbols)):
            if self.grammar.nonTerminalSymbols[i].is_start():
                if self.probability_array[len(self.sequence) - 1][0][i] != self.default_value:
                    if math.isinf(-result):
                        result = 0.0
                    result = result + self.probability_array[len(self.sequence) - 1][0][i].item_1
        return result

    def parse_sentence(self, sequence: str, positive: bool):

        self.__logger.info('Parsing sentence {0}. Belongs to grammar: {1}'.format(sequence, positive))

        jobs_queue = deque()
        sequence_length = len(sequence)
        self._init_symbol_sequence(sequence)
        self.init_tables(sequence_length, jobs_queue)
        self.init_first_row(positive)

        jobs_storage_proxy = StorageActor.start(jobs_queue).proxy()
        rules_storage_proxy = RulesStorageActor.start(self.grammar.get_rules()).proxy()
        rules_prob_storage_proxy = RulesAndProbabilityStorage.start(self.rules_table, self.probability_array).proxy()
        parsing_state_proxy = JobsStateStorage.start(self.cells_parsing_states_table).proxy()

        tasks = []

        for i in range(4):
            executor = TaskExecutorActor.start(jobs_storage_proxy,
                                               rules_prob_storage_proxy,
                                               parsing_state_proxy,
                                               rules_storage_proxy)
            task = executor.ask({'command': 'start'}, block=False)
            tasks.append(task)

        for task in tasks:
            result = task.get()

        rules_prob_storage_proxy: RulesAndProbabilityStorage = rules_prob_storage_proxy
        self.probability_array = rules_prob_storage_proxy.get_probability_array().get()
        self. rules_table = rules_prob_storage_proxy.get_rules_table().get()
        rules_to_add = rules_prob_storage_proxy.get_rule_to_add().get()

        pykka.ActorRegistry.stop_all()

        if self.learning_on:
            for rule in rules_to_add:
                self.__apply_aggressive_and_final_covering(rule[0], rule[1])


        # # Iterate through upper triangle of the cyk matrix
        # for i in range(1, sequence_length):
        #     for j in range(sequence_length - i):
        #         for k in range(i):
        #             for rule in self.grammar.get_rules():
        #                 if rule.right2 is not None:
        #                     first_rule_index = rule.right1.index
        #                     second_rule_index = rule.right2.index
        #                     if self.probability_array[k][j][first_rule_index] is not None \
        #                             and self.probability_array[i - k - 1][j + k + 1][second_rule_index] is not None:
        #                         rule.tmp_used = True
        #                         rule_left_index = rule.left.index
        #
        #                         parent_cell_probability = self.probability_array[k][j][first_rule_index]
        #                         parent_cell_2_probability = \
        #                             self.probability_array[i - k - 1][j + k + 1][second_rule_index]
        #                         current_cell_probability = self.probability_array[i][j][rule_left_index]
        #
        #                         self.probability_array[i][j][rule_left_index] = \
        #                             self.__new_calculate_cell(parent_cell_probability, parent_cell_2_probability,
        #                                                       current_cell_probability, rule)
        #                         new_rule = sCellRule(rule, Coordinates(k, j), Coordinates(i - k - 1, j + k + 1))
        #                         self.rules_table[i][j].append(new_rule)
        #
        #         # Check if probability for cell found
        #         is_rule_occured = self.__find_if_non_terminal_or_start_rule_occured_in_cell(i, j)
        #         # Aggresive and final covering
        #         if not is_rule_occured and positive and \
        #                         self.__settings.get_value('covering', 'is_full_covering_allowed') == "True":
        #             self.__apply_aggressive_and_final_covering(i, j)


    def get_rules_from_rules_table(self):
        for i in range(len(self.rules_table)):
            print([str(rule[0].rule) if len(rule) > 0 else "-" for rule in self.rules_table[i]][0:len(self.rules_table)-i])
        print("\n\n")
        for i in range(len(self.rules_table)):
            print([str(rule[0].rule)+" (i: "+str(round(rule[0].inside, 4))+", o: "+str(round(rule[0].outside, 4))+")"
                   if len(rule) > 0 else "-" for rule in self.rules_table[i]][0:len(self.rules_table)-i])

    def is_parsed(self, result: float) -> bool:
        if result is None:
            return False
        # TODO: we use 0 in both cases, but originally it was two different settings
        if self.learning_on:
            parsing_threshold = self.parsing_threshold
        else:
            parsing_threshold = self.parsing_threshold
        self.__logger.debug("Result: {:.20f}. Parsing threshold: {:.10f}".format(result, parsing_threshold))
        return result > parsing_threshold

    def __init_cell(self, index: int, rule: sRule):
        rule_left_index = rule.left.index
        self.probability_array[0][index][rule_left_index] = ProbabilityArrayCell()
        if self.mode == "Viterbi":
            self.probability_array[0][index][rule_left_index].item_1 = math.log10(rule.probability)
        else:
            self.probability_array[0][index][rule_left_index].item_1 = rule.probability
        self.probability_array[0][index][rule_left_index].item_2 = rule.probability

    def __new_calculate_cell(self, parent_cell_prob: ProbabilityArrayCell, parent_cell_2_prob: ProbabilityArrayCell,
                             cell_prob: ProbabilityArrayCell, rule: Rule) -> ProbabilityArrayCell:
        if self.mode == "BaumWelch":
            cell_probability = self.__calculate_baum_welch_rule_cell_probability(cell_prob,
                                                                                 parent_cell_prob,
                                                                                 parent_cell_2_prob, rule)
        elif self.mode == "Viterbi":
            cell_probability = self.__calculate_viterbi_rule_cell_probability(cell_prob,
                                                           parent_cell_prob,
                                                           parent_cell_2_prob, rule)
        elif self.mode == "MinProb":
            cell_probability =  self.__calculate_min_prob_rule_cell_probability(cell_prob,
                                                            parent_cell_prob,
                                                            parent_cell_2_prob, rule)
        return cell_probability

    # TODO: remove completly
    def __calculate_cell(self, parent_cell_1: Coordinates,
                         parent_cell_2: Coordinates,
                         cell_coordinates: Coordinates,
                         rule: Rule):

        rule_left_index = rule.left.index
        rule_right_1_index = rule.right1.index
        rule_right_2_index = rule.right2.index
        cell_probability = self.probability_array[cell_coordinates.x][cell_coordinates.y][rule_left_index]
        parent_cell_1_probability = self.probability_array[parent_cell_1.x][parent_cell_1.y][rule_right_1_index]
        parent_cell_2_probability = self.probability_array[parent_cell_2.x][parent_cell_2.y][rule_right_2_index]

        if self.mode == "BaumWelch":
            cell_probability = self.__calculate_baum_welch_rule_cell_probability(cell_probability,
                                                                                 parent_cell_1_probability,
                                                                                 parent_cell_2_probability, rule)
        elif self.mode == "Viterbi":
            cell_probability = self.__calculate_viterbi_rule_cell_probability(cell_probability,
                                                           parent_cell_1_probability,
                                                           parent_cell_2_probability, rule)
        elif self.mode == "MinProb":
            cell_probability = self.__calculate_min_prob_rule_cell_probability(cell_probability,
                                                            parent_cell_1_probability,
                                                            parent_cell_2_probability, rule)
        self.probability_array[cell_coordinates.x][cell_coordinates.y][rule_left_index] = cell_probability

    def __calculate_baum_welch_rule_cell_probability(self, cell_probability: ProbabilityArrayCell,
                                                     parent_cell_1_probability: ProbabilityArrayCell,
                                                     parent_cell_2_probability: ProbabilityArrayCell,
                                                     rule: sRule) -> ProbabilityArrayCell:

        if cell_probability == self.default_value:
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

    def __calculate_viterbi_rule_cell_probability(self, cell_probability: ProbabilityArrayCell,
                                                  parent_cell_1_probability: ProbabilityArrayCell,
                                                  parent_cell_2_probability: ProbabilityArrayCell,
                                                  rule: sRule):
        if cell_probability == self.default_value:
            cell_probability = ProbabilityArrayCell()
            cell_probability.item_1 = math.log10(rule.probability) + \
                                      parent_cell_1_probability.item_1 * parent_cell_2_probability.item_1

            cell_probability.item_2 = (rule.probability *
                                       parent_cell_1_probability.item_2 *
                                       parent_cell_2_probability.item_2)

        else:
            cell_probability.item_1 = max(cell_probability.item_1, math.log10(parent_cell_1_probability.item_1 +
                                                                              parent_cell_2_probability.item_1))

            cell_probability.item_2 = cell_probability.item_2 + (rule.probability *
                                                                 parent_cell_1_probability.item_2 *
                                                                 parent_cell_2_probability.item_2)
        return cell_probability

    def __calculate_min_prob_rule_cell_probability(self, cell_probability: ProbabilityArrayCell,
                                                   parent_cell_1_probability: ProbabilityArrayCell,
                                                   parent_cell_2_probability: ProbabilityArrayCell,
                                                   rule: sRule):
        if cell_probability == self.default_value:
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

    def find_matching_rules_in_rules_container(self, i_index, j_index, given_symbol):
        """
        Finds all rules in the cell [i_index][j_index] which have the given symbol on the left side
        :param i_index:
        :param j_index:
        :param given_symbol:
        :return:
        """
        cellRules = []
        for i in range(len(self.rules_table[i_index][j_index])):
            cellRule: sCellRule = self.rules_table[i_index][j_index][i]
            if cellRule.rule.left == given_symbol:
                cellRules.append(cellRule)
        return cellRules

    def init_first_row(self, positive: bool):
        for i in range(len(self.sequence)):
            covering = None
            was = False
            # TODO: dictionary can fasten this search
            for rule in self.grammar.get_rules():
                if rule.right1 == self.sequence[i]:
                    was = True
                    self.__init_cell(i, rule)
                    rule.tmp_used = True
                    self.rules_table[0][i].append(sCellRule(rule))
            if not was and positive:
                if len(self.sequence) > 1:
                    covering = self.terminal_covering
                elif self.__settings.get_value('covering', 'is_start_covering_allowed') == "True":
                    covering = self.start_covering

                if covering is not None:
                    new_rule = covering.add_new_rule(self.grammar, self.sequence[i])
                    self.__generated_rules_count += 1
                    new_rule.tmp_used = True
                    self.__init_cell(i, new_rule)
                    self.rules_table[0][i].append(sCellRule(new_rule))
            self.cells_parsing_states_table[0][i] = True

    def __apply_aggressive_and_final_covering(self, i: int, j: int):
        """
        Performs aggressive or final covering on the given cell of the cyk table
        :param i:
        :param j:
        :return:
        """
        new_rule = None
        valid_combinations_of_indexes = []
        for m in range(i):
            tmp_symbols_1 = self.__get_cell_symbols(m, j)
            tmp_symbols_2 = self.__get_cell_symbols(i - m - 1, j + m + 1)
            if len(tmp_symbols_1) > 0 and len(tmp_symbols_2) > 0:
                valid_combinations_of_indexes.append(m)
        if len(valid_combinations_of_indexes) > 0:
            random = randint(0, len(valid_combinations_of_indexes) - 1)
            symbols_1 = self.__get_cell_symbols(valid_combinations_of_indexes[random], j)
            symbols_2 = self.__get_cell_symbols(i - valid_combinations_of_indexes[random] - 1,
                                                j + valid_combinations_of_indexes[random] + 1)
            index_1 = randint(0, len(symbols_1) - 1)
            index_2 = randint(0, len(symbols_2) - 1)
            if i is not len(self.sequence) - 1:
                if RandomUtils.make_random_decision_with_probability(
                        float(self.__settings.get_value('covering', 'aggressive_covering_probability'))):
                    covering = self.aggressive_covering
                    new_rule = covering.add_new_rule(self.grammar, symbols_1[index_1], symbols_2[index_2])
            elif self.__settings.get_value('covering', 'is_full_covering_allowed') == "True":
                covering = self.final_covering
                new_rule = covering.add_new_rule(self.grammar, symbols_1[index_1], symbols_2[index_2])
            if new_rule is not None:
                self.__generated_rules_count += 1
                new_rule.tmp_used = True
                new_cell_rule = sCellRule(new_rule, Coordinates(valid_combinations_of_indexes[random], j),
                                          Coordinates(i - valid_combinations_of_indexes[random] - 1,
                                                      j + valid_combinations_of_indexes[random] + 1))
                self.rules_table[i][j].append(new_cell_rule)
                self.__calculate_cell(Coordinates(valid_combinations_of_indexes[random], j),
                                      Coordinates(i - valid_combinations_of_indexes[random] - 1,
                                                  j + valid_combinations_of_indexes[random] + 1), Coordinates(i, j),
                                      new_rule)

    def __get_cell_symbols(self, i_index: int, j_index: int):
        """
        Find all non terminal rules which have assigned probability
        :param i_index:
        :param j_index:
        :return:
        """
        result = []
        for k in range(len(self.grammar.nonTerminalSymbols)):
            if self.probability_array[i_index][j_index][k] is not None:
                result.append(self.grammar.nonTerminalSymbols[k])
        return result

    def __find_if_non_terminal_or_start_rule_occured_in_cell(self, i_index: int, j_index) -> bool:
        """
        Checks whether in the cell [i][j] occured any of the non terminal rules or start rule
        :param i_index:
        :param j_index:
        :return:
        """
        if i_index != (len(self.sequence) - 1):
            for k in range(len(self.grammar.nonTerminalSymbols)):
                if self.probability_array[i_index][j_index][k] is not None:
                    return True
            return False
        else:
            return self.probability_array[i_index][j_index][self.grammar.get_start_symbol().index] is not None

    def __update_grammars_positives_and_negatives(self, is_result_parsed: bool, positive: bool):
        if is_result_parsed and positive:
            self.grammar.truePositive += 1
        elif not is_result_parsed and not positive:
            self.grammar.trueNegative += 1
        elif is_result_parsed and not positive:
            self.grammar.falsePositive += 1
        elif not is_result_parsed and positive:
            self.grammar.falseNegative += 1


    def __fill_usages_for_start_cell_rules(self, cyk_start_cell_rules, positive):
        """
        Check if the parsed sentence contains start symbol if so fill table usages
        :param cyk_start_cell_rules:
        :param positive:
        :return:
        """
        for i in range(len(cyk_start_cell_rules)):
            if cyk_start_cell_rules[i].rule.is_start():
                self.fill_rules_table_usages(cyk_start_cell_rules[i], positive)


