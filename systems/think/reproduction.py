import config.constants as constants
from core.world import World
from events.world import WorldEvent, WorldEventType, BirthPayload


class ReproductionThinkSystem:
    """
    Рождаемость популяции за тик: базовая ставка, плодовитость генома,
    сытость, приспособленность к биому и заполненность региона.
    Крупные виды размножаются медленнее.
    """

    def process(self, world: World) -> None:
        for population in world.living_populations():
            region = population.region
            fitness = population.genome.fitness(region.biome)
            load = world.region_load(region)
            fecundity = 0.5 + population.genome.fecundity / 100
            body = 1 - population.genome.size / 250
            rate = (
                constants.REPRODUCTION_BASE * fecundity * body
                * population.satiety * fitness * max(0.0, 1 - load)
            )
            births = world.round_random(population.size * rate)
            if births > 0:
                world.events.append(
                    WorldEvent[BirthPayload](
                        type=WorldEventType.BIRTH,
                        population_id=population.id,
                        payload=BirthPayload(count=births),
                    )
                )
