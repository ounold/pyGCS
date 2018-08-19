import time

import pykka as pykka

from modules.GCSBase.domain.Coordinates import Coordinates
from modules.Parsers.CYK.sGCS.ParallelCykOrderedJobs import CykIndexes
from modules.Parsers.CYK.sGCS.actors import JobsStateStorage, RulesStorageActor
from modules.Parsers.CYK.sGCS.actors.RulesAndProbabilityStorageActor import RulesAndProbabilityStorage
from modules.Parsers.CYK.sGCS.actors.StorageActor import StorageActor
from modules.Stochastic.Stochastic import Stochastic
from modules.sGCS.domain.sCellRule import sCellRule


class TaskExecutorActor(pykka.ThreadingActor):
    def __init__(self, jobs_storage_proxy: StorageActor,
                 rules_prob_proxy: RulesAndProbabilityStorage,
                 parsing_state_proxy: JobsStateStorage,
                 rules_storage_proxy: RulesStorageActor):
        super(TaskExecutorActor, self).__init__()
        self.jobs_storage_proxy = jobs_storage_proxy
        self.rules_prob_proxy = rules_prob_proxy
        self.parsing_state_proxy = parsing_state_proxy
        self.rules_storage_proxy = rules_storage_proxy

    def on_receive(self, message):
        if message.get('command') == 'start':
            self.start_execution()

    def start_execution(self):
        while True:
            job: CykIndexes = self.jobs_storage_proxy.get_cell_job().get()

            if job is None:
                return self.rules_prob_proxy.get_rule_to_add(), self.rules_prob_proxy.get_rules_table(), self.rules_prob_proxy.get_probability_array()
            i = job.i
            j = job.j
            was = False
            for k in range(i):

                cell_up_state = self.parsing_state_proxy.get_cell_state(k, j).get()
                cell_cross_state = self.parsing_state_proxy.get_cell_state(i - k - 1, j + k + 1).get()

                while cell_up_state is False and cell_cross_state is False:
                    cell_up_state = self.parsing_state_proxy.get_cell_state(k, j).get()
                    cell_cross_state = self.parsing_state_proxy.get_cell_state(i - k - 1, j + k + 1).get()

                rules = self.rules_storage_proxy.get_rules().get()
                probability_array = self.rules_prob_proxy.get_probability_array().get()

                for rule in rules:
                    if rule.right2 is not None:
                        first_rule_index = rule.right1.index
                        second_rule_index = rule.right2.index
                        if probability_array[k][j][first_rule_index] is not None \
                                and probability_array[i - k - 1][j + k + 1][second_rule_index] is not None:
                            rule.tmp_used = True
                            rule_left_index = rule.left.index
                            was = True
                            parent_cell_probability = probability_array[k][j][first_rule_index]
                            parent_cell_2_probability = \
                                probability_array[i - k - 1][j + k + 1][second_rule_index]
                            current_cell_probability = probability_array[i][j][rule_left_index]
                            current_cell_probability = Stochastic.new_calculate_cell('BaumWelch', None, parent_cell_probability,
                                                          parent_cell_2_probability,
                                                          current_cell_probability,
                                                          rule)
                            new_rule = sCellRule(rule, Coordinates(k, j), Coordinates(i - k - 1, j + k + 1))
                            self.rules_prob_proxy.update_rules_table(i, j, new_rule)
                            self.rules_prob_proxy.update_probability_array(i, j, rule_left_index, current_cell_probability)
            if not was:
                self.rules_prob_proxy.add_rule_to_add([i, j])
            self.parsing_state_proxy.update_cell_state(i, j)
