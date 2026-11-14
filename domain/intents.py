from dataclasses import dataclass


@dataclass
class AdjustWater:
    region_id: int
    delta: float


@dataclass
class AddPlants:
    region_id: int
    amount: float


@dataclass
class ResizeRegion:
    region_id: int
    delta: int


@dataclass
class NudgeGene:
    population_id: int
    gene: str
    delta: float
