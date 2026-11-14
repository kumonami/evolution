from core.world import World
from domain.commands.commands import BornCommand
from systems.base import commands_of


class ReproductionExecuteSystem:
    def process(self, world: World) -> None:
        for cmd in commands_of(world, BornCommand):
            population = world.get_population(cmd.population_id)
            if population:
                population.size += cmd.count
