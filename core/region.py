from typing import Tuple
from core.biome import Biome


class Region:
    def __init__(self, id: int, coordinates: Tuple[int, int], biome: Biome,
                 plants_limit: float, plants_stock: float, capacity: int):
        self.id = id
        self.coordinates = coordinates
        self.biome = biome
        self.plants_limit = plants_limit
        self.plants_stock = plants_stock
        self.capacity = capacity

    def __str__(self) -> str:
        return f"({self.coordinates[0]}, {self.coordinates[1]}) {self.biome.name}"

    @property
    def plants_growth_rate(self) -> float:
        return self.biome.plants_growth_rate

    def get_x(self) -> int:
        return self.coordinates[0]

    def get_y(self) -> int:
        return self.coordinates[1]

    def grow_plants(self, amount: float) -> None:
        self.plants_stock = min(self.plants_limit, self.plants_stock + amount)

    def consume_plants(self, amount: float) -> None:
        self.plants_stock = max(0.0, self.plants_stock - amount)
