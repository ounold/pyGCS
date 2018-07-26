from modules.Crowding.crowding import Crowding
from modules.Crowding.dummy_crowding import DummyCrowding
from modules.Crowding.standard_crowding import StandardCrowding
from settings.settings import Settings


class CrowdingDeterminer:

    @staticmethod
    def get_crowding(settings: Settings) -> Crowding:
        crowding_enabled = settings.get_value('crowding', 'crowding_enabled') == "True"
        if crowding_enabled:
            return StandardCrowding(settings)
        else:
            return DummyCrowding(settings)
