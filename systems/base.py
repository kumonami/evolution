from core.world import World


def commands_of(world: World, *command_types) -> list:
    return [c for c in world.commands if isinstance(c, command_types)]
