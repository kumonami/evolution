import argparse
from core.simulation import Simulation
from generation.world import WorldGenerator

TICK_DURATION = 0.5


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
    import ui.pygame.constants as ui_constants
    from ui.pygame.renderer import Renderer

    pygame.init()
    screen = pygame.display.set_mode((ui_constants.SCREEN_X, ui_constants.SCREEN_Y))
    pygame.display.set_caption("Evolution")
    clock = pygame.time.Clock()
    renderer = Renderer(screen)
    world = WorldGenerator.generate(seed=seed)
    simulation = Simulation(world)
    tick_duration = TICK_DURATION
    paused = False
    elapsed = 0.0
    running = True
    while running:
        delta = clock.tick(60) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key in (pygame.K_EQUALS, pygame.K_PLUS, pygame.K_KP_PLUS):
                    tick_duration = max(0.02, tick_duration / 2)
                elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    tick_duration = min(4.0, tick_duration * 2)
        if not paused and world.is_running:
            elapsed += delta
            if elapsed >= tick_duration:
                elapsed = 0.0
                simulation.tick()
        renderer.render(world, paused, tick_duration)
        pygame.display.flip()
    pygame.quit()


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
