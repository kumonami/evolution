import unittest
from types import SimpleNamespace
from ui.pygame.animation import Animator, creature_radius
from ui.pygame.series import feed_lines, species_series, total_series


def make_world(populations):
    return SimpleNamespace(populations={p.id: p for p in populations})


def make_population(pop_id, species_id=1, region_id=1, size=50):
    return SimpleNamespace(
        id=pop_id, size=size, influenced=False,
        region=SimpleNamespace(id=region_id),
        species=SimpleNamespace(id=species_id, type_id=1),
        genome=SimpleNamespace(temperature=50, power=50),
    )


SLOTS = {1: [(10, 10), (20, 20), (30, 30)], 2: [(100, 100), (110, 110)]}


class AnimatorTest(unittest.TestCase):
    def setUp(self):
        self.animator = Animator(SLOTS, (255, 255, 255), (255, 200, 0))

    def test_first_sync_has_no_effects(self):
        self.animator.sync(make_world([make_population(1), make_population(2)]))
        self.assertEqual(self.animator.effects, [])
        self.assertEqual({s.slot for s in self.animator.sprites.values()}, {0, 1})

    def test_new_population_and_new_species_make_effects(self):
        self.animator.sync(make_world([make_population(1)]))
        self.animator.sync(make_world([make_population(1), make_population(2, species_id=5)]))
        kinds = [e.kind for e in self.animator.effects]
        self.assertEqual(kinds.count("ring"), 2)
        self.assertIn("Новый вид #5", [e.text for e in self.animator.effects])

    def test_removed_population_becomes_fading_ghost(self):
        self.animator.sync(make_world([make_population(1)]))
        self.animator.sync(make_world([]))
        self.assertEqual(len(self.animator.ghosts), 1)
        self.animator.update(2.0)
        self.assertEqual(self.animator.ghosts, [])

    def test_migration_retargets_sprite_to_new_region_slot(self):
        population = make_population(1)
        self.animator.sync(make_world([population]))
        population.region = SimpleNamespace(id=2)
        self.animator.sync(make_world([population]))
        sprite = self.animator.sprites[1]
        self.assertEqual((sprite.tx, sprite.ty), (100, 100))
        before = sprite.x
        self.animator.update(0.1)
        self.assertGreater(sprite.x, before)

    def test_freed_slot_is_reused(self):
        self.animator.sync(make_world([make_population(1), make_population(2)]))
        self.animator.sync(make_world([make_population(2)]))
        self.animator.sync(make_world([make_population(2), make_population(3)]))
        self.assertEqual(self.animator.sprites[3].slot, 0)

    def test_radius_is_bounded(self):
        self.assertEqual(creature_radius(0), 10)
        self.assertEqual(creature_radius(10 ** 6), 28)


class SeriesTest(unittest.TestCase):
    def test_species_and_total_series(self):
        history = [
            {"tick": 0, "species": {1: {"size": 10}, 2: {"size": 5}}},
            {"tick": 10, "species": {1: {"size": 12}}},
        ]
        self.assertEqual(species_series(history, 2), [(0, 5), (10, 0)])
        self.assertEqual(total_series(history), [(0, 15), (10, 12)])

    def test_feed_filters_noise_and_keeps_order(self):
        entries = ["[1] [hunting] x", "[2] [evolution] a", "[3] [world] y", "[4] [player] b"]
        self.assertEqual(feed_lines(entries, 5), [(2, "evolution", "a"), (4, "player", "b")])
        self.assertEqual(feed_lines(entries, 1), [(4, "player", "b")])


if __name__ == "__main__":
    unittest.main()
