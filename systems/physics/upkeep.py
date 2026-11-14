import config.constants as constants
from core.world import World


class UpkeepSystem:
    """
    Начало тика: естественная смертность (выше у плохо приспособленных),
    сброс кулдауна миграции и подсчёт потребности в еде на текущий размер.
    """

    def process(self, world: World) -> None:
        for population in world.living_populations():
            fitness = population.genome.fitness(population.region.biome)
            rate = constants.NATURAL_MORTALITY * (2 - fitness)
            population.decrease(world.round_random(population.size * rate))
            population.cooldown = max(0, population.cooldown - 1)
            population.food_required = population.total_need
            population.food_received = 0.0
