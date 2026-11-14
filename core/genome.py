from dataclasses import dataclass, replace
from random import Random

TRAITS = ("size", "speed", "power", "fecundity", "temperature")
ABILITIES = ("swim", "fly", "dig", "climb")
GENES = TRAITS + ABILITIES
MAX_GENE = 100.0


def clamp_gene(value: float) -> float:
    return max(0.0, min(MAX_GENE, value))


@dataclass
class Genome:
    size: float
    speed: float
    power: float
    fecundity: float
    temperature: float
    swim: float = 0.0
    fly: float = 0.0
    dig: float = 0.0
    climb: float = 0.0

    def copy(self) -> "Genome":
        return replace(self)

    def as_dict(self) -> dict:
        return {gene: getattr(self, gene) for gene in GENES}

    @property
    def food_need(self) -> float:
        return (self.size + self.speed + self.power * 0.5) / 100

    @property
    def attack(self) -> float:
        return self.power * 0.6 + self.speed * 0.4

    @property
    def defense(self) -> float:
        return self.speed * 0.5 + self.size * 0.3 + self.power * 0.2

    @property
    def prey_value(self) -> float:
        return 1.0 + self.size / 40

    def distance(self, other: "Genome") -> float:
        total = sum(abs(getattr(self, g) - getattr(other, g)) for g in GENES)
        return total / len(GENES)

    def fitness(self, biome) -> float:
        """
        Приспособленность генома к биому, значение 0.1..1.
        Складывается из соответствия температуры биома и выраженности умений,
        которые биом востребует (climb в горах, dig в пустыне и т.д.).
        """
        temperature_fit = max(0.1, 1 - abs(self.temperature - biome.temperature) / 80)
        demand = biome.ability_demand
        weight = sum(demand.values())
        if weight <= 0:
            return temperature_fit
        match = sum(getattr(self, a) / 100 * w for a, w in demand.items()) / weight
        return temperature_fit * (0.75 + 0.25 * match)

    def mutated(self, rng: Random, strength: float, biome) -> "Genome":
        """
        Возвращает новый геном со случайными сдвигами признаков.
        Температура дрейфует в сторону температуры биома, востребованные
        умения появляются и растут, невостребованные постепенно теряются.
        """
        values = self.as_dict()
        for trait in ("size", "speed", "power", "fecundity"):
            if rng.random() < 0.5:
                values[trait] += rng.gauss(0, strength)
        pull = (biome.temperature - values["temperature"]) * 0.1 * rng.random()
        values["temperature"] += rng.gauss(0, strength * 0.5) + pull
        for ability in ABILITIES:
            weight = biome.ability_demand.get(ability, 0.0)
            if weight > 0:
                values[ability] += rng.random() * strength * weight
            else:
                values[ability] -= rng.random() * strength * 0.3
        return Genome(**{gene: clamp_gene(value) for gene, value in values.items()})

    @staticmethod
    def blend(first: "Genome", first_weight: float, second: "Genome", second_weight: float) -> "Genome":
        total = first_weight + second_weight
        return Genome(**{
            gene: (getattr(first, gene) * first_weight + getattr(second, gene) * second_weight) / total
            for gene in GENES
        })
