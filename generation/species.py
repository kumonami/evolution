from enum import Enum
from random import Random
import config.constants as constants
from core.biome import Biome
from core.genome import ABILITIES, Genome, clamp_gene


class SpeciesType(Enum):
    HERBIVORE = (constants.HERBIVORE_TYPE, "herbivore")
    OMNIVORE = (constants.OMNIVORE_TYPE, "omnivore")
    CARNIVORE = (constants.CARNIVORE_TYPE, "carnivore")

    def __init__(self, id_: int, name_: str):
        self.id = id_
        self.species_name = name_


class GenomeGenerator:
    @staticmethod
    def generate(rng: Random, biome: Biome, species_type: SpeciesType) -> Genome:
        """
        Начальные характеристики подчиняются компромиссу: сумма размера,
        скорости и силы фиксирована, поэтому крупный вид медленнее и наоборот.
        Температура близка к биому рождения, востребованные умения слегка развиты.
        """
        total = constants.SPECIES_INITIAL_CHARACTERISTICS
        speed = rng.randint(max(1, total - 200), 100)
        remaining = total - speed
        size = rng.randint(max(0, remaining - 100), min(100, remaining))
        power = remaining - size
        if species_type is SpeciesType.CARNIVORE:
            size, power = min(size, power), max(size, power)
        genome = Genome(
            size=size,
            speed=speed,
            power=power,
            fecundity=rng.randint(30, 70),
            temperature=clamp_gene(biome.temperature + rng.randint(-10, 10)),
        )
        for ability in ABILITIES:
            weight = biome.ability_demand.get(ability, 0.0)
            if weight > 0:
                setattr(genome, ability, clamp_gene(weight * rng.randint(20, 60)))
        return genome
