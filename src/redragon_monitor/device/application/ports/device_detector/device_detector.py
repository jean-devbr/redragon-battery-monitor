from typing import Protocol

from redragon_monitor.device.domain.device_interface import DeviceInterface


class DeviceDetector(Protocol):
    def find(self) -> list[DeviceInterface]: ...
