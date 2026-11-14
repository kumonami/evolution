from enum import Enum


class EventType(Enum):
    WORLD = "world"
    PLANTS = "plants"
    MIGRATION = "migration"
    DEATH = "death"
    EATING = "eating"
    EVOLUTION = "evolution"
    HUNTING = "hunting"
    BIRTH = "birth"
