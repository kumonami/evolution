import unittest
import config.constants as constants
from core.genome import Genome
from core.world import World
from generation.biome import BiomeGenerator
from generation.region import RegionGenerator
from systems.physics.plant_growth import PlantGrowthSystem
from systems.think.hunting import HuntingThinkSystem


def build(attack_power: float, seed: int = 1):
    world = World(seed=seed)
    biome = BiomeGenerator.generate(world.rng)
    region = RegionGenerator.generate(world.rng, 1, biome, 0, 0)
    world.add_region(region)
    prey_genome = Genome(40, 40, 40, 50, biome.temperature)
    predator_genome = Genome(40, 50, attack_power, 50, biome.temperature)
    prey = world.register_species(constants.HERBIVORE_TYPE, prey_genome)
    predator = world.register_species(constants.CARNIVORE_TYPE, predator_genome)
    world.add_population(prey, prey_genome, region, 1000)
    hunter = world.add_population(predator, predator_genome, region, 100)
    return world, hunter


def kills_for(attack_power: float) -> int:
    total = 0
    for seed in range(1, 21):
        world, hunter = build(attack_power, seed)
        HuntingThinkSystem().process(world)
        total += sum(sum(e.payload.kills.values()) for e in world.events)
    return total


class HuntingStrengthTest(unittest.TestCase):
    def test_stronger_predator_kills_more_prey(self):
        weak, strong = kills_for(20), kills_for(100)
        self.assertGreater(strong, weak * 1.5)

    def test_food_gained_never_exceeds_need(self):
        world, hunter = build(100)
        HuntingThinkSystem().process(world)
        for event in world.events:
            self.assertLessEqual(event.payload.food_amount, hunter.meat_need + 1e-9)


class PlantRegrowthTest(unittest.TestCase):
    def setUp(self):
        self.world = World(seed=1)
        biome = BiomeGenerator.generate(self.world.rng)
        self.region = RegionGenerator.generate(self.world.rng, 1, biome, 0, 0)
        self.world.add_region(self.region)

    def test_grazed_out_region_regrows_slowly(self):
        self.region.plants_stock = 0
        PlantGrowthSystem().process(self.world)
        expected = self.region.plants_growth_rate * constants.PLANT_MIN_GROWTH
        self.assertAlmostEqual(self.region.plants_stock, expected)

    def test_standing_biomass_regrows_at_full_rate(self):
        self.region.plants_stock = self.region.plants_growth_rate * constants.PLANT_BIOMASS_TICKS
        before = self.region.plants_stock
        PlantGrowthSystem().process(self.world)
        self.assertAlmostEqual(self.region.plants_stock - before, self.region.plants_growth_rate)

    def test_initial_stock_is_a_stable_starting_biomass(self):
        reference = self.region.plants_growth_rate * constants.PLANT_BIOMASS_TICKS
        self.assertEqual(self.region.plants_stock, min(self.region.plants_limit, reference))


if __name__ == "__main__":
    unittest.main()
