import config.constants as constants
from core.world import World
from events.event import EventType


class HistorySystem:
    """
    Фиксирует вымирание видов и раз в HISTORY_INTERVAL тиков сохраняет снимок
    мира: численность и средний геном по каждому живому виду.
    """

    def process(self, world: World) -> None:
        alive = {}
        for population in world.living_populations():
            alive.setdefault(population.species.id, []).append(population)
        for species in world.species.values():
            if not species.is_extinct and species.id not in alive:
                species.extinct_tick = world.tick
                world.logger.log(world.tick, EventType.EVOLUTION, f"Вид {species.id} вымер")
        if world.tick % constants.HISTORY_INTERVAL == 0:
            world.history.append({
                "tick": world.tick,
                "species": {sid: self._summary(pops) for sid, pops in alive.items()},
            })

    @staticmethod
    def _summary(populations: list) -> dict:
        total = sum(p.size for p in populations)
        genes = populations[0].genome.as_dict().keys()
        average = {
            gene: sum(getattr(p.genome, gene) * p.size for p in populations) / total
            for gene in genes
        }
        return {"size": total, "genome": average}
