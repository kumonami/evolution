import config.constants as constants
from core.world import World
from events.world import (
    WorldEvent, WorldEventType, StarvationPayload, ShortagePayload,
)
from systems.think.scouting import find_better_region


class HungerThinkSystem:
    """
    Оценка сытости популяций. При голоде часть особей гибнет, а если
    миграция не на кулдауне и есть более кормный соседний регион,
    формируется событие нехватки еды с указанием цели миграции.
    """

    def process(self, world: World) -> None:
        threshold = constants.HUNGER_THRESHOLD
        for population in world.living_populations():
            satiety = population.satiety
            if satiety >= threshold:
                continue
            deaths = world.round_random(
                population.size * constants.STARVATION_RATE * (1 - satiety / threshold)
            )
            if deaths > 0:
                world.events.append(
                    WorldEvent[StarvationPayload](
                        type=WorldEventType.STARVATION,
                        population_id=population.id,
                        payload=StarvationPayload(deaths=deaths),
                    )
                )
            if population.cooldown > 0:
                continue
            target = find_better_region(world, population)
            if target:
                world.events.append(
                    WorldEvent[ShortagePayload](
                        type=WorldEventType.FOOD_SHORTAGE,
                        population_id=population.id,
                        payload=ShortagePayload(severity=1 - satiety, target_region_id=target.id),
                    )
                )
