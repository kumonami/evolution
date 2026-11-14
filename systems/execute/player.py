import config.constants as constants
from core.genome import GENE_LABELS, GENES, clamp_gene
from core.world import World
from domain.commands.commands import PlayerCommand
from domain.intents import AddPlants, AdjustWater, NudgeGene, ResizeRegion
from events.event import EventType
from systems.base import commands_of


class PlayerExecuteSystem:
    """
    Применяет вмешательство игрока. Любое изменение среды или генома помечает
    затронутые популяции как influenced, и виды, которые от них произойдут,
    попадут в дерево эволюции как результат косвенного влияния игрока.
    """

    def process(self, world: World) -> None:
        for cmd in commands_of(world, PlayerCommand):
            intent = cmd.intent
            if isinstance(intent, AdjustWater):
                self._water(world, intent)
            elif isinstance(intent, AddPlants):
                self._plants(world, intent)
            elif isinstance(intent, ResizeRegion):
                self._resize(world, intent)
            elif isinstance(intent, NudgeGene):
                self._nudge(world, intent)

    def _touch_region(self, world: World, region) -> None:
        for population in world.populations_in(region):
            population.influenced = True

    def _water(self, world: World, intent: AdjustWater) -> None:
        region = world.get_region(intent.region_id)
        if not region:
            return
        biome = region.biome
        biome.humidity = max(0.0, min(100.0, biome.humidity + intent.delta))
        biome.ability_demand["swim"] = biome.humidity / 200
        self._touch_region(world, region)
        world.logger.log(world.tick, EventType.PLAYER,
                         f"Влажность региона {region} теперь {biome.humidity:.0f}")

    def _plants(self, world: World, intent: AddPlants) -> None:
        region = world.get_region(intent.region_id)
        if not region:
            return
        region.grow_plants(intent.amount)
        self._touch_region(world, region)
        world.logger.log(world.tick, EventType.PLAYER,
                         f"В регион {region} добавлено {intent.amount:.0f} растений")

    def _resize(self, world: World, intent: ResizeRegion) -> None:
        region = world.get_region(intent.region_id)
        if not region:
            return
        region.capacity = max(constants.MIN_REGION_CAPACITY, region.capacity + intent.delta)
        self._touch_region(world, region)
        world.logger.log(world.tick, EventType.PLAYER,
                         f"Вместимость региона {region} теперь {region.capacity}")

    def _nudge(self, world: World, intent: NudgeGene) -> None:
        population = world.get_population(intent.population_id)
        if not population or intent.gene not in GENES:
            return
        value = getattr(population.genome, intent.gene) + intent.delta
        setattr(population.genome, intent.gene, clamp_gene(value))
        population.influenced = True
        world.logger.log(world.tick, EventType.PLAYER,
                         f"Признак «{GENE_LABELS[intent.gene]}» популяции {population.id} сдвинут на {intent.delta:+.0f}")
