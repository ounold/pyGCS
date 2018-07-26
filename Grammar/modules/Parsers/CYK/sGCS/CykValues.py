from modules.Covering import Covering
from modules.sGCS.sGCS_grammar import sGCSGrammar
from settings.settings import Settings


class CykValues:
    def __init__(self, grammar: sGCSGrammar, is_learning_on: bool, sentence: str, settings: Settings,
                 start_covering: Covering = None, final_covering: Covering = None,
                 aggressive_covering: Covering = None, terminal_covering: Covering = None):
        self.grammar = grammar
        self.is_learning_on = is_learning_on
        self.default_value = None
        self.probability_array = None
        self.sentence = sentence
        self.positive = False
        self.sequence = []
        self.rules_table = None
        self.mode = settings.get_value('general', 's_mode')
        self.settings = settings
        self.is_parsed = False
        self.start_covering = start_covering
        self.final_covering = final_covering
        self.aggressive_covering = aggressive_covering
        self.terminal_covering = terminal_covering