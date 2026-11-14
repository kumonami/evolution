from collections import deque
from events.event import EventType
import config.constants as constants


class WorldLogger:
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.entries = deque(maxlen=constants.LOG_LIMIT)

    def log(self, tick: int, event_type: EventType, msg: str) -> str:
        entry = f"[{tick}] [{event_type.value}] {msg}"
        self.entries.append(entry)
        if self.verbose:
            print(entry)
        return entry
