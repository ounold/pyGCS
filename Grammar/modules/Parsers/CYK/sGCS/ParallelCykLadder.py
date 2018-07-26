import math
from multiprocessing import Lock, Pool
from random import randint

from modules.Crowding.crowding import Crowding
from modules.GCSBase.SingleExampleEvaluation import SingleExampleEvaluation
from modules.GCSBase.domain import Rule
from modules.GCSBase.domain.CellRule import CellRule
from modules.GCSBase.domain.Coordinates import Coordinates
from modules.GCSBase.domain.symbol import Symbol
from modules.GCSBase.utils.random_utils import RandomUtils
from modules.GCSBase.utils.symbol_utils import SymbolFinder
from modules.Parsers.CYK.Base.RulesTableCell import RulesTableCell
from modules.Parsers.CYK.sGCS.CykValues import CykValues
from modules.Parsers.CYK.sGCS.ProbabilityArrayCell import ProbabilityArrayCell
from modules.Visualisation.iteration import Iteration
from modules.sGCS.domain.sCellRule import sCellRule
from modules.sGCS.domain.sRule import sRule
from modules.sGCS.sGCS_grammar import sGCSGrammar
from settings.settings import Settings

lock = Lock()


def cyk_result_ladder(sentence: str, grammar: sGCSGrammar, is_sentence_positive: bool, is_learning_on: bool,
               settings: Settings, crowding: Crowding, iteration: Iteration = None):
    cyk_values = CykValues(grammar, is_learning_on, sentence, settings, crowding, iteration)
    __init_probability_array(cyk_values)
    __init_symbols_sequence(cyk_values)
    __init_rules_table(cyk_values)
    __init_first_row(cyk_values, is_sentence_positive, settings)
    __parse_sentence(cyk_values)
    result = __get_result(cyk_values)
    cyk_values.is_parsed = __is_parsed(result, is_learning_on, settings)
    cyk_start_cell_rules = cyk_values.rules_table[len(sentence) - 1][0].cell_rules
    cyk_start_cell_rules_probability = cyk_values.probability_array[len(cyk_values.sequence) - 1][0]
    __fill_usages_for_start_cell_rules(cyk_values, cyk_start_cell_rules, is_sentence_positive)
    __remove_unused_cell_rules(cyk_values)
    __fill_debts_profits(cyk_values, is_sentence_positive, settings)
    __update_rules_count_after_sentence_parsing(cyk_values, is_learning_on, cyk_start_cell_rules,
                                                cyk_start_cell_rules_probability, is_sentence_positive, settings)
    __update_grammars_positives_and_negatives(cyk_values, cyk_values.is_parsed, is_sentence_positive)

    for rule in cyk_values.grammar.get_rules():
        rule.tmp_used = False

    return __create_evaluation(cyk_values, sentence, result)


def __init_rules_probabilities(cyk_values: CykValues):
    for rule in cyk_values.grammar.get_rules():
        rule: sRule = rule
        rule.sum_inside_outside_usage_probability = 0.0
        rule.positive_sum_inside_outside_usages = 0.0
        rule.negative_sum_inside_outside_usages = 0.0


def __init_probability_array(cyk_values: CykValues):
    cyk_values.probability_array = [
        [[cyk_values.default_value for i in range(len(cyk_values.grammar.nonTerminalSymbols))]
         for j in range(len(cyk_values.sentence))]
        for k in range(len(cyk_values.sentence))]


def __init_symbols_sequence(cyk_values: CykValues):
    cyk_values.sequence = [None] * len(cyk_values.sentence)
    for i in range(len(cyk_values.sentence)):
        cyk_values.sequence[i] = SymbolFinder.find_symbol_by_char(cyk_values.grammar.terminalSymbols,
                                                                  cyk_values.sentence[i])


def __init_rules_table(cyk_values: CykValues):
    cyk_values.rules_table = [[RulesTableCell() for i in range(len(cyk_values.sentence))] for j in range(len(cyk_values.sentence))]


