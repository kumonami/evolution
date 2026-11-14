import unittest
from core.simulation import Simulation
from domain.intents import AddPlants, AdjustWater, NudgeGene, ResizeRegion
from generation.world import WorldGenerator


class PlayerInterventionTest(unittest.TestCase):
    def setUp(self):
        self.world = WorldGenerator.generate(seed=1)
        self.simulation = Simulation(self.world)
        self.region = next(iter(self.world.regions.values()))
        self.population = self.world.populations_in(self.region)[0]

    def apply(self, intent):
        self.world.submit(intent)
        self.simulation.apply_interventions()

    def test_water_changes_humidity_and_swim_demand(self):
        before = self.region.biome.humidity
        self.apply(AdjustWater(self.region.id, 10))
        self.assertEqual(self.region.biome.humidity, min(100, before + 10))
        self.assertEqual(self.region.biome.ability_demand["swim"], self.region.biome.humidity / 200)

    def test_plants_added_up_to_limit(self):
        self.region.plants_stock = 0
        self.apply(AddPlants(self.region.id, 500))
        self.assertEqual(self.region.plants_stock, min(500, self.region.plants_limit))

    def test_capacity_has_lower_bound(self):
        self.apply(ResizeRegion(self.region.id, -10 ** 6))
        self.assertEqual(self.region.capacity, 500)

    def test_nudge_gene_clamped_and_marks_influence(self):
        self.population.genome.speed = 95
        self.apply(NudgeGene(self.population.id, "speed", 30))
        self.assertEqual(self.population.genome.speed, 100)
        self.assertTrue(self.population.influenced)

    def test_unknown_gene_is_ignored(self):
        self.apply(NudgeGene(self.population.id, "wings", 10))
        self.assertFalse(self.population.influenced)

    def test_water_marks_region_populations(self):
        self.apply(AdjustWater(self.region.id, -10))
        self.assertTrue(all(p.influenced for p in self.world.populations_in(self.region)))

    def test_influenced_population_gives_influenced_species(self):
        from domain.commands.commands import SpeciateCommand
        from systems.execute.speciation import SpeciationExecuteSystem
        self.population.influenced = True
        self.world.commands.append(SpeciateCommand(self.population.id))
        SpeciationExecuteSystem().process(self.world)
        self.assertEqual(self.population.species.origin, "influenced")
        self.assertFalse(self.population.influenced)

    def test_intents_applied_at_tick_start(self):
        self.world.submit(AddPlants(self.region.id, 100))
        self.simulation.tick()
        self.assertEqual(self.world.intents, [])


if __name__ == "__main__":
    unittest.main()


class SpeciesNudgeTest(unittest.TestCase):
    def setUp(self):
        from domain.intents import NudgeSpecies
        self.NudgeSpecies = NudgeSpecies
        self.world = WorldGenerator.generate(seed=1)
        self.simulation = Simulation(self.world)
        source = next(iter(self.world.populations.values()))
        region = next(r for r in self.world.regions.values() if r.id != source.region.id)
        self.species = source.species
        self.first = source
        self.second = self.world.add_population(source.species, source.genome.copy(), region, 30)
        self.other = next(p for p in self.world.populations.values() if p.species.id != source.species.id)

    def test_all_populations_of_species_change_and_others_do_not(self):
        self.first.genome.power = 40
        self.second.genome.power = 60
        other_power = self.other.genome.power
        self.world.submit(self.NudgeSpecies(self.species.id, "power", 10))
        self.simulation.apply_interventions()
        self.assertEqual(self.first.genome.power, 50)
        self.assertEqual(self.second.genome.power, 70)
        self.assertEqual(self.other.genome.power, other_power)
        self.assertTrue(self.first.influenced and self.second.influenced)
        self.assertFalse(self.other.influenced)

    def test_species_anchor_is_not_changed(self):
        anchor = self.species.anchor.power
        self.world.submit(self.NudgeSpecies(self.species.id, "power", 10))
        self.simulation.apply_interventions()
        self.assertEqual(self.species.anchor.power, anchor)

    def test_species_genome_is_size_weighted(self):
        self.first.size = 100
        self.second.size = 100
        self.first.genome.speed = 20
        self.second.genome.speed = 60
        self.assertAlmostEqual(self.world.species_genome(self.species.id).speed, 40)
