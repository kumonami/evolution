import config.constants as constants
from core.world import World


class MetabolismSystem:
    """
    Обновляет сытость по итогам питания. Сытость инерционна: это скользящее
    среднее доли удовлетворённой потребности. Голод накапливает стресс,
    который затухает при хорошем питании.
    """

    def process(self, world: World) -> None:
        inertia = constants.SATIETY_INERTIA
        for population in world.living_populations():
            required = population.food_required
            ratio = 1.0 if required <= 0 else min(1.0, population.food_received / required)
            population.satiety = inertia * population.satiety + (1 - inertia) * ratio
            hunger_stress = max(0.0, 1 - population.satiety / constants.HUNGER_THRESHOLD)
            population.stress = max(population.stress * 0.9, hunger_stress)
