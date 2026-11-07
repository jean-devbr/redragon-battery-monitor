from typing import Protocol


class UpdateLauncher(Protocol):
    def launch(self, language: str) -> bool: ...

    def manual_command(self) -> str: ...