def __init_first_row(cyk_values: CykValues, is_sentence_positive: bool, settings: Settings):
    for i in range(len(cyk_values.sequence)):
        covering = None
        was = False
        # TODO: dictionary can fasten this search
        for rule in cyk_values.grammar.get_rules():
            if rule.right1 == cyk_values.sequence[i]:
                rule: sRule = rule
                was = True
                __init_cell(cyk_values, i, rule)
                rule.tmp_used = True
                cyk_values.rules_table[0][i].cell_rules.append(sCellRule(rule))
        if not was and is_sentence_positive:
            if len(cyk_values.sequence) > 1:
                covering = cyk_values.terminal_covering
            elif settings.get_value('covering', 'is_start_covering_allowed') == "True":
                covering = cyk_values.start_covering

            if covering is not None:
                new_rule = covering.add_new_rule(cyk_values.grammar, cyk_values.sequence[i])
                new_rule.tmp_used = True
                __init_cell(cyk_values, i, new_rule)
                cyk_values.rules_table[0][i].cell_rules.append(sCellRule(new_rule))
        cyk_values.rules_table[0][i].parsed = True


def __init_cell(cyk_values: CykValues, index: int, rule: sRule):
    rule_left_index = rule.left.index
    cyk_values.probability_array[0][index][rule_left_index] = ProbabilityArrayCell()
    if cyk_values.mode == "Viterbi":
        cyk_values.probability_array[0][index][rule_left_index].item_1 = math.log10(rule.probability)
    else:
        cyk_values.probability_array[0][index][rule_left_index].item_1 = rule.probability
        cyk_values.probability_array[0][index][rule_left_index].item_2 = rule.probability


def __parse_sentence(cyk_values: CykValues):
    sequence_length = len(cyk_values.sentence)
    if sequence_length != 1:
        pool = Pool(sequence_length - 1)
        job_args = [(cyk_values, j) for j in range(0, sequence_length - 1)]
        pool.starmap(__compute_rule, job_args)
        pool.close()
        pool.join()


def __compute_rule(cyk_values: CykValues, j: int):

    i = 1

    while j + i < len(cyk_values.sentence):
        for rule in cyk_values.grammar.get_rules():
            for k in range(i):
                if rule.right2 is not None:
                    first_rule_index = rule.right1.index
                    second_rule_index = rule.right2.index

                    while not cyk_values.rules_table[k][j].parsed \
                            and not cyk_values.rules_table[i - k - 1][j + k + 1].parsed:
                        continue

                    if cyk_values.probability_array[k][j][first_rule_index] is not None \
                            and cyk_values.probability_array[i - k - 1][j + k + 1][second_rule_index] is not None:
                        rule.tmp_used = True
                        rule_left_index = rule.left.index

                        parent_cell_probability = cyk_values.probability_array[k][j][first_rule_index]
                        parent_cell_2_probability = cyk_values.probability_array[i - k - 1][j + k + 1][
                            second_rule_index]
                        current_cell_probability = cyk_values.probability_array[i][j][rule_left_index]

                        cyk_values.probability_array[i][j][rule_left_index] = \
                            __calculate_cell(cyk_values, parent_cell_probability, parent_cell_2_probability,
                                             current_cell_probability, rule)
                        new_rule = sCellRule(rule, Coordinates(k, j), Coordinates(i - k - 1, j + k + 1))

                        lock.acquire()
                        cyk_values.rules_table[i][j].cell_rules.append(new_rule)
                        lock.release()
        cyk_values.rules_table[i][j].parsed = True
        i = i + 1


def __calculate_cell(cyk_values: CykValues, parent_cell_prob: ProbabilityArrayCell,
                     parent_cell_2_prob: ProbabilityArrayCell,
                     cell_prob: ProbabilityArrayCell, rule: Rule) -> ProbabilityArrayCell:
    if cyk_values.mode == "BaumWelch":
        cell_probability = __calculate_baum_welch_rule_cell_probability(cyk_values.default_value, cell_prob,
                                                                        parent_cell_prob,
                                                                        parent_cell_2_prob, rule)
    elif cyk_values.mode == "Viterbi":
        cell_probability = __calculate_viterbi_rule_cell_probability(cyk_values.default_value, cell_prob,
                                                                     parent_cell_prob,
                                                                     parent_cell_2_prob, rule)
    elif cyk_values.mode == "MinProb":
        cell_probability = __calculate_min_prob_rule_cell_probability(cyk_values.default_value, cell_prob,
                                                                      parent_cell_prob,
                                                                      parent_cell_2_prob, rule)
    return cell_probability


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


