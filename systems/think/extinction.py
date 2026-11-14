import config.constants as constants
from core.world import World
from events.world import WorldEvent, WorldEventType, DeathPayload


class ExtinctionThinkSystem:
    def process(self, world: World) -> None:
        for population in world.living_populations():
            if population.size < constants.EXTINCTION_LIMIT:
                world.events.append(
                    WorldEvent[DeathPayload](
                        type=WorldEventType.EXTINCTION,
                        population_id=population.id,
                        payload=DeathPayload(reason="extinction"),
                    )
                )
