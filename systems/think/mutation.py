import config.constants as constants
from core.world import World
from events.world import WorldEvent, WorldEventType, MutationPayload


class MutationThinkSystem:
    """
    Шанс мутации за тик растёт со стрессом популяции (голод, миграция).
    Мутация возможна только у достаточно крупной популяции
    и пока в регионе не исчерпан лимит популяций.
    """

    def process(self, world: World) -> None:
        for population in world.living_populations():
            if population.size < constants.MUTATION_MIN_SOURCE_SIZE:
                continue
            if world.populations_limit_reached(population.region):
                continue
            chance = constants.MUTATION_CHANCE * (1 + population.stress * constants.MUTATION_STRESS_BOOST)
            if world.rng.random() >= chance:
                continue
            world.events.append(
                WorldEvent[MutationPayload](
                    type=WorldEventType.MUTATION,
                    population_id=population.id,
                    payload=MutationPayload(strength=constants.MUTATION_STRENGTH * (1 + population.stress)),
                )
            )
