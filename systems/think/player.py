from core.world import World
from events.world import PlayerPayload, WorldEvent, WorldEventType


class PlayerThinkSystem:
    """
    Превращает накопленные запросы игрока в события. Запросы живут в
    world.intents между тиками и забираются целиком при каждом проходе.
    """

    def process(self, world: World) -> None:
        intents, world.intents = world.intents, []
        for intent in intents:
            world.events.append(
                WorldEvent[PlayerPayload](
                    type=WorldEventType.PLAYER_ACTION,
                    population_id=getattr(intent, "population_id", 0),
                    payload=PlayerPayload(intent=intent),
                )
            )
