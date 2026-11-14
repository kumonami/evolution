from dataclasses import dataclass, field


@dataclass
class Biome:
    id: int
    name: str
    humidity: float
    temperature: float
    max_plants_multiplier: int
    plants_stock: int
    complexity: int
    ability_demand: dict = field(default_factory=dict)

    @property
    def plants_growth_rate(self) -> float:
        return self.humidity * 10
