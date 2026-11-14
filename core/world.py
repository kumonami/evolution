from random import Random
from typing import Optional
import random
import config.constants as constants
from core.genome import Genome
from core.population import Population
from core.region import Region
from core.species import Species
from logger.world import WorldLogger


class World:
    def __init__(self, seed: Optional[int] = None, verbose: bool = False):
        self.seed = seed if seed is not None else random.randrange(2 ** 32)
        self.rng = Random(self.seed)
        self.tick = 0
        self.logger = WorldLogger(verbose)
        self.regions: dict[int, Region] = {}
        self.populations: dict[int, Population] = {}
        self.species: dict[int, Species] = {}
        self.events: list = []
        self.commands: list = []
        self.history: list = []
        self._region_grid: dict[tuple, Region] = {}
        self._next_population_id = 1
        self._next_species_id = 1

    @property
    def is_running(self) -> bool:
        return len(self.populations) > 0

    def round_random(self, value: float) -> int:
        whole = int(value)
        return whole + (1 if self.rng.random() < value - whole else 0)

    def add_region(self, region: Region) -> None:
        self.regions[region.id] = region
        self._region_grid[tuple(region.coordinates)] = region

    def neighbors(self, region: Region) -> list[Region]:
        x, y = region.get_x(), region.get_y()
        cells = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
        return [self._region_grid[c] for c in cells if c in self._region_grid]

    def register_species(self, type_id: int, anchor: Genome,
                         parent_id: Optional[int] = None, origin: str = "natural") -> Species:
        species = Species(
            id=self._next_species_id,
            parent_id=parent_id,
            type_id=type_id,
            anchor=anchor.copy(),
            born_tick=self.tick,
            origin=origin,
        )
        self._next_species_id += 1
        self.species[species.id] = species
        return species

    def add_population(self, species: Species, genome: Genome, region: Region, size: int,
                       satiety: float = 1.0, stress: float = 0.0) -> Population:
        population = Population(
            id=self._next_population_id,
            species=species,
            genome=genome,
            region=region,
            size=size,
            satiety=satiety,
            stress=stress,
            born_tick=self.tick,
        )
        self._next_population_id += 1
        self.populations[population.id] = population
        return population

    def remove_population(self, population: Population) -> None:
        population.is_alive = False
        self.populations.pop(population.id, None)

    def get_population(self, population_id: int) -> Optional[Population]:
        return self.populations.get(population_id)

    def get_region(self, region_id: int) -> Optional[Region]:
        return self.regions.get(region_id)

    def living_populations(self) -> list[Population]:
        return [p for p in self.populations.values() if p.is_alive]

    def populations_in(self, region: Region) -> list[Population]:
        return [p for p in self.populations.values() if p.is_alive and p.region.id == region.id]

    def region_load(self, region: Region) -> float:
        total = sum(p.size for p in self.populations_in(region))
        return total / region.capacity

    def populations_limit_reached(self, region: Region) -> bool:
        return len(self.populations_in(region)) >= constants.MAX_POPULATIONS_PER_REGION
