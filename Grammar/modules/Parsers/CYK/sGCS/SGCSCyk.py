import _pickle as pickle
import copy
import json
import logging
import math
import time
from random import randint

from py4j.java_gateway import JavaGateway

from modules.Covering.Covering import Covering
from modules.GCSBase.SingleExampleEvaluation import SingleExampleEvaluation
from modules.GCSBase.domain.Coordinates import Coordinates
from modules.GCSBase.utils.random_utils import RandomUtils
from modules.Parsers.CYK.sGCS.ProbabilityArrayCell import ProbabilityArrayCell
from modules.Stochastic.Stochastic import Stochastic
from modules.sGCS.domain.sCellRule import sCellRule
from modules.sGCS.domain.sRule import sRule
from modules.sGCS.sGCS_grammar import sGCSGrammar
from ..Base import CYKBase


class SGCSCyk(CYKBase.CYKBase):
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

    @property
    def Stochastic(self):
        return self.__Stochastic

    def cyk_result(self, sentence: str, grammar: sGCSGrammar, positive: bool,
                   learning_on: bool, covering_on: bool, negative_covering: bool) -> SingleExampleEvaluation:
        self.grammar = grammar
        self.parsing_sentence_rules = set()
        self.learning_on = learning_on
        self.__generated_rules_count = 0

        self.Stochastic.init_rules_inside_outside_probabilities(self)


        self._init_symbol_sequence(sentence)

        if self.settings.get_value('cyk', 'parsing_language') == 'Java':
            self.java_parse_sentence(sentence)
        else:
            self.parse_sentence(sentence, positive, covering_on, negative_covering)

        result = self.get_result()

        is_result_parsed = self.is_parsed(result, len(sentence))
        self.__logger.info('Sentence {0} parsed by cyk as positive: {1}.'.format(sentence, is_result_parsed))
        full_rules_table = copy.deepcopy(self.rules_table)
        cyk_start_cell_rules = self.rules_table[len(self.sequence) - 1][0]
        cyk_start_cell_rules_probability = self.probability_array[len(self.sequence) - 1][0]

        self.__fill_usages_for_start_cell_rules(cyk_start_cell_rules, positive, is_result_parsed)

        self._remove_unused_cell_rules(len(sentence))
        if self.settings.get_value('general', 'fitness_enabled') == 'True':
            self._fill_debts_profits(sentence, positive)

        prob = self.Stochastic.update_rules_count_after_sentence_parsing(self, learning_on, cyk_start_cell_rules,
                                                                         cyk_start_cell_rules_probability, positive)

        grammar.examples_probs.append(prob)
        self.__update_grammars_positives_and_negatives(is_result_parsed, positive)

        for rule in self.grammar.get_rules():
            rule.tmp_used = False
        if self.settings.get_value('general', 'visualization_enable') == 'True':
            sentence_parsing_data = (sentence, positive, pickle.loads(pickle.dumps(self.rules_table, -1)))
            self.grammar.iteration.sentence_rules_parsing_data.append(sentence_parsing_data)

        return self.__create_evaluation(sentence, result, full_rules_table, positive)

    def java_parse_sentence(self, sequence: str):
        json_grammar = self.grammar.save_to_json()
        gateway = JavaGateway()
        cyk = gateway.entry_point
        cyk_result = cyk.runCyk(sequence, json_grammar)

        result = json.loads(cyk_result)
        rt = result['rules_table']
        pt = result['probability_table']

        for i in range(len(sequence)):
            for j in range(len(sequence) - i):
                rules = []
                pts = []
                for rule in rt[i][j]['rules']:
                    rules.append(sCellRule.fromCellRuleDict(rule))
                rt[i][j] = rules
                for p in pt[i][j]:
                    if p['item_1'] != -1 and p['item_2'] != -1:
                        pts.append(ProbabilityArrayCell(p['item_1'], p['item_2']))
                    else:
                        pts.append(self.default_value)
                pt[i][j] = pts
        self.rules_table = rt
        self.probability_array = pt

        if self.learning_on:
            rules_to_add = result['rules_to_add']
            for cell_indexes in rules_to_add:
                self.__apply_aggressive_and_final_covering(cell_indexes['i'], cell_indexes['j'])

    def __create_evaluation(self, sentence, result: float, rules_table_copy, positive) -> SingleExampleEvaluation:
        return SingleExampleEvaluation(result, self.is_parsed(result, len(sentence)), self.rules_table, rules_table_copy, sentence, positive)

    def get_result(self) -> float:
        result = 0.0

        for i in range(len(self.grammar.nonTerminalSymbols)):
            if self.grammar.nonTerminalSymbols[i].is_start():
                if self.probability_array[len(self.sequence) - 1][0][i] != self.default_value:
                    if self.mode == "Viterbi":
                        res = 10 ** self.probability_array[len(self.sequence) - 1][0][i].item_1
                    else:
                        res = self.probability_array[len(self.sequence) - 1][0][i].item_1
                    result = result + res

        """
        for i in range(len(self.rules_table[len(self.sequence) - 1][0])):
            if self.rules_table[len(self.sequence) - 1][0][i].rule.is_start():
                if self.probability_array[len(self.sequence) - 1][0][i] != self.default_value:
                    if math.isinf(-result):
                        result = 0.0
                    result = result + self.probability_array[len(self.sequence) - 1][0][i].item_1
        """
        return result

    def parse_sentence(self, sequence: str, positive: bool, covering_on, negative_covering):

        self.__logger.info('Parsing sentence {0}. Belongs to grammar: {1}'.format(sequence, positive))

        sequence_length = len(sequence)
        self._init_probability_array(sequence_length, len(self.grammar.nonTerminalSymbols))
        self._init_rules_table(sequence_length)
        self.init_first_row(positive)

        s_time = time.time()
        # Iterate through upper triangle of the cyk matrix
        for i in self.iteration_generator(sequence_length):
            for j in self.iteration_generator(sequence_length - i):
                for k in self.iteration_generator(i):
                    for rule in self.grammar.get_rules():
                        if rule.right2 is not None:
                            first_rule_index = rule.right1.index
                            second_rule_index = rule.right2.index
                            if self.probability_array[k][j][first_rule_index] is not None \
                                    and self.probability_array[i - k - 1][j + k + 1][second_rule_index] is not None:
                                rule.tmp_used = True
                                rule_left_index = rule.left.index

                                parent_cell_probability = self.probability_array[k][j][first_rule_index]
                                parent_cell_2_probability = \
                                    self.probability_array[i - k - 1][j + k + 1][second_rule_index]
                                current_cell_probability = self.probability_array[i][j][rule_left_index]

                                self.probability_array[i][j][rule_left_index] = \
                                    self.__Stochastic.new_calculate_cell(self.mode, self.default_value, parent_cell_probability, parent_cell_2_probability,
                                                              current_cell_probability, rule)
                                new_rule = sCellRule(rule, Coordinates(k, j), Coordinates(i - k - 1, j + k + 1))
                                self.rules_table[i][j].append(new_rule)
                # Check if probability for cell found
                is_rule_occured = self.__find_if_non_terminal_or_start_rule_occured_in_cell(i, j)
                # Aggresive and final covering
                if not is_rule_occured and positive and covering_on and \
                                self.settings.get_value('covering', 'is_full_covering_allowed') == "True":
                    self.__apply_aggressive_and_final_covering(i, j)

    def get_rules_from_rules_table(self):
        # for i in range(len(self.rules_table)):
        #     print(["/".join([crule[i].rule.short() for i in range(len(crule))])
        #            if len(crule) > 0 else "-" for crule in self.rules_table[i]][0:len(self.rules_table) - i])
        # print("\n")
        # for i in range(len(self.rules_table)):
        #     print(["/".join([str(crule[i].rule.probability) for i in range(len(crule))])
        #            if len(crule) > 0 else "-" for crule in self.rules_table[i]][0:len(self.rules_table) - i])
        pass

    def is_parsed(self, result: float, l) -> bool:
        if result is None:
            return False

        parsing_threshold = self.parsing_threshold
        self.__logger.debug("Result: {:.20f}. Parsing threshold: {:.10f}".format(result, parsing_threshold))

        if self.settings.get_value("sgcs", "scaled_treshold")  == "True":
            new_result = result ** (1/l)
        else:
            new_result = result

        return new_result > parsing_threshold

    def __init_cell(self, index: int, rule: sRule):
        rule_left_index = rule.left.index
        self.probability_array[0][index][rule_left_index] = ProbabilityArrayCell()
        if self.mode == "Viterbi":
            self.probability_array[0][index][rule_left_index].item_1 = math.log10(rule.probability)
        else:
            self.probability_array[0][index][rule_left_index].item_1 = rule.probability
        self.probability_array[0][index][rule_left_index].item_2 = rule.probability




    @staticmethod
    def find_matching_rules_in_rules_container(rules_table, i_index, j_index, given_symbol):
        """
        Finds all rules in the cell [i_index][j_index] which have the given symbol on the left side
        :param i_index:
        :param j_index:
        :param given_symbol:
        :return:
        """
        cellRules = []
        for i in range(len(rules_table[i_index][j_index])):
            cellRule: sCellRule = rules_table[i_index][j_index][i]
            if cellRule.rule.left.index == given_symbol.index:
                cellRules.append(cellRule)
        return cellRules

    def init_first_row(self, positive: bool):
        for i in self.iteration_generator(len(self.sequence)):
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

    def __apply_aggressive_and_final_covering(self, i: int, j: int):
        """
        Performs aggressive or final covering on the given cell of the cyk table
        :param i:
        :param j:
        :return:
        """
        new_rule = None
        valid_combinations_of_indexes = []
        for m in self.iteration_generator(i):
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
            # print("Need rule: {}". format(symbols_1[index_1], symbols_2[index_2]))
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
                self.__Stochastic.calculate_cell(self.mode, self.default_value, self.probability_array, Coordinates(valid_combinations_of_indexes[random], j),
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

    def __fill_usages_for_start_cell_rules(self, cyk_start_cell_rules, positive, is_result_parsed):
        """
        Check if the parsed sentence contains start symbol if so fill table usages
        :param cyk_start_cell_rules:
        :param positive:
        :return:
        """
        for i in range(len(cyk_start_cell_rules)):
            if cyk_start_cell_rules[i].rule.is_start():
                self.fill_rules_table_usages(cyk_start_cell_rules[i], positive, is_result_parsed)

        for r in self.grammar.get_rules():
            if positive:
                r.usage_in_distinct_proper += r in self.parsing_sentence_rules
                if is_result_parsed:
                    r.usage_in_distinct_proper_parsed += r in self.parsing_sentence_rules
            elif not positive:
                r.usage_in_distinct_invalid += r in self.parsing_sentence_rules
                if is_result_parsed:
                    r.usage_in_distinct_invalid_parsed += r in self.parsing_sentence_rules

    def get_coords(self, x):
        # print(x.rule)
        cell1 = [x.cell_1_coordinates.x, x.cell_1_coordinates.y]
        cell2 = [x.cell_2_coordinates.x, x.cell_2_coordinates.y]
        rules_cell1 = [r.rule.short() for r in self.rules_table[cell1[0]][cell1[1]]]
        rules_cell2 = [r.rule.short() for r in self.rules_table[cell2[0]][cell2[1]]]
        return [rules_cell1, rules_cell2]
