import random
from math import sin, cos
import pygame
import ui.pygame.theme as theme


def region_background(biome_id: int, size, seed: int) -> pygame.Surface:
    """
    Процедурный фон региона: вертикальный градиент биома, мягкие пятна
    и декор (деревья, дюны, скалы). Рисуется один раз и кэшируется.
    """
    width, height = size
    rng = random.Random(seed)
    top, bottom = theme.BIOME_COLORS.get(biome_id, theme.BIOME_COLORS[1])
    surface = pygame.Surface(size)
    for y in range(height):
        pygame.draw.line(surface, theme.mix(top, bottom, y / height), (0, y), (width, y))
    for _ in range(18):
        blob = pygame.Surface((200, 200), pygame.SRCALPHA)
        tone = (255, 255, 255, 5) if rng.random() < 0.5 else (0, 0, 0, 6)
        reach = rng.randint(50, 95)
        for step in range(6):
            pygame.draw.circle(blob, tone, (100, 100), int(reach * (1 - step / 7)))
        surface.blit(blob, (rng.randint(-60, width - 60), rng.randint(-60, height - 60)))
    decorate = {1: _forest, 2: _desert, 3: _mountains}.get(biome_id, _forest)
    decorate(surface, rng, width, height)
    return surface


def _forest(surface, rng, width, height) -> None:
    for _ in range(34):
        x, y, s = rng.randint(10, width - 10), rng.randint(50, height - 10), rng.randint(6, 12)
        pygame.draw.rect(surface, (60, 40, 28), (x - 1, y, 3, s // 2))
        pygame.draw.polygon(surface, (22, 70, 42), [(x, y - s * 2), (x - s, y + 2), (x + s, y + 2)])
        pygame.draw.polygon(surface, (30, 92, 56), [(x, y - s * 2), (x - s * 0.6, y - 2), (x + s * 0.6, y - 2)])


def _desert(surface, rng, width, height) -> None:
    for _ in range(14):
        x, y, w = rng.randint(0, width - 60), rng.randint(60, height - 10), rng.randint(60, 140)
        pygame.draw.arc(surface, (240, 220, 160), (x, y, w, 26), 0.1, 3.0, 2)
        pygame.draw.arc(surface, (170, 130, 70), (x + 4, y + 6, w, 26), 3.3, 6.1, 2)
    for _ in range(7):
        x, y = rng.randint(10, width - 10), rng.randint(60, height - 10)
        pygame.draw.rect(surface, (86, 130, 84), (x - 2, y - 14, 4, 16), border_radius=2)
        pygame.draw.rect(surface, (86, 130, 84), (x - 8, y - 9, 3, 7), border_radius=2)
        pygame.draw.rect(surface, (86, 130, 84), (x + 5, y - 11, 3, 8), border_radius=2)


def _mountains(surface, rng, width, height) -> None:
    for _ in range(16):
        x, y, s = rng.randint(10, width - 10), rng.randint(70, height - 4), rng.randint(16, 34)
        pygame.draw.polygon(surface, (64, 70, 84), [(x, y - s), (x - s, y), (x + s, y)])
        pygame.draw.polygon(surface, (104, 112, 128), [(x, y - s), (x - s, y), (x - s * 0.1, y)])
        pygame.draw.polygon(surface, (236, 240, 248), [(x, y - s), (x - s * 0.34, y - s * 0.64), (x + s * 0.34, y - s * 0.64)])


def rounded_mask(surface: pygame.Surface, radius: int) -> pygame.Surface:
    result = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    pygame.draw.rect(result, (255, 255, 255, 255), result.get_rect(), border_radius=radius)
    result.blit(surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return result


def draw_creature(surface, type_id: int, color, radius: float, t: float, phase: float) -> None:
    """
    Силуэт существа: травоядное с длинным телом и ушами, всеядное круглое,
    хищник с зубчатой спиной. Лёгкое покачивание зависит от времени.
    """
    cx, cy = surface.get_width() / 2, surface.get_height() / 2 + sin(t * 3 + phase) * radius * 0.05
    r = radius
    dark = theme.mix(color, (0, 0, 0), 0.35)
    light = theme.mix(color, (255, 255, 255), 0.35)
    if type_id == 3:
        points = [(cx - r, cy + r * 0.5), (cx - r * 0.8, cy - r * 0.2), (cx - r * 0.45, cy - r * 0.9),
                  (cx - r * 0.1, cy - r * 0.35), (cx + r * 0.25, cy - r * 0.85), (cx + r * 0.6, cy - r * 0.3),
                  (cx + r * 1.1, cy - r * 0.1), (cx + r * 0.9, cy + r * 0.45), (cx + r * 0.1, cy + r * 0.8)]
        pygame.draw.polygon(surface, color, points)
        pygame.draw.polygon(surface, dark, points, 2)
        eye = (cx + r * 0.62, cy - r * 0.05)
        pygame.draw.circle(surface, (255, 240, 200), eye, max(2, r * 0.13))
        pygame.draw.circle(surface, (120, 0, 0), eye, max(1, r * 0.06))
        pygame.draw.polygon(surface, (250, 250, 250),
                            [(cx + r * 0.88, cy + r * 0.1), (cx + r * 0.78, cy + r * 0.38), (cx + r * 0.7, cy + r * 0.1)])
        return
    if type_id == 1:
        body = pygame.Rect(0, 0, r * 2.0, r * 1.45)
        body.center = (cx - r * 0.1, cy + r * 0.1)
        pygame.draw.ellipse(surface, color, body)
        pygame.draw.ellipse(surface, light, body.inflate(-r * 0.7, -r * 0.9).move(0, r * 0.2))
        pygame.draw.circle(surface, color, (cx + r * 0.85, cy - r * 0.35), r * 0.5)
        for dx in (0.7, 1.0):
            ear = pygame.Rect(0, 0, r * 0.22, r * 0.55)
            ear.center = (cx + r * dx, cy - r * 0.95)
            pygame.draw.ellipse(surface, dark, ear)
        eye = (cx + r * 1.02, cy - r * 0.4)
    else:
        pygame.draw.circle(surface, color, (cx - r * 0.1, cy + r * 0.1), r)
        pygame.draw.circle(surface, light, (cx - r * 0.1, cy + r * 0.35), r * 0.55)
        pygame.draw.circle(surface, color, (cx + r * 0.8, cy - r * 0.4), r * 0.55)
        for dx in (0.55, 1.05):
            pygame.draw.circle(surface, dark, (cx + r * dx, cy - r * 0.9), r * 0.2)
        eye = (cx + r * 0.98, cy - r * 0.45)
    pygame.draw.circle(surface, (255, 255, 255), eye, max(2, r * 0.13))
    pygame.draw.circle(surface, (20, 20, 30), eye, max(1, r * 0.06))


def creature_color(type_id: int, temperature: float, power: float):
    base = theme.TYPE_COLORS.get(type_id, theme.TEXT)
    warm, cool = (255, 150, 70), (90, 170, 255)
    tint = warm if temperature >= 50 else cool
    color = theme.mix(base, tint, min(0.4, abs(temperature - 50) / 50 * 0.4))
    return theme.mix(color, (0, 0, 0), max(0.0, (50 - power) / 50 * 0.25))


def water_drop(surface, pos, color) -> None:
    x, y = pos
    pygame.draw.polygon(surface, color, [(x, y - 7), (x - 5, y + 1), (x + 5, y + 1)])
    pygame.draw.circle(surface, color, (x, y + 2), 5)


def pond_points(rng_seed: int, width: int, height: int, count: int) -> list:
    rng = random.Random(rng_seed)
    return [(rng.randint(40, width - 60), rng.randint(70, height - 40), rng.randint(22, 38)) for _ in range(count)]


def grass_points(rng_seed: int, width: int, height: int, count: int) -> list:
    rng = random.Random(rng_seed * 7 + 1)
    return [(rng.randint(8, width - 8), rng.randint(46, height - 8)) for _ in range(count)]


def unit(angle: float):
    return cos(angle), sin(angle)
