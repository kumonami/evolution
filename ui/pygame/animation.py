from dataclasses import dataclass
from math import exp, sqrt
from typing import Optional

MAX_RADIUS = 28
MIN_RADIUS = 10
SPAWN_LIFE = 0.7
SPECIES_LIFE = 1.4
TEXT_LIFE = 1.6
GHOST_LIFE = 0.9


def creature_radius(size: float) -> float:
    return max(MIN_RADIUS, min(MAX_RADIUS, MIN_RADIUS + sqrt(max(size, 0)) * 0.9))


@dataclass
class Sprite:
    pop_id: int
    species_id: int
    type_id: int
    region_id: int
    slot: int
    x: float
    y: float
    tx: float
    ty: float
    radius: float
    target_radius: float
    size: int
    influenced: bool
    temperature: float
    power: float
    alpha: float = 1.0
    dying: bool = False
    age: float = 0.0


@dataclass
class Effect:
    kind: str
    x: float
    y: float
    color: tuple
    life: float
    text: str = ""
    age: float = 0.0
    radius: float = 20.0

    @property
    def progress(self) -> float:
        return min(1.0, self.age / self.life)


class Animator:
    """
    Сглаживает отображение мира между тиками. По разнице состояния мира
    находит появление, миграцию и исчезновение популяций, новые виды, а также
    запускает визуальные эффекты. Симуляция об аниматоре ничего не знает.
    """

    def __init__(self, slots: dict, spawn_color: tuple, species_color: tuple):
        self.slots = slots
        self.spawn_color = spawn_color
        self.species_color = species_color
        self.sprites: dict[int, Sprite] = {}
        self.ghosts: list[Sprite] = []
        self.effects: list[Effect] = []
        self.known_species: set = set()
        self._initial = True

    def sync(self, world) -> None:
        for population in world.populations.values():
            sprite = self.sprites.get(population.id)
            if sprite is None:
                sprite = self._create(population)
            elif sprite.region_id != population.region.id:
                sprite.region_id = population.region.id
                sprite.slot = self._free_slot(population.region.id, population.id)
                sprite.tx, sprite.ty = self.slots[sprite.region_id][sprite.slot]
            self._refresh(sprite, population)
            self._note_species(sprite, population)
        for pop_id in [i for i in self.sprites if i not in world.populations]:
            sprite = self.sprites.pop(pop_id)
            sprite.dying = True
            sprite.age = 0.0
            self.ghosts.append(sprite)
        self._initial = False

    def update(self, dt: float) -> None:
        follow = 1 - exp(-dt * 7)
        for sprite in self.sprites.values():
            sprite.x += (sprite.tx - sprite.x) * follow
            sprite.y += (sprite.ty - sprite.y) * follow
            sprite.radius += (sprite.target_radius - sprite.radius) * follow
            sprite.age += dt
        for ghost in self.ghosts:
            ghost.age += dt
            ghost.alpha = max(0.0, 1 - ghost.age / GHOST_LIFE)
            ghost.radius *= 1 - dt * 0.6
        self.ghosts = [g for g in self.ghosts if g.alpha > 0]
        for effect in self.effects:
            effect.age += dt
        self.effects = [e for e in self.effects if e.age < e.life]

    def float_text(self, x: float, y: float, value: str, color: tuple) -> None:
        self.effects.append(Effect("text", x, y, color, TEXT_LIFE, text=value))

    def sprite_at(self, pos) -> Optional[Sprite]:
        for sprite in reversed(list(self.sprites.values())):
            reach = sprite.radius + 6
            if (pos[0] - sprite.x) ** 2 + (pos[1] - sprite.y) ** 2 <= reach ** 2:
                return sprite
        return None

    def _create(self, population) -> Sprite:
        region_id = population.region.id
        slot = self._free_slot(region_id, population.id)
        x, y = self.slots[region_id][slot]
        radius = creature_radius(population.size)
        sprite = Sprite(
            pop_id=population.id, species_id=population.species.id, type_id=population.species.type_id,
            region_id=region_id, slot=slot, x=x, y=y, tx=x, ty=y, radius=radius * 0.4,
            target_radius=radius, size=population.size, influenced=population.influenced,
            temperature=population.genome.temperature, power=population.genome.power,
        )
        self.sprites[population.id] = sprite
        if not self._initial:
            self.effects.append(Effect("ring", x, y, self.spawn_color, SPAWN_LIFE, radius=radius))
        return sprite

    def _refresh(self, sprite: Sprite, population) -> None:
        sprite.size = population.size
        sprite.target_radius = creature_radius(population.size)
        sprite.influenced = population.influenced
        sprite.temperature = population.genome.temperature
        sprite.power = population.genome.power
        sprite.species_id = population.species.id

    def _note_species(self, sprite: Sprite, population) -> None:
        species_id = population.species.id
        if species_id in self.known_species:
            return
        self.known_species.add(species_id)
        if self._initial:
            return
        self.effects.append(Effect("ring", sprite.tx, sprite.ty, self.species_color, SPECIES_LIFE,
                                   radius=sprite.target_radius + 6))
        self.effects.append(Effect("text", sprite.tx, sprite.ty - sprite.target_radius - 10,
                                   self.species_color, TEXT_LIFE, text=f"Новый вид #{species_id}"))

    def _free_slot(self, region_id: int, pop_id: int) -> int:
        slots = self.slots[region_id]
        used = {s.slot for s in self.sprites.values() if s.region_id == region_id and s.pop_id != pop_id}
        for index in range(len(slots)):
            if index not in used:
                return index
        return pop_id % len(slots)