def __calculate_viterbi_rule_cell_probability(default_value, cell_probability: ProbabilityArrayCell,
                                              parent_cell_1_probability: ProbabilityArrayCell,
                                              parent_cell_2_probability: ProbabilityArrayCell,
                                              rule: sRule):
    if cell_probability == default_value:
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


def __find_if_non_terminal_or_start_rule_occured_in_cell(cyk_values: CykValues, i_index: int, j_index) -> bool:
    """
    Checks whether in the cell [i][j] occured any of the non terminal rules or start rule
    :param i_index:
    :param j_index:
    :return:
    """
    if i_index != (len(cyk_values.sequence) - 1):
        for k in range(len(cyk_values.grammar.nonTerminalSymbols)):
            if cyk_values.probability_array[i_index][j_index][k] is not None:
                return True
        return False
    else:
        return cyk_values.probability_array[i_index][j_index][cyk_values.grammar.get_start_symbol().index] is not None


def __apply_aggressive_and_final_covering(cyk_values: CykValues, i: int, j: int):
    """
    Performs aggressive or final covering on the given cell of the cyk table
    :param i:
    :param j:
    :return:
    """
    new_rule = None
    valid_combinations_of_indexes = []
    for m in range(i):
        tmp_symbols_1 = __get_cell_symbols(cyk_values, m, j)
        tmp_symbols_2 = __get_cell_symbols(cyk_values, i - m - 1, j + m + 1)
        if len(tmp_symbols_1) > 0 and len(tmp_symbols_2) > 0:
            valid_combinations_of_indexes.append(m)
    if len(valid_combinations_of_indexes) > 0:
        random = randint(0, len(valid_combinations_of_indexes) - 1)
        symbols_1 = __get_cell_symbols(cyk_values, valid_combinations_of_indexes[random], j)
        symbols_2 = __get_cell_symbols(cyk_values, i - valid_combinations_of_indexes[random] - 1,
                                       j + valid_combinations_of_indexes[random] + 1)
        index_1 = randint(0, len(symbols_1) - 1)
        index_2 = randint(0, len(symbols_2) - 1)
        if i is not len(cyk_values.sequence) - 1:
            if RandomUtils.make_random_decision_with_probability(
                    float(cyk_values.settings.get_value('covering', 'aggressive_covering_probability'))):
                covering = cyk_values.aggressive_covering
                new_rule = covering.add_new_rule(cyk_values.grammar, symbols_1[index_1], symbols_2[index_2])
        elif cyk_values.settings.get_value('covering', 'is_full_covering_allowed') == "True":
            covering = cyk_values.final_covering
            new_rule = covering.add_new_rule(cyk_values.grammar, symbols_1[index_1], symbols_2[index_2])
        if new_rule is not None:
            new_rule.tmp_used = True
            new_cell_rule = sCellRule(new_rule, Coordinates(valid_combinations_of_indexes[random], j),
                                      Coordinates(i - valid_combinations_of_indexes[random] - 1,
                                                  j + valid_combinations_of_indexes[random] + 1))
            cyk_values.rules_table[i][j].cell_rules.append(new_cell_rule)
            __calculate_cell(cyk_values, cyk_values.probability_array[valid_combinations_of_indexes[random]][j][
                new_rule.right1.index],
                             cyk_values.probability_array[i - valid_combinations_of_indexes[random] - 1][
                                 j + valid_combinations_of_indexes[random] + 1][new_rule.right2.index],
                             cyk_values.probability_array[i][j][new_rule.left.index],
                             new_rule)


def __get_cell_symbols(cyk_values: CykValues, i_index: int, j_index: int):
    """
    Find all non terminal rules which have assigned probability
    :param i_index:
    :param j_index:
    :return:
    """
    result = []
    for k in range(len(cyk_values.grammar.nonTerminalSymbols)):
        if cyk_values.probability_array[i_index][j_index][k] is not None:
            result.append(cyk_values.grammar.nonTerminalSymbols[k])
    return result


def __get_result(cyk_values: CykValues) -> float:
    if cyk_values.mode == 'Viterbi':
        result = -math.inf
    else:
        result = 0.0
    for i in range(len(cyk_values.grammar.nonTerminalSymbols)):
        if cyk_values.grammar.nonTerminalSymbols[i].is_start():
            if cyk_values.probability_array[len(cyk_values.sequence) - 1][0][i] != cyk_values.default_value:
                if math.isinf(-result):
                    result = 0.0
                result = result + cyk_values.probability_array[len(cyk_values.sequence) - 1][0][i].item_1
    return result


