from dataclasses import dataclass
from typing import Callable, Optional
import pygame
import ui.pygame.theme as theme


@dataclass
class Zone:
    rect: pygame.Rect
    on_click: Callable
    enabled: bool = True


def rounded(surface, color, rect, radius: int = 8, border=None, border_width: int = 1) -> None:
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    if border:
        pygame.draw.rect(surface, border, rect, border_width, border_radius=radius)


def text(surface, font, value: str, pos, color=theme.TEXT, anchor: str = "topleft"):
    image = font.render(value, True, color)
    rect = image.get_rect(**{anchor: pos})
    surface.blit(image, rect)
    return rect


def fit_text(font, value: str, width: int) -> str:
    if font.size(value)[0] <= width:
        return value
    while value and font.size(value + "…")[0] > width:
        value = value[:-1]
    return value + "…"


def alpha_circle(surface, color, center, radius: int, alpha: int, width: int = 0) -> None:
    size = radius * 2 + 4
    layer = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(layer, (*color, max(0, min(255, alpha))), (size // 2, size // 2), radius, width)
    surface.blit(layer, (center[0] - size // 2, center[1] - size // 2))


class Ui:
    """
    Кнопки в режиме немедленной отрисовки: каждый кадр кнопка рисуется
    и регистрирует свою зону. Клик обрабатывается по зонам предыдущего кадра,
    поэтому ввод идёт только через мышь и экранные кнопки.
    """

    def __init__(self, fonts: theme.Fonts):
        self.fonts = fonts
        self.zones: list[Zone] = []
        self._previous: list[Zone] = []
        self.mouse = (0, 0)
        self.pressed = False

    def begin(self, mouse, pressed: bool) -> None:
        self._previous = self.zones
        self.zones = []
        self.mouse = mouse
        self.pressed = pressed

    def click(self, pos) -> bool:
        for zone in reversed(self.zones or self._previous):
            if zone.enabled and zone.rect.collidepoint(pos):
                zone.on_click()
                return True
        return False

    def button(self, surface, rect, label: Optional[str] = None, icon: Optional[str] = None,
               on_click: Optional[Callable] = None, enabled: bool = True,
               accent: bool = False, active: bool = False, font=None) -> None:
        rect = pygame.Rect(rect)
        hover = enabled and rect.collidepoint(self.mouse)
        if not enabled:
            color = theme.BUTTON_DISABLED
        elif self.pressed and hover:
            color = theme.BUTTON_PRESSED
        elif accent or active:
            color = theme.BUTTON_ACCENT_HOVER if hover else theme.BUTTON_ACCENT
        else:
            color = theme.BUTTON_HOVER if hover else theme.BUTTON
        rounded(surface, color, rect, 8)
        ink = theme.TEXT if enabled else theme.MUTED
        if icon:
            self._icon(surface, icon, rect, ink)
        if label:
            text(surface, font or self.fonts.body, label, rect.center, ink, "center")
        if on_click:
            self.zones.append(Zone(rect, on_click, enabled))

    @staticmethod
    def _icon(surface, icon: str, rect, color) -> None:
        cx, cy = rect.center
        if icon == "play":
            pygame.draw.polygon(surface, color, [(cx - 5, cy - 8), (cx - 5, cy + 8), (cx + 8, cy)])
        elif icon == "pause":
            pygame.draw.rect(surface, color, (cx - 7, cy - 8, 5, 16), border_radius=1)
            pygame.draw.rect(surface, color, (cx + 2, cy - 8, 5, 16), border_radius=1)
        elif icon == "minus":
            pygame.draw.line(surface, color, (cx - 6, cy), (cx + 6, cy), 2)
        elif icon == "plus":
            pygame.draw.line(surface, color, (cx - 6, cy), (cx + 6, cy), 2)
            pygame.draw.line(surface, color, (cx, cy - 6), (cx, cy + 6), 2)


def bar(surface, rect, value: float, maximum: float, color) -> None:
    rect = pygame.Rect(rect)
    rounded(surface, theme.BUTTON_DISABLED, rect, rect.height // 2)
    ratio = max(0.0, min(1.0, value / maximum if maximum else 0.0))
    if ratio > 0:
        fill = pygame.Rect(rect.left, rect.top, max(rect.height, int(rect.width * ratio)), rect.height)
        rounded(surface, color, fill, rect.height // 2)


def sparkline(surface, fonts: theme.Fonts, rect, series: list, color, title: str) -> None:
    """
    Мини-график ряда (tick, value): заливка под линией, подпись заголовка,
    последнее значение и диапазон тиков по краям.
    """
    rect = pygame.Rect(rect)
    rounded(surface, theme.CARD, rect, 10, theme.CARD_BORDER)
    text(surface, fonts.small, title, (rect.left + 10, rect.top + 6), theme.MUTED)
    plot = pygame.Rect(rect.left + 10, rect.top + 26, rect.width - 20, rect.height - 46)
    if len(series) < 2:
        text(surface, fonts.small, "нет данных", plot.center, theme.MUTED, "center")
        return
    ticks = [t for t, _ in series]
    values = [v for _, v in series]
    t0, t1 = ticks[0], ticks[-1]
    top = max(max(values), 1)
    points = [
        (plot.left + (t - t0) / max(1, t1 - t0) * plot.width, plot.bottom - v / top * plot.height)
        for t, v in series
    ]
    layer = pygame.Surface(rect.size, pygame.SRCALPHA)
    area = [(x - rect.left, y - rect.top) for x, y in points]
    area += [(points[-1][0] - rect.left, plot.bottom - rect.top), (points[0][0] - rect.left, plot.bottom - rect.top)]
    pygame.draw.polygon(layer, (*color, 50), area)
    surface.blit(layer, rect.topleft)
    pygame.draw.lines(surface, color, False, points, 2)
    text(surface, fonts.bold, str(int(values[-1])), (rect.right - 10, rect.top + 6), theme.TEXT, "topright")
    text(surface, fonts.small, str(t0), (plot.left, rect.bottom - 18), theme.MUTED)
    text(surface, fonts.small, str(t1), (plot.right, rect.bottom - 18), theme.MUTED, "topright")
