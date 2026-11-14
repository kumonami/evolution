import config.constants as constants
from core.world import World
from domain.commands.commands import KillCommand, ShrinkCommand
from events.event import EventType
from systems.base import commands_of


class ShrinkExecuteSystem:
    def process(self, world: World) -> None:
        for cmd in commands_of(world, ShrinkCommand):
            population = world.get_population(cmd.population_id)
            if population:
                population.decrease(cmd.amount)


class KillExecuteSystem:
    """
    Удаляет популяции из мира. Вымирание по размеру перепроверяется
    в момент исполнения, так как за стадию популяция могла вырасти.
    """

    def process(self, world: World) -> None:
        for cmd in commands_of(world, KillCommand):
            population = world.get_population(cmd.population_id)
            if not population:
                continue
            if cmd.reason == "extinction" and population.size >= constants.EXTINCTION_LIMIT:
                continue
            world.remove_population(population)
            world.logger.log(
                world.tick, EventType.DEATH,
                f"Популяция {population.id} (вид {population.species.id}) исчезла из региона {population.region}",
            )