def __is_parsed(result: float, is_learing_on: bool, settings: Settings):
    if result is None:
        return False
    # TODO: we use 0 in both cases, but originally it was two different settings
    if is_learing_on:
        parsing_threshold = float(settings.get_value('sgcs', 'parsing_threshold'))
    else:
        parsing_threshold = float(settings.get_value('sgcs', 'parsing_threshold'))
    return result > parsing_threshold


def __fill_usages_for_start_cell_rules(cyk_values: CykValues, cyk_start_cell_rules, positive):
    """
    Check if the parsed sentence contains start symbol if so fill table usages
    :param cyk_start_cell_rules:
    :param positive:
    :return:
    """
    for i in range(len(cyk_start_cell_rules)):
        if cyk_start_cell_rules[i].rule.is_start():
            __fill_rules_table_usages(cyk_values, cyk_start_cell_rules[i], positive)


def __fill_rules_table_usages(cyk_values: CykValues, current_cell: CellRule, positive: bool):
    """
    :param current_cell:
    :param positive:
    :return:
    """
    cell_rules_to_analyse = [current_cell]
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
                # self.__logger.info(str(cell_rule.rule) + " usages in proper parsing + 1")
                cell_rule.rule.usages_in_proper_parsing += 1
            else:
                # self.__logger.info(str(cell_rule.rule) + " usages in invalid parsing + 1")
                cell_rule.rule.usages_in_invalid_parsing += 1

            # Check rule parents and add them to analysis if they exists
            if cell_rule.cell_1_coordinates is not None:
                c1x = cell_rule.cell_1_coordinates.x
                c1y = cell_rule.cell_1_coordinates.y
                right1 = cell_rule.rule.right1
                count_1 = len(cyk_values.rules_table[c1x][c1y].cell_rules)
                for i in range(count_1):
                    if cyk_values.rules_table[c1x][c1y].cell_rules[i].rule.left == right1:
                        new_cell_rules.append(cyk_values.rules_table[c1x][c1y].cell_rules[i])
            if cell_rule.cell_2_coordinates is not None:
                c2x = cell_rule.cell_2_coordinates.x
                c2y = cell_rule.cell_2_coordinates.y
                right2 = cell_rule.rule.right2
                count_2 = len(cyk_values.rules_table[c2x][c2y].cell_rules)
                for i in range(count_2):
                    if cyk_values.rules_table[c2x][c2y].cell_rules[i].rule.left == right2:
                        new_cell_rules.append(cyk_values.rules_table[c2x][c2y].cell_rules[i])
        cell_rules_to_analyse = new_cell_rules


def __remove_unused_cell_rules(cyk_values: CykValues):
    """
    Removes every rule which has not been used in parsing
    :param sentence_length:
    """
    sentence_length = len(cyk_values.sentence)
    for i in range(sentence_length):
        for j in range(sentence_length):
            for k in reversed(range(len(cyk_values.rules_table[i][j].cell_rules))):
                if not cyk_values.rules_table[i][j].cell_rules[k].used_in_parsing:
                    cyk_values.rules_table[i][j].cell_rules.pop(k)


def __fill_debts_profits(cyk_values: CykValues, is_sentence_positive: bool, settings: Settings):
    __init_rules_value(cyk_values, settings)
    __compute_rules_values(cyk_values)
    __update_rule_profit_and_debt(cyk_values, is_sentence_positive)


def __init_rules_value(cyk_values: CykValues, settings: Settings):
    """
    Initiates the base amount of the first row of rules table
    :param sentence_length: length of the given sentence
    :return:
    """
    for i in range(len(cyk_values.sentence)):
        for j in range(len(cyk_values.rules_table[0][i].cell_rules)):
            cyk_values.rules_table[0][i].cell_rules[j].tmp_val = float(settings.get_value('rules', 'base_amount'))


