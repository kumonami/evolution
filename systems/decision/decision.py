from collections import defaultdict
import config.constants as constants
from core.world import World
from domain.commands.commands import (
    BornCommand, EatPlantsCommand, HuntCommand, KillCommand, MergeCommand,
    MigrateCommand, MutateCommand, PlayerCommand, ShrinkCommand, SpeciateCommand, SplitCommand,
)
from events.world import WorldEvent, WorldEventType

DIRECT = {
    WorldEventType.FEED: lambda e: EatPlantsCommand(e.population_id, e.payload.amount),
    WorldEventType.HUNT: lambda e: HuntCommand(e.population_id, e.payload.food_amount, e.payload.kills),
    WorldEventType.BIRTH: lambda e: BornCommand(e.population_id, e.payload.count),
    WorldEventType.MUTATION: lambda e: MutateCommand(e.population_id, e.payload.strength),
    WorldEventType.STARVATION: lambda e: ShrinkCommand(e.population_id, e.payload.deaths, "starvation"),
    WorldEventType.PLAYER_ACTION: lambda e: PlayerCommand(e.payload.intent),
    WorldEventType.SPECIATION: lambda e: SpeciateCommand(e.population_id),
    WorldEventType.MERGE: lambda e: MergeCommand(e.population_id, e.payload.absorbed_id),
}

RELOCATION = {
    WorldEventType.FOOD_SHORTAGE: (
        constants.MIGRATION_SEVERITY,
        lambda e: MigrateCommand(e.population_id, e.payload.target_region_id),
    ),
    WorldEventType.OVERPOPULATION: (
        constants.OVERPOPULATION_SEVERITY,
        lambda e: SplitCommand(e.population_id, e.payload.target_region_id, e.payload.split_size, e.payload.reason),
    ),
    WorldEventType.EXPANSION: (
        0.0,
        lambda e: SplitCommand(e.population_id, e.payload.target_region_id, e.payload.split_size, e.payload.reason),
    ),
}


class DecisionSystem:
    """
    Связующее звено между think и execute. События одной популяции
    сводятся к набору команд: прямые события превращаются в команды как есть,
    а конкурирующие события переселения (миграция, раскол, колонизация)
    сравниваются по severity, и исполняется только сильнейшее из тех,
    что превысили свой порог. Событие вымирания отменяет остальные.
    """

    def process(self, world: World) -> None:
        by_population = defaultdict(list)
        for event in world.events:
            by_population[event.population_id].append(event)
        for population_id, events in by_population.items():
            self._decide(world, population_id, events)

    def _decide(self, world: World, population_id: int, events: list[WorldEvent]) -> None:
        extinction = next((e for e in events if e.type == WorldEventType.EXTINCTION), None)
        if extinction:
            world.commands.append(KillCommand(population_id, extinction.payload.reason))
            return
        relocation = []
        for event in events:
            builder = DIRECT.get(event.type)
            if builder:
                world.commands.append(builder(event))
            elif event.type in RELOCATION:
                relocation.append(event)
        if not relocation:
            return
        winner = max(relocation, key=lambda e: e.severity)
        threshold, builder = RELOCATION[winner.type]
        if winner.severity >= threshold:
            world.commands.append(builder(winner))
