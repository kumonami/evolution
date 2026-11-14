import time
import pygame
import config.constants as constants
import ui.pygame.constants as ui
import ui.pygame.theme as theme
import ui.pygame.widgets as widgets
from core.simulation import Simulation
from core.world import World
from domain.intents import AddPlants, AdjustWater, NudgeGene, ResizeRegion
from ui.pygame.map_view import MapView
from ui.pygame.panel import SidePanel
from ui.pygame.tree_view import TreeView


class App:
    """
    Окно игры. Весь ввод идёт мышью через кнопки: верхняя панель управляет
    временем и экраном, правая панель вмешивается в выбранный регион или
    популяцию. Действия применяются сразу, в том числе на паузе.
    """

    def __init__(self, world: World, simulation: Simulation):
        self.world = world
        self.simulation = simulation
        self.screen = pygame.display.set_mode((ui.SCREEN_X, ui.SCREEN_Y))
        pygame.display.set_caption("Evolution")
        self.clock = pygame.time.Clock()
        self.fonts = theme.Fonts()
        self.kit = widgets.Ui(self.fonts)
        self.map_view = MapView(self.screen, self.fonts, world)
        self.tree_view = TreeView(self.screen, self.fonts)
        self.panel = SidePanel(self.screen, self.fonts, self.kit)
        self.view = "map"
        self.paused = False
        self.speed_index = ui.DEFAULT_SPEED_INDEX
        self.elapsed = 0.0
        self.selected_region = None
        self.selected_population = None
        self.selected_species = None
        self.running = True
        self.started = time.time()
        self.map_view.animator.sync(world)

    @property
    def tick_duration(self) -> float:
        return ui.BASE_TICK_DURATION / ui.SPEEDS[self.speed_index]

    def run(self) -> None:
        while self.running:
            delta = self.clock.tick(60) / 1000
            for event in pygame.event.get():
                self.handle(event)
            self.step(delta)
            self.draw()
            pygame.display.flip()
        pygame.quit()

    def step(self, delta: float) -> None:
        if not self.paused and self.world.is_running:
            self.elapsed += delta
            if self.elapsed >= self.tick_duration:
                self.elapsed = 0.0
                self.simulation.tick()
        self.map_view.animator.sync(self.world)
        self.map_view.animator.update(delta)

    def handle(self, event) -> None:
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not self.kit.click(event.pos):
                self.on_click(event.pos)
        elif event.type == pygame.MOUSEWHEEL and self.view == "tree":
            self.tree_view.scroll_by(-event.y * 48)

    def on_click(self, pos) -> None:
        if self.view == "tree":
            species_id = self.tree_view.species_at(pos)
            if species_id:
                self.selected_species = species_id
            return
        sprite = self.map_view.animator.sprite_at(pos)
        if sprite:
            self.selected_population = sprite.pop_id
            self.selected_region = sprite.region_id
            return
        region_id = self.map_view.region_at(pos)
        if region_id:
            self.selected_region = region_id
            self.selected_population = None

    def draw(self) -> None:
        mouse = pygame.mouse.get_pos()
        self.kit.begin(mouse, pygame.mouse.get_pressed()[0])
        self.screen.fill(theme.BACKGROUND)
        if self.view == "tree":
            self.tree_view.render(self.world, self.selected_species, mouse)
            self.panel.draw_species(self.world, self.world.species.get(self.selected_species))
        else:
            if self.selected_population and not self.world.get_population(self.selected_population):
                self.selected_population = None
            self.map_view.render(self.world, self.selected_region, self.selected_population, time.time() - self.started)
            self.panel.draw_map(self.world, self.selected_region, self.selected_population, self)
        self.topbar()

    def topbar(self) -> None:
        bar = pygame.Rect(0, 0, ui.SCREEN_X, ui.TOPBAR_HEIGHT)
        pygame.draw.rect(self.screen, theme.TOPBAR, bar)
        pygame.draw.line(self.screen, theme.CARD_BORDER, bar.bottomleft, bar.bottomright, 1)
        y = 10
        self.kit.button(self.screen, (12, y, 40, 36), icon="play" if self.paused else "pause",
                        on_click=self.toggle_pause, accent=self.paused)
        self.kit.button(self.screen, (60, y, 34, 36), icon="minus", on_click=lambda: self.change_speed(-1),
                        enabled=self.speed_index > 0)
        widgets.text(self.screen, self.fonts.bold, f"x{ui.SPEEDS[self.speed_index]:g}", (125, 28), theme.TEXT, "center")
        self.kit.button(self.screen, (156, y, 34, 36), icon="plus", on_click=lambda: self.change_speed(1),
                        enabled=self.speed_index < len(ui.SPEEDS) - 1)
        self.kit.button(self.screen, (206, y, 170, 36), label="Дерево эволюции" if self.view == "map" else "Карта мира",
                        on_click=self.toggle_view, accent=self.view == "tree")
        if self.view == "tree":
            self.kit.button(self.screen, (386, y, 34, 36), icon="minus", on_click=lambda: self.tree_view.change_zoom(0.8))
            widgets.text(self.screen, self.fonts.small, "масштаб", (453, 28), theme.MUTED, "center")
            self.kit.button(self.screen, (486, y, 34, 36), icon="plus", on_click=lambda: self.tree_view.change_zoom(1.25))
        total = sum(p.size for p in self.world.populations.values())
        alive = len({p.species.id for p in self.world.populations.values()})
        stats = f"тик {self.world.tick}    особей {total}    видов {alive} из {len(self.world.species)}"
        widgets.text(self.screen, self.fonts.body, stats, (ui.SCREEN_X - 16, 28), theme.TEXT, "midright")
        if not self.world.is_running:
            widgets.text(self.screen, self.fonts.bold, "Жизнь исчезла", (ui.SCREEN_X - 470, 28), theme.RED, "midright")

    def toggle_pause(self) -> None:
        self.paused = not self.paused

    def toggle_view(self) -> None:
        self.view = "tree" if self.view == "map" else "map"

    def change_speed(self, delta: int) -> None:
        self.speed_index = max(0, min(len(ui.SPEEDS) - 1, self.speed_index + delta))

    def water(self, delta: float) -> None:
        self._act(AdjustWater(self.selected_region, delta), f"влажность {delta:+.0f}", theme.CYAN)

    def plants(self) -> None:
        amount = constants.PLAYER_PLANTS_AMOUNT
        self._act(AddPlants(self.selected_region, amount), f"+{amount:.0f} растений", theme.GREEN)

    def capacity(self, delta: int) -> None:
        self._act(ResizeRegion(self.selected_region, delta), f"вместимость {delta:+d}", theme.GOLD)

    def nudge(self, gene: str, delta: float) -> None:
        name = ui.GENE_NAMES.get(gene, gene)
        self._act(NudgeGene(self.selected_population, gene, delta), f"{name} {delta:+.0f}", theme.GOLD)

    def _act(self, intent, label: str, color) -> None:
        self.world.submit(intent)
        self.simulation.apply_interventions()
        center = self.map_view.region_center(self.selected_region)
        self.map_view.animator.float_text(center[0], center[1], label, color)
