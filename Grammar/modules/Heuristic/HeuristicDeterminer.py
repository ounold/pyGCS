from modules.Crowding.crowding import Crowding
from modules.Heuristic.GeneticAlgorithm.genetic_algorithm import GeneticAlgorithm
from modules.Heuristic.Heuristic import Heuristic
from modules.Heuristic.SplitAndMerge.split_and_merge import SplitAndMerge
from settings.settings import Settings


class HeuristicDeterminer:

    @staticmethod
    def get_heuristic(settings: Settings, crowding: Crowding = None) -> Heuristic:
        heuristic_algorithm = settings.get_value('general', 'heuristic_algorithm')
        if heuristic_algorithm == "ga":
            return GeneticAlgorithm(crowding, settings)
        elif heuristic_algorithm == "split_and_merge":
            return SplitAndMerge(settings=settings)
        else:
            raise RuntimeError("No heuristic algorithm selected")