from modules.Covering import Covering
from modules.Covering.CoveringPlus.aggressive_covering_plus import AggressiveCoveringPlus
from modules.Covering.CoveringPlus.final_covering_plus import FinalCoveringPlus
from modules.Covering.CoveringPlus.start_covering_plus import StartCoveringPlus
from modules.Covering.CoveringPlus.terminal_covering_plus import TerminalCoveringPlus
from modules.Covering.CoveringPlus.terminal_no_repetition_covering import TerminalNoRepetitionCovering
from modules.Covering.NakamuraCovering.aggressive_nakamura_covering import AggressiveNakamuraCovering
from modules.Covering.NakamuraCovering.terminal_nakamura_covering import TerminalNakamuraCovering
from modules.Covering.NewCovering.aggressive_new_covering import AggressiveNewCovering
from modules.Covering.NewCovering.terminal_new_covering import TerminalNewCovering
from modules.Covering.SmartCovering.aggressive_smart_covering import AggressiveSmartCovering
from modules.Covering.SmartCovering.terminal_smart_covering import TerminalSmartCovering
from modules.Covering.SmartCoveringWithTabu.aggressive_smart_covering_with_tabu import AggressiveSmartCoveringWithTabu
from modules.Covering.StandardCovering.aggressive_standard_covering import AggressiveStandardCovering
from modules.Covering.StandardCovering.final_standard_covering import FinalStandardCovering
from modules.Covering.StandardCovering.start_standard_covering import StartStandardCovering
from modules.Covering.StandardCovering.terminal_standard_covering import TerminalStandardCovering
from modules.Crowding.crowding import Crowding
from settings.settings import Settings


class CoveringDeterminer:
    @staticmethod
    def get_terminal_covering(settings: Settings, crowding: Crowding = None) -> Covering:
        covering_type = settings.get_value('covering', 'terminal_covering_type')
        if covering_type == "new_covering":
            return TerminalNewCovering(crowding, settings)
        elif covering_type == "smart_covering":
            return TerminalSmartCovering(crowding)
        elif covering_type == "nakamura_covering":
            return TerminalNakamuraCovering(crowding)
        elif covering_type == "covering_plus":
            return TerminalCoveringPlus()
        elif covering_type == "standard_covering":
            return TerminalStandardCovering()
        elif covering_type == "no_repetition_covering":
            return TerminalNoRepetitionCovering(settings)
        else:
            raise RuntimeError("No terminal covering selected")

    @staticmethod
    def get_aggressive_covering(settings: Settings, crowding: Crowding = None) -> Covering:
        covering_type = settings.get_value('covering', 'aggressive_covering_type')
        if covering_type == "smart_covering_with_tabu":
            return AggressiveSmartCoveringWithTabu(crowding)
        elif covering_type == "smart_covering":
            return AggressiveSmartCovering(crowding)
        elif covering_type == "nakamura_covering":
            return AggressiveNakamuraCovering(crowding)
        elif covering_type == "covering_plus":
            return AggressiveCoveringPlus(crowding)
        elif covering_type == "standard_covering":
            return AggressiveStandardCovering(crowding)
        elif covering_type == "new_covering":
            return AggressiveNewCovering(crowding, settings)
        else:
            raise RuntimeError("No aggressive covering selected")

    @staticmethod
    def get_final_covering(settings: Settings, crowding: Crowding = None) -> Covering:
        covering_type = settings.get_value('covering', 'final_covering_type')
        if covering_type == "covering_plus":
            return FinalCoveringPlus(crowding)
        elif covering_type == "standard_covering":
            return FinalStandardCovering(crowding)
        else:
            raise RuntimeError("No final covering selected")

    @staticmethod
    def get_start_covering(settings: Settings, crowding: Crowding = None) -> Covering:
        covering_type = settings.get_value('covering', 'start_covering_type')
        if covering_type == "covering_plus":
            return StartCoveringPlus()
        elif covering_type == "standard_covering":
            return StartStandardCovering()
        else:
            raise RuntimeError("No start covering selected")
