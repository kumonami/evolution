import os
import unittest

from core.genome import GENES

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

try:
    import pygame
except ImportError:
    pygame = None


@unittest.skipIf(pygame is None, "pygame is not installed")
class AppButtonsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()

    def setUp(self):
        from core.simulation import Simulation
        from generation.world import WorldGenerator
        from ui.pygame.app import App
        self.world = WorldGenerator.generate(seed=2)
        self.simulation = Simulation(self.world)
        self.app = App(self.world, self.simulation)
        self.app.paused = True
        self.app.draw()

    def click(self, x, y):
        self.app.handle(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(x, y)))
        self.app.step(0.0)
        self.app.draw()

    def test_pause_button_toggles_pause(self):
        self.click(32, 28)
        self.assertFalse(self.app.paused)

    def test_speed_buttons_change_speed(self):
        before = self.app.speed_index
        self.click(173, 28)
        self.assertEqual(self.app.speed_index, before + 1)
        self.click(77, 28)
        self.assertEqual(self.app.speed_index, before)

    def test_tree_button_switches_view(self):
        self.click(290, 28)
        self.assertEqual(self.app.view, "tree")
        self.click(290, 28)
        self.assertEqual(self.app.view, "map")

    def test_clicking_creature_selects_population_and_region(self):
        sprite = next(iter(self.app.map_view.animator.sprites.values()))
        self.click(sprite.x, sprite.y)
        self.assertEqual(self.app.selected_population, sprite.pop_id)
        self.assertEqual(self.app.selected_region, sprite.region_id)

    def test_plants_button_adds_plants_to_selected_region(self):
        sprite = next(iter(self.app.map_view.animator.sprites.values()))
        self.click(sprite.x, sprite.y)
        region = self.world.get_region(sprite.region_id)
        region.plants_stock = 0
        zone = next(z for z in self.app.kit.zones if z.rect.width == 54)
        self.click(*zone.rect.center)
        self.assertGreater(region.plants_stock, 0)

    def test_gene_plus_button_nudges_selected_population(self):
        sprite = next(iter(self.app.map_view.animator.sprites.values()))
        self.click(sprite.x, sprite.y)
        population = self.world.get_population(sprite.pop_id)
        population.genome.fly = 0
        gene_buttons = sorted(
            (z for z in self.app.kit.zones if z.rect.size == (22, 19)),
            key=lambda z: (z.rect.top, -z.rect.left),
        )
        fly_plus = gene_buttons[GENES.index("fly") * 2]
        self.click(*fly_plus.rect.center)
        self.assertEqual(population.genome.fly, 10)
        self.assertTrue(population.influenced)

    def test_clicking_map_does_not_trigger_keyboard_actions(self):
        self.app.handle(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE, mod=0))
        self.assertTrue(self.app.paused)


if __name__ == "__main__":
    unittest.main()
