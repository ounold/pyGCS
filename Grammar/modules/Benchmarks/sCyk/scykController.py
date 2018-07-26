import time

from modules.Covering.CoveringUtils.covering_determiner import CoveringDeterminer
from modules.Crowding.standard_crowding import StandardCrowding
from modules.Loader.abbadingo_format_loader import AbbadingoFormatLoader
from modules.Parsers.CYK.sGCS.ParallelCykLadder import cyk_result_ladder
from modules.Parsers.CYK.sGCS.ParallelCykOrderedJobs import cyk_result_ordered_jobs
from modules.Parsers.CYK.sGCS.ParallerCyk import cyk_result
from modules.Parsers.CYK.sGCS.SGCSCyk import SGCSCyk
from modules.Visualisation.iteration import Iteration
from modules.sGCS.sGCS_grammar import sGCSGrammar
from settings.settings import Settings


class ScykController:
    def __init__(self, settings: Settings = None):
        self.__settings = settings
        self.crowding = None
        self.final_covering = None
        self.terminal_covering = None
        self.aggressive_covering = None
        self.start_covering = None
        self.iteration = None

    def run_benchmark(self):
        iterations = 10
        self.empty_grammar_tests_with_learning(iterations)

    def empty_grammar_tests_with_learning(self, iterations):
        test_data_list = self.__settings.get_value("general", "parallel_test_set_path").split(",")
        learning_on = False
        seq_times = []
        par_times = []
        par_ladder_times = []
        par_ordered_jobs_times = []

        for test_data in test_data_list:
            abbading_format_loader = AbbadingoFormatLoader()
            abbading_format_loader.load(test_data)
            test_data = abbading_format_loader.input_data
            grammar = sGCSGrammar(self.__settings)
            grammar.init_grammar(test_data)
            self.init_crowding_and_covering(grammar)

            print('Starting sequential scyk testing')
            for i in range(iterations):
                self.benchmark_sequential_scyk(grammar, test_data, learning_on, seq_times)
            print('Finished sequential scyk testing')

            # print('Starting parallel scyk testing')
            # for i in range(iterations):
            #     self.benchmark_parallel_scyk(grammar, test_data, self.iteration, learning_on, par_times)
            # print('Finished parallel scyk testing')
            #
            # print('Starting parallel scyk ladder testing')
            # for i in range(iterations):
            #     self.benchmark_parallel_scyk_ladder(grammar, test_data, self.iteration, learning_on, par_ladder_times)
            # print('Finished parallel scyk ladder testing')

            print('Starting parallel scyk ordered jobs testing')
            for i in range(iterations):
                self.benchmark_parallel_scyk_ordered_jobs(grammar, test_data, self.iteration, learning_on,
                                                          par_ordered_jobs_times)
            print('Finished parallel scyk scyk ordered jobs testing')

            seq_dict = self.benchmark_sequential_scyk_with_dict_result(grammar, test_data, learning_on, iterations)

            # print('Starting parallel scyk dictionary generation')
            # par_dict = self.benchmark_parallel_scyk_with_dict_result(grammar, test_data, self.iteration, learning_on,
            #                                                          iterations)
            # print('Finished parallel scyk dictionary generation')
            #
            # print('Starting parallel scyk ladder dictionary generation')
            # par_ladder_dict = self.benchmark_parallel_ladder_scyk_with_dict_result(grammar, test_data, self.iteration,
            #                                                                        learning_on,
            #                                                                        iterations)
            # print('Finished parallel scyk ladder dictionary generation')

            print('Starting parallel scyk ordered jobs dictionary generation')
            par_ordered_jobs_dict = self.benchmark_parallel_ordered_scyk_with_dict_result(grammar, test_data,
                                                                                          self.iteration,
                                                                                          learning_on,
                                                                                          iterations)
            print('Finished parallel scyk ordered jobs dictionary generation')

            with open("results_seq_lon", "w") as f:
                f.write(str(seq_times))

            with open("results_par_lon", "w") as f:
                f.write(str(par_times))

            with open("results_par_ladder_lon", "w") as f:
                f.write(str(par_ladder_times))

            with open("results_par_ordered_jobs_lon", "w") as f:
                f.write(str(par_ordered_jobs_times))

            with open("results_seq_lon_dict", "w") as f:
                f.write(str(seq_dict))

            # with open("results_par_lon_dict", "w") as f:
            #     f.write(str(par_dict))
            #
            # with open("results_par_ladder_lon_dict", "w") as f:
            #     f.write(str(par_ladder_dict))

            with open("results_par_ordered_jobs_lon_dict", "w") as f:
                f.write(str(par_ordered_jobs_dict))

    def benchmark_sequential_scyk(self, grammar: sGCSGrammar, test_data, learning_on, seq_times):
        scyk = SGCSCyk(grammar, None, self.__settings, self.start_covering, self.final_covering,
                       self.aggressive_covering, self.terminal_covering)
        for example in test_data:
            start_time = time.time()
            scyk.cyk_result(example.sequence, grammar, example.positive, learning_on)
            end_time = time.time()
            seq_times.append(str(end_time - start_time))

    def benchmark_parallel_scyk(self, grammar: sGCSGrammar, test_data, iteration, learning_on, par_times):
        for example in test_data:
            start_time = time.time()
            cyk_result(example.sequence, grammar, example.positive, learning_on, self.__settings, self.crowding,
                       iteration)
            end_time = time.time()
            par_times.append(str(end_time - start_time))

    def benchmark_parallel_scyk_ladder(self, grammar: sGCSGrammar, test_data, iteration, learning_on, par_ladder_times):
        for example in test_data:
            start_time = time.time()
            cyk_result_ladder(example.sequence, grammar, example.positive, learning_on, self.__settings, self.crowding,
                              iteration)
            end_time = time.time()
            par_ladder_times.append(str(end_time - start_time))

    def benchmark_sequential_scyk_with_dict_result(self, grammar: sGCSGrammar, test_data, learning_on, iterations):
        scyk = SGCSCyk(grammar, None, self.__settings, self.start_covering, self.final_covering,
                       self.aggressive_covering, self.terminal_covering)
        seq_example_dictionary = dict()
        for example in test_data:
            start_time = time.time()
            for iteration in range(iterations):
                scyk.cyk_result(example.sequence, grammar, example.positive, learning_on)
            end_time = time.time()
            seq_example_dictionary[example.sequence] = str(end_time - start_time)
        return seq_example_dictionary

    def benchmark_parallel_scyk_ordered_jobs(self, grammar: sGCSGrammar, test_data, iteration, learning_on,
                                             par_ordered_times):
        for example in test_data:
            start_time = time.time()
            cyk_result_ordered_jobs(example.sequence, grammar, example.positive, learning_on, self.__settings,
                                    self.crowding,
                                    iteration)
            end_time = time.time()
            par_ordered_times.append(str(end_time - start_time))

    def benchmark_parallel_ordered_scyk_with_dict_result(self, grammar: sGCSGrammar, test_data, iteration, learning_on,
                                                         iterations):
        par_example_dictionary = dict()
        for example in test_data:
            start_time = time.time()
            for i in range(iterations):
                cyk_result_ordered_jobs(example.sequence, grammar, example.positive, learning_on, self.__settings,
                                        self.crowding,
                                        iteration)
            end_time = time.time()
            par_example_dictionary[example.sequence] = str(end_time - start_time)
        return par_example_dictionary

    def benchmark_parallel_scyk_with_dict_result(self, grammar: sGCSGrammar, test_data, iteration, learning_on,
                                                 iterations):
        par_example_dictionary = dict()
        for example in test_data:
            start_time = time.time()
            for i in range(iterations):
                cyk_result(example.sequence, grammar, example.positive, learning_on, self.__settings, self.crowding,
                           iteration)
            end_time = time.time()
            par_example_dictionary[example.sequence] = str(end_time - start_time)
        return par_example_dictionary

    def benchmark_parallel_ladder_scyk_with_dict_result(self, grammar: sGCSGrammar, test_data, iteration, learning_on,
                                                        iterations):
        par_example_dictionary = dict()
        for example in test_data:
            start_time = time.time()
            for i in range(iterations):
                cyk_result_ladder(example.sequence, grammar, example.positive, learning_on, self.__settings,
                                  self.crowding,
                                  iteration)
            end_time = time.time()
            par_example_dictionary[example.sequence] = str(end_time - start_time)
        return par_example_dictionary

    def init_crowding_and_covering(self, grammar: sGCSGrammar):
        self.crowding = StandardCrowding(self.__settings)
        self.final_covering = CoveringDeterminer.get_final_covering(self.__settings, self.crowding)
        self.terminal_covering = CoveringDeterminer.get_terminal_covering(self.__settings, self.crowding)
        self.aggressive_covering = CoveringDeterminer.get_aggressive_covering(self.__settings, self.crowding)
        self.start_covering = CoveringDeterminer.get_start_covering(self.__settings, self.crowding)
        self.iteration = Iteration()
        self.iteration.add_rules(grammar.get_rules())
        self.crowding.iteration = self.iteration
        self.final_covering.iteration = self.iteration
        self.terminal_covering.iteration = self.iteration
        self.aggressive_covering.iteration = self.iteration
        self.start_covering.iteration = self.iteration
