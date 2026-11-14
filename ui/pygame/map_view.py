import pygame
import ui.pygame.constants as ui
import ui.pygame.theme as theme
import ui.pygame.widgets as widgets
from ui.pygame import art
from ui.pygame.animation import Animator, creature_radius

GRASS_COUNT = 110
MAX_PONDS = 4
SLOT_STEP_X = 66
SLOT_STEP_Y = 78
HEADER_SPACE = 74


class MapView:
    def __init__(self, screen, fonts: theme.Fonts, world):
        self.screen = screen
        self.fonts = fonts
        self.rects = self._layout(world)
        self.art = {}
        self.grass = {}
        for region in world.regions.values():
            rect = self.rects[region.id]
            background = art.region_background(region.biome.id, rect.size, region.id)
            self.art[region.id] = art.rounded_mask(background, 16)
            self.grass[region.id] = art.grass_points(region.id, rect.width, rect.height, GRASS_COUNT)
        self.animator = Animator(self._slots(), theme.TEXT, theme.GOLD)

    def _layout(self, world) -> dict:
        cols = max(r.get_x() for r in world.regions.values()) + 1
        rows = max(r.get_y() for r in world.regions.values()) + 1
        area_h = ui.SCREEN_Y - ui.TOPBAR_HEIGHT
        width = ui.MAP_WIDTH // cols
        height = area_h // rows
        gap = ui.REGION_GAP
        return {
            region.id: pygame.Rect(region.get_x() * width + gap, ui.TOPBAR_HEIGHT + region.get_y() * height + gap,
                                   width - gap * 2, height - gap * 2)
            for region in world.regions.values()
        }

    def _slots(self) -> dict:
        slots = {}
        for region_id, rect in self.rects.items():
            cols = max(1, (rect.width - 20) // SLOT_STEP_X)
            rows = max(1, (rect.height - HEADER_SPACE - 20) // SLOT_STEP_Y)
            offset = (rect.width - cols * SLOT_STEP_X) / 2 + SLOT_STEP_X / 2
            slots[region_id] = [
                (rect.left + offset + c * SLOT_STEP_X, rect.top + HEADER_SPACE + r * SLOT_STEP_Y + SLOT_STEP_Y / 2)
                for r in range(rows) for c in range(cols)
            ]
        return slots

    def region_at(self, pos):
        for region_id, rect in self.rects.items():
            if rect.collidepoint(pos):
                return region_id
        return None

    def region_center(self, region_id: int):
        return self.rects[region_id].center

    def render(self, world, selected_region, selected_population, t: float) -> None:
        for region in world.regions.values():
            self._region(world, region, region.id == selected_region, t)
        for sprite in sorted(self.animator.sprites.values(), key=lambda s: s.y):
            self._creature(sprite, sprite.pop_id == selected_population, t)
        for ghost in self.animator.ghosts:
            self._creature(ghost, False, t)
        for effect in self.animator.effects:
            self._effect(effect)

    def _region(self, world, region, selected: bool, t: float) -> None:
        rect = self.rects[region.id]
        self.screen.blit(self.art[region.id], rect.topleft)
        self._ponds(region, rect)
        self._grass(region, rect)
        border = theme.ACCENT if selected else (0, 0, 0)
        pygame.draw.rect(self.screen, border, rect, 3 if selected else 1, border_radius=16)
        self._header(world, region, rect)

    def _ponds(self, region, rect) -> None:
        count = min(MAX_PONDS, int(region.biome.humidity // 20))
        for x, y, size in art.pond_points(region.id, rect.width, rect.height, MAX_PONDS)[:count]:
            layer = pygame.Surface((size * 3, size * 2), pygame.SRCALPHA)
            pygame.draw.ellipse(layer, (70, 150, 220, 120), layer.get_rect())
            pygame.draw.ellipse(layer, (150, 205, 245, 90), layer.get_rect().inflate(-size * 0.7, -size * 0.6))
            self.screen.blit(layer, (rect.left + x - size * 1.5, rect.top + y - size))

    def _grass(self, region, rect) -> None:
        reference = max(1.0, region.plants_growth_rate * 15)
        shown = int(min(1.0, region.plants_stock / reference) * GRASS_COUNT)
        for x, y in self.grass[region.id][:shown]:
            px, py = rect.left + x, rect.top + y
            pygame.draw.line(self.screen, (120, 220, 120), (px, py), (px - 2, py - 5), 1)
            pygame.draw.line(self.screen, (150, 235, 140), (px, py), (px + 2, py - 6), 1)

    def _header(self, world, region, rect) -> None:
        pill = pygame.Rect(rect.left + 10, rect.top + 10, rect.width - 20, 44)
        layer = pygame.Surface(pill.size, pygame.SRCALPHA)
        pygame.draw.rect(layer, (12, 14, 20, 150), layer.get_rect(), border_radius=12)
        self.screen.blit(layer, pill.topleft)
        name = ui.BIOME_NAMES.get(region.biome.id, "Регион")
        widgets.text(self.screen, self.fonts.bold, f"{name} · {region.id}", (pill.left + 12, pill.top + 5), theme.TEXT)
        art.water_drop(self.screen, (pill.left + 17, pill.top + 33), (110, 190, 245))
        widgets.text(self.screen, self.fonts.small, f"{region.biome.humidity:.0f}", (pill.left + 26, pill.top + 25), theme.TEXT)
        widgets.text(self.screen, self.fonts.small, f"растения {int(region.plants_stock)}", (pill.left + 64, pill.top + 25), (160, 230, 150))
        load = min(1.0, world.region_load(region))
        widgets.bar(self.screen, (pill.right - 96, pill.top + 29, 84, 6), load, 1.0, theme.GOLD if load > 0.9 else theme.ACCENT)
        widgets.text(self.screen, self.fonts.small, "заселённость", (pill.right - 12, pill.top + 7), theme.MUTED, "topright")

    def _creature(self, sprite, selected: bool, t: float) -> None:
        radius = max(4.0, sprite.radius)
        size = int(radius * 5)
        layer = pygame.Surface((size, size), pygame.SRCALPHA)
        phase = sprite.pop_id * 1.7
        color = art.creature_color(sprite.type_id, sprite.temperature, sprite.power)
        pygame.draw.ellipse(layer, (0, 0, 0, 70), pygame.Rect(size / 2 - radius * 1.1, size / 2 + radius * 0.7, radius * 2.2, radius * 0.6))
        for index in range(min(8, sprite.size // 14)):
            angle = index * 2.4 + phase + t * 0.6
            ox, oy = art.unit(angle)
            dot = (size / 2 + ox * radius * 1.7, size / 2 + oy * radius * 1.1 + radius * 0.2)
            pygame.draw.circle(layer, (*color, 160), dot, max(2, radius * 0.18))
        art.draw_creature(layer, sprite.type_id, color, radius, t, phase)
        if sprite.alpha < 1.0:
            layer.set_alpha(int(255 * sprite.alpha))
        self.screen.blit(layer, (sprite.x - size / 2, sprite.y - size / 2))
        if sprite.dying:
            return
        if sprite.influenced:
            widgets.alpha_circle(self.screen, theme.GOLD, (sprite.x, sprite.y), int(radius + 6), 200, 2)
        if selected:
            widgets.alpha_circle(self.screen, theme.TEXT, (sprite.x, sprite.y), int(radius + 11), 230, 2)
        widgets.text(self.screen, self.fonts.small, str(sprite.size), (sprite.x, sprite.y - radius - 6), theme.TEXT, "midbottom")
        widgets.text(self.screen, self.fonts.small, f"#{sprite.species_id}", (sprite.x, sprite.y + radius + 5), (235, 235, 245), "midtop")

    def _effect(self, effect) -> None:
        progress = effect.progress
        fade = int(255 * (1 - progress))
        if effect.kind == "ring":
            radius = int(effect.radius + progress * 46)
            widgets.alpha_circle(self.screen, effect.color, (effect.x, effect.y), radius, fade, 3)
        else:
            y = effect.y - progress * 34
            image = self.fonts.bold.render(effect.text, True, effect.color)
            image.set_alpha(fade)
            self.screen.blit(image, image.get_rect(center=(effect.x, y)))
