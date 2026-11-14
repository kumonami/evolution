from dataclasses import dataclass, field


@dataclass
class Command:
    population_id: int


@dataclass
class EatPlantsCommand(Command):
    amount: float


@dataclass
class HuntCommand(Command):
    food_amount: float
    kills: dict = field(default_factory=dict)


@dataclass
class BornCommand(Command):
    count: int


@dataclass
class MutateCommand(Command):
    strength: float


@dataclass
class ShrinkCommand(Command):
    amount: int
    reason: str


@dataclass
class KillCommand(Command):
    reason: str


@dataclass
class MigrateCommand(Command):
    target_region_id: int


@dataclass
class SplitCommand(Command):
    target_region_id: int
    size: int
    reason: str


@dataclass
class MergeCommand(Command):
    absorbed_id: int


@dataclass
class SpeciateCommand(Command):
    pass
