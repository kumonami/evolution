import time
import pygame
import config.constants as constants
import ui.pygame.constants as ui
import ui.pygame.theme as theme
import ui.pygame.widgets as widgets
from core.simulation import Simulation
from core.world import World
from domain.intents import AddPlants, AdjustWater, NudgeGene, NudgeSpecies, ResizeRegion
from ui.pygame.animation import Animator
from ui.pygame.layout import Layout
from ui.pygame.map_view import MapView
from ui.pygame.panel import SidePanel
from ui.pygame.tree_view import TreeView


class App:
    """
    Окно игры. Весь ввод идёт мышью через кнопки: верхняя панель управляет
    временем, экраном, полноэкранным режимом и скрытием правой панели,
    правая панель вмешивается в выбранный регион, популяцию или весь вид.
    Окно меняет размер, карта перестраивается под него. Действия применяются
    сразу, в том числе на паузе.
    """

    def __init__(self, world: World, simulation: Simulation):
        self.world = world
        self.simulation = simulation
        self.windowed_size = (ui.SCREEN_X, ui.SCREEN_Y)
        self.fullscreen = False
        self.screen = pygame.display.set_mode(self.windowed_size, pygame.RESIZABLE)
        pygame.display.set_caption("Evolution")
        self.clock = pygame.time.Clock()
        self.fonts = theme.Fonts()
        self.kit = widgets.Ui(self.fonts)
        self.animator = Animator({}, theme.TEXT, theme.GOLD)
        self.view = "map"
        self.paused = False
        self.speed_index = ui.DEFAULT_SPEED_INDEX
        self.elapsed = 0.0
        self.selected_region = None
        self.selected_population = None
        self.selected_species = None
        self.scope = "population"
        self.panel_visible = True
        self.running = True
        self.started = time.time()
        self.tree_view = None
        self.build_views()
        self.animator.sync(world)

    @property
    def tick_duration(self) -> float:
        return ui.BASE_TICK_DURATION / ui.SPEEDS[self.speed_index]

    def build_views(self) -> None:
        width, height = self.screen.get_size()
        self.layout = Layout(width, height, self.panel_visible)
        self.map_view = MapView(self.screen, self.fonts, self.world, self.layout, self.animator)
        scroll, zoom = (self.tree_view.scroll, self.tree_view.zoom) if self.tree_view else (0.0, 1.0)
        self.tree_view = TreeView(self.screen, self.fonts, self.layout, scroll, zoom)
        self.panel = SidePanel(self.screen, self.fonts, self.kit, self.layout)

    def resize(self, width: int, height: int) -> None:
        width, height = max(width, ui.MIN_WIDTH), max(height, ui.MIN_HEIGHT)
        if not self.fullscreen:
            self.windowed_size = (width, height)
        self.screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
        self.build_views()

    def on_window_resized(self, width: int, height: int) -> None:
        """
        Реакция на изменение окна пользователем. Если размер уже совпадает
        с текущей раскладкой, ничего не перестраивается, чтобы смена режима
        не зациклилась на собственных событиях изменения размера.
        """
        if width < ui.MIN_WIDTH or height < ui.MIN_HEIGHT:
            self.resize(width, height)
            return
        self.windowed_size = (width, height)
        self.screen = pygame.display.get_surface()
        if self.screen.get_size() != (self.layout.width, self.layout.height):
            self.build_views()

    def toggle_fullscreen(self) -> None:
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode(self.windowed_size, pygame.RESIZABLE)
        self.build_views()

    def toggle_panel(self) -> None:
        self.panel_visible = not self.panel_visible
        self.build_views()

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
        self.animator.sync(self.world)
        self.animator.update(delta)

    def handle(self, event) -> None:
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.VIDEORESIZE and not self.fullscreen:
            self.on_window_resized(event.w, event.h)
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
        sprite = self.animator.sprite_at(pos)
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
            if self.panel_visible:
                self.panel.draw_species(self.world, self.world.species.get(self.selected_species), self)
        else:
            if self.selected_population and not self.world.get_population(self.selected_population):
                self.selected_population = None
            self.map_view.render(self.world, self.selected_region, self.selected_population, time.time() - self.started)
            if self.panel_visible:
                self.panel.draw_map(self.world, self.selected_region, self.selected_population, self)
        self.topbar()

    def topbar(self) -> None:
        bar = self.layout.topbar
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
        right = self.layout.width - 12
        self.kit.button(self.screen, (right - 150, y, 150, 36), label="Окно" if self.fullscreen else "Полный экран",
                        on_click=self.toggle_fullscreen, active=self.fullscreen)
        right -= 158
        self.kit.button(self.screen, (right - 100, y, 100, 36), label="Панель", on_click=self.toggle_panel,
                        active=self.panel_visible)
        right -= 116
        total = sum(p.size for p in self.world.populations.values())
        alive = len({p.species.id for p in self.world.populations.values()})
        stats = f"тик {self.world.tick}    особей {total}    видов {alive} из {len(self.world.species)}"
        widgets.text(self.screen, self.fonts.body, stats, (right, 28), theme.TEXT, "midright")
        if not self.world.is_running:
            widgets.text(self.screen, self.fonts.bold, "Жизнь исчезла", (right - 360, 28), theme.RED, "midright")

    def toggle_pause(self) -> None:
        self.paused = not self.paused

    def toggle_view(self) -> None:
        self.view = "tree" if self.view == "map" else "map"

    def change_speed(self, delta: int) -> None:
        self.speed_index = max(0, min(len(ui.SPEEDS) - 1, self.speed_index + delta))

    def set_scope(self, scope: str) -> None:
        self.scope = scope

    def water(self, delta: float) -> None:
        self._act(AdjustWater(self.selected_region, delta), f"влажность {delta:+.0f}", theme.CYAN)

    def plants(self) -> None:
        amount = constants.PLAYER_PLANTS_AMOUNT
        self._act(AddPlants(self.selected_region, amount), f"+{amount:.0f} растений", theme.GREEN)

    def capacity(self, delta: int) -> None:
        self._act(ResizeRegion(self.selected_region, delta), f"вместимость {delta:+d}", theme.GOLD)

    def nudge(self, gene: str, delta: float) -> None:
        population = self.world.get_population(self.selected_population)
        if not population:
            return
        name = ui.GENE_NAMES.get(gene, gene)
        if self.scope == "species":
            intent = NudgeSpecies(population.species.id, gene, delta)
            label = f"{name} {delta:+.0f} всему виду"
        else:
            intent = NudgeGene(population.id, gene, delta)
            label = f"{name} {delta:+.0f}"
        self._act(intent, label, theme.GOLD, population.region.id)

    def nudge_species(self, gene: str, delta: float) -> None:
        if self.selected_species not in self.world.species:
            return
        name = ui.GENE_NAMES.get(gene, gene)
        self._act(NudgeSpecies(self.selected_species, gene, delta), f"{name} {delta:+.0f} всему виду", theme.GOLD)

    def _act(self, intent, label: str, color, region_id=None) -> None:
        self.world.submit(intent)
        self.simulation.apply_interventions()
        region_id = region_id or self.selected_region
        if region_id and self.view == "map":
            center = self.map_view.region_center(region_id)
            self.animator.float_text(center[0], center[1], label, color)
