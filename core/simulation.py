from dataclasses import dataclass, field
from core.world import World
from systems.decision.decision import DecisionSystem
from systems.execute.death import KillExecuteSystem, ShrinkExecuteSystem
from systems.execute.feeding import FeedingExecuteSystem
from systems.execute.hunting import HuntingExecuteSystem
from systems.execute.merge import MergeExecuteSystem
from systems.execute.migration import MigrationExecuteSystem
from systems.execute.mutation import MutationExecuteSystem
from systems.execute.player import PlayerExecuteSystem
from systems.execute.reproduction import ReproductionExecuteSystem
from systems.execute.speciation import SpeciationExecuteSystem
from systems.physics.history import HistorySystem
from systems.physics.metabolism import MetabolismSystem
from systems.physics.plant_growth import PlantGrowthSystem
from systems.physics.upkeep import UpkeepSystem
from systems.think.extinction import ExtinctionThinkSystem
from systems.think.feeding import FeedingThinkSystem
from systems.think.hunger import HungerThinkSystem
from systems.think.hunting import HuntingThinkSystem
from systems.think.merge import MergeThinkSystem
from systems.think.mutation import MutationThinkSystem
from systems.think.player import PlayerThinkSystem
from systems.think.reproduction import ReproductionThinkSystem
from systems.think.speciation import SpeciationThinkSystem
from systems.think.spread import SpreadThinkSystem


@dataclass
class Stage:
    name: str
    think: list
    execute: list
    after: list = field(default_factory=list)


class Simulation:
    """
    Один тик мира: вмешательство игрока -> physics -> стадия питания -> стадия жизни -> история.
    Каждая стадия проходит цикл think -> decision -> execute, после чего
    события и команды очищаются. Системы не знают друг о друге и
    общаются только через события и команды.
    """

    def __init__(self, world: World):
        self.world = world
        self.decision = DecisionSystem()
        self.before = [PlantGrowthSystem(), UpkeepSystem()]
        self.intervention = Stage(
            name="intervention",
            think=[PlayerThinkSystem()],
            execute=[PlayerExecuteSystem()],
        )
        self.stages = [
            Stage(
                name="nutrition",
                think=[FeedingThinkSystem(), HuntingThinkSystem()],
                execute=[FeedingExecuteSystem(), HuntingExecuteSystem()],
                after=[MetabolismSystem()],
            ),
            Stage(
                name="life",
                think=[
                    ExtinctionThinkSystem(), HungerThinkSystem(), ReproductionThinkSystem(),
                    SpreadThinkSystem(), MutationThinkSystem(), SpeciationThinkSystem(), MergeThinkSystem(),
                ],
                execute=[
                    ShrinkExecuteSystem(), ReproductionExecuteSystem(), MutationExecuteSystem(),
                    MigrationExecuteSystem(), SpeciationExecuteSystem(), MergeExecuteSystem(), KillExecuteSystem(),
                ],
            ),
        ]
        self.after = [HistorySystem()]

    def apply_interventions(self) -> None:
        """
        Применяет накопленные запросы игрока немедленно, не продвигая время.
        Вызывается интерфейсом после действия и в начале каждого тика.
        """
        if self.world.intents:
            self._run_stage(self.intervention)

    def _run_stage(self, stage: Stage) -> None:
        world = self.world
        for system in stage.think:
            system.process(world)
        self.decision.process(world)
        for system in stage.execute:
            system.process(world)
        world.events.clear()
        world.commands.clear()
        for system in stage.after:
            system.process(world)

    def tick(self) -> None:
        world = self.world
        self.apply_interventions()
        for system in self.before:
            system.process(world)
        for stage in self.stages:
            self._run_stage(stage)
        for system in self.after:
            system.process(world)
        world.tick += 1

    def run(self, ticks: int) -> None:
        for _ in range(ticks):
            if not self.world.is_running:
                break
            self.tick()
