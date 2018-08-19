import datetime
import logging
import time
import random
from typing import List
from modules.Covering.Covering import Covering
from modules.Crowding.crowding import Crowding
from modules.GCSBase.SingleExampleEvaluation import SingleExampleEvaluation
from modules.GCSBase.domain.CellRule import CellRule
from modules.GCSBase.domain.results import Results
from modules.GCSBase.domain.types.AaaRulesHandlingType import AaaRulesHandlingType
from modules.GCSBase.grammar.Results import Results
from modules.GCSBase.grammar.grammar import Grammar
from modules.Heuristic.Heuristic import Heuristic
from modules.Loader.test_data import TestData
from modules.Visualisation.iteration import Iteration
from modules.Visualisation.result import Result
from modules.sGCS.domain.sRule import sRule
from modules.sGCS.sGCS_grammar import sGCSGrammar
from settings.settings import Settings
import pickle


class GCSBase:
    def __init__(self, settings: Settings, grammar: Grammar = None, ga: Heuristic = None, cyk=None,
                 crowding: Crowding = None,
                 start_covering: Covering = None, final_covering: Covering = None,
                 aggressive_covering: Covering = None, terminal_covering: Covering = None):

        self.__grammar = grammar
        self.__ga = ga
        self.__cyk = cyk
        self.__crowding = crowding
        self.__settings = settings
        self.__logger = logging.getLogger("gcs_base")
        self.__logger.info("GCSBase Module inited.")
        # TODO 3 Metody delegate
        self.on_step_ended = None
        self.on_iteration_ended = None
        self.on_learning_ended = None
        self.on_example_processing_ended = None
        self.__train_data = None
        self.__test_data = None
        self.last_results = Results()
        self.result_map = dict()
        self.learning_mode = False
        self.rules_handling_type = AaaRulesHandlingType[self.settings.get_value('general', 'aaa_rules_handling_type')]
        self.adaptive_elitism_alpha: float = float(self.settings.get_value('general', 'adaptive_elitism_alpha'))
        self.io_grammar_difference_stop = self.settings.get_value('sgcs', 'io_grammar_difference_stop')

        self.aggressive_covering_probability = self.settings.get_value('covering', 'aggressive_covering_probability')
        self.is_full_covering_allowed = self.settings.get_value('covering', 'is_full_covering_allowed')
        self.is_universal_covering_allowed = self.settings.get_value('covering', 'is_universal_covering_allowed')
        self.is_start_covering_allowed = self.settings.get_value('covering', 'is_start_covering_allowed')
        self.is_terminal_covering_allowed = self.settings.get_value('covering', 'is_terminal_covering_allowed')
        self.is_ga_allowed = self.settings.get_value('genetic_algorithm', 'is_ga_allowed')
        self.negative_covering = self.settings.get_value('covering', 'negative_covering') == "True"

        self.non_terminal_productions_number = int(
            self.settings.get_value('general', 'non_terminal_productions_number'))

        self.start_covering = start_covering
        self.final_covering = final_covering
        self.aggressive_covering = aggressive_covering
        self.terminal_covering = terminal_covering

    @property
    def grammar(self) -> Grammar:
        return self.__grammar

    @property
    def settings(self):
        return self.__settings

    @property
    def ga(self):
        return self.__ga

    @property
    def cyk(self):
        return self.__cyk

    @property
    def crowding(self):
        return self.__crowding

    @property
    def test_data(self):
        return self.__test_data

    @test_data.setter
    def test_data(self, test_data):
        self.__test_data = test_data

    @property
    def train_data(self):
        return self.__train_data

    @train_data.setter
    def train_data(self, train_data):
        self.__train_data = train_data

    def reset_grammar(self):
        self.grammar.init_grammar(self.train_data)

    def process(self, collect_data, widget_process):
        #random.seed(23)
        #self.reset_grammar()
        max_step = int(self.settings.get_value("general", "max_evolutionary_steps"))
        ev_step = 0
        widget_process.max = max_step
        widget_process.description = "Calculating {}/{}".format(ev_step, max_step)
        stop_condition = False
        self.learning_mode = True
        sim_result = Result()
        self.__logger.info("Start elite number = " + str(self.settings.get_value("crowding", "elite_rules_number")))

        self.ga.reset()
        # main loop
        while not stop_condition:
            # print("************************************************************************************")
            # print("Induction step {0} of {1} ({2}%)".format(ev_step, max_step, round(ev_step/max_step*100)))
            iteration = Iteration()
            iteration.add_rules(list(self.grammar.get_rules()))
            self.set_iteration(iteration)
            start_time = time.time()

            # Genetic algorithm
            if self.settings.get_value("genetic_algorithm", "is_ga_allowed") == "True" and \
                            len(self.grammar.rulesContainer.non_terminal_rules) > 0:
                # print("[process] Running GA")
                self.ga.run(self.grammar)
                self.__logger.info("[process] Refreshing rules")
                self.grammar.correct_grammar()

            # Grammar induction
            self.__logger.info("[process] grammar induction start, step " + str(ev_step + 1))
            self.__logger.info("Number of rules in grammar: {0} total = {1} terminal + {2} nonterminal ({3} aaa)"
                               .format(len(self.grammar.get_rules()),
                                       len(self.grammar.get_terminal_rules()),
                                       len(self.grammar.get_non_terminal_rules()),
                                       self.grammar.rulesContainer.count_aaa_rules()))
            self.grammar_induction(iteration)
            self.__logger.info("[process] grammar induction ended " + str(ev_step + 1))

            self.grammar.rulesContainer.make_rules_older()

            if self.settings.get_value('genetic_algorithm', 'grammar_restoring_enabled') == "True":
                self.grammar.rulesContainer.reset_usages_and_points()
                self.parse_dataset(self.train_data, covering_on=False)
                self.refresh_rules_params(benchmark=True)
                self.ga.restore_if_necessary(self.grammar)

            # Saving results
            self.__logger.info("Evaluating grammar")
            self.evaluate_grammar_and_save_results_to_iteration(iteration)
            self.__logger.info("Finished evaluating grammar")
            # print(self.grammar)

            if self.settings.get_value("general", "allow_adaptive_elitism") == "True":
                self.adjust_elite_rules_number(iteration)

            """
            # TODO - w oryginale tutaj jest obiekt MySettings, wszędzie indziej workingCopySettings
            if self.settings.get_value("general", "allow_lock_removal_algorithm") == "True" and \
                    self.handle_lock_if_occurred(sim_result.get_last_iteration(), iteration):
                self.evaluate_grammar_and_save_results_to_iteration(iteration)
            """

            iteration.set_final_production_number(len(self.grammar.rulesContainer.terminal_rules),
                                                  len(self.grammar.rulesContainer.non_terminal_rules),
                                                  self.grammar.rulesContainer.count_aaa_rules(),
                                                  self.grammar.rulesContainer.terminal_rules,
                                                  self.grammar.rulesContainer.non_terminal_rules)

            # Finalizing
            ev_step += 1
            widget_process.value = ev_step
            if self.on_step_ended is not None:
                self.on_step_ended(ev_step, int(self.settings.get_value("general", "max_evolutionary_steps")))

            if collect_data:
                if self.settings.get_value("general", "pickle_on") == "True":
                    pickled_iteration = pickle.loads(pickle.dumps(iteration, -1))
                else:
                    pickled_iteration = iteration
                sim_result.add_iteration(pickled_iteration)

            # Checking for stop condition
            met = self.grammar.calc_metrics()
            Sens = met["Sensitivity"]
            Spec = met["Specificity"]
            stop_condition = (ev_step == int(self.settings.get_value("general", "max_evolutionary_steps")) or
                              self.settings.get_value("general",
                                                      "is_perfectly_fit_stop_condition_allowed") == "True" and
                              self.grammar.is_grammar_perfectly_fit(len(self.train_data)) or Sens > 0.9 and Spec > 0.9)
            self.__logger.info('Stop condition: {0}'.format(str(stop_condition)))

            end_time = time.time()
            self.__logger.info("[process] Induction step ended. Elapsed time: " + str(end_time - start_time) +
                               " step: " + str(ev_step))
            self.__logger.info("[process] True Positives = {0}, False Negatives = {1}, True Negatives = {2},"
                               "False Positives = {3}".format(self.grammar.truePositive, self.grammar.falseNegative,
                                                              self.grammar.trueNegative, self.grammar.falsePositive))
            widget_process.description = "Calculating {}/{}:".format(ev_step, max_step)
        widget_process.description = "Done {}/{}".format(max_step, max_step)
        widget_process.bar_style = "success"
        if self.settings.get_value("general", "remove_grammar_unused_rules_after_learning") == "True":
            self.grammar.remove_unused_rules_and_symbols()

        self.grammar.correct_grammar()
        if isinstance(self.grammar, sGCSGrammar):
            self.normalize_grammar()

        sim_result.final_grammar = self.grammar
        sim_result.settings = self.settings

        if self.on_iteration_ended is not None:
            self.on_iteration_ended(self.last_results, 1, 1)
        if self.on_learning_ended is not None:
            self.on_learning_ended(self.last_results)
        final_rules = list(self.grammar.get_rules())
        final_rules.sort(key=lambda x: str(x.left), reverse=True)
        self.benchmark_run(test=True)

        # print("Final rules")
        # for r in final_rules:
        #     print("{}, {}".format(r.short(), round(r.probability, 2)))
        #
        # print("Evolutionary steps = {}".format(ev_step))
        return sim_result, final_rules

        print("Evolutionary steps = {}".format(ev_step))
        return sim_result

    def correct_grammar(self):
        # Correction of grammar
        if self.settings.get_value("general", "is_grammar_correction_allowed") == "True":
            print("[process] Correcting grammar")
            self.grammar.correct_grammar()

        if self.settings.get_value("general", "remove_parsing_only_negative_rules_at_end_of_iteration") == "True":
            print("[process] Removing bad rules")
            self.grammar.remove_bad_rules()

        if self.settings.get_value('crowding', 'shrinking_enabled') == "True":
            print("[process] Shrinking")
            self.grammar.shrink_to_proper_size(self.non_terminal_productions_number)
        self.normalize_grammar()

    def random_fitness(self):
        for rule in self.grammar.get_rules():
            rule.fitness = random.uniform(0, 1)

    def normalize_fitness(self):
        for symbol in self.grammar.nonTerminalSymbols:
            fitness_sum = 0
            for rule in self.grammar.get_rules():
                if rule.left == symbol:
                    fitness_sum += rule.fitness
            for rule in self.grammar.get_rules():
                if rule.left == symbol:
                    rule.fitness_normalized = rule.fitness / fitness_sum

    def save_rules_in_file(self, rules: List[sRule], file_name):
        with open('{}.csv'.format(file_name), 'w') as file:
            file.write('Rule;Fitness;Fitness Normalized;Probability;;Correlation Fitness-Probability;Correlation Fitness Normalized-Probability')
            file.write('\n')
            for rule in rules:
                line = '{} -> {}{};{};{};{}'.format(rule.left, (rule.right1 or ""), (rule.right2 or ""), rule.fitness, rule.fitness_normalized, rule.probability)
                file.write(line)
                file.write('\n')



    def adjust_elite_rules_number(self, iteration: Iteration):
        adaptive_elitism_alpha = float(self.settings.get_value('general', 'adaptive_elitism_alpha'))
        non_terminal_productions_number = int(self.settings.get_value('general', 'non_terminal_productions_number'))
        elitism_upper_bound = float(self.settings.get_value('general', 'elitism_upper_bound'))

        if iteration.results.fitness <= adaptive_elitism_alpha:
            elite_rules_number = iteration.results.fitness * elitism_upper_bound * non_terminal_productions_number
        else:
            elite_rules_number = elitism_upper_bound * non_terminal_productions_number - iteration.results.fitness * elitism_upper_bound * non_terminal_productions_number
        self.settings.set_value('general', 'elite_rules_number', str(elite_rules_number))
        self.__logger.info('elite rules number = {}'.format(elite_rules_number))

    def normalize_grammar(self):
        self.grammar.normalize_grammar()

    def grammar_induction(self, iteration_to_fill, benchmark=False, test=False):
        self.grammar.rulesContainer.reset_usages_and_points()
        #self.grammar.reset_grammar()
        # iteration_to_fill.add_rules(list(self.grammar.get_rules()))

        self.result_map = dict()
        # self.set_iteration(iteration_to_fill)
        # parse every sentence
        if test:
            examples = self.test_data
        else:
            examples = self.train_data

        if benchmark:
            self.parse_dataset(examples, covering_on=False)
        else:
            # print("[Grammar Induction] Parsing with covering on")
            self.parse_dataset(examples, covering_on=True)
            self.correct_grammar()
            #for r in self.grammar.get_rules(): print(r)
            #self.refresh_rules_params(benchmark)
            # print("[Grammar Induction] Parsing with covering off and estimating probs")
            # print("Number of rules in grammar: {}".format(len(self.grammar.get_rules())))
            for i in range(10):
                # print("\nEM iteration: {}".format(i))
                self.grammar.rulesContainer.reset_usages_and_points()
                self.parse_dataset(examples, covering_on=False)
                self.refresh_rules_params(benchmark)
            self.normalize_grammar()
                #for r in self.grammar.get_rules(): print(r)
                #self.parse_dataset(examples, covering_on=False)

    def parse_dataset(self, examples,  covering_on):
        self.grammar.reset_grammar()
        count_positives = 0
        count_negatives = 0

        sum_pos_prob = 0
        sum_neg_prob = 0
        sum_pos_parsed = 0
        sum_neg_parsed= 0
        for example in examples:
            if example.positive:
                count_positives += 1
            else:
                count_negatives += 1
            result = self.cyk.cyk_result(example.sequence, self.grammar, example.positive,
                                         self.learning_mode,  covering_on, self.negative_covering)
            # result = cyk_result_ordered_jobs(example.sequence, self.grammar, example.positive, self.learning_mode,
            #                                  self.settings, None, iteration_to_fill,
            #                                  self.start_covering, self.final_covering, self.aggressive_covering,
            #                                  self.terminal_covering)
            # self.__grammar = result.grammar
            # result = self.cyk.cyk_result(example.sequence, self.grammar, example.positive, self.learning_mode)
            if self.on_example_processing_ended is not None:
                self.on_example_processing_ended(example, result.mParsed, examples.count)
            self.result_map[example.id_data] = result
            if result.positive:
                sum_pos_prob += result.mParam
                sum_pos_parsed += result.mParsed
            else:
                sum_neg_prob += result.mParam
                sum_neg_parsed += result.mParsed
        # print("TP: {}, FP: {}, FN: {}, TN: {}, mean positive probability = {}, mean negative probability ()".
        #       format(self.grammar.truePositive, self.grammar.falsePositive, self.grammar.falseNegative, self.grammar.trueNegative,
        #              0 if sum_pos_parsed == 0 else (sum_pos_prob-sum_neg_prob)/sum_pos_parsed),
        #       )
        if isinstance(self.grammar, sGCSGrammar):
            self.grammar.positives_sample_amount = count_positives
            self.grammar.negative_sample_amount = count_negatives

    def evaluate_grammar_and_save_results_to_iteration(self, iteration: Iteration):
        iteration.results = self.benchmark_run(test=False)
        # iteration.result_map = self.result_map
        self.__logger.info("Filling report rules")
        iteration.fill_report_rules()

    def refresh_rules_params(self, benchmark=False):
        if not benchmark:
            self.grammar.adjust_parameters()
        if self.settings.get_value('general', 'fitness_enabled') == 'True':
            self.grammar.rulesContainer.count_fitness()
        else:
            self.grammar.rulesContainer.count_fitness(self.grammar.truePositive + self.grammar.falseNegative,
                                                      self.grammar.trueNegative + self.grammar.falsePositive)

    def parse_single_example(self, example: TestData):
        self.learning_mode_off()
        result: SingleExampleEvaluation = self.cyk.cyk_result(example.sequence, self.grammar, False)
        self.learning_mode_on()
        return result.mParsed

    def handle_lock_if_occurred(self, last_iteration: Iteration, current_iteration: Iteration):
        if last_iteration is None:
            return False
        if last_iteration.results.false_negative != 0 or current_iteration.results.false_negative != 0:
            return False
        for train_data in last_iteration.result_map:
            if last_iteration.result_map[train_data].mParsed != \
                    current_iteration.result_map[train_data].mParsed:
                return False

        self.remove_worst_rule_by_reversed_roulette(current_iteration)
        return True

    def remove_worst_rule_by_reversed_roulette(self, current_iteration: Iteration):
        rule_to_remove = self.grammar.rulesContainer.get_rule_to_remove_by_reversed_roulette()
        self.__logger.info("De_lock rule to remove = {0}".format(rule_to_remove))
        current_iteration.remove_selective_de_lock_rule(rule_to_remove)
        self.grammar.remove_rule(rule_to_remove)

    def learning_mode_off(self):
        self.settings.set_value('covering', 'aggressive_covering_probability', str(0))
        self.settings.set_value('covering', 'is_full_covering_allowed', str(False))
        self.settings.set_value('covering', 'is_universal_covering_allowed', str(False))
        self.settings.set_value('covering', 'is_start_covering_allowed', str(False))
        self.settings.set_value('covering', 'is_terminal_covering_allowed', str(False))
        self.settings.set_value('genetic_algorithm', 'is_ga_allowed', str(False))

    def learning_mode_on(self):
        self.settings.set_value('covering', 'aggressive_covering_probability', self.aggressive_covering_probability)
        self.settings.set_value('covering', 'is_full_covering_allowed', self.is_full_covering_allowed)
        self.settings.set_value('covering', 'is_universal_covering_allowed', self.is_universal_covering_allowed)
        self.settings.set_value('covering', 'is_start_covering_allowed', self.is_start_covering_allowed)
        self.settings.set_value('covering', 'is_terminal_covering_allowed', self.is_terminal_covering_allowed)
        self.settings.set_value('genetic_algorithm', 'is_ga_allowed', self.is_ga_allowed)

    def benchmark_run(self, test=False):
        self.__logger.info("Running benchmark")
        # print("Running benchmark")
        self.learning_mode_off()
        self.grammar_induction(Iteration(), benchmark=True, test=test)
        last_fitness: float = self.last_results.fitness if self.last_results is not None else 0.0
        fitness_diff = last_fitness - self.last_results.fitness
        self.fill_results()
        if type(self.grammar) is sGCSGrammar:
            if 0 < fitness_diff < self.io_grammar_difference_stop:
                self.grammar.new_ones_only = True
            else:
                self.grammar.new_ones_only = False
        self.learning_mode_on()
        self.__logger.info("Finishing benchmark")
        return self.last_results

    def benchmark_run_testing_threshold(self):
        self.learning_mode = False
        self.learning_mode_off()
        self.grammar_induction(Iteration(), True)
        self.fill_results()
        self.learning_mode = True
        return self.last_results

    def fill_results(self):
        self.last_results: Results = Results()
        self.last_results.true_positive = self.grammar.truePositive
        self.last_results.true_negative = self.grammar.trueNegative
        self.last_results.false_positive = self.grammar.falsePositive
        self.last_results.false_negative = self.grammar.falseNegative

        self.last_results.sensitivity = self.grammar.calculate_sensitivity()
        self.last_results.specificity = self.grammar.calculate_specificity()
        self.last_results.f1 = self.grammar.calculate_f1()
        self.last_results.precision = self.grammar.calculate_precision()

        self.last_results.count = len(self.train_data)
        self.last_results.fitness = self.grammar.calculate_grammar_fitness(len(self.train_data))

    def save_trees(self):
        current_time = datetime.datetime.now().strftime('%Y.%m.%d_%H-%M-%S')
        file = open('tree_{}.txt'.format(current_time), 'w')
        for test_example in self.result_map:
            if test_example.positive and self.result_map[test_example.id_data].mParsed:
                tree = self.get_tree(self.result_map[test_example.id_data].rulesTable,
                                     self.result_map[test_example.id_data].
                                     rulesTable[len(test_example.sequence) - 1][0])
                text = '{} {}\n'.format(test_example.sequence, tree)
                file.write(text)

    def get_tree(self, rules_table, cell_rule_list: List[CellRule]) -> str:
        cr: CellRule = cell_rule_list[0]
        if cr.rule.is_terminal(self.rules_handling_type):
            return '{} ({})'.format(cr.rule.left.value, cr.rule.right1.value)
        first_tree = self.get_tree(rules_table, rules_table[cr.cell_1_coordinates.x][cr.cell_1_coordinates.y])
        second_tree = self.get_tree(rules_table, rules_table[cr.cell_2_coordinates.x][cr.cell_2_coordinates.y])
        return '{} ({}, {})'.format(cr.rule.left.value, first_tree, second_tree)

    def set_iteration(self, iteration_to_fill: Iteration) -> None:
        self.ga.set_iteration(iteration_to_fill)
        self.grammar.set_iteration(iteration_to_fill)
        self.crowding.set_iteration(iteration_to_fill)

        self.terminal_covering.set_iteration(iteration_to_fill)
        self.final_covering.set_iteration(iteration_to_fill)
        self.aggressive_covering.set_iteration(iteration_to_fill)
        self.start_covering.set_iteration(iteration_to_fill)
