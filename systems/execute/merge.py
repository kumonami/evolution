from core.genome import Genome
from core.world import World
from domain.commands.commands import MergeCommand
from systems.base import commands_of


class MergeExecuteSystem:
    def process(self, world: World) -> None:
        for cmd in commands_of(world, MergeCommand):
            survivor = world.get_population(cmd.population_id)
            absorbed = world.get_population(cmd.absorbed_id)
            if not survivor or not absorbed:
                continue
            survivor.genome = Genome.blend(survivor.genome, survivor.size, absorbed.genome, absorbed.size)
            total = survivor.size + absorbed.size
            survivor.satiety = (survivor.satiety * survivor.size + absorbed.satiety * absorbed.size) / total
            survivor.stress = max(survivor.stress, absorbed.stress)
            survivor.influenced = survivor.influenced or absorbed.influenced
            survivor.size = total
            world.remove_population(absorbed)
