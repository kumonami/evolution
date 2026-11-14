import argparse
from core.simulation import Simulation
from generation.world import WorldGenerator


def run_headless(seed, ticks: int) -> None:
    world = WorldGenerator.generate(seed=seed)
    simulation = Simulation(world)
    simulation.run(ticks)
    alive = {p.species.id for p in world.populations.values()}
    total = sum(p.size for p in world.populations.values())
    print(f"seed={world.seed} tick={world.tick} populations={len(world.populations)} "
          f"individuals={total} species_alive={len(alive)} species_total={len(world.species)}")


def run_gui(seed) -> None:
    import pygame
    from ui.pygame.app import App

    pygame.init()
    world = WorldGenerator.generate(seed=seed)
    App(world, Simulation(world)).run()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--ticks", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=None)
    args = parser.parse_args()
    if args.headless:
        run_headless(args.seed, args.ticks)
    else:
        run_gui(args.seed)
