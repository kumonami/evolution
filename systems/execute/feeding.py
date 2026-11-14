from core.world import World
from domain.commands.commands import EatPlantsCommand
from systems.base import commands_of


class FeedingExecuteSystem:
    def process(self, world: World) -> None:
        for cmd in commands_of(world, EatPlantsCommand):
            population = world.get_population(cmd.population_id)
            if not population:
                continue
            population.region.consume_plants(cmd.amount)
            population.food_received += cmd.amount
