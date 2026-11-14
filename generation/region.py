from random import Random
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
            plants_stock=biome.plants_stock,
            capacity=rng.randint(1000, 7000),
        )
