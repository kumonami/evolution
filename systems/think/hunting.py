import config.constants as constants
from core.population import Population
from core.world import World
from events.world import WorldEvent, WorldEventType, HuntPayload


class HuntingThinkSystem:
    """
    Охота хищников и всеядных на другие популяции региона.
    Удачность определяется атакой хищника против защиты жертвы: чем она выше,
    тем большая доля популяции-жертвы доступна для охоты за тик.
    Численность жертв уменьшается в локальном пуле по ходу расчёта,
    чтобы несколько хищников не съели одну и ту же добычу дважды.
    """

    def process(self, world: World) -> None:
        for region in world.regions.values():
            local = world.populations_in(region)
            predators = [p for p in local if p.meat_need > 0]
            if not predators:
                continue
            world.rng.shuffle(predators)
            pool = {p.id: p.size for p in local}
            for predator in predators:
                event = self._hunt(world, predator, local, pool)
                if event:
                    world.events.append(event)

    def _hunt(self, world: World, predator: Population, local: list, pool: dict):
        need = predator.meat_need
        gained = 0.0
        kills = {}
        preys = [
            q for q in local
            if q.species.type_id != constants.CARNIVORE_TYPE
            and q.species.id != predator.species.id
            and pool[q.id] > 0
        ]
        world.rng.shuffle(preys)
        for prey in preys:
            if need <= 0:
                break
            value = prey.genome.prey_value
            catch = self._catch_chance(predator, prey)
            reachable = pool[prey.id] * constants.MAX_HUNT_FRACTION * catch * 2
            killed = min(world.round_random(need / value), int(reachable))
            if killed <= 0:
                continue
            pool[prey.id] -= killed
            kills[prey.id] = killed
            gained += killed * value
            need -= killed * value
        if not kills:
            return None
        return WorldEvent[HuntPayload](
            type=WorldEventType.HUNT,
            population_id=predator.id,
            payload=HuntPayload(food_amount=gained, kills=kills),
        )

    @staticmethod
    def _catch_chance(predator: Population, prey: Population) -> float:
        diff = predator.genome.attack - prey.genome.defense
        return max(0.05, min(0.95, 0.5 + diff / 200))
