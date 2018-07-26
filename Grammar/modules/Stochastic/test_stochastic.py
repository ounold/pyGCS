from unittest import TestCase
from copy import deepcopy
from settings.settings import Settings
from modules.Stochastic.Stochastic import Stochastic
from modules.GCSBase.grammar.grammar import Grammar
from modules.sGCS.sGCS_grammar import sGCSGrammar
from modules.sGCS.domain.sRule import sRule
from modules.GCSBase.domain.symbol import Symbol
from modules.GCSBase.domain.Rule import Rule
from modules.sGCS.sGCS import sGCS
import ipywidgets as widgets

from modules.GCSBase.domain.types.AaaRulesHandlingType import AaaRulesHandlingType
import random
from modules.Loader.abbadingo_format_loader import AbbadingoFormatLoader



class TestStochastic(TestCase):

    def test_Normalize(self):
        # grammar = sGCSGrammar()
        # s = Symbol("A", 2)
        # rule_1 = sRule([Symbol("A", 2), Symbol("B", 2), Symbol("C", 2)])
        # rule_2 = sRule([Symbol("A", 2), Symbol("C", 2), Symbol("D", 2)])
        # rule_1.probability = 0.1
        # rule_2.probability = 0.4
        #
        # grammar.rulesContainer.rules.append(rule_1)
        # grammar.rulesContainer.nonTerminalRules.append(rule_1)
        # grammar.rulesContainer.rules.append(rule_2)
        # grammar.rulesContainer.nonTerminalRules.append(rule_2)
        # grammar.symbols.append(s)
        #
        # grammar.normalize_grammar()
        # #stoch.normalize(grammar)
        # prob1 = grammar.rulesContainer.rules[0].probability
        # prob2 = grammar.rulesContainer.rules[1].probability
        #
        # self.assertEqual(prob1 + prob2, 1)
        # self.assertEqual(prob1, 0.2)
        # self.assertEqual(prob2, 0.8)
        pass

    def test_Estimate(self):
        random.seed(23)
        self.__settings = Settings('test_app.ini')
        self.__gcs = sGCS(self.__settings)
        self.__stochastic = Stochastic()
        abbading_format_loader = AbbadingoFormatLoader()
        abbading_format_loader.load('../../NewTestSets/TomitaNew/tomita_1.txt')
        self.__gcs.train_data = abbading_format_loader.input_data
        self.__gcs.reset_grammar()
        non_terminal_rules = set()
        non_terminal_rules = deepcopy(self.__gcs.grammar.get_non_terminal_rules())
        for rule in non_terminal_rules:
            self.__gcs.grammar.remove_rule(rule)
        n_symbols = self.__gcs.grammar.nonTerminalSymbols
        t_symbols = self.__gcs.grammar.terminalSymbols
        self.__gcs.grammar.add_rules([sRule([n_symbols[0], n_symbols[0], n_symbols[1]], prob=random.uniform(0, 1)),
                                      sRule([n_symbols[0], n_symbols[0], n_symbols[2]], prob=random.uniform(0, 1)),
                                      sRule([n_symbols[1], t_symbols[1]], prob=random.uniform(0, 1)),
                                      sRule([n_symbols[2], t_symbols[0]], prob=random.uniform(0, 1)),
                                      sRule([n_symbols[0], t_symbols[1]], prob=random.uniform(0, 1)),
                                      sRule([n_symbols[0], t_symbols[0]], prob=random.uniform(0, 1))])
        all_rules = self.__gcs.grammar.get_rules()
        are_terminals = [rule.is_terminal(AaaRulesHandlingType.TERMINALS) for rule in all_rules]
        loader_widget = widgets.IntProgress(value=0, min=0, step=1, bar_style='info',
                                            orientation='horizontal',
                                            layout=widgets.Layout(width='100%', height='100%'),
                                            style={'description_width': 'initial'})
        self.__stochastic.normalize(self.__gcs.grammar)
        self.__gcs.process(True, loader_widget)
        all_rules = self.__gcs.grammar.get_rules()
        pass

