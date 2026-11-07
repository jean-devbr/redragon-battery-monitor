from pathlib import Path
from typing import Protocol


class Autostart(Protocol):
    def is_enabled(self) -> bool: ...

    def enable(self) -> Path: ...

    def disable(self) -> None: ...
