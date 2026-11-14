from core.world import World
from events.world import WorldEvent, WorldEventType, FeedPayload


class FeedingThinkSystem:
    """
    Распределение растений региона между популяциями, которым они нужны.
    Если растений меньше суммарной потребности, каждая популяция получает
    долю, пропорциональную своей потребности.
    """

    def process(self, world: World) -> None:
        for region in world.regions.values():
            eaters = [p for p in world.populations_in(region) if p.plant_need > 0]
            total_need = sum(p.plant_need for p in eaters)
            if total_need <= 0:
                continue
            ratio = min(1.0, region.plants_stock / total_need)
            for population in eaters:
                world.events.append(
                    WorldEvent[FeedPayload](
                        type=WorldEventType.FEED,
                        population_id=population.id,
                        payload=FeedPayload(amount=population.plant_need * ratio),
                    )
                )
