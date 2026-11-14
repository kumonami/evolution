from typing import Optional
import config.constants as constants
from core.population import Population
from core.region import Region
from core.world import World

SCORE_CAP = 2.0


def food_score(world: World, region: Region, population: Population) -> float:
    """
    Оценка обеспеченности популяции едой в регионе: отношение предложения
    к суммарному спросу всех конкурентов, включая саму популяцию.
    Для растительной и мясной частей рациона считается отдельно.
    """
    others = [q for q in world.populations_in(region) if q.id != population.id]
    share = population.meat_share
    score = 0.0
    if share < 1:
        supply = region.plants_stock + region.plants_growth_rate
        demand = population.plant_need + sum(q.plant_need for q in others)
        score += (1 - share) * min(SCORE_CAP, supply / demand if demand > 0 else SCORE_CAP)
    if share > 0:
        supply = sum(
            q.size * q.genome.prey_value for q in others
            if q.species.type_id != constants.CARNIVORE_TYPE and q.species.id != population.species.id
        )
        demand = population.meat_need + sum(q.meat_need for q in others)
        score += share * min(SCORE_CAP, supply / demand if demand > 0 else 0.0)
    return score * population.genome.fitness(region.biome)


def find_better_region(world: World, population: Population) -> Optional[Region]:
    current = food_score(world, population.region, population)
    best, best_score = None, current * constants.BETTER_REGION_MARGIN
    for region in world.neighbors(population.region):
        score = food_score(world, region, population)
        if score > best_score:
            best, best_score = region, score
    return best


def find_any_neighbor(world: World, population: Population) -> Optional[Region]:
    candidates = world.neighbors(population.region)
    if not candidates:
        return None
    return world.rng.choice(candidates)
