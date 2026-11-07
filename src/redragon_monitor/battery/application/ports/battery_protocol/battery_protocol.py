from typing import Protocol

from redragon_monitor.battery.domain.battery_reading import BatteryReading


class BatteryProtocol(Protocol):
    def build_query(self) -> bytes: ...

    def is_response(self, data: bytes) -> bool: ...

    def parse(self, data: bytes) -> BatteryReading: ...
