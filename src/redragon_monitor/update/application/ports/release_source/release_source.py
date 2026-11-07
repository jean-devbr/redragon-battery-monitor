from typing import Protocol

from redragon_monitor.update.domain.version import Version


class ReleaseSource(Protocol):
    def latest_version(self) -> Version: ...
