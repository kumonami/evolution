import config.constants as constants
from core.world import World
from domain.commands.commands import MutateCommand
from systems.base import commands_of


class MutationExecuteSystem:
    """
    Мутация выделяет из популяции группу мутантов с изменённым геномом.
    Мутанты остаются вариантом прежнего вида, а новый вид появляется
    только если они закрепились (см. SpeciationThinkSystem).
    """

    def process(self, world: World) -> None:
        for cmd in commands_of(world, MutateCommand):
            population = world.get_population(cmd.population_id)
            if not population or population.size < constants.MUTATION_MIN_SOURCE_SIZE:
                continue
            if world.populations_limit_reached(population.region):
                continue
            size = max(constants.EXTINCTION_LIMIT, int(population.size * constants.MUTANT_FRACTION))
            genome = population.genome.mutated(world.rng, cmd.strength, population.region.biome)
            population.size -= size
            world.add_population(population.species, genome, population.region, size,
                                 satiety=population.satiety, stress=population.stress,
                                 influenced=population.influenced)
