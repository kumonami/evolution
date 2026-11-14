from dataclasses import dataclass
from typing import Optional
from core.genome import Genome


@dataclass
class Species:
    id: int
    parent_id: Optional[int]
    type_id: int
    anchor: Genome
    born_tick: int = 0
    extinct_tick: Optional[int] = None
    origin: str = "natural"

    @property
    def is_extinct(self) -> bool:
        return self.extinct_tick is not None
