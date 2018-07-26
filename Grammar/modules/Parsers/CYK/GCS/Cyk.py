from modules.Covering.Covering import Covering
from modules.GCSBase.domain import Coordinates
from modules.GCSBase.domain.CellRule import CellRule
from random import randint
from modules.Parsers.CYK.Base.CYKBase import CYKBase


class Cyk(CYKBase):
    def __init__(self, settings):
        super().__init__(settings)
        self.max_value = True
        self.default_value = False
        self.covering = Covering()

    def calculate_cell(self, c1idx1, c1idx2, c2idx1, c2idx2, coidx1, coidx2, rule):
        left_index = rule.left.index
        right_1_index = rule.right1.index
        right_2_index = rule.right2.index
        self.probability_array[coidx1, coidx2, left_index] = self.probability_array[c1idx1, c1idx2, right_1_index] and self.probability_array[
            c2idx1, c2idx2, right_2_index]
        return 0.0

    def init_cell(self, index, rule):
        rule_index = self.grammar.find_non_terminal_symbol_index(rule.value)
        self.probability_array[0, index, rule_index] = True

    def get_result(self):
        result = self.default_value
        for i in range(len(self.grammar.nonTerminalSymbols)):
            if self.grammar.nonTerminalSymbols[i].is_start():
                if self.probability_array[len(self.sequence) - 1, 0, i] != self.default_value:
                    result = True
        return result

    def get_cell_symbols(self, index1, index2):
        result = []
        for k in range(len(self.grammar.nonTerminalSymbols)):
            if self.probability_array[index1][index2][k] == self.default_value:
                result.append(self.grammar.nonTerminalSymbols[k])
        return result

    def single_example_evaluation(self, sentence: str, grammar, positive: bool, learning_on: bool):
        self.grammar = grammar
        self.init_symbol_sequence(sentence)
        self.init_rules_table(self.default_value, sentence)
        for i in range(len(sentence)):
            was = False
            for rule in grammar.rules:
                if rule.right1 == self.sequence[1]:
                    was = True
                    self.init_cell(i, rule)
                    rule.tmp_used = True
                    self.rules_table[0, i].append(CellRule(rule))
            if not was and positive:
                if len(self.sequence) > 1 and self.__settings.isTerminalCoveringAllowed:
                    new_rule = self.covering.terminalCovering(grammar, self.sequence[i])
                    new_rule.tmp_used = True
                    self.init_cell(i, new_rule)
                    self.rules_table[0, i].append(CellRule(new_rule))
                elif self.__settings.isStartCoveringAllowed:
                    new_rule = self.covering.startCovering(grammar, self.sequence[i])
                    new_rule.tmp_used = True
                    self.init_cell(i, new_rule)
                    self.rules_table[0, i].append(CellRule(new_rule))
        # TODO: check ranges
        for i in range(1, len(self.sequence)):
            for j in range(0, len(self.sequence) - i):
                for k in range(i):
                    for rule in self.grammar.rules:
                        if rule.right2 is not None:
                            right_1_index = self.grammar.find_non_terminal_symbol_index(rule.right1.value)
                            right_2_index = self.grammar.find_non_terminal_symbol_index(rule.right2.value)
                            if self.probability_array[k, j, right_1_index] != self.default_value and \
                                            self.probability_array[k, j, right_2_index] != self.default_value:
                                rule.tmp_used = True
                                self.calculate_cell(k, j, i - k - 1, j + k + 1, i, j, rule)
                                self.rules_table[i][j].append(
                                    CellRule(rule, Coordinates(k, j), Coordinates(i - k - 1, j + k + 1)))
                    was = False
                    if i != len(self.sequence) - 1:
                        for k in range(len(grammar.nonTerminalSymbols)):
                            # TODO: check this condition
                            if self.probability_array[i][j][k] == self.default_value:
                                was = True
                    else:
                        start_symbol_index = grammar.find_non_terminal_symbol_index(grammar.start_symbol.value)
                        # TODO: check this condition
                        if self.probability_array[i, k, start_symbol_index] != self.default_value:
                            was = True
                    # Agresywne finalne pokrycie
                    if not was and positive:
                        newRule = None
                        valid_combination_indexes = []
                        # TODO: check range
                        for m in range(i):
                            random = randint(0, len(valid_combination_indexes))
                            symbols1 = self.get_cell_symbols(valid_combination_indexes[random], j)
                            symbols2 = self.get_cell_symbols(i - valid_combination_indexes[random],
                                                             j + valid_combination_indexes[random] + 1)
                            idx1 = randint(0, len(symbols1))
                            idx2 = randint(0, len(symbols2))
                            if i != len(self.sequence) - 1:
                                if self.throwADice():
                                    newRule = self.covering.AggressiveCovering(grammar, symbols1[idx1], symbols2[idx2]);
                            elif self.__settings.isFullCoveringAllowed:
                                newRule = self.covering.FinalCovering(grammar, symbols1[idx1], symbols2[idx2])
                            if newRule is not None:
                                newRule.tmp_used = True
                                self.rules_table[i][j].append(
                                    CellRule(newRule, Coordinates(valid_combination_indexes[random], j),
                                             Coordinates(i - valid_combination_indexes[random] - 1,
                                                         j + valid_combination_indexes[random] + 1)))
                                self.calculate_cell(valid_combination_indexes[random], j,
                                                    i - valid_combination_indexes[random] - 1,
                                                    j + valid_combination_indexes[random] + 1, i, j, newRule);
        result = self.get_result()
        for i in range(len(self.rules_table[len(self.sequence) - 1][0])):
            if self.rules_table[self.rules_table[len(self.sequence) - 1]][0].is_start():
                self.fill_rules_table_usages(self.rules_table[len(self.sequence) - 1][0][i], positive)
        evaluation = SingleExampleEvaluation()
        evaluation.m_param = result
        evaluation.m_parsed = result
        print(evaluation)
        evaluation.rules_table = self.rules_table

        return evaluation

