import logging

from modules.GCSBase.grammar.grammar import Grammar


class Result:

    def __init__(self, settings=None):
        self.__settings = settings
        self.__iterations = []
        self.__final_grammar: Grammar = None
        self.__learning_set_name = None
        self.__logger = logging.getLogger("result")
        self.__logger.info("Result Module inited.")

    @property
    def iterations(self):
        return self.__iterations

    @property
    def final_grammar(self):
        return self.__final_grammar

    @property
    def learning_set_name(self):
        return self.__learning_set_name

    @iterations.setter
    def iterations(self, iterations):
        self.__iterations = iterations

    @final_grammar.setter
    def final_grammar(self, final_grammar):
        self.__final_grammar = final_grammar
    
    @learning_set_name.setter
    def learning_set_name(self, learning_set_name):
        self.__learning_set_name = learning_set_name

    def add_iteration(self, iteration):
        self.__iterations.append(iteration)

    def get_last_iteration(self):
        if len(self.iterations) == 0:
            return None
        else:
            return self.iterations[-1]

    def __str__(self):
        return str(self.__final_grammar)
