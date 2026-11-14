import config.constants as constants
from core.world import World
from domain.commands.commands import MigrateCommand, SplitCommand
from events.event import EventType
from systems.base import commands_of


class MigrationExecuteSystem:
    def process(self, world: World) -> None:
        for cmd in commands_of(world, SplitCommand):
            self._split(world, cmd)
        for cmd in commands_of(world, MigrateCommand):
            self._move(world, cmd)

    def _split(self, world: World, cmd: SplitCommand) -> None:
        population = world.get_population(cmd.population_id)
        target = world.get_region(cmd.target_region_id)
        if not population or not target:
            return
        size = min(cmd.size, population.size - constants.EXTINCTION_LIMIT)
        if size < constants.EXTINCTION_LIMIT:
            return
        population.size -= size
        population.cooldown = constants.MIGRATION_COOLDOWN
        colony = world.add_population(population.species, population.genome.copy(), target, size,
                                      satiety=population.satiety, stress=population.stress)
        colony.cooldown = constants.MIGRATION_COOLDOWN
        world.logger.log(
            world.tick, EventType.MIGRATION,
            f"Популяция {population.id} отправила {size} особей ({cmd.reason}) в {target}",
        )

    def _move(self, world: World, cmd: MigrateCommand) -> None:
        """
        Миграция переносит популяцию целиком. Часть особей теряется в пути,
        а оставшиеся получают максимальный стресс, повышающий шанс мутации.
        """
        population = world.get_population(cmd.population_id)
        target = world.get_region(cmd.target_region_id)
        if not population or not target:
            return
        population.decrease(world.round_random(population.size * constants.MIGRATION_LOSS))
        population.region = target
        population.stress = 1.0
        population.cooldown = constants.MIGRATION_COOLDOWN
        world.logger.log(
            world.tick, EventType.MIGRATION,
            f"Популяция {population.id} мигрировала в {target}",
        )
