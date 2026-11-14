import config.constants as constants
from core.world import World
from events.world import WorldEvent, WorldEventType, SpeciationPayload


class SpeciationThinkSystem:
    """
    Новый вид признаётся, когда популяция закрепилась (достаточно крупная
    и существует не меньше SPECIATION_MIN_AGE тиков) и её геном ушёл
    от родоначального генома вида дальше SPECIATION_THRESHOLD.
    Так недолговечные мутанты не засоряют дерево эволюции.
    """

    def process(self, world: World) -> None:
        for population in world.living_populations():
            if population.size < constants.SPECIATION_MIN_SIZE:
                continue
            if world.tick - population.born_tick < constants.SPECIATION_MIN_AGE:
                continue
            distance = population.genome.distance(population.species.anchor)
            if distance >= constants.SPECIATION_THRESHOLD:
                world.events.append(
                    WorldEvent[SpeciationPayload](
                        type=WorldEventType.SPECIATION,
                        population_id=population.id,
                        payload=SpeciationPayload(distance=distance),
                    )
                )
