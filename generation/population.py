from typing import Optional
from core.genome import Genome
from core.population import Population
from core.region import Region
from core.species import Species
from core.world import World
import config.constants as constants


class PopulationGenerator:
    @staticmethod
    def generate(world: World, species: Species, genome: Genome, region: Region,
                 size: Optional[int] = None) -> Population:
        if size is None:
            size = world.rng.randint(constants.MIN_INITIAL_POPULATION_SIZE, constants.MAX_INITIAL_POPULATION_SIZE)
        return world.add_population(species, genome, region, size)
