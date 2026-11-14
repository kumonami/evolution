import pygame
import config.constants as constants
import ui.pygame.constants as ui
from core.genome import GENES
from core.simulation import Simulation
from core.world import World
from domain.intents import AddPlants, AdjustWater, NudgeGene, ResizeRegion
from ui.pygame.renderer import Renderer
from ui.pygame.tree_view import TreeView

GENE_KEYS = {
    pygame.K_1: GENES[0], pygame.K_2: GENES[1], pygame.K_3: GENES[2], pygame.K_4: GENES[3],
    pygame.K_5: GENES[4], pygame.K_6: GENES[5], pygame.K_7: GENES[6], pygame.K_8: GENES[7],
    pygame.K_9: GENES[8],
}
TICK_DURATION = 0.5


class App:
    """
    Окно игры: карта мира с панелью выбора и вмешательства игрока,
    а по клавише T экран дерева эволюции. Действия игрока отправляются
    в мир как запросы и применяются сразу, даже на паузе.
    """

    def __init__(self, world: World, simulation: Simulation):
        self.world = world
        self.simulation = simulation
        self.screen = pygame.display.set_mode((ui.SCREEN_X, ui.SCREEN_Y))
        pygame.display.set_caption("Evolution")
        self.clock = pygame.time.Clock()
        self.renderer = Renderer(self.screen)
        self.tree_view = TreeView(self.screen)
        self.view = "map"
        self.paused = False
        self.tick_duration = TICK_DURATION
        self.elapsed = 0.0
        self.selected_region = None
        self.selected_population = None
        self.message = ""
        self.message_time = 0.0
        self.running = True

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
        if self.message_time > 0:
            self.message_time -= delta
            if self.message_time <= 0:
                self.message = ""
        if self.paused or not self.world.is_running:
            return
        self.elapsed += delta
        if self.elapsed >= self.tick_duration:
            self.elapsed = 0.0
            self.simulation.tick()

    def draw(self) -> None:
        if self.view == "tree":
            self.tree_view.render(self.world, pygame.mouse.get_pos())
            return
        if self.selected_population and not self.world.get_population(self.selected_population):
            self.selected_population = None
        self.renderer.render(self.world, self.selected_region, self.selected_population,
                             self.paused, self.tick_duration, self.message)

    def handle(self, event) -> None:
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.KEYDOWN:
            self.on_key(event.key, bool(event.mod & pygame.KMOD_SHIFT))
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.view == "map":
            self.on_click(event.pos)

    def on_click(self, pos) -> None:
        hit = self.renderer.hit_test(pos)
        if not hit:
            return
        kind, ident = hit
        if kind == "population":
            population = self.world.get_population(ident)
            self.selected_population = ident
            self.selected_region = population.region.id if population else None
        else:
            self.selected_region = ident
            self.selected_population = None

    def on_key(self, key: int, shift: bool) -> None:
        if key == pygame.K_t:
            self.view = "tree" if self.view == "map" else "map"
        elif key == pygame.K_SPACE:
            self.paused = not self.paused
        elif key in (pygame.K_EQUALS, pygame.K_PLUS, pygame.K_KP_PLUS):
            self.tick_duration = max(0.02, self.tick_duration / 2)
        elif key in (pygame.K_MINUS, pygame.K_KP_MINUS):
            self.tick_duration = min(4.0, self.tick_duration * 2)
        elif self.view == "map":
            self.on_intervention_key(key, shift)

    def on_intervention_key(self, key: int, shift: bool) -> None:
        sign = -1 if shift else 1
        region = self.selected_region
        if key == pygame.K_h and region:
            self.act(AdjustWater(region, sign * constants.PLAYER_WATER_STEP), "water")
        elif key == pygame.K_g and region:
            self.act(AddPlants(region, constants.PLAYER_PLANTS_AMOUNT), "plants +500")
        elif key == pygame.K_c and region:
            self.act(ResizeRegion(region, sign * constants.PLAYER_CAPACITY_STEP), "capacity")
        elif key in GENE_KEYS and self.selected_population:
            gene = GENE_KEYS[key]
            delta = sign * constants.PLAYER_GENE_STEP
            self.act(NudgeGene(self.selected_population, gene, delta), f"{gene} {delta:+.0f}")

    def act(self, intent, label: str) -> None:
        self.world.submit(intent)
        self.simulation.apply_interventions()
        self.message = f"applied: {label}"
        self.message_time = ui.MESSAGE_LIFETIME
