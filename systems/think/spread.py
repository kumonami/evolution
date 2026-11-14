import config.constants as constants
from core.world import World
from events.world import WorldEvent, WorldEventType, SplitPayload
from systems.think.scouting import find_any_neighbor, find_better_region


class SpreadThinkSystem:
    """
    Расселение популяций. Перенаселённый регион даёт событие с severity,
    а сытая крупная популяция иногда отправляет колонистов в соседний регион
    с минимальной severity, чтобы вид постепенно осваивал карту.
    """

    def process(self, world: World) -> None:
        for population in world.living_populations():
            if population.cooldown > 0:
                continue
            load = world.region_load(population.region)
            if load > constants.OVERPOPULATION_LOAD:
                target = find_better_region(world, population) or find_any_neighbor(world, population)
                if target:
                    self._emit(world, population, target, load - constants.OVERPOPULATION_LOAD + 0.1,
                               int(population.size * constants.SPLIT_FRACTION), WorldEventType.OVERPOPULATION, "overpopulation")
                continue
            if population.size < constants.EXPANSION_MIN_SIZE or population.satiety < 0.8:
                continue
            if world.rng.random() >= constants.EXPANSION_CHANCE:
                continue
            target = find_any_neighbor(world, population)
            if target:
                self._emit(world, population, target, constants.EXPANSION_SEVERITY,
                           int(population.size * constants.EXPANSION_FRACTION), WorldEventType.EXPANSION, "expansion")

    @staticmethod
    def _emit(world, population, target, severity, size, event_type, reason) -> None:
        world.events.append(
            WorldEvent[SplitPayload](
                type=event_type,
                population_id=population.id,
                payload=SplitPayload(severity=severity, target_region_id=target.id,
                                     split_size=size, reason=reason),
            )
        )
