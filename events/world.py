from dataclasses import dataclass, field
from enum import Enum
from typing import Generic, Optional, TypeVar

T = TypeVar("T")


class WorldEventType(Enum):
    FEED = 1
    HUNT = 2
    BIRTH = 3
    MUTATION = 4
    STARVATION = 5
    EXTINCTION = 6
    FOOD_SHORTAGE = 7
    OVERPOPULATION = 8
    EXPANSION = 9
    MERGE = 10
    SPECIATION = 11


@dataclass
class WorldEvent(Generic[T]):
    type: WorldEventType
    population_id: int
    payload: T

    @property
    def severity(self) -> Optional[float]:
        return getattr(self.payload, "severity", None)


@dataclass
class FeedPayload:
    amount: float


@dataclass
class HuntPayload:
    food_amount: float
    kills: dict = field(default_factory=dict)


@dataclass
class BirthPayload:
    count: int


@dataclass
class MutationPayload:
    strength: float


@dataclass
class StarvationPayload:
    deaths: int


@dataclass
class DeathPayload:
    reason: str


@dataclass
class ShortagePayload:
    severity: float
    target_region_id: int


@dataclass
class SplitPayload:
    severity: float
    target_region_id: int
    split_size: int
    reason: str


@dataclass
class SpeciationPayload:
    distance: float


@dataclass
class MergePayload:
    absorbed_id: int
