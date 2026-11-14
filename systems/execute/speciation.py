from core.world import World
from domain.commands.commands import SpeciateCommand
from events.event import EventType
from systems.base import commands_of


class SpeciationExecuteSystem:
    def process(self, world: World) -> None:
        for cmd in commands_of(world, SpeciateCommand):
            population = world.get_population(cmd.population_id)
            if not population:
                continue
            parent = population.species
            species = world.register_species(parent.type_id, population.genome, parent_id=parent.id)
            population.species = species
            world.logger.log(
                world.tick, EventType.EVOLUTION,
                f"Новый вид {species.id} от вида {parent.id} в регионе {population.region}",
            )
