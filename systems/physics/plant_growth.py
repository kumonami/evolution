from core.world import World


class PlantGrowthSystem:
    def process(self, world: World) -> None:
        for region in world.regions.values():
            region.grow_plants(region.plants_growth_rate)
