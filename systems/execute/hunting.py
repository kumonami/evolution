from core.world import World
from domain.commands.commands import HuntCommand
from events.event import EventType
from systems.base import commands_of


class HuntingExecuteSystem:
    def process(self, world: World) -> None:
        for cmd in commands_of(world, HuntCommand):
            predator = world.get_population(cmd.population_id)
            if not predator:
                continue
            predator.food_received += cmd.food_amount
            for prey_id, killed in cmd.kills.items():
                prey = world.get_population(prey_id)
                if prey:
                    prey.decrease(killed)
            world.logger.log(
                world.tick, EventType.HUNTING,
                f"Популяция {predator.id} добыла {cmd.food_amount:.1f} еды, жертв: {sum(cmd.kills.values())}",
            )
