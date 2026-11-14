from math import sqrt
import pygame
import ui.pygame.constants as ui
from core.population import Population
from core.region import Region
from core.world import World


class Renderer:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont(None, 22)

    def render(self, world: World, paused: bool, tick_duration: float) -> None:
        self.screen.fill((0, 0, 0))
        cols = max(r.get_x() for r in world.regions.values()) + 1
        rows = max(r.get_y() for r in world.regions.values()) + 1
        width = ui.SCREEN_X // cols
        height = (ui.SCREEN_Y - ui.HUD_HEIGHT) // rows
        for region in world.regions.values():
            left, top = region.get_x() * width, region.get_y() * height + ui.HUD_HEIGHT
            self._region(region, left, top, width, height)
            local = world.populations_in(region)
            for index, population in enumerate(local):
                self._population(population, left + 40 + (index % 6) * 60, top + 70 + (index // 6) * 60)
        self._hud(world, paused, tick_duration)

    def _region(self, region: Region, left: int, top: int, width: int, height: int) -> None:
        color = ui.BIOME_COLORS.get(region.biome.id, (200, 100, 200))
        pygame.draw.rect(self.screen, color, pygame.Rect(left, top, width, height))
        pygame.draw.rect(self.screen, (255, 165, 0), pygame.Rect(left, top, width, height), 2)
        label = f"{region.biome.name}  plants: {int(region.plants_stock)}"
        self.screen.blit(self.font.render(label, True, (0, 0, 0)), (left + 6, top + 6))

    def _population(self, population: Population, x: int, y: int) -> None:
        color = ui.TYPE_COLORS.get(population.species.type_id, (255, 255, 255))
        radius = max(3, min(26, int(sqrt(population.size))))
        pygame.draw.circle(self.screen, color, (x, y), radius)
        label = self.font.render(f"s{population.species.id}", True, (255, 255, 255))
        self.screen.blit(label, (x - 10, y + radius + 2))

    def _hud(self, world: World, paused: bool, tick_duration: float) -> None:
        total = sum(p.size for p in world.populations.values())
        alive = len({p.species.id for p in world.populations.values()})
        state = "PAUSED" if paused else f"{tick_duration:.2f}s/tick"
        text = (f"tick {world.tick}  populations {len(world.populations)}  individuals {total}  "
                f"species alive {alive}/{len(world.species)}  {state}  [space] pause  [+/-] speed")
        self.screen.blit(self.font.render(text, True, (255, 255, 255)), (8, 12))
