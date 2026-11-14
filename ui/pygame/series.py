import re

LOG_PATTERN = re.compile(r"^\[(\d+)\] \[(\w+)\] (.*)$")
LOG_KINDS = ("evolution", "player", "migration", "death")


def species_series(history: list, species_id: int) -> list:
    return [(snap["tick"], snap["species"].get(species_id, {"size": 0})["size"]) for snap in history]


def total_series(history: list) -> list:
    return [(snap["tick"], sum(s["size"] for s in snap["species"].values())) for snap in history]


def feed_lines(entries, limit: int, kinds=LOG_KINDS) -> list:
    """
    Последние записи журнала мира нужных видов в формате (tick, kind, message).
    Частые записи об охоте и питании отбрасываются, чтобы не заливать ленту.
    """
    result = []
    for entry in reversed(entries):
        match = LOG_PATTERN.match(entry)
        if match and match.group(2) in kinds:
            result.append((int(match.group(1)), match.group(2), match.group(3)))
            if len(result) >= limit:
                break
    result.reverse()
    return result
