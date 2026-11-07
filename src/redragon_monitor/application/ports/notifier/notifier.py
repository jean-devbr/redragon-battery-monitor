from typing import Protocol


class Notifier(Protocol):
    def low_battery(self, percent: int) -> bool: ...
