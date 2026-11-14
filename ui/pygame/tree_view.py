import pygame
import ui.pygame.constants as ui
import ui.pygame.theme as theme
import ui.pygame.widgets as widgets
from core.tree import layout_tree

LEFT = 28
RIGHT = 120
AXIS_HEIGHT = 30
BASE_STEP = 24
GRID_STEPS = (10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000)
ZOOM_MIN = 0.5
ZOOM_MAX = 2.0


def grid_step(ticks: int) -> int:
    for step in GRID_STEPS:
        if ticks / step <= 10:
            return step
    return GRID_STEPS[-1]


class TreeView:
    """
    Дерево эволюции: каждому виду своя горизонтальная линия жизни от
    рождения до вымирания, потомки соединены плавными ветвями с родителем.
    Прокрутка колесом мыши по вертикали, масштаб строк кнопками на верхней панели.
    """

    def __init__(self, screen, fonts: theme.Fonts):
        self.screen = screen
        self.fonts = fonts
        self.area = pygame.Rect(0, ui.TOPBAR_HEIGHT, ui.MAP_WIDTH, ui.SCREEN_Y - ui.TOPBAR_HEIGHT)
        self.scroll = 0.0
        self.zoom = 1.0
        self.hits: list = []
        self._content = 0.0

    def scroll_by(self, delta: float) -> None:
        limit = max(0.0, self._content - (self.area.height - AXIS_HEIGHT))
        self.scroll = max(0.0, min(limit, self.scroll + delta))

    def change_zoom(self, factor: float) -> None:
        self.zoom = max(ZOOM_MIN, min(ZOOM_MAX, self.zoom * factor))
        self.scroll_by(0)

    def species_at(self, pos):
        for rect, species_id in self.hits:
            if rect.collidepoint(pos):
                return species_id
        return None

    def render(self, world, selected_id, hover) -> None:
        pygame.draw.rect(self.screen, theme.BACKGROUND, self.area)
        rows = layout_tree(world)
        step = BASE_STEP * self.zoom
        self._content = len(rows) * step + 24
        self.scroll_by(0)
        scale = (self.area.width - LEFT - RIGHT) / max(1, world.tick)
        origin_y = self.area.top + AXIS_HEIGHT + 14 - self.scroll
        self._grid(world, scale)
        by_id = {r.species.id: r for r in rows}
        body = pygame.Rect(self.area.left, self.area.top + AXIS_HEIGHT, self.area.width, self.area.height - AXIS_HEIGHT)
        self.screen.set_clip(body)
        glow = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        self.hits = []
        points = {r.species.id: (LEFT + r.start * scale, origin_y + r.row * step) for r in rows}
        for row in rows:
            parent = by_id.get(row.species.parent_id)
            if parent:
                self._branch(points[parent.species.id], points[row.species.id], row)
        for row in rows:
            x0, y = points[row.species.id]
            x1 = LEFT + row.end * scale
            if y < body.top - step or y > body.bottom + step:
                continue
            self._row(row, x0, x1, y, step, glow, row.species.id == selected_id, hover)
        self.screen.blit(glow, (0, 0))
        for row in rows:
            x0, y = points[row.species.id]
            if body.top - step < y < body.bottom + step:
                self._label(row, LEFT + row.end * scale, y)
        self.screen.set_clip(None)
        self._scrollbar(step, len(rows))
        self._legend()

    def _grid(self, world, scale: float) -> None:
        step = grid_step(world.tick)
        tick = 0
        while tick <= world.tick:
            x = LEFT + tick * scale
            pygame.draw.line(self.screen, theme.CARD_BORDER, (x, self.area.top + AXIS_HEIGHT), (x, self.area.bottom), 1)
            widgets.text(self.screen, self.fonts.small, str(tick), (x, self.area.top + 8), theme.MUTED, "midtop")
            tick += step
        pygame.draw.line(self.screen, theme.CARD_BORDER, (self.area.left, self.area.top + AXIS_HEIGHT),
                         (self.area.right, self.area.top + AXIS_HEIGHT), 1)
        widgets.text(self.screen, self.fonts.small, "тики", (self.area.right - 10, self.area.top + 8), theme.MUTED, "topright")

    def _color(self, row):
        base = theme.ORIGIN_COLORS.get(row.species.origin, theme.GREEN)
        return base if not row.species.is_extinct else theme.mix(base, theme.BACKGROUND, 0.55)

    def _branch(self, start, end, row) -> None:
        sx, sy = start
        ex, ey = end
        run = min(18, max(4, ex - sx))
        points = []
        for index in range(13):
            t = index / 12
            smooth = t * t * (3 - 2 * t)
            points.append((ex - run + run * smooth, sy + (ey - sy) * t))
        pygame.draw.lines(self.screen, theme.mix(self._color(row), theme.BACKGROUND, 0.2), False, points, 2)

    def _row(self, row, x0: float, x1: float, y: float, step: float, glow, selected: bool, hover) -> None:
        color = self._color(row)
        alive = not row.species.is_extinct
        hit = pygame.Rect(int(x0) - 8, int(y - step / 2), int(x1 - x0) + 70, int(step))
        self.hits.append((hit, row.species.id))
        hovered = hover is not None and hit.collidepoint(hover)
        if selected or hovered:
            pygame.draw.rect(glow, (*theme.ACCENT, 38 if selected else 22), hit.inflate(24, 0), border_radius=8)
        if alive:
            pygame.draw.line(glow, (*color, 60), (x0, y), (x1, y), 11)
        pygame.draw.line(self.screen, color, (x0, y), (x1, y), 4 if alive else 3)
        dot = theme.TYPE_COLORS.get(row.species.type_id, theme.TEXT)
        pygame.draw.circle(self.screen, theme.BACKGROUND, (x0, y), 7)
        pygame.draw.circle(self.screen, dot, (x0, y), 5)
        if selected:
            pygame.draw.circle(self.screen, theme.TEXT, (x0, y), 8, 2)
        if not alive:
            pygame.draw.line(self.screen, theme.RED, (x1 - 4, y - 4), (x1 + 4, y + 4), 2)
            pygame.draw.line(self.screen, theme.RED, (x1 - 4, y + 4), (x1 + 4, y - 4), 2)

    def _label(self, row, x1: float, y: float) -> None:
        alive = not row.species.is_extinct
        value = f"#{row.species.id}  {row.size}" if alive else f"#{row.species.id}"
        widgets.text(self.screen, self.fonts.small, value, (x1 + 10, y), theme.TEXT if alive else theme.MUTED, "midleft")

    def _scrollbar(self, step: float, count: int) -> None:
        visible = self.area.height - AXIS_HEIGHT
        if self._content <= visible:
            return
        track = pygame.Rect(self.area.right - 8, self.area.top + AXIS_HEIGHT + 4, 4, visible - 8)
        widgets.rounded(self.screen, theme.CARD, track, 2)
        thumb_h = max(24, track.height * visible / self._content)
        limit = self._content - visible
        thumb_y = track.top + (track.height - thumb_h) * (self.scroll / limit)
        widgets.rounded(self.screen, theme.MUTED, (track.left, thumb_y, track.width, thumb_h), 2)

    def _legend(self) -> None:
        pill = pygame.Rect(self.area.left + 12, self.area.bottom - 36, 560, 26)
        layer = pygame.Surface(pill.size, pygame.SRCALPHA)
        pygame.draw.rect(layer, (12, 14, 20, 200), layer.get_rect(), border_radius=13)
        self.screen.blit(layer, pill.topleft)
        x = pill.left + 14
        items = [(1, "травоядное"), (2, "всеядное"), (3, "хищник")]
        for type_id, label in items:
            pygame.draw.circle(self.screen, theme.TYPE_COLORS[type_id], (x, pill.centery), 5)
            x = widgets.text(self.screen, self.fonts.small, label, (x + 10, pill.centery), theme.TEXT, "midleft").right + 16
        for name, label in (("natural", "естественный"), ("influenced", "влияние игрока")):
            pygame.draw.line(self.screen, theme.ORIGIN_COLORS[name], (x, pill.centery), (x + 20, pill.centery), 4)
            x = widgets.text(self.screen, self.fonts.small, label, (x + 26, pill.centery), theme.TEXT, "midleft").right + 16
        pygame.draw.line(self.screen, theme.RED, (x - 4, pill.centery - 4), (x + 4, pill.centery + 4), 2)
        pygame.draw.line(self.screen, theme.RED, (x - 4, pill.centery + 4), (x + 4, pill.centery - 4), 2)
        widgets.text(self.screen, self.fonts.small, "вымер", (x + 10, pill.centery), theme.TEXT, "midleft")
