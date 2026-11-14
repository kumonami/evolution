from math import sqrt
import pygame
import ui.pygame.constants as ui
from core.genome import GENES
from core.population import Population
from core.region import Region
from core.world import World

HELP_LINES = (
    "[Space] pause   [+/-] speed   [T] tree",
    "Click region or population to select",
    "Region:  [H] water +10  [Shift+H] -10",
    "         [G] plants +500",
    "         [C] capacity +500  [Shift+C] -500",
    "Population: [1-5] size speed power",
    "  fecundity temperature  (+10)",
    "  [6-9] swim fly dig climb  (+10)",
    "  hold Shift for -10",
)


class Renderer:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont(None, 22)
        self.small = pygame.font.SysFont(None, 19)
        self.hitboxes: list = []

    def render(self, world: World, selected_region, selected_population, paused: bool,
               tick_duration: float, message: str) -> None:
        self.screen.fill(ui.BACKGROUND)
        self.hitboxes = []
        cols = max(r.get_x() for r in world.regions.values()) + 1
        rows = max(r.get_y() for r in world.regions.values()) + 1
        width = ui.MAP_WIDTH // cols
        height = (ui.SCREEN_Y - ui.HUD_HEIGHT) // rows
        for region in world.regions.values():
            left, top = region.get_x() * width, region.get_y() * height + ui.HUD_HEIGHT
            rect = pygame.Rect(left, top, width, height)
            self.hitboxes.append(("region", region.id, rect))
            self._region(region, rect, region.id == selected_region)
            local = world.populations_in(region)
            for index, population in enumerate(local):
                x = left + 40 + (index % 6) * 60
                y = top + 70 + (index // 6) * 60
                self._population(population, x, y, population.id == selected_population)
        self._hud(world, paused, tick_duration)
        self._panel(world, selected_region, selected_population, message)

    def hit_test(self, pos):
        for kind, ident, shape in reversed(self.hitboxes):
            if kind == "population":
                x, y, radius = shape
                if (pos[0] - x) ** 2 + (pos[1] - y) ** 2 <= radius ** 2:
                    return kind, ident
        for kind, ident, shape in self.hitboxes:
            if kind == "region" and shape.collidepoint(pos):
                return kind, ident
        return None

    def _region(self, region: Region, rect, selected: bool) -> None:
        color = ui.BIOME_COLORS.get(region.biome.id, (200, 100, 200))
        pygame.draw.rect(self.screen, color, rect)
        border = ui.SELECTION if selected else (255, 165, 0)
        pygame.draw.rect(self.screen, border, rect, 4 if selected else 2)
        label = f"{region.biome.name}  plants: {int(region.plants_stock)}"
        self.screen.blit(self.font.render(label, True, (0, 0, 0)), (rect.left + 8, rect.top + 8))

    def _population(self, population: Population, x: int, y: int, selected: bool) -> None:
        color = ui.TYPE_COLORS.get(population.species.type_id, (255, 255, 255))
        radius = max(3, min(26, int(sqrt(population.size))))
        pygame.draw.circle(self.screen, color, (x, y), radius)
        if population.influenced:
            pygame.draw.circle(self.screen, ui.ORIGIN_COLORS["influenced"], (x, y), radius + 3, 2)
        if selected:
            pygame.draw.circle(self.screen, ui.SELECTION, (x, y), radius + 6, 2)
        label = self.small.render(f"s{population.species.id}", True, (255, 255, 255))
        self.screen.blit(label, (x - 10, y + radius + 3))
        self.hitboxes.append(("population", population.id, (x, y, radius + 4)))

    def _hud(self, world: World, paused: bool, tick_duration: float) -> None:
        total = sum(p.size for p in world.populations.values())
        alive = len({p.species.id for p in world.populations.values()})
        state = "PAUSED" if paused else f"{tick_duration:.2f}s/tick"
        text = (f"tick {world.tick}   populations {len(world.populations)}   individuals {total}   "
                f"species alive {alive}/{len(world.species)}   {state}")
        self.screen.blit(self.font.render(text, True, ui.TEXT), (8, 12))

    def _panel(self, world: World, selected_region, selected_population, message: str) -> None:
        left = ui.MAP_WIDTH
        pygame.draw.rect(self.screen, ui.PANEL_BACKGROUND, pygame.Rect(left, 0, ui.PANEL_WIDTH, ui.SCREEN_Y))
        y = 12
        region = world.get_region(selected_region) if selected_region else None
        population = world.get_population(selected_population) if selected_population else None
        if region:
            y = self._lines(self._region_lines(world, region), left + 12, y, ui.TEXT)
            y += 10
        if population:
            y = self._lines(self._population_lines(population), left + 12, y, ui.TEXT)
            y += 10
        if not region and not population:
            y = self._lines(["Nothing selected"], left + 12, y, ui.MUTED)
        if message:
            self.screen.blit(self.font.render(message, True, ui.ORIGIN_COLORS["influenced"]),
                             (left + 12, ui.SCREEN_Y - 30 - 20 * len(HELP_LINES)))
        self._lines(HELP_LINES, left + 12, ui.SCREEN_Y - 12 - 19 * len(HELP_LINES), ui.MUTED, small=True)

    def _lines(self, lines, x: int, y: int, color, small: bool = False) -> int:
        font = self.small if small else self.font
        step = 19 if small else 22
        for line in lines:
            self.screen.blit(font.render(line, True, color), (x, y))
            y += step
        return y

    @staticmethod
    def _region_lines(world: World, region: Region) -> list:
        biome = region.biome
        return [
            f"Region {region.id}: {biome.name}",
            f"humidity {biome.humidity:.0f}   temperature {biome.temperature:.0f}",
            f"plants {int(region.plants_stock)} / {int(region.plants_limit)}",
            f"growth {region.plants_growth_rate:.0f}/tick",
            f"capacity {region.capacity}   load {world.region_load(region):.2f}",
        ]

    @staticmethod
    def _population_lines(population: Population) -> list:
        species = population.species
        lines = [
            f"Population {population.id}   species {species.id}",
            f"{ui.TYPE_NAMES.get(species.type_id, '?')}   size {population.size}",
            f"satiety {population.satiety:.2f}   stress {population.stress:.2f}",
            f"fitness {population.genome.fitness(population.region.biome):.2f}",
            "influenced by player" if population.influenced else "natural",
        ]
        genes = population.genome.as_dict()
        lines.extend(f"{index + 1} {gene}: {genes[gene]:.0f}" for index, gene in enumerate(GENES))
        return lines
