from dataclasses import dataclass, field


@dataclass
class Command:
    pass


@dataclass
class EatPlantsCommand(Command):
    population_id: int
    amount: float


@dataclass
class HuntCommand(Command):
    population_id: int
    food_amount: float
    kills: dict = field(default_factory=dict)


@dataclass
class BornCommand(Command):
    population_id: int
    count: int


@dataclass
class MutateCommand(Command):
    population_id: int
    strength: float


@dataclass
class ShrinkCommand(Command):
    population_id: int
    amount: int
    reason: str


@dataclass
class KillCommand(Command):
    population_id: int
    reason: str


@dataclass
class MigrateCommand(Command):
    population_id: int
    target_region_id: int


@dataclass
class SplitCommand(Command):
    population_id: int
    target_region_id: int
    size: int
    reason: str


@dataclass
class MergeCommand(Command):
    population_id: int
    absorbed_id: int


@dataclass
class SpeciateCommand(Command):
    population_id: int


@dataclass
class PlayerCommand(Command):
    intent: object
