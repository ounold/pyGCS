import logging

from modules.Covering.CoveringUtils.covering_determiner import CoveringDeterminer
from modules.Crowding.crowding_determiner import CrowdingDeterminer
from modules.GCSBase.GCSBase import GCSBase
from modules.Heuristic.GeneticAlgorithm.genetic_algorithm import GeneticAlgorithm
from modules.Parsers.CYK.sGCS.SGCSCyk import SGCSCyk
from modules.Stochastic.Stochastic import Stochastic
from modules.sGCS.sGCS_grammar import sGCSGrammar


class sGCS(GCSBase):

    def __init__(self, settings):
        self.__settings = settings
        self.__grammar = sGCSGrammar(settings)
        self.__crowding = CrowdingDeterminer.get_crowding(settings)

        self.__final_covering = CoveringDeterminer.get_final_covering(self.__settings, self.__crowding)
        self.__terminal_covering = CoveringDeterminer.get_terminal_covering(self.__settings, self.__crowding)
        self.__aggressive_covering = CoveringDeterminer.get_aggressive_covering(self.__settings, self.__crowding)
        self.__start_covering = CoveringDeterminer.get_start_covering(self.__settings, self.__crowding)

        cyk = SGCSCyk(self.__grammar, None, self.__settings,
                      aggressive_covering=self.__aggressive_covering,
                      terminal_covering=self.__terminal_covering,
                      final_covering=self.__final_covering,
                      start_covering=self.__start_covering)
        heuristic = GeneticAlgorithm(self.__crowding, self.__settings)

        super().__init__(settings, self.__grammar, heuristic, cyk, self.__crowding,
                         aggressive_covering=self.__aggressive_covering,
                         terminal_covering=self.__terminal_covering,
                         final_covering=self.__final_covering,
                         start_covering=self.__start_covering)
        self.__logger = logging.getLogger("sgcs")
        self.__logger.info("SGCS Module inited.")
        self.__logger.info(self.grammar)
        self.__stochastic = Stochastic(self.__settings)
