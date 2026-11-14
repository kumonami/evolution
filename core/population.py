from dataclasses import dataclass
import config.constants as constants
from core.genome import Genome
from core.region import Region
from core.species import Species

METABOLISM = {
    constants.HERBIVORE_TYPE: constants.HERBIVORE_METABOLISM,
    constants.OMNIVORE_TYPE: constants.OMNIVORE_METABOLISM,
    constants.CARNIVORE_TYPE: constants.CARNIVORE_METABOLISM,
}


@dataclass
class Population:
    id: int
    species: Species
    genome: Genome
    region: Region
    size: int
    satiety: float = 1.0
    stress: float = 0.0
    cooldown: int = 0
    food_required: float = 0.0
    food_received: float = 0.0
    is_alive: bool = True
    born_tick: int = 0
    influenced: bool = False

    @property
    def total_need(self) -> float:
        return self.size * self.genome.food_need * METABOLISM[self.species.type_id]

    @property
    def meat_share(self) -> float:
        """
        Доля рациона, которую популяция добывает охотой.
        Травоядные 0, хищники 1. Всеядные берут больше мяса,
        когда растений в регионе не хватает на их потребность.
        """
        type_id = self.species.type_id
        if type_id == constants.CARNIVORE_TYPE:
            return 1.0
        if type_id == constants.OMNIVORE_TYPE:
            if self.region.plants_stock < self.total_need:
                return constants.OMNIVORE_MEAT_SHARE_SCARCE
            return constants.OMNIVORE_MEAT_SHARE
        return 0.0

    @property
    def plant_need(self) -> float:
        return self.total_need * (1 - self.meat_share)

    @property
    def meat_need(self) -> float:
        return self.total_need * self.meat_share

    def decrease(self, amount: int) -> None:
        self.size = max(0, self.size - int(amount))
