from enum import Enum
from random import Random
from core.biome import Biome
import config.constants as constants


class BiomeType(Enum):
    FOREST = (constants.FOREST_TYPE_ID, "forest", 70, 40, 100, 200, 1, {"climb": 0.5})
    DESERT = (constants.DESERT_TYPE_ID, "desert", 10, 90, 30, 50, 10, {"dig": 0.6})
    MOUNTAINS = (constants.MOUNTAINS_TYPE_ID, "mountains", 30, 20, 60, 100, 5, {"climb": 0.6, "fly": 0.3})

    def __init__(self, biome_id, biome_name, humidity, temperature,
                 max_plants_multiplier, initial_plant_stock, complexity, abilities):
        self.id = biome_id
        self.biome_name = biome_name
        self.humidity = humidity
        self.temperature = temperature
        self.max_plants_multiplier = max_plants_multiplier
        self.initial_plant_stock = initial_plant_stock
        self.complexity = complexity
        self.abilities = abilities


class BiomeGenerator:
    @staticmethod
    def generate(rng: Random) -> Biome:
        biome_type = rng.choice(list(BiomeType))
        humidity = max(0, min(100, biome_type.humidity + rng.randint(-2, 2)))
        temperature = max(0, min(100, biome_type.temperature + rng.randint(-2, 2)))
        demand = dict(biome_type.abilities)
        demand["swim"] = humidity / 200
        return Biome(
            id=biome_type.id,
            name=biome_type.biome_name,
            humidity=humidity,
            temperature=temperature,
            max_plants_multiplier=biome_type.max_plants_multiplier,
            plants_stock=biome_type.initial_plant_stock,
            complexity=biome_type.complexity,
            ability_demand=demand,
        )
