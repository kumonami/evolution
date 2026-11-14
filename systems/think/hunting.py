import config.constants as constants
from core.population import Population
from core.world import World
from events.world import WorldEvent, WorldEventType, HuntPayload


class HuntingThinkSystem:
    """
    Охота хищников и всеядных на другие популяции региона.
    Число попыток за тик пропорционально размеру хищной популяции и голоду,
    удачность определяется атакой хищника против защиты жертвы. Сильный
    хищник убивает заметно больше, а съедает лишь сколько ему нужно:
    избыток убитых остаётся зря, так что сила видна и на численности жертв.
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
        attempts = (
            predator.size * constants.HUNT_RATE * predator.meat_share
            * max(0.3, 1.5 - predator.satiety)
        )
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
            if attempts <= 0:
                break
            catch = self._catch_chance(predator, prey) * pool[prey.id] / (pool[prey.id] + constants.HUNT_REFUGE)
            catch = max(0.02, catch)
            reachable = int(pool[prey.id] * constants.MAX_HUNT_FRACTION * catch * 2)
            killed = min(world.round_random(attempts * catch), reachable)
            if killed <= 0:
                continue
            pool[prey.id] -= killed
            kills[prey.id] = killed
            gained += killed * prey.genome.prey_value
            attempts -= killed / catch
        if not kills:
            return None
        return WorldEvent[HuntPayload](
            type=WorldEventType.HUNT,
            population_id=predator.id,
            payload=HuntPayload(food_amount=min(gained, predator.meat_need), kills=kills),
        )

    @staticmethod
    def _catch_chance(predator: Population, prey: Population) -> float:
        diff = predator.genome.attack - prey.genome.defense
        return max(0.05, min(0.95, 0.5 + diff / constants.HUNT_CATCH_SPREAD))
