from dataclasses import dataclass
from core.species import Species
from core.world import World


@dataclass
class TreeRow:
    species: Species
    row: int
    start: int
    end: int
    size: int
    depth: int


def layout_tree(world: World) -> list[TreeRow]:
    """
    Раскладка дерева эволюции по строкам: каждому виду своя строка,
    потомки идут сразу под родителем в порядке рождения (обход в глубину).
    Жизнь вида отрезок от born_tick до вымирания или текущего тика.
    """
    children: dict = {}
    roots = []
    for species in sorted(world.species.values(), key=lambda s: (s.born_tick, s.id)):
        if species.parent_id is None or species.parent_id not in world.species:
            roots.append(species)
        else:
            children.setdefault(species.parent_id, []).append(species)
    sizes: dict = {}
    for population in world.populations.values():
        sizes[population.species.id] = sizes.get(population.species.id, 0) + population.size
    rows: list[TreeRow] = []
    stack = [(root, 0) for root in reversed(roots)]
    while stack:
        species, depth = stack.pop()
        end = species.extinct_tick if species.extinct_tick is not None else world.tick
        rows.append(TreeRow(species, len(rows), species.born_tick, end, sizes.get(species.id, 0), depth))
        for child in reversed(children.get(species.id, [])):
            stack.append((child, depth + 1))
    return rows
