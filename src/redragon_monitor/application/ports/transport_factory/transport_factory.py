from typing import Protocol

from redragon_monitor.application.ports.transport import Transport


class TransportFactory(Protocol):
    def __call__(self, path: str) -> Transport: ...