def __compute_rules_values(cyk_values: CykValues):
    """
    For each cell in upper triangle of the cyk matrix iterates through the rules it contains and
    possible parents of the cell[i][j]. If the parents [k][j] and [i - k -1][j + k + 1]
    both matches the rule it updates it's temporary value.
    :return:
    """
    # For each cell in upper triangle of the cyk table
    for i in range(1, len(cyk_values.sequence)):
        for j in range(len(cyk_values.sequence) - i):
            for k in range(i):
                # for each rule in the cell [i][j]
                for cell_rule_index in range(len(cyk_values.rules_table[i][j].cell_rules)):
                    parent_1 = -1
                    parent_2 = -1
                    # Check each rule in the first possible parent of the cell
                    for parent_rule_index in range(len(cyk_values.rules_table[k][j].cell_rules)):
                        # Check whether the rule right 1 symbol can be created from checked parent rule
                        if cyk_values.rules_table[k][j].cell_rules[parent_rule_index].rule.left.value == \
                                cyk_values.rules_table[i][j].cell_rules[cell_rule_index].rule.right1.value:
                            parent_1 = parent_rule_index

                    # Check each rule in the second posible parent of the cell
                    for parent_rule_index in range(len(cyk_values.rules_table[i - k - 1][j + k + 1].cell_rules)):
                        # Check whether the rule right 2 (if exists) can be be created from checked parent rule
                        if cyk_values.rules_table[i][j].cell_rules[cell_rule_index].rule.right2 is not None and \
                                cyk_values.rules_table[i - k - 1][j + k + 1].cell_rules[parent_rule_index].rule.left.value \
                                == cyk_values.rules_table[i][j].cell_rules[cell_rule_index].rule.right2.value:
                            parent_2 = parent_rule_index

                    # If both parents exists
                    if parent_1 != -1 and parent_2 != -1:
                        cyk_values.rules_table[i][j].cell_rules[cell_rule_index].tmp_val = \
                            __compute_new_tmp_value(cyk_values.rules_table[k][j].cell_rules[parent_1],
                                                    cyk_values.rules_table[i - k - 1][j + k + 1].cell_rules[parent_2],
                                                    cyk_values.settings)


def __compute_new_tmp_value(cell_rule_1: CellRule, cell_rule_2: CellRule, settings: Settings) -> float:
    """
    Takes the temporary values of the rule parents and calculates new temporaty value
    :param cell_rule_1: First parent of the checked rule
    :param cell_rule_2: Second parent of the checked rule
    :return:
    """
    return cell_rule_1.tmp_val * float(
        settings.get_value('rules', 'base_amount_reduction_coefficient')) \
           + cell_rule_2.tmp_val * float(
        settings.get_value('rules', 'base_amount_reduction_coefficient'))


def __update_rule_profit_and_debt(cyk_values: CykValues, positive: bool):
    """
    Updated each rule profit and debt
    :param positive:
    :param cyk_values
    :return:
    """
    for i in range(len(cyk_values.sequence)):
        for j in range(len(cyk_values.sequence)):
            for k in range(len(cyk_values.rules_table[i][j].cell_rules)):
                if positive is True:
                    cyk_values.rules_table[i][j].cell_rules[k].rule.profit += cyk_values.rules_table[i][j].cell_rules[k].tmp_val
                else:
                    cyk_values.rules_table[i][j].cell_rules[k].rule.debt += cyk_values.rules_table[i][j].cell_rules[k].tmp_val


def __update_rules_count_after_sentence_parsing(cyk_values: CykValues, learning_on: bool, cyk_start_cell_rules,
                                                cyk_start_cell_rules_probability, positive: bool, settings: Settings):
    if learning_on and settings.get_value('covering', 'is_terminal_covering_allowed') == "True":
        sentence_probability = __calculate_sentence_probability(cyk_values, cyk_start_cell_rules,
                                                                cyk_start_cell_rules_probability, positive)
        for rule in cyk_values.grammar.get_rules():
            rule: sRule = rule
            rule.calculate_counts(sentence_probability)


def __calculate_sentence_probability(cyk_values: CykValues, cyk_start_cell_rules, cyk_start_cell_rules_probabilities,
                                     positive):
    __calculate_inside_probabilities(cyk_values)
    start_cell_rules = []
    for i in range(len(cyk_start_cell_rules)):
        if cyk_start_cell_rules[i].rule.is_start():
            start_cell_rules.append(cyk_start_cell_rules[i])
    __calculate_outside_probabilities(cyk_values, start_cell_rules)

    start_cell_rules = []
    for i in range(len(cyk_values.rules_table[len(cyk_values.sequence) - 1][0].cell_rules)):
        if cyk_start_cell_rules[i].rule.is_start():
            start_cell_rules.append(cyk_start_cell_rules[i])
    __count(cyk_values, start_cell_rules, positive)

    sentence_probability: float = 0.0
    for i in range(len(cyk_values.grammar.nonTerminalSymbols)):
        if cyk_values.grammar.nonTerminalSymbols[i].is_start():
            if cyk_start_cell_rules_probabilities[i] is not cyk_values.default_value:
                sentence_probability += cyk_start_cell_rules_probabilities[i].item_2
    return sentence_probability


