import config.constants as constants
from core.world import World
from events.world import WorldEvent, WorldEventType, MergePayload


class MergeThinkSystem:
    """
    Слияние близких по геному популяций одного вида в одном регионе.
    Меньшая популяция поглощается большей, цепочки слияний исключены.
    """

    def process(self, world: World) -> None:
        for region in world.regions.values():
            local = sorted(world.populations_in(region), key=lambda p: -p.size)
            used = set()
            for i, survivor in enumerate(local):
                if survivor.id in used:
                    continue
                for other in local[i + 1:]:
                    if other.id in used or other.species.id != survivor.species.id:
                        continue
                    if survivor.genome.distance(other.genome) >= constants.MERGE_DISTANCE:
                        continue
                    used.update((survivor.id, other.id))
                    world.events.append(
                        WorldEvent[MergePayload](
                            type=WorldEventType.MERGE,
                            population_id=survivor.id,
                            payload=MergePayload(absorbed_id=other.id),
                        )
                    )
                    break
