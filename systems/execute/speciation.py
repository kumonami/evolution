from core.world import World
from domain.commands.commands import SpeciateCommand
from events.event import EventType
from systems.base import commands_of


class SpeciationExecuteSystem:
    """
    Регистрирует новый вид. Если популяция до этого подвергалась влиянию
    игрока, вид помечается как influenced (жёлтый в дереве эволюции),
    и метка с популяции снимается, чтобы дальнейшие виды были естественными.
    """

    def process(self, world: World) -> None:
        for cmd in commands_of(world, SpeciateCommand):
            population = world.get_population(cmd.population_id)
            if not population:
                continue
            parent = population.species
            origin = "influenced" if population.influenced else "natural"
            species = world.register_species(parent.type_id, population.genome,
                                             parent_id=parent.id, origin=origin)
            population.species = species
            population.influenced = False
            world.logger.log(
                world.tick, EventType.EVOLUTION,
                f"Новый вид {species.id} от вида {parent.id} в регионе {population.region}",
            )