def __calculate_inside_probabilities(cyk_values: CykValues):
    for i in range(len(cyk_values.sequence)):
        for j in range(len(cyk_values.sequence)):
            for cell_rule in cyk_values.rules_table[i][j].cell_rules:
                try:
                    cell_rule.inside = cyk_values.probability_array[i][j][cell_rule.rule.left.index].item_2
                except:
                    print("i = {}, j = {}".format(i, j))


def __count(cyk_values: CykValues, cell_rules_to_analyse, is_sentence_positive: bool):
    """
    For each given rule check if it was already calculated and if not calculates inside outside probabilities
    for it. Then checks all rules which start with this rule either first right or second right symbol.
    :param cell_rules_to_analyse:
    :param is_sentence_positive:
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
                rules = __find_matching_rules_in_rules_container(cyk_values, cell_one_x, cell_one_y, right_1)
                new_cell_rules.extend(rules)
                right_one_rules.extend(rules)
            if cell_rule.cell_2_coordinates is not None:
                cell_two_x = cell_rule.cell_2_coordinates.x
                cell_two_y = cell_rule.cell_2_coordinates.y
                right_2: Symbol = cell_rule.rule.right2
                rules = __find_matching_rules_in_rules_container(cyk_values, cell_two_x, cell_two_y, right_2)
                new_cell_rules.extend(rules)
                right_two_rules.extend(rules)
            __calculate_inside_outside_for_cell_rule(cell_rule, right_one_rules,
                                                     right_two_rules, is_sentence_positive)
        cell_rules_to_analyse = new_cell_rules


def __calculate_outside_probabilities(cyk_values: CykValues, cell_rules_to_analyse):
    for rule in cell_rules_to_analyse:
        rule.outside = 1.0
    for i in reversed(range(len(cyk_values.sequence))):
        for j in reversed(range(len(cyk_values.sequence))):
            rules_processed = []
            for rule_parent in cyk_values.rules_table[i][j].cell_rules:
                if rules_processed.__contains__(rule_parent.rule):
                    continue
                rules_processed.append(rule_parent.rule)
                for k in reversed(range(i - 1)):
                    children_1 = [child for child in cyk_values.rules_table[k][j].cell_rules
                                  if child.rule.left == rule_parent.rule.right1]
                    children_2 = [child for child in cyk_values.rules_table[i - k - 1][j + k + 1].cell_rules
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


def __find_matching_rules_in_rules_container(cyk_values: CykValues, i_index, j_index, given_symbol):
    """
    Finds all rules in the cell [i_index][j_index] which have the given symbol on the left side
    :param i_index:
    :param j_index:
    :param given_symbol:
    :return:
    """
    cellRules = []
    for i in range(len(cyk_values.rules_table[i_index][j_index].cell_rules)):
        cellRule: sCellRule = cyk_values.rules_table[i_index][j_index].cell_rules[i]
        if cellRule.rule.left == given_symbol:
            cellRules.append(cellRule)
    return cellRules


def __calculate_inside_outside_for_cell_rule(cell_rule: sCellRule, right_one_rules,
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


def __update_grammars_positives_and_negatives(cyk_values: CykValues, is_result_parsed: bool, positive: bool):
    if is_result_parsed and positive:
        cyk_values.grammar.truePositive += 1
    elif not is_result_parsed and not positive:
        cyk_values.grammar.trueNegative += 1
    elif is_result_parsed and not positive:
        cyk_values.grammar.falsePositive += 1
    elif not is_result_parsed and positive:
        cyk_values.grammar.falseNegative += 1


def __create_evaluation(cyk_values: CykValues, sentence, result: float) -> SingleExampleEvaluation:
    evaluation = SingleExampleEvaluation()
    evaluation.mParam = result
    evaluation.mParsed = cyk_values.is_parsed
    evaluation.rulesTable = cyk_values.rules_table
    evaluation.sentence = sentence
    return evaluation
