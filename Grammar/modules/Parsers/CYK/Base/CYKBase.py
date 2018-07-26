import logging
from modules.Covering.Covering import Covering
from modules.GCSBase.domain.CellRule import CellRule
from modules.GCSBase.grammar.grammar import Grammar
from modules.GCSBase.utils.symbol_utils import SymbolFinder


class CYKBase:
    def __init__(self, grammar: Grammar, default_value, settings,
                 start_covering: Covering = None, final_covering: Covering = None,
                 aggressive_covering: Covering = None, terminal_covering: Covering = None):
        self.__logger = logging.getLogger("cyk_base")
        self.probability_array = None
        self.sequence = None
        self.rules_table = None
        self.grammar = grammar
        self._settings = settings
        self.default_value = default_value
        self.start_covering = start_covering
        self.final_covering = final_covering
        self.aggressive_covering = aggressive_covering
        self.terminal_covering = terminal_covering


        if settings is not None:
            self.__base_amount = float(self._settings.get_value('rules', 'base_amount'))
            self.__base_amount_reduction_coefficient = float(
                self._settings.get_value('rules', 'base_amount_reduction_coefficient'))

    def _init_rules_table(self, sentence_length: int):
        """
        Initilise rules table for storing values which can be placed in the cyk table at tab[i][j]
        :param sentence_length:
        :return:
        """
        self.rules_table = [[[] for i in range(sentence_length)] for j in range(sentence_length)]

    def _init_probability_array(self, sentence_length: int, non_terminal_symbols_length: int):
        """
        Initialise probability array of length [n][n][k] where n is the given sentence length
        and k is the non terminal symbols count
        """
        self.probability_array = [[[self.default_value for i in range(non_terminal_symbols_length)]
                                   for j in range(sentence_length)]
                                  for k in range(sentence_length)]

    def _init_symbol_sequence(self, sentence: str):
        """
        Fill the sequence array with the symbols found by the value of every character in the sentence
        :param sentence: string
        """
        self.sequence = [None] * len(sentence)
        for i in range(len(sentence)):
            self.sequence[i] = SymbolFinder.find_symbol_by_char(self.grammar.terminalSymbols, sentence[i])

    def fill_rules_table_usages(self, current_cell: CellRule, positive: bool):
        """
        :param current_cell:
        :param positive:
        :return:
        """
        cell_rules_to_analyse = [current_cell]
        it_count = 1
        while len(cell_rules_to_analyse) > 0:
            new_cell_rules = []
            for cell_rule in cell_rules_to_analyse:
                # Check if the rule have already been used in parsing
                if cell_rule.used_in_parsing:
                    continue
                # If not update rule's parameters
                cell_rule.called_number += 1
                cell_rule.used_in_parsing = True
                if positive:
                    #self.__logger.info(str(cell_rule.rule) + " usages in proper parsing + 1")
                    cell_rule.rule.usages_in_proper_parsing += 1
                else:
                    #self.__logger.info(str(cell_rule.rule) + " usages in invalid parsing + 1")
                    cell_rule.rule.usages_in_invalid_parsing += 1

                # Check rule parents and add them to analysis if they exists
                if cell_rule.cell_1_coordinates is not None:
                    c1x = cell_rule.cell_1_coordinates.x
                    c1y = cell_rule.cell_1_coordinates.y
                    right1 = cell_rule.rule.right1
                    count_1 = len(self.rules_table[c1x][c1y])
                    for i in range(count_1):
                        if self.rules_table[c1x][c1y][i].rule.left == right1:
                            new_cell_rules.append(self.rules_table[c1x][c1y][i])
                if cell_rule.cell_2_coordinates is not None:
                    c2x = cell_rule.cell_2_coordinates.x
                    c2y = cell_rule.cell_2_coordinates.y
                    right2 = cell_rule.rule.right2
                    count_2 = len(self.rules_table[c2x][c2y])
                    for i in range(count_2):
                        if self.rules_table[c2x][c2y][i].rule.left == right2:
                            new_cell_rules.append(self.rules_table[c2x][c2y][i])
            cell_rules_to_analyse = new_cell_rules
            it_count += 1

    def _remove_unused_cell_rules(self, sentence_length: int):
        """
        Removes every rule which has not been used in parsing
        :param sentence_length:
        """
        for i in range(sentence_length):
            for j in range(sentence_length):
                for k in reversed(range(len(self.rules_table[i][j]))):
                    if not self.rules_table[i][j][k].used_in_parsing:
                        self.rules_table[i][j].pop(k)

    def _fill_debts_profits(self, sentence: str, positive: bool):
        sentence_length = len(sentence)
        self.init_rules_value(sentence_length)
        self.__compute_rules_values()
        self.update_rule_profit_and_debt(positive)

    def init_rules_value(self, sentence_length: int):
        """
        Initiates the base amount of the first row of rules table
        :param sentence_length: length of the given sentence
        :return:
        """
        for i in range(sentence_length):
            for j in range(len(self.rules_table[0][i])):
                self.rules_table[0][i][j].tmp_val = self.__base_amount

    def __compute_rules_values(self):
        """
        For each cell in upper triangle of the cyk matrix iterates through the rules it contains and
        possible parents of the cell[i][j]. If the parents [k][j] and [i - k -1][j + k + 1]
        both matches the rule it updates it's temporary value.
        :return:
        """
        # For each cell in upper triangle of the cyk table
        for i in range(1, len(self.sequence)):
            for j in range(len(self.sequence) - i):
                for k in range(i):
                    # for each rule in the cell [i][j]
                    for cell_rule_index in range(len(self.rules_table[i][j])):
                        parent_1 = -1
                        parent_2 = -1
                        # Check each rule in the first possible parent of the cell
                        for parent_rule_index in range(len(self.rules_table[k][j])):
                            # Check whether the rule right 1 symbol can be created from checked parent rule
                            if self.rules_table[k][j][parent_rule_index].rule.left.value == \
                                    self.rules_table[i][j][cell_rule_index].rule.right1.value:
                                parent_1 = parent_rule_index

                        # Check each rule in the second posible parent of the cell
                        for parent_rule_index in range(len(self.rules_table[i - k - 1][j + k + 1])):
                            # Check whether the rule right 2 (if exists) can be be created from checked parent rule
                            if self.rules_table[i][j][cell_rule_index].rule.right2 is not None and \
                                            self.rules_table[i - k - 1][j + k + 1][parent_rule_index].rule.left.value \
                                            == self.rules_table[i][j][cell_rule_index].rule.right2.value:
                                parent_2 = parent_rule_index

                        # If both parents exists
                        if parent_1 != -1 and parent_2 != -1:
                            #self.__logger.info("Patents indexes: [{0}][{1}]".format(parent_1, parent_2))
                            self.rules_table[i][j][cell_rule_index].tmp_val = \
                                self.__compute_new_tmp_value(self.rules_table[k][j][parent_1],
                                                             self.rules_table[i - k - 1][j + k + 1][parent_2])

    def __compute_new_tmp_value(self, cell_rule_1: CellRule, cell_rule_2: CellRule) -> float:
        """
        Takes the temporary values of the rule parents and calculates new temporaty value
        :param cell_rule_1: First parent of the checked rule
        :param cell_rule_2: Second parent of the checked rule
        :return:
        """
        return cell_rule_1.tmp_val * self.__base_amount_reduction_coefficient \
            + cell_rule_2.tmp_val * self.__base_amount_reduction_coefficient

    def update_rule_profit_and_debt(self, positive: bool):
        """
        Updated each rule profit and debt
        :param positive:
        :return:
        """
        for i in range(len(self.sequence)):
            for j in range(len(self.sequence)):
                for k in range(len(self.rules_table[i][j])):
                    if positive is True:
                        self.rules_table[i][j][k].rule.profit += self.rules_table[i][j][k].tmp_val
                    else:
                        self.rules_table[i][j][k].rule.debt += self.rules_table[i][j][k].tmp_val
