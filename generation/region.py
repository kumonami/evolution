from random import Random
import config.constants as constants
from core.biome import Biome
from core.region import Region


class RegionGenerator:
    @staticmethod
    def generate(rng: Random, id: int, biome: Biome, x: int, y: int) -> Region:
        return Region(
            id=id,
            coordinates=(x, y),
            biome=biome,
            plants_limit=biome.max_plants_multiplier * biome.plants_stock,
            plants_stock=min(biome.max_plants_multiplier * biome.plants_stock,
                             biome.plants_growth_rate * constants.PLANT_BIOMASS_TICKS),
            capacity=rng.randint(1000, 7000),
        )
