import pygame
import ui.pygame.constants as ui
from core.genome import GENES
from core.tree import TreeRow, layout_tree
from core.world import World

LEFT = 70
RIGHT = 120
TOP = 60
BOTTOM = 30
ROW_MAX = 26
ROW_MIN = 8


class TreeView:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont(None, 22)
        self.small = pygame.font.SysFont(None, 18)

    def render(self, world: World, hover) -> None:
        self.screen.fill(ui.BACKGROUND)
        rows = layout_tree(world)
        scale_x, step = self._scales(world, len(rows))
        by_id = {r.species.id: r for r in rows}
        positions = {r.species.id: (self._x(r.start, scale_x), self._y(r.row, step)) for r in rows}
        for row in rows:
            parent = by_id.get(row.species.parent_id)
            if parent:
                x, y = positions[row.species.id]
                pygame.draw.line(self.screen, ui.MUTED, (x, positions[parent.species.id][1]), (x, y), 1)
        hovered = None
        for row in rows:
            if self._draw_row(row, positions[row.species.id], scale_x, hover):
                hovered = row
        self._header(world, len(rows))
        if hovered:
            self._tooltip(hovered, hover)

    def _scales(self, world: World, count: int):
        scale_x = (ui.SCREEN_X - LEFT - RIGHT) / max(1, world.tick)
        step = max(ROW_MIN, min(ROW_MAX, (ui.SCREEN_Y - TOP - BOTTOM) / max(1, count)))
        return scale_x, step

    @staticmethod
    def _x(tick: int, scale_x: float) -> int:
        return int(LEFT + tick * scale_x)

    @staticmethod
    def _y(row: int, step: float) -> int:
        return int(TOP + row * step)

    def _draw_row(self, row: TreeRow, start, scale_x: float, hover) -> bool:
        x0, y = start
        x1 = self._x(row.end, scale_x)
        color = ui.ORIGIN_COLORS.get(row.species.origin, ui.ORIGIN_COLORS["natural"])
        alive = not row.species.is_extinct
        if not alive:
            color = tuple(int(c * 0.45) for c in color)
        pygame.draw.line(self.screen, color, (x0, y), (x1, y), 3 if alive else 2)
        pygame.draw.circle(self.screen, ui.TYPE_COLORS.get(row.species.type_id, ui.TEXT), (x0, y), 4)
        if alive:
            label = self.small.render(f"s{row.species.id}  {row.size}", True, ui.TEXT)
            self.screen.blit(label, (x1 + 8, y - 6))
        else:
            pygame.draw.line(self.screen, color, (x1 - 4, y - 4), (x1 + 4, y + 4), 2)
            pygame.draw.line(self.screen, color, (x1 - 4, y + 4), (x1 + 4, y - 4), 2)
        return hover is not None and x0 - 6 <= hover[0] <= x1 + 6 and abs(hover[1] - y) <= 6

    def _header(self, world: World, count: int) -> None:
        title = f"Evolution tree   tick {world.tick}   species {count}   [T] back"
        self.screen.blit(self.font.render(title, True, ui.TEXT), (LEFT, 14))
        x = LEFT
        for name, color in ui.ORIGIN_COLORS.items():
            pygame.draw.line(self.screen, color, (x, 42), (x + 24, 42), 3)
            label = "natural" if name == "natural" else "player influence"
            self.screen.blit(self.small.render(label, True, ui.MUTED), (x + 30, 35))
            x += 170

    def _tooltip(self, row: TreeRow, hover) -> None:
        species = row.species
        genome = species.anchor.as_dict()
        lines = [
            f"species {species.id}   parent {species.parent_id}",
            f"{ui.TYPE_NAMES.get(species.type_id, '?')}   origin {species.origin}",
            f"born {species.born_tick}   " + ("alive" if not species.is_extinct else f"extinct {species.extinct_tick}"),
            f"size now {row.size}",
            " ".join(f"{g[:3]} {genome[g]:.0f}" for g in GENES[:5]),
            " ".join(f"{g[:3]} {genome[g]:.0f}" for g in GENES[5:]),
        ]
        width = max(self.small.size(line)[0] for line in lines) + 16
        height = 18 * len(lines) + 10
        x = min(hover[0] + 14, ui.SCREEN_X - width - 4)
        y = min(hover[1] + 14, ui.SCREEN_Y - height - 4)
        pygame.draw.rect(self.screen, ui.PANEL_BACKGROUND, pygame.Rect(x, y, width, height))
        pygame.draw.rect(self.screen, ui.MUTED, pygame.Rect(x, y, width, height), 1)
        for i, line in enumerate(lines):
            self.screen.blit(self.small.render(line, True, ui.TEXT), (x + 8, y + 6 + i * 18))
