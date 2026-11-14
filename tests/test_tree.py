import unittest
from core.genome import Genome
from core.tree import layout_tree
from core.world import World


class TreeLayoutTest(unittest.TestCase):
    def test_children_follow_parent_in_birth_order(self):
        world = World(seed=1)
        genome = Genome(50, 50, 50, 50, 50)
        root = world.register_species(1, genome)
        world.tick = 5
        first = world.register_species(1, genome, parent_id=root.id)
        world.tick = 9
        second = world.register_species(1, genome, parent_id=root.id)
        grandchild = world.register_species(1, genome, parent_id=first.id)
        rows = layout_tree(world)
        self.assertEqual([r.species.id for r in rows], [root.id, first.id, grandchild.id, second.id])
        self.assertEqual([r.depth for r in rows], [0, 1, 2, 1])
        self.assertEqual([r.row for r in rows], [0, 1, 2, 3])

    def test_extinct_species_ends_at_extinction_tick(self):
        world = World(seed=1)
        species = world.register_species(1, Genome(50, 50, 50, 50, 50))
        species.extinct_tick = 7
        world.tick = 20
        self.assertEqual(layout_tree(world)[0].end, 7)

    def test_alive_species_ends_at_current_tick(self):
        world = World(seed=1)
        world.register_species(1, Genome(50, 50, 50, 50, 50))
        world.tick = 20
        self.assertEqual(layout_tree(world)[0].end, 20)


if __name__ == "__main__":
    unittest.main()
