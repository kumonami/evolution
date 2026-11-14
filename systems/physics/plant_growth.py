import config.constants as constants
from core.world import World


class PlantGrowthSystem:
    """
    Прирост растений зависит от накопленной биомассы: при полном выедании
    запас почти не восстанавливается, а при запасе в PLANT_BIOMASS_TICKS
    тиков прироста растёт с полной скоростью. Поэтому нулевой запас
    означает перевыпас и голод травоядных.
    """

    def process(self, world: World) -> None:
        for region in world.regions.values():
            rate = region.plants_growth_rate
            reference = max(1.0, rate * constants.PLANT_BIOMASS_TICKS)
            factor = max(constants.PLANT_MIN_GROWTH, min(1.0, region.plants_stock / reference))
            region.grow_plants(rate * factor)
