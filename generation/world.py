from typing import Optional
import config.constants as constants
from core.world import World
from events.event import EventType
from generation.biome import BiomeGenerator
from generation.population import PopulationGenerator
from generation.region import RegionGenerator
from generation.species import GenomeGenerator, SpeciesType


class WorldGenerator:
    @staticmethod
    def generate(size_x: int = 3, size_y: int = 2, seed: Optional[int] = None,
                 verbose: bool = False) -> World:
        """
        Сначала собирается карта регионов с биомами, затем в каждый регион
        добавляется травоядный вид, а с шансом SECOND_SPECIES_CHANCE ещё
        всеядный или хищный, чтобы в мире сразу были пищевые цепочки.
        """
        world = World(seed=seed, verbose=verbose)
        WorldGenerator._build_regions(world, size_x, size_y)
        WorldGenerator._settle_species(world)
        return world

    @staticmethod
    def _build_regions(world: World, size_x: int, size_y: int) -> None:
        region_id = 0
        for x in range(size_x):
            for y in range(size_y):
                region_id += 1
                biome = BiomeGenerator.generate(world.rng)
                world.add_region(RegionGenerator.generate(world.rng, region_id, biome, x, y))

    @staticmethod
    def _settle_species(world: World) -> None:
        for region in world.regions.values():
            types = [SpeciesType.HERBIVORE]
            if world.rng.random() < constants.SECOND_SPECIES_CHANCE:
                types.append(world.rng.choice([SpeciesType.OMNIVORE, SpeciesType.CARNIVORE]))
            herbivore_size = None
            for species_type in types:
                genome = GenomeGenerator.generate(world.rng, region.biome, species_type)
                species = world.register_species(species_type.id, genome)
                size = WorldGenerator._start_size(world, species_type, herbivore_size)
                population = PopulationGenerator.generate(world, species, genome, region, size)
                if species_type is SpeciesType.HERBIVORE:
                    herbivore_size = population.size
                world.logger.log(
                    world.tick, EventType.WORLD,
                    f"В регион {region} добавлена популяция {population.id} вида {species.id} ({species_type.species_name})",
                )

    @staticmethod
    def _start_size(world: World, species_type: SpeciesType, herbivore_size):
        """
        Хищники и всеядные стартуют долей от численности травоядных региона,
        иначе в первые же тики они выедают жертв и вымирают.
        """
        if herbivore_size is None or species_type is SpeciesType.HERBIVORE:
            return None
        low, high = (constants.CARNIVORE_START_SHARE if species_type is SpeciesType.CARNIVORE
                     else constants.OMNIVORE_START_SHARE)
        return max(constants.MIN_START_SIZE, int(herbivore_size * world.rng.uniform(low, high)))
